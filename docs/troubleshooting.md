# Troubleshooting

## Docker is unavailable

Start Docker Desktop with Linux containers and run `docker info`. The harness uses
real containers; it cannot run with the daemon stopped or in Windows-container mode.

## Port already allocated

Run `python harness.py init`, edit `APP_PORT`, `ADDON_PORT`, and `PUBLIC_URL` in `.env`,
then run `up`. The defaults (`8103`, `9103`) differ from the other fitness harnesses.

## Invalid credentials or unhealthy app

The app health check makes an authenticated API request, so a malformed key or
mismatched environment is a real readiness failure. Keys use `drv_` plus 64 hex characters.
Inspect `python harness.py logs`. Do not expose `.env` in an issue.

Generated bcrypt hashes must be single-quoted in `.env` to preserve `$` characters.
The demo password and `ADMIN_PASSWORD_HASH` must match. The daemon uses a separate
readiness check and does not require a web metrics port of its own.

## Missing or duplicate seed activities

Run `python harness.py seed`. Dates are frozen in `runtime/seed-manifest.json`.
Seeding checks activity names before re-queueing deterministic filenames. If you
have intentionally renamed/deleted fixture data, reset the sandbox for a fresh baseline.

## Tests look idle

Duplicate replay and new file imports wait for the real daemon schedule. Look for
`Waiting:` and `Still waiting:` messages. The shared wait helper defaults to 370 seconds.
Inspect Dreeve's `/admin/file-imports` page for failed files and the daemon logs for cron jobs.

## Addon cannot connect

Use `http://app:8080` inside Docker. Host `localhost:8103` refers to a different
network context. Mount the same host `watch/` directory if exporting files, and
give completed files an appropriate readable mode before atomic publication.

## Reset and project isolation

`down` retains data. `reset --yes` deletes only volumes owned by the configured
Compose project and generated files beneath this harness's `runtime`, `reports`,
and `watch` directories. It keeps `.env`. Keep `COMPOSE_PROJECT_NAME` unique and
never point the sandbox at production Dreeve volumes or personal workout files.
