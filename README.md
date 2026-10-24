<h1 align="center">Dreeve addon testing harness</h1>
<h4 align="center">Run a seeded Dreeve Docker sandbox with a real API, example addon, and containerized integration tests.</h4>

<p align="center">
<img alt="Issues" src="https://img.shields.io/github/issues/willtheorangeguy/dreeve-addon-harness">
<img alt="Pull requests" src="https://img.shields.io/github/issues-pr/willtheorangeguy/dreeve-addon-harness">
<img alt="Integration" src="https://github.com/willtheorangeguy/dreeve-addon-harness/actions/workflows/integration.yml/badge.svg">
<img alt="Docs" src="https://github.com/willtheorangeguy/dreeve-addon-harness/actions/workflows/docs.yml/badge.svg">
<img alt="Docs lint" src="https://github.com/willtheorangeguy/dreeve-addon-harness/actions/workflows/docs-lint.yml/badge.svg">
<img alt="License" src="https://img.shields.io/github/license/willtheorangeguy/dreeve-addon-harness">
</p>

## Key features

- Full Dreeve **v5.6.2**, pinned by image digest, with its real web app and daemon.
- Eight synthetic workouts across six sports, including heart-rate, cadence, and power streams.
- Working admin login, generated local API key, shared watch folder, and persistent SQLite storage.
- Read-only example addon that fetches activities through Dreeve's authenticated API.
- Automatic loading of `compose.override.yaml` for future addons and mock upstream services.
- Real scheduled file imports, HTTP uploads, duplicate detection, API edits/deletes, and JUnit reports.
- Same `harness.py` workflow as the [wger](https://github.com/willtheorangeguy/wger-addon-harness)
  and [SparkyFitness](https://github.com/willtheorangeguy/sparkyfitness-addon-harness) harnesses.

## Installation

Requires Docker with Linux containers, **Docker Compose v2.24.4+**, and host
**Python 3.10+**. No host pip installation is needed. Tools and tests run in containers.

```sh
git clone https://github.com/willtheorangeguy/dreeve-addon-harness.git
cd dreeve-addon-harness
python harness.py up
```

First startup generates `.env`, a random application secret and API key, and a real
bcrypt hash for the demo password. It starts Dreeve, seeds the fixtures, verifies
them through the API, and starts the example addon.

- **Dreeve:** http://localhost:8103
- **Example addon:** http://localhost:9103
- **Admin username:** `demo`
- **Admin password:** `HarnessDemo123!`

The ports avoid the wger/SparkyFitness harness defaults. Change `.env` before
startup if those ports are occupied. Services bind to loopback only.

## Usage

```sh
python harness.py test-unit
python harness.py test
python harness.py status
python harness.py logs
python harness.py down
```

`test` starts and seeds the stack if needed, then runs real HTTP integration checks.
Allow **up to 12 minutes**, plus initial image downloads/builds: duplicate replay
and new imports wait for the unchanged Dreeve daemon's five-minute schedule.
Initial seeding uses Dreeve's explicit import command so `up` is ready quickly.

`down` stops the sandbox and keeps its data. Re-running `up` or `seed` preserves
the existing fixture dates and does not duplicate workouts. To remove this sandbox's
volumes and generated files while keeping `.env` credentials:

```sh
python harness.py reset --yes
```

## Test your own addon

Copy `compose.addon.example.yaml` to `compose.override.yaml`, adapt it to your addon,
and run `python harness.py up`. The controller includes the override automatically.
Your addon can use:

- Dreeve's internal URL: `http://app:8080`
- API credential: inherited `DREEVE_API_KEY`, sent as `Authorization: Bearer ...`
- Watch folder: mount `./watch:/watch` to deliver FIT/TCX/GPX files
- Runtime fixture information: `/runtime/seed-manifest.json`
- Optional credential handoff: `/runtime/credentials.json` (sandbox only; ignored by Git)

See [addon development](docs/addons.md) for the override contract, mock-service
examples, custom integration tests, and attaching another project's source tree.

## Testing

Run `python harness.py test-unit` for host tests, then `python harness.py test` for
the full Docker workflow. See [test coverage and reports](docs/testing.md).

## Documentation

Read the [documentation site](https://williamvdg.me/dreeve-addon-harness/) or browse
[`docs/`](docs/index.md): [Getting started](docs/getting-started.md) ·
[Configuration](docs/configuration.md) · [API](docs/api.md) · [Addon development](docs/addons.md).

## Support

Open a [GitHub Discussion](https://github.com/willtheorangeguy/dreeve-addon-harness/discussions/new) or file an [issue](https://github.com/willtheorangeguy/dreeve-addon-harness/issues/new/choose).

## Contributing

Contributions welcome. See the org-wide [Contributing Guide](https://github.com/willtheorangeguy/.github/blob/main/CONTRIBUTING.md) and [Code of Conduct](https://github.com/willtheorangeguy/.github/blob/main/CODE_OF_CONDUCT.md).

## License

MIT — see [`LICENSE.md`](LICENSE.md).

## Attribution

Runs upstream [Dreeve](https://github.com/dreeveapp/dreeve) without modifying it.
Image/source references are recorded in [upstream.json](upstream.json).
Extracted and generalized from the full-stack tests in
[dreeve-hadge-connector](https://github.com/willtheorangeguy/dreeve-hadge-connector/tree/v0.1.0/tests/integration).
This repository has no runtime dependency on that connector or any private GitHub repository.

The harness is MIT licensed; Dreeve retains its AGPL-3.0 license and `fit-tool`
retains its BSD-3-Clause license. See [LICENSE.md](LICENSE.md).
