# Usage and configuration

| Command | Behavior |
| --- | --- |
| `python harness.py init` | Generate `.env` and local folders without starting the stack |
| `python harness.py up` | Start app/daemon, seed missing fixtures, verify the API, start the addon |
| `python harness.py seed` | Recreate missing fixture activities and verify all seed values |
| `python harness.py test` | Start/seed if needed and run containerized integration checks |
| `python harness.py status` | Show all services, including stopped one-shot tools |
| `python harness.py logs` | Follow the last 100 log lines for all services |
| `python harness.py config` | Validate the merged Compose configuration without printing secrets |
| `python harness.py down` | Stop services; retain volumes and generated files |
| `python harness.py reset --yes` | Remove this sandbox's volumes and generated data; retain `.env` |

## Configuration

| Variable | Default / meaning |
| --- | --- |
| `COMPOSE_PROJECT_NAME` | `dreeve-addon-harness`; use a unique value for another copy |
| `APP_PORT` | Host loopback port `8103` |
| `ADDON_PORT` | Host loopback port `9103` |
| `PUBLIC_URL` | `http://localhost:8103`; change with `APP_PORT` |
| `DEMO_USERNAME` | `demo` |
| `DEMO_PASSWORD` | `HarnessDemo123!`; used by login tests |
| `ADMIN_PASSWORD_HASH` | Generated bcrypt hash; quote it in `.env` |
| `APP_SECRET` | Random signing secret generated on first use |
| `DREEVE_API_KEY` | Generated `drv_` key with 64 hex characters |
| `SEED_END_DATE` | Optional `YYYY-MM-DD`; otherwise freezes first seed's UTC date |
| `CHECK_EXAMPLE_ADDON` | `true`; set `false` when replacing the example with a different API |

Do not commit `.env` or the generated `runtime`, `watch`, and `reports` directories.
The convenience `runtime/credentials.json` is a credential for this sandbox.
Container environment values are visible to users with Docker access.

## Persistence

Dreeve uses named volumes for its database, imported files, and render cache.
The host `watch/` directory is shared by Dreeve, seed/test tools, and any addon
that mounts it. `runtime/seed-manifest.json` freezes fixture dates between starts.

Seeding uses deterministic filenames and checks existing activity names before
queueing files. Re-running seed therefore preserves existing fixture identities.
To choose a different seed date, run `reset --yes`, change `SEED_END_DATE`, and run `up`.

## Direct Compose commands

After `harness.py init`, you can use commands such as:

```sh
docker compose exec app bin/console app:import:files
docker compose --profile tools run --rm seed python seed.py --verify
```

If `compose.override.yaml` exists, Docker Compose also loads that filename by
default. The controller lists it explicitly and behaves the same from any working directory.
