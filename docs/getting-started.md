# Getting started

1. Install Docker Desktop (Linux containers) or Docker Engine with Compose v2.24.4+.
2. Install Python 3.10+ on the host. No Python packages are required on the host.
3. Clone the repository and run `python harness.py up`.
4. Open http://localhost:8103/admin/login and sign in as `demo` with `HarnessDemo123!`.
5. Open http://localhost:9103 to inspect the working example addon's JSON response.

The first run pulls the pinned Dreeve image and creates credentials in `.env`.
It generates and imports eight small synthetic FIT activities. You should see
running, cycling, walking, strength, yoga, and swimming activities in Dreeve.

For custom ports, run `python harness.py init`, edit `APP_PORT`, `ADDON_PORT`, and
`PUBLIC_URL` in `.env`, then run `python harness.py up`. Do not copy `.env.example`
verbatim to `.env`: its credential generation placeholders are filled by the controller.

The default username/password are for this local demo only. If you change
`DEMO_PASSWORD`, also replace `ADMIN_PASSWORD_HASH` with a matching bcrypt hash.
Keep bcrypt hashes single-quoted in `.env` so Compose preserves their dollar signs.
`DEMO_USERNAME` and the plaintext password are passed to test containers only;
Dreeve receives `ADMIN_USERNAME` and the password hash.

This is a disposable development sandbox. Keep its Compose project name, volumes,
and data folders separate from your personal Dreeve installation.
