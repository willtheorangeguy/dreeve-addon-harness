# API

The public entry point is the `harness.py` controller. Addons communicate with Dreeve over HTTP. The internal Python API client is a test helper, not a packaged library.

## Controller interface

```sh
python harness.py --help
python harness.py up
```

| Argument or flag | Type | Default | Description |
| --- | --- | --- | --- |
| `command` | required choice | none | One of `init`, `up`, `seed`, `test`, `test-unit`, `test-override`, `status`, `logs`, `config`, `down`, `reset` |
| `--yes` | flag | off | Required for `reset`; has no effect for other commands |
| `-h`, `--help` | flag | off | Print help and exit before initialization |

Each command has a complete invocation in [usage](./usage.md#commands). Success returns zero. Handled controller failures print `Harness failed: ...` to stderr and exit 1. Argument errors, including `reset` without `--yes`, exit 2. Output is progress text or delegated Compose output, not a stable JSON interface.

## Example addon HTTP interface

The addon listens on port 8080 inside Docker and host loopback port 9103. GET on any path, including `/` and `/health`, invokes the same snapshot handler without parameters or a request body.

```sh
curl http://localhost:9103/
curl http://localhost:9103/health
```

The response is `application/json`. The following excerpt shows the stable scalar fields; full responses also contain `activities` and `seed`:

```json
{
  "platform": "dreeve",
  "activity_count": 8,
  "sports": ["Ride", "Run", "Swim", "Walk", "WeightTraining", "Yoga"],
  "implementation": "default-addon"
}
```

`activities` contains complete list records. `seed` contains the saved manifest, or null if absent. Counts can exceed eight after custom imports. The supplied replacement changes `implementation` to `api-inspector`.

| Status | Response and cause |
| --- | --- |
| `200` | Snapshot containing platform, activity count, sports, activities, seed, and implementation |
| `503` | `{"error": "Application API unavailable"}` for a `RuntimeError` or `OSError` while fetching the snapshot |
| `501` | Standard-library HTTP server error for unsupported methods, including POST |

Each GET fetches every activity page. `/health` therefore depends on upstream authenticated API access. The addon has no incoming authentication; the host port is loopback-bound by default.

## Dreeve HTTP integration

Inside Compose, use `http://app:8080`. From the host use `http://localhost:8103`. Send the generated API key as `Authorization: Bearer <key>`. The helper sets `Origin` from `PUBLIC_URL`, uses a 30-second request timeout, and raises `APIError` with the status and path while discarding raw error bodies.

The following surfaces are exercised by this checkout. The [Dreeve HTTP API documentation](https://docs.dreeve.app/api/) owns the full upstream contract. This table reports the assertions made against the pinned image, including failure cases.

| Method and path | Input | Verified result |
| --- | --- | --- |
| `GET /api/v1/status` | Authenticated request | Successful nonempty readiness response |
| `GET /api/v1/activities` | `pagination[page]`, `pagination[size]` | `activities` and `pagination.totalPages`; bad/missing key: 401; page 0: 400 |
| `GET /api/v1/activities/{id}` | ID from a list record | Activity fields matching list values; unknown/deleted ID: 404 |
| `GET /api/v1/activities/{id}/streams` | Activity ID | Time, heart rate, power, cadence, and coordinate arrays; fixture coordinates are empty |
| `GET /api/v1/activities/{id}/gpx` | Activity ID | Summary-only strength fixture: 404 |
| `POST /api/v1/activity/upload` | Multipart field `file` with FIT bytes | 202 and `status: queued`; unsupported `.txt`: 422 |
| `GET /api/v1/file-imports` | Pagination parameters | `fileImports` records; duplicate replay eventually has `status: skipped` |
| `PATCH /api/v1/activities/{id}` | JSON, e.g. `{"description": "Addon roundtrip verified"}` | Updated activity; invalid `sportType: NotASport`: 400 without changing stored sport |
| `DELETE /api/v1/activities/{id}` | Activity ID | Temporary record removed; subsequent GET: 404 |

### Call the authenticated API

After `python harness.py up`, use the tools container's existing environment rather than placing a secret on the command line:

```sh
docker compose --profile tools run --rm test python -c 'from client import API; data = API().request("/api/v1/activities?pagination[size]=2"); print(len(data["activities"]))'
```

```text
2
```

To observe the missing-credential response:

```sh
docker compose --profile tools run --rm test python -c 'from client import API; API().request("/api/v1/activities", authenticated=False)'
```

The final traceback line is:

```text
client.APIError: HTTP 401 from /api/v1/activities
```

`API.activities()` requests 100 items per page, with a safety limit of 100 pages. It raises `RuntimeError` when that bound is exceeded.

### Exercise writes and scheduled imports

```sh
python harness.py test
```

The integration suite generates real FIT bytes, uploads files, polls import status, reads details and streams, patches names/descriptions, deletes temporary records, and asserts missing-resource responses. It writes `reports/roundtrip.json` and `reports/junit.xml`. The runnable request/response assertions live in `tests/integration/test_platform.py` and `test_extended.py`; run them through the controller so seed audit prerequisites exist.

Read [testing](./testing.md#platform-coverage) for the covered cases and [addon development](./addons.md#integration-contract) for file publication and upload guidance. Preserve the seeded records when exploring writes.
