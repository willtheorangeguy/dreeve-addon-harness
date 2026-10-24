# Known Issues — dreeve-addon-harness

Concrete defects and gaps found while writing this repository's documentation.
**Nothing here was changed** — each one needs a code, configuration, or
licensing decision rather than a documentation one.

Ordered by severity. See [`docs/roadmap.md`](../roadmap.md) for the narrative version,
which also covers deliberate non-goals.

**1 open:** 1 medium.

## 1. Daemon health does not verify scheduled import progress

**Severity:** Medium
**Where:** `scripts/health.php`, daemon branch

**What:** The check succeeds when the SQLite database exists and PID 1's command contains app:daemon:run. It does not inspect scheduler execution or recent import progress.

**Why it matters:** Scheduled work can stop progressing while Compose still reports a healthy daemon, leaving integration import waits to time out.

**Suggested fix:** Define an upstream-supported scheduler heartbeat or progress probe and a timeout that accommodates the upstream five-minute schedule before extending readiness.
