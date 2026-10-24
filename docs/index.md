# Dreeve addon testing harness

Run a seeded Dreeve Docker sandbox with a real API, example addon, and containerized integration tests. This harness gives addon developers synthetic workouts, local credentials, and repeatable checks without connecting to a personal Dreeve installation.

## Key features

- Dreeve v5.6.2 web app and daemon pinned to an image digest.
- Eight synthetic workouts across six sports, including sensor streams.
- Generated application secret, API key, and bcrypt password hash.
- Replaceable read-only addon with authenticated API access.
- Reseed, restart, scheduled import, upload, and duplicate-detection checks.
- JUnit results and JSON diagnostics for local runs and CI.

## Quick start

With Python 3.10+ and Docker Compose v2.24.4+ installed:

```sh
git clone https://github.com/willtheorangeguy/dreeve-addon-harness.git
cd dreeve-addon-harness
python harness.py up
```

Open [Dreeve](http://localhost:8103/admin/login) and sign in as `demo` with `HarnessDemo123!`. Open the [example addon](http://localhost:9103/) to inspect its JSON snapshot. Follow [getting started](./getting-started.md) for prerequisites, output, and port changes.

## Where to next

<div class="grid cards" markdown>

- **Configure the sandbox**

    Read the [configuration reference](./configuration.md) for credentials, ports, fixture dates, and persistence.

- **Build an addon**

    Use the [addon development guide](./addons.md) to replace the example service and attach mocks or source trees.

- **Understand the interfaces**

    Read the [API reference](./api.md) and [architecture](./architecture.md) before adding integration behavior.

- **Verify a change**

    Run the [test suites](./testing.md), inspect [CI/CD](./ci-cd.md), or diagnose [startup failures](./troubleshooting.md).

</div>

## Support

Open a [GitHub Discussion](https://github.com/willtheorangeguy/dreeve-addon-harness/discussions/new) or file an [issue](https://github.com/willtheorangeguy/dreeve-addon-harness/issues/new/choose). Include the command, runtime versions, and redacted diagnostics. Keep `.env` and `runtime/credentials.json` private.
