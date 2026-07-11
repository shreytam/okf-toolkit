<!-- Paste this into your project's CLAUDE.md (or AGENTS.md) to turn on
     automatic OKF consume/maintain behavior for coding agents. -->

## Project knowledge (OKF)

This repo keeps curated knowledge in an OKF bundle at `knowledge/`
(markdown + YAML frontmatter; see the bundle's root `index.md` first —
it's designed for progressive disclosure, so navigate index-by-index
instead of reading every file).

- **Before non-trivial tasks**: consult the bundle for relevant concepts
  (services, tables, metrics, runbooks, decisions) instead of
  re-discovering from source.
- **After changes that alter documented behavior**: update the affected
  concept files, keep `type` frontmatter intact, update the directory's
  `index.md`, and append a dated entry to `log.md`
  (`## YYYY-MM-DD`, newest first).
- **New durable knowledge** discovered while working (a gotcha, a join
  path, a decision): capture it as a new concept file with at minimum
  `type` frontmatter, cross-linked from related concepts.
