import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import harness


class ControllerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.patch_root = patch.object(harness, 'ROOT', self.root)
        self.patch_root.start()
        self.addCleanup(self.patch_root.stop)
        self.addCleanup(self.temporary.cleanup)

    def test_override_is_automatically_included(self):
        command = harness.compose_command('config', '--quiet')
        self.assertNotIn(str(self.root / 'compose.override.yaml'), command)
        (self.root / 'compose.override.yaml').touch()
        self.assertIn(str(self.root / 'compose.override.yaml'), harness.compose_command('config'))
        self.assertEqual(command[-2:], ['config', '--quiet'])

    def test_initialization_quotes_hash_and_preserves_credentials(self):
        source = Path(__file__).resolve().parents[2]
        (self.root / '.env.example').write_bytes((source / '.env.example').read_bytes())
        (self.root / 'upstream.json').write_text(json.dumps({'application_image': 'example/image@sha256:test'}))
        hashed = '$2y$12$' + 'a' * 53
        with patch.object(subprocess, 'run', return_value=subprocess.CompletedProcess([], 0, hashed)) as run:
            harness.init()
            content = (self.root / '.env').read_text()
            self.assertIn("ADMIN_PASSWORD_HASH='" + hashed + "'", content)
            self.assertNotIn('GENERATE_', content)
            self.assertIn('DREEVE_API_KEY=drv_', content)
            harness.init()
            self.assertEqual((self.root / '.env').read_text(), content)
            self.assertEqual(run.call_count, 1)
            self.assertNotIn('HarnessDemo123!', repr(run.call_args.args))

    def test_reset_requires_flag_before_initialization(self):
        with patch('sys.argv', ['harness.py', 'reset']), patch.object(harness, 'init') as init:
            with self.assertRaises(SystemExit) as caught:
                harness.main()
            self.assertEqual(caught.exception.code, 2)
            init.assert_not_called()

    def test_reset_only_removes_generated_files(self):
        for name in ('runtime', 'reports', 'watch'):
            directory = self.root / name
            directory.mkdir()
            (directory / 'generated').write_text('synthetic')
        (self.root / 'keep.txt').write_text('keep')
        harness.clear_generated()
        self.assertEqual((self.root / 'keep.txt').read_text(), 'keep')
        self.assertTrue(all(not list((self.root / name).iterdir()) for name in ('runtime', 'reports', 'watch')))

    def test_reset_rejects_redirected_directory(self):
        with tempfile.TemporaryDirectory() as other:
            try:
                os.symlink(other, self.root / 'runtime', target_is_directory=True)
            except OSError:
                self.skipTest('Creating directory symlinks is not permitted on this host')
            with self.assertRaises(RuntimeError):
                harness.clear_generated()


if __name__ == '__main__':
    unittest.main()
