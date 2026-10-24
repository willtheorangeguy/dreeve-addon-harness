# CI/CD

## Application checks

`.github/workflows/integration.yml` runs on every push, pull request, and manual dispatch. It grants read-only repository access.

| Job | Runtime | Checks | Artifact |
| --- | --- | --- | --- |
| `unit` | Ubuntu and Windows, each with Python 3.10 and 3.12 | `python harness.py test-unit` | `unit-<os>-python-<version>` containing `reports/unit.xml` |
| `integration` | Ubuntu, Python 3.12, Docker | `python harness.py test` | `integration-reports` containing `reports/` |

The integration job has a 30-minute timeout. Artifact upload runs even on failure, and shutdown is attempted afterward with `python harness.py down`. Local full tests retain the sandbox instead. See [testing](./testing.md#reports) for individual reports.

Reproduce the job's entry points locally:

```sh
python harness.py test-unit
python harness.py test
python harness.py down
```

## Documentation build and deployment

`.github/workflows/docs.yml` calls the shared [MkDocs build workflow](https://github.com/willtheorangeguy/mkdocs/blob/main/.github/workflows/docs-build.yml). Relevant pushes to `main` or `master`, and manual dispatches, build and deploy the documentation. It stages the design system, runs a strict build, uploads the HTML artifact, and deploys through the `github-pages` environment.

The caller grants `contents: read`, `pages: write`, and `id-token: write`. Deployments share the `pages` concurrency group and are not cancelled midway. The site owns the Pages root for this repository at [the documentation site](https://williamvdg.me/dreeve-addon-harness/).

Pages must use **GitHub Actions** as its publishing source. This is a repository setting, independent of committing the workflow. Maintainers can inspect it with GitHub CLI:

```sh
gh api repos/willtheorangeguy/dreeve-addon-harness/pages --jq .build_type
gh workflow run docs.yml --repo willtheorangeguy/dreeve-addon-harness
```

The source should report `workflow`. The repository homepage points to the documentation URL.

## Documentation pull-request checks

`.github/workflows/docs-lint.yml` calls the shared lint workflow for documentation pull requests and manual dispatches. It runs Markdown style checks, a strict site build, and external-link checks. It does not deploy.

`mkdocs.yml` inherits theme, plugins, extensions, and validation from `.mkdocs-shared/shared/mkdocs.base.yml`. Both callers use the shared repository's `main` branch, so shared updates apply on the next run. Do not redeclare `plugins` or `markdown_extensions` locally: MkDocs replaces those lists instead of merging them.

Follow [development](./development.md#preview-the-documentation) to stage the same assets locally. `docs/docs.instructions.md` and `docs/internal/` remain source-only and are excluded from the published site.
