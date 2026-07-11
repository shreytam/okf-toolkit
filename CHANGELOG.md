# Changelog

All notable changes to the OKF Toolkit plugin are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.1] - 2026-07-11

### Added

- Four skills for Google's Open Knowledge Format (OKF) v0.1:
  - `okf-author` — build conformant knowledge bundles from schemas, docs, and runbooks
  - `okf-explore` — navigate and query existing bundles via progressive disclosure
  - `okf-validate` — run the bundled conformance checker (`validate_okf.py`)
  - `okf-visualize` — render a bundle as a self-contained interactive HTML knowledge graph (`okf_visualize.py`)
- `templates/CLAUDE-okf.md` for automatic knowledge-base upkeep in coding projects
- Self-contained marketplace manifest for one-command install
- Apache-2.0 license
- CI workflow validating manifests, scripts, and skill frontmatter on every push

[0.2.1]: https://github.com/shreytam/okf-toolkit/releases/tag/v0.2.1
