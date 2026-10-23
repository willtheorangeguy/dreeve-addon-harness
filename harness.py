"""Portable Dreeve sandbox controller; Python 3.10+, Docker Compose v2, no host pip dependencies."""

import argparse
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def compose_command(*args):
    command = ['docker', 'compose', '--project-directory', str(ROOT),
               '--env-file', str(ROOT / '.env'), '-f', str(ROOT / 'compose.yaml')]
    if (ROOT / 'compose.override.yaml').exists():
        command += ['-f', str(ROOT / 'compose.override.yaml')]
    return command + list(args)


def compose(*args, **kwargs):
    return subprocess.run(compose_command(*args), cwd=ROOT, check=True, **kwargs)


def init():
    env_path = ROOT / '.env'
    if not env_path.exists():
        image = json.loads((ROOT / 'upstream.json').read_text())['application_image']
        password = 'HarnessDemo123!'
        # The plaintext password is passed in the child environment, never in shell arguments.
        hashed = subprocess.run(
            ['docker', 'run', '--rm', '-e', 'DEMO_PASSWORD', '--entrypoint', 'php', image,
             '-r', 'echo password_hash(getenv("DEMO_PASSWORD"), PASSWORD_BCRYPT);'],
            env=os.environ | {'DEMO_PASSWORD': password}, capture_output=True, text=True, check=True)
        password_hash = hashed.stdout.strip()
        if not re.fullmatch(r'\$2[aby]\$\d\d\$[./A-Za-z0-9]{53}', password_hash):
            raise RuntimeError('Dreeve did not produce a valid bcrypt password hash')
        content = (ROOT / '.env.example').read_text(encoding='utf-8')
        content = content.replace('GENERATE_APP_SECRET', secrets.token_hex(32))
        content = content.replace('GENERATE_DREEVE_API_KEY', 'drv_' + secrets.token_hex(32))
        # Single quotes preserve bcrypt's dollar signs during Compose interpolation.
        content = content.replace('GENERATE_ADMIN_PASSWORD_HASH', "'" + password_hash + "'")
        with env_path.open('x', encoding='utf-8') as stream:
            stream.write(content)
        env_path.chmod(0o600)
    if 'GENERATE_' in env_path.read_text(encoding='utf-8'):
        raise RuntimeError('The .env file still contains generation placeholders; remove it and rerun init')
    for folder in ['runtime', 'reports', 'watch']:
        path = ROOT / folder
        path.mkdir(exist_ok=True)
        path.chmod(0o777)


def seed():
    compose('run', '--rm', '-T', 'seed')
    compose('exec', '-T', 'app', 'bin/console', 'app:import:files')
    compose('run', '--rm', '-T', 'seed', 'python', 'seed.py', '--verify')


def ready():
    compose('up', '-d', '--build', '--wait', '--wait-timeout', '300', 'app', 'daemon')
    # Tool images are built explicitly: `run` must work on a fresh checkout.
    compose('--profile', 'tools', '--profile', 'addon', 'build', 'seed', 'test', 'example-addon')
    seed()
    compose('--profile', 'addon', 'up', '-d', '--wait', '--wait-timeout', '120', 'example-addon')


def clear_generated():
    for name in ('runtime', 'reports', 'watch'):
        target = ROOT / name
        if target.is_symlink() or target.resolve().parent != ROOT.resolve():
            raise RuntimeError(f'Refusing to clear redirected directory: {name}')
        if not target.exists():
            continue
        for child in target.iterdir():
            if child.is_symlink():
                child.unlink()
            elif not child.resolve().is_relative_to(target.resolve()):
                raise RuntimeError(f'Refusing to clear redirected child in {name}')
            elif child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['init', 'up', 'seed', 'test', 'status', 'logs', 'config', 'down', 'reset'])
    parser.add_argument('--yes', action='store_true', help='Required for reset: removes only this sandbox data')
    args = parser.parse_args()
    if args.command == 'reset' and not args.yes:
        parser.error('reset deletes this sandbox data; pass --yes')
    init()
    if args.command in ('up', 'test'):
        ready()
        if args.command == 'test':
            try:
                compose('run', '--rm', '-T', 'test')
            finally:
                with (ROOT / 'reports/compose.log').open('w', encoding='utf-8') as stream:
                    compose('--profile', '*', 'logs', '--no-color', stdout=stream, stderr=subprocess.STDOUT)
        else:
            print('Ready. Dreeve: http://localhost:8103; addon: http://localhost:9103 (see .env for ports).')
    elif args.command == 'seed':
        compose('--profile', 'tools', 'build', 'seed')
        seed()
    elif args.command == 'reset':
        compose('--profile', '*', 'down', '--volumes', '--remove-orphans')
        clear_generated()
        print('Sandbox data removed. Credentials in .env were kept. Run: python harness.py up')
    elif args.command == 'down':
        compose('--profile', '*', 'down', '--remove-orphans')
    elif args.command == 'status':
        compose('--profile', '*', 'ps', '-a')
    elif args.command == 'logs':
        compose('--profile', '*', 'logs', '--tail', '100', '-f')
    elif args.command == 'config':
        compose('config', '--quiet')
    else:
        print('Initialized .env and local runtime directories.')


if __name__ == '__main__':
    try:
        main()
    except (subprocess.CalledProcessError, OSError, RuntimeError, ValueError) as error:
        print(f'Harness failed: {error}', file=sys.stderr)
        raise SystemExit(1)
