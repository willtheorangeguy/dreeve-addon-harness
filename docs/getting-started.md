# Getting started

<!-- markdownlint-disable MD046 -->
<!-- Material tab contents use indented fenced code blocks. -->

## Prerequisites

Verify a running Linux Docker daemon, Compose v2.24.4+, and Python 3.10+:

```sh
docker info
docker compose version
python --version
git --version
```

## Install

=== "Windows"

    ```powershell
    git clone https://github.com/willtheorangeguy/dreeve-addon-harness.git
    Set-Location dreeve-addon-harness
    ```

=== "Linux / macOS"

    ```sh
    git clone https://github.com/willtheorangeguy/dreeve-addon-harness.git
    cd dreeve-addon-harness
    ```

Use `python3` in place of `python` if that is your host's executable name. See [installation](./installation.md) for upgrading and removal.

## First run

1. Start the sandbox:

    ```sh
    python harness.py up
    ```

    On success, the final message is:

    ```text
    Ready. See .env for the app/addon ports and README.md for demo login.
    ```

2. Open [Dreeve admin login](http://localhost:8103/admin/login) and sign in as `demo` with `HarnessDemo123!`.
3. Open the [example addon](http://localhost:9103/) to inspect its JSON response. Expect `platform: dreeve`, `implementation: default-addon`, at least eight activities, and eight seed fixtures.
4. Run `python harness.py status`. The `app`, `daemon`, and `example-addon` services should be running and healthy. One-shot tools can have exited successfully.

## What happened

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

## Next steps

- Follow [addon development](./addons.md) to replace the snapshot service.
- Run `python harness.py test-unit` or the full `python harness.py test` workflow described in [testing](./testing.md).
- Read [configuration](./configuration.md) before changing credentials, ports, or fixture dates.
- Use `python harness.py down` to stop services while retaining data. See [usage](./usage.md#persistence) before resetting.
