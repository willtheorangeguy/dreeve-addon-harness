# Configuration

The controller reads `harness.json`, generates `.env` from `.env.example` on first use, and passes explicit file paths to Docker Compose. There is no generic CLI configuration override: `--yes` only acknowledges reset.

## Precedence

For Compose interpolation, your shell environment takes precedence over `.env`; expressions with a fallback in `compose.yaml` use that fallback when unset or empty. `compose.override.yaml`, when present, merges after `compose.yaml` and can replace container settings. The controller supplies the project directory and environment-file path explicitly, so invocation from another working directory uses this checkout.

Seed date selection is `SEED_END_DATE` > the saved manifest's `end_date` > today's UTC date. A configured date that disagrees with the existing manifest fails instead of replacing it.

## Environment file

Names are explicit uppercase identifiers, not a generated prefix scheme. Example values below describe the checked-in template or the controller's generated format.

| Option | Type | Default | Description |
| --- | --- | --- | --- |
| `COMPOSE_PROJECT_NAME` | string | `dreeve-addon-harness` | Namespace for Compose services and volumes. Example: `dreeve-addon-harness-copy`. Use a unique value for another sandbox. |
| `APP_PORT` | port | `8103` | App host port, bound to `127.0.0.1`. Example: `8104`. |
| `ADDON_PORT` | port | `9103` | Addon host port, bound to `127.0.0.1`. Example: `9104`. |
| `PUBLIC_URL` | URL | `http://localhost:8103` | Browser-facing app URL and API request Origin. Change alongside `APP_PORT`. Example: `http://localhost:8104`. |
| `DEMO_USERNAME` | string | `demo` | Becomes Dreeve's `ADMIN_USERNAME`; also used by login tests. Example: `demo`. |
| `DEMO_PASSWORD` | string | `HarnessDemo123!` | Plaintext login-test password. Must match the separately stored bcrypt hash. Example: `HarnessDemo123!`. |
| `ADMIN_PASSWORD_HASH` | bcrypt string | generated | Controller runs PHP `password_hash` in the pinned Dreeve image. Store single-quoted, with a format such as `$2y$10$` followed by 53 bcrypt characters. |
| `APP_SECRET` | string | generated | Random 64-character hexadecimal signing secret. Generate with `python harness.py init`. |
| `DREEVE_API_KEY` | string | generated | `drv_` plus 64 hexadecimal characters. Generate with `python harness.py init`; sent as a Bearer token. |
| `SEED_END_DATE` | ISO date or empty | empty | Example: `2026-10-23`. Empty freezes the first seed's UTC date in the manifest. |
| `CHECK_EXAMPLE_ADDON` | string | `true` | Only case-insensitive `true` enables example-interface assertions. Use `false` for a custom interface. The supplied replacement-addon check still runs. |

Compose rejects invalid port mappings or interpolation errors when `config --quiet` runs. An invalid seed date raises `ValueError` in the seed tool. Unresolved `GENERATE_` markers in an existing `.env` are fatal; the controller does not overwrite an existing file or regenerate a changed password hash.

!!! warning
    Editing `DEMO_PASSWORD` does not regenerate `ADMIN_PASSWORD_HASH`. Keep them in sync, and single-quote the hash so Compose preserves its dollar signs. Do not copy `.env.example` unchanged into `.env`.

## Container environment

The base Compose file maps host settings into these service values. A custom override can change them.

| Option | Type | Default | Description |
| --- | --- | --- | --- |
| `IMPORT_MODE` | string | `files` | Dreeve imports local files. Example: `files`. |
| `APP_ENV` | string | `prod` | Upstream runtime mode. Example: `prod`. |
| `TZ` | string | `UTC` | App and daemon time zone. Example: `UTC`. |
| `APP_URL` | URL | app: `PUBLIC_URL`; tools: `http://app:8080` | Upstream browser URL versus internal API client base. |
| `TARGET` | string | `dreeve` | Selects the Dreeve adapter in shared tooling. Example: `dreeve`. Other adapters in shared source are not configured by this repository. |
| `FRONTEND_URL` | URL | `http://app:8080` | Internal web URL for tests. |
| `PYTHONPATH` | path | `/harness/scripts` | Makes shared helpers importable in tools containers. |
| `PYTHONDONTWRITEBYTECODE` | string | `1` | Prevents bytecode writes into mounted source. |

`ADMIN_USERNAME` receives `DEMO_USERNAME`. The `test` service additionally receives `DEMO_USERNAME` and `DEMO_PASSWORD`; the app receives the hash, not the plaintext password.

## Controller configuration

`harness.json` describes the platform adapter. These are repository implementation settings, not ordinary user preferences.

| Option | Type | Default | Description |
| --- | --- | --- | --- |
| `platform` | string | `dreeve` | Platform metadata. Example: `dreeve`. |
| `services` | array | `["app", "daemon"]` | Services started and awaited before tools build. |
| `restart_services` | array | `["app", "daemon"]` | Services restarted during the persistence audit. |
| `build_services` | array | `["seed", "test", "example-addon"]` | Images built by the startup workflow. |
| `seed_mode` | string | `files` | Runs explicit Dreeve file import and verification after fixture generation. |
| `generated_dirs` | array | `["runtime", "reports", "watch"]` | Direct children created by init and cleared by reset. Redirected directories are refused. |

`upstream.json` records the verified release, source revision, image digest, verification date, deployment reference, and extraction provenance. `application_image` is used for credential generation; `compose.yaml` independently pins the running app image. Keep the two image references aligned during an upstream update.

## Examples

Generate credentials before changing non-secret settings:

```sh
python harness.py init
```

Edit these lines in the generated file, preserving its generated secret values:

```dotenv title=".env (non-secret settings)"
COMPOSE_PROJECT_NAME=dreeve-addon-harness-copy
APP_PORT=8104
ADDON_PORT=9104
PUBLIC_URL=http://localhost:8104
CHECK_EXAMPLE_ADDON=false
SEED_END_DATE=2026-10-23
```

Then validate without printing secrets:

```sh
python harness.py config
python harness.py up
```

Choose `SEED_END_DATE` before the first seed. To change an existing fixture date, reset the sandbox before starting it again. See [usage](./usage.md#persistence).

## Credential storage

`.env`, `runtime/credentials.json`, and container environments contain sandbox secrets. They are ignored by Git. Do not paste them into issues. Docker users can inspect container environments. Generated directories are made writable for containers; treat the checkout as local development data.
