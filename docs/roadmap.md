# Roadmap and limitations

This page records current boundaries evidenced by the source and test suite. The repository contains no committed release schedule or promised feature milestones.

## Current boundaries

- The stack is verified against Dreeve v5.6.2 at the digest recorded in `upstream.json`. Compatibility with another upstream release requires a new verification run.
- Fixtures contain no GPS coordinates. Weather, geocoding, and route-specific behavior require additional addon fixtures.
- Tests exercise HTTP login and frontend HTML. They do not use browser automation or production identity providers.
- Scheduled import checks retain Dreeve's five-minute daemon schedule. Downloads and builds add to the test duration.
- The supplied addon only reads API data and exposes a JSON snapshot. Implement addon-specific behavior and assertions in your override.
- Shared source includes other fitness platform adapters. This checkout configures only Dreeve and does not offer a runtime platform selector.
- API activity pagination has a 100-page safety limit at 100 items per page. The client raises an error if collection exceeds that bound.

## Extension points

Use [addon development](./addons.md) to attach an external build context, upstream mock, separate state volume, or custom test command. Use [testing](./testing.md#extend-the-suite) to add assertions while preserving fixture dates and cleaning temporary records.

```sh
python harness.py test-override
```

This verifies the existing replacement path before you adapt it. Propose further work in [GitHub issues](https://github.com/willtheorangeguy/dreeve-addon-harness/issues), with a concrete scenario and expected behavior.
