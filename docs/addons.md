# Addon development

The default addon is a small read-only HTTP service in `scripts/addon.py`. Its JSON
response comes from real `GET /api/v1/activities` requests, using `scripts/client.py`.
It listens on `0.0.0.0:8080` inside Docker and loopback port `9103` on the host.

## Replace the example

```sh
cp compose.addon.example.yaml compose.override.yaml
```

The supplied override builds the working standalone `addons/api-inspector` template.
Try it unchanged first, then edit it to use your own image/source checkout. `harness.py` automatically
includes it. Set `CHECK_EXAMPLE_ADDON=false` in `.env` if your addon does not expose
the example's JSON interface. That skips only the example-addon assertions; real
Dreeve import, authentication, and round-trip checks remain enabled.

The override replaces the service named `example-addon`, so the existing `up` and
`test` commands still start it. Use an appropriate health check for your addon.
If it does not listen on port 8080, override `ports` and its readiness check too.

To point at a project beside this harness:

```yaml
services:
  example-addon:
    image: my-dreeve-addon:local
    build:
      context: ../my-dreeve-addon
      dockerfile: Dockerfile
    command: !reset null
    working_dir: !reset null
    volumes:
      - ./watch:/watch
    healthcheck:
      disable: true
```

When using an already-built image without a build context, set `build: !reset null`
as well. Specifying `dockerfile: Dockerfile` for a custom build replaces the tool
Dockerfile inherited from the base service.

## Integration contract

- Reach Dreeve at **`http://app:8080`** from another Compose service.
- Read `DREEVE_API_KEY` from the inherited environment; send `Authorization: Bearer <key>`.
- Or read `/runtime/credentials.json`, containing `api_key`, `app_url`, and `public_url`.
- A file exporter can mount **`./watch:/watch`** and atomically rename completed
  `.fit`, `.tcx`, or `.gpx` files into that directory.
- An HTTP exporter can upload multipart field **`file`** to **`POST /api/v1/activity/upload`**.
  A `202 queued` response means the daemon will import it later; poll the activities
  and file-import APIs to confirm completion.
- Keep addon state in a separate named volume, declared in the override.
- A mock upstream can be another service in the override; address it by service name.

API documentation: [Dreeve HTTP API](https://docs.dreeve.app/api/).

## Add custom tests and upstream mocks

You can extend `compose.override.yaml` with additional services:

```yaml
services:
  mock-upstream:
    image: python:3.12-slim
    working_dir: /fixtures
    command: [python, -m, http.server, '8080']
    volumes:
      - ./addons/my-addon/fixtures:/fixtures:ro
  example-addon:
    environment:
      UPSTREAM_URL: http://mock-upstream:8080
    depends_on:
      mock-upstream:
        condition: service_started
  test:
    volumes:
      - ./addons/my-addon/tests:/addon-tests:ro
    command: [python, -m, unittest, discover, -s, /addon-tests, -v]
```

The controller also starts addon dependencies declared in the override. Replace the
`test` service command to run your suite instead of the supplied harness checks,
or leave it unchanged and add assertions to a separate test service. If you replace
the test command, write your own JUnit output to `/reports` if you want it uploaded by CI.

For stateful upstream APIs, implement the required authentication and response
sequence in a mock server. The Hadge connector's [HTTP mock and real Git fixture](https://github.com/willtheorangeguy/dreeve-hadge-connector/tree/v0.1.0/tests/integration)
provide a concrete example for GitHub-backed addons. This harness remains usable
for connectors that do not involve GitHub.

## Run the supplied addon check

```sh
python harness.py test-override
```

This builds and runs `addons/api-inspector`, checks its distinct implementation
marker and API snapshot, then restores your original addon. The full `test`
command includes this check too. Add tests under `tests/integration/test_*.py`
to retain the common JUnit runner while extending its coverage.
