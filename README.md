# OKF Toolkit

Skills for working with the [Open Knowledge Format (OKF) v0.1](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) — Google's open, vendor-neutral spec for representing organizational knowledge as markdown files with YAML frontmatter that AI agents and humans can both consume.

## Skills

| Skill | What it does |
|-------|--------------|
| **okf-author** | Convert schemas, data dictionaries, runbooks, API docs, or whole folders into a conformant OKF bundle — concepts, cross-links, index.md, log.md — and validate before delivering. |
| **okf-explore** | Navigate and query an existing bundle via progressive disclosure (index-first), trace concept relationships, answer questions from it, and edit it safely. |
| **okf-validate** | Run the bundled conformance checker (`validate_okf.py`) against a directory and report errors/warnings with concrete fixes. |
| **okf-visualize** | Render a bundle as a self-contained interactive HTML knowledge graph (`okf_visualize.py`) — searchable, click-through, shareable. |

Each skill carries the full OKF v0.1 spec in `references/okf-spec.md`.

## Example prompts

- "Turn the data dictionary in this folder into an OKF bundle"
- "What does our knowledge bundle say about the orders table?"
- "Validate ./shopdb against the OKF spec"

## Automatic upkeep in coding projects

Paste `templates/CLAUDE-okf.md` into your project's `CLAUDE.md` to make coding agents consult the bundle before tasks and write knowledge back after changes.

## Install

**Claude Code** — add this repo as a marketplace, then install:

```
/plugin marketplace add shreytam/okf-toolkit
/plugin install okf-toolkit@okf-toolkit
```

Or point Claude Code at a local checkout without the marketplace: `claude --plugin-dir <path-to-this-folder>`.

**Cowork** — download [`okf-toolkit.plugin`](https://github.com/shreytam/okf-toolkit/releases/latest/download/okf-toolkit.plugin) from the [latest release](https://github.com/shreytam/okf-toolkit/releases/latest), open it, and click install.

## License

This plugin is licensed under the [Apache License 2.0](LICENSE) — see [`NOTICE`](NOTICE) for attributions. The vendored OKF v0.1 spec (`references/okf-spec.md`) is by the Google Cloud Data Cloud team, also Apache-2.0, from the [reference repository](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf), with its original attribution headers retained.

No MCP servers, hooks, or credentials required.
