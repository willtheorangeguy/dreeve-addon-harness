# Usage

The controller resolves paths relative to `harness.py`, so commands behave the same from another working directory. Every command except `test-unit` and argument-parser help initializes the sandbox first. A fresh `init`, `status`, or `config` therefore needs Docker to generate the bcrypt hash.

## Commands

| Command | Behavior |
| --- | --- |
| `python harness.py init` | Generate `.env` and local folders without starting the stack; uses Docker for bcrypt generation |
| `python harness.py up` | Start app/daemon, seed missing fixtures, verify the API, start the addon |
| `python harness.py seed` | Recreate missing fixture activities and verify all seed values |
| `python harness.py test-unit` | Run host unit tests without Docker |
| `python harness.py test-override` | Verify reseeding and the supplied replacement addon |
| `python harness.py test` | Verify reseeding, integration behavior, restart persistence, and addon replacement |
| `python harness.py status` | Show all services, including stopped one-shot tools |
| `python harness.py logs` | Follow the last 100 log lines for all services |
| `python harness.py config` | Validate the merged Compose configuration without printing secrets |
| `python harness.py down` | Stop services; retain volumes and generated files |
| `python harness.py reset --yes` | Remove this sandbox's volumes and generated data; retain `.env` |

## Configuration

See [configuration](./configuration.md) for environment variables, defaults, precedence, and examples. The [API reference](./api.md) describes CLI flags and HTTP interfaces.

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
