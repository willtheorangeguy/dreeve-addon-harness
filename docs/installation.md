# Installation

<!-- markdownlint-disable MD046 -->
<!-- Material tab contents use indented fenced code blocks. -->

Install the harness from source. The application, fixture generator, and integration tools run in Linux containers. Host controller and unit tests use Python's standard library.

## Requirements

| Dependency | Requirement | Verification |
| --- | --- | --- |
| Python | 3.10+ on the host | `python --version` |
| Docker | Docker Desktop in Linux-container mode or Docker Engine | `docker info` |
| Docker Compose | v2.24.4+ for the override reset tags | `docker compose version` |
| Git | Required for cloning | `git --version` |
| Network | Access to GitHub, GHCR, Docker image registries, and Python package downloads on first build | `docker pull python:3.12-slim` |

The controller supports Windows and Linux, which are covered by CI. The documentation toolchain is a separate optional installation described in [development](./development.md#preview-the-documentation).

## Install from source

=== "Windows"

    ```powershell
    git clone https://github.com/willtheorangeguy/dreeve-addon-harness.git
    Set-Location dreeve-addon-harness
    python harness.py up
    ```

=== "Linux / macOS"

    ```sh
    git clone https://github.com/willtheorangeguy/dreeve-addon-harness.git
    cd dreeve-addon-harness
    python3 harness.py up
    ```

There is no published Python package or standalone executable. Do not install `requirements-tools.txt` on the host for ordinary use: `Dockerfile.tools` installs its pinned `fit-tool` dependency in the tools image.

For port changes before startup, run `python harness.py init`, edit `.env`, and then run `python harness.py up`. `init` uses the pinned Dreeve image to generate the password hash, so Docker must already be running.

## Verify the installation

```sh
python harness.py status
python harness.py test-unit
```

`status` displays Compose services, including stopped one-shot tools. After `up`, `app`, `daemon`, and `example-addon` should be running and healthy. The unit command writes `reports/unit.xml` and returns zero when its tests pass. Check the [addon JSON response](http://localhost:9103/) for `platform: dreeve`, at least eight activities, and eight seed fixtures.

## Upgrading

Stop the sandbox, update the checkout, and rebuild through the controller:

```sh
python harness.py down
git pull --ff-only
python harness.py up
```

`down` retains named volumes and generated files. The upstream application reference is recorded in `upstream.json` and pinned independently in `compose.yaml`. Review both when intentionally updating Dreeve. The harness supplies no migration or backup guarantee for upstream image changes.

## Uninstalling

```sh
python harness.py reset --yes
```

This deletes the sandbox's Compose volumes and generated data in `runtime/`, `reports/`, and `watch/`. It retains `.env`. After stopping and resetting, remove your checkout and its remaining local credentials if you no longer need them. Downloaded images remain in Docker's image cache.
