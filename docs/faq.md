# FAQ

???+ question "Does this connect to my existing Dreeve installation?"
    No. The base Compose file starts a separate app and daemon with project-scoped named volumes and synthetic data. Keep `COMPOSE_PROJECT_NAME` unique, and do not attach personal or production volumes to an override.

??? question "Why does init need Docker if the controller has no dependencies?"
    Python orchestrates credential creation, but PHP inside the pinned Dreeve image generates the bcrypt hash. `test-unit` bypasses initialization and runs without Docker.

??? question "Why do full tests take several minutes?"
    Duplicate replay and round-trip import tests wait for the unchanged upstream daemon schedule. Startup seeding uses an explicit import command. Full tests can take up to twelve minutes plus downloads and builds.

??? question "Does down delete my workouts or change fixture dates?"
    `down` retains volumes and generated files. The manifest freezes fixture dates, and reseeding checks existing names. `reset --yes` removes sandbox data while retaining `.env` credentials.

??? question "Can my addon expose a different HTTP interface?"
    Yes. Set `CHECK_EXAMPLE_ADDON=false`, provide its health check, and add your own assertions. That setting skips the default snapshot assertions. The explicit supplied-addon replacement check still runs and then restores your addon.

??? question "Are the heart-rate and power streams real athlete data?"
    No. `fit-tool` generates synthetic FIT files. Coordinates are omitted to avoid weather and geocoding dependencies. Add route fixtures separately for GPS behavior.

??? question "Is this repository AGPL licensed because it runs Dreeve?"
    The harness is MIT licensed. Dreeve retains its AGPL-3.0 license, and `fit-tool` retains BSD-3-Clause. See the [license](./license.md) and upstream projects for their terms.
