# Fixtures and test coverage

Dreeve v5.6.2 is pinned to a specific multi-platform image digest. `upstream.json`
records the matching upstream revision and deployment reference.

## Synthetic dataset

Eight activities span the two weeks ending at `SEED_END_DATE`:

| Activity | Sport | Distance | Duration | Samples |
| --- | --- | --- | --- | --- |
| Harness Easy Run | Run | 3 km | 15 min | Heart rate, distance |
| Harness Commute Ride | Ride | 7 km | 20 min | Heart rate, cadence, power, distance |
| Harness Walk | Walk | 1.2 km | 15 min | Heart rate, distance |
| Harness Strength | WeightTraining | None | 30 min | Summary only |
| Harness Yoga | Yoga | None | 20 min | Summary only |
| Harness Swim | Swim | 0.6 km | 15 min | Heart rate, distance |
| Harness Interval Run | Run | 4 km | 20 min | Heart rate, distance |
| Harness Long Ride | Ride | 10 km | 30 min | Heart rate, cadence, power, distance |

FIT files are generated with `fit-tool` 0.9.16 and parsed by Dreeve's independent
Go FIT decoder. Sensor samples are explicitly synthetic test data. Coordinates
are omitted so tests do not depend on weather/geocoding services. Add your own
route fixtures in an addon when testing GPS-specific features.

## Integration checks

`python harness.py test` checks the actual application, not a Dreeve mock:

- API values, six sport mappings, sensor streams, and summary-only activities.
- Rejection of missing and incorrect bearer tokens.
- Admin login with a session cookie and CSRF token using the real demo password.
- Example addon reads through Dreeve's authenticated HTTP API.
- Re-uploading all eight seed FIT files creates skipped imports, not duplicate activities.
- Both a watch-folder file and an HTTP upload are imported by the unchanged daemon.
- Imported test activities can be read, patched, and deleted through the API.
- Test activities are removed after the round trip; the eight seed workouts remain.

The daemon uses its real five-minute cron schedule. Seed import is triggered explicitly
to make initial startup quick; replay and round-trip test assertions wait for scheduled imports.
Allow up to twelve minutes for tests and twenty-five minutes for a cold CI run.

## Reports and host unit tests

JUnit output and API snapshots are written to `reports/`. API snapshots contain
synthetic workouts only, with no API keys or login passwords. `runtime/` contains
the sandbox credentials and is not uploaded by CI.

The host controller tests use Python's standard library and do not start Docker:

```sh
python -m unittest discover -s tests/unit -v
```

They cover credential generation, correct bcrypt quoting, preservation of an existing
`.env`, automatic override inclusion, and safeguards around resetting generated data.
