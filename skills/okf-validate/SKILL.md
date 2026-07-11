---
name: okf-validate
description: Validate a directory against the Open Knowledge Format (OKF) v0.1 conformance rules using a bundled checker script. Use this skill whenever the user asks to validate, lint, check, or verify an OKF bundle, asks "is this bundle conformant/valid", wants a conformance report before publishing or sharing a knowledge bundle, or asks why an OKF bundle isn't being consumed correctly by an agent.
---

# Validating OKF Bundles

Run the bundled conformance checker:

(`scripts/validate_okf.py` lives under this skill's base directory —
use its absolute path, since the shell's working directory is elsewhere.)

```bash
python3 <skill-base-dir>/scripts/validate_okf.py <bundle-dir>
```

Exit 0 = conformant, 1 = errors. It checks the three hard rules from spec
§9 and emits soft warnings.

## Interpreting results

**Errors (must fix — bundle is not conformant):**
- A non-reserved `.md` file with no parseable YAML frontmatter.
- Frontmatter missing a non-empty `type` field (the only required field).
- Reserved-file misuse: frontmatter in `log.md`, or frontmatter in an
  `index.md` outside the bundle root (the root index may carry only
  `okf_version`).

**Warnings (judgment calls — report, don't auto-fix without asking):**
- Broken internal links: legal per spec §5.3 (they can mark
  not-yet-written knowledge). Flag them; fix only typos, e.g. a link that
  almost matches an existing file.
- Missing `title`/`description`: recommended, not required. Offer to fill
  them in — descriptions feed index generation and search snippets.
- `log.md` without ISO `## YYYY-MM-DD` headings; index files without links.

## Reporting

Give the user: conformant or not, concept/file counts, each error with
the file path and the concrete fix, and warnings grouped by kind with a
recommendation. If the user wants fixes applied, make the minimal edits
(preserving unknown frontmatter keys) and re-run the checker to confirm
it passes.

For spec details behind any rule, see `references/okf-spec.md`. For
authoring new bundles use `okf-author`; for navigating/querying use
`okf-explore`.
