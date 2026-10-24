# Development

<!-- markdownlint-disable MD046 -->
<!-- Material tab contents use indented fenced code blocks. -->

The host controller has no pip dependencies. Work on lifecycle code with the unit suite, then use the real container stack for changes involving Dreeve, fixture generation, or addons.

## Set up

```sh
git clone https://github.com/willtheorangeguy/dreeve-addon-harness.git
cd dreeve-addon-harness
python harness.py test-unit
```

Use Python 3.10+ on the host. Docker with Compose v2.24.4+ is required for container checks. Tools containers use Python 3.12, including `datetime.UTC` in fixture and integration code; host runtime support does not imply that every container script runs on Python 3.10.

## Change and verify

```sh
python harness.py test-unit
python harness.py test
```

Add controller, API client, or reporting checks under `tests/unit/`. Add real HTTP checks under `tests/integration/`. The shared JUnit runner discovers `test_*.py`. See [testing](./testing.md) for fixture invariants, cleanup, coverage, and report paths.

`test` retains the sandbox locally and writes Compose diagnostics even on failure. Stop it after inspection:

```sh
python harness.py down
```

There is no configured application linter, formatter, or type-checker command. The existing [integration workflow](./ci-cd.md) is the repository's executable check set.

## Work on an addon

Start with `compose.addon.example.yaml` and the standalone `addons/api-inspector` template. The [addon guide](./addons.md) covers external source checkouts, health checks, mock services, and custom test commands. Preserve the service name `example-addon` so the controller can manage it.

## Update the upstream pin

Review `upstream.json` and the Dreeve image reference in `compose.yaml` together. Credential generation uses the former; running services use the latter. Record the verified revision and release, then run the full test workflow against a disposable sandbox. Do not change the daemon schedule to shorten integration tests: scheduled imports are part of the behavior under test.

## Preview the documentation

Clone the shared theme into the ignored directory, then run its helper from this repository root. The helper installs the shared dependencies and stages assets before building or serving.

=== "Windows"

    ```powershell
    git clone --depth 1 https://github.com/willtheorangeguy/mkdocs .mkdocs-shared
    python -m venv .venv
    .\.venv\Scripts\Activate.ps1
    .\.mkdocs-shared\scripts\docs-serve.ps1 -Build
    ```

=== "Linux / macOS"

    ```sh
    git clone --depth 1 https://github.com/willtheorangeguy/mkdocs .mkdocs-shared
    python3 -m venv .venv
    . .venv/bin/activate
    bash .mkdocs-shared/scripts/docs-serve.sh --build
    ```

If `.mkdocs-shared` already exists, update that checkout instead of cloning again. Omit `-Build` or `--build` to serve a local preview. After staging, `mkdocs build --strict` validates the site with zero warnings. Generated assets and output are ignored; commit documentation source, `mkdocs.yml`, and workflow callers.

## Contribute

Follow the org-wide [contributing guide](https://github.com/willtheorangeguy/.github/blob/main/CONTRIBUTING.md) and [code of conduct](https://github.com/willtheorangeguy/.github/blob/main/CODE_OF_CONDUCT.md). Include relevant JUnit or redacted diagnostics with a behavior change. Report security concerns through the org-wide [security policy](https://github.com/willtheorangeguy/.github/blob/main/SECURITY.md).
