---
name: okf-author
description: Author conformant Open Knowledge Format (OKF) v0.1 bundles — Google's open markdown+YAML-frontmatter spec for packaging organizational knowledge (tables, datasets, metrics, APIs, runbooks, playbooks) so AI agents and humans can consume it. Use this skill whenever the user mentions OKF, Open Knowledge Format, knowledge bundles, an "LLM wiki", agent-readable documentation, or wants to convert schemas, data dictionaries, catalogs, runbooks, internal docs, or a codebase (services, modules, API endpoints, architecture decisions) into a portable markdown knowledge base — even if they don't say "OKF" explicitly.
---

# Authoring OKF Bundles

OKF (Open Knowledge Format) v0.1 represents knowledge as a directory of
markdown files with YAML frontmatter. Each file is one **concept** (a table,
metric, API, runbook, …); the file path is its identity; markdown links
between files form a knowledge graph. The full specification is in
`references/okf-spec.md` — consult it for any detail not covered here.

## Workflow

### 1. Understand the source material

Identify the concepts in what the user gives you (schemas, docs, CSVs, API
definitions, tribal knowledge in prose). One concept = one file. Ask the user
only if the grouping is genuinely ambiguous.

### 2. Plan the hierarchy

Group concepts into subdirectories by kind or domain — e.g. `tables/`,
`datasets/`, `metrics/`, `playbooks/`, `apis/`, `references/`. The directory
layout is free-form; pick what makes the bundle self-explanatory to someone
running `ls`. Two filenames are **reserved** at every level and must never be
used for concepts: `index.md` (directory listing) and `log.md` (change
history).

### 3. Write each concept document

Every concept file needs YAML frontmatter delimited by `---` lines, then a
markdown body:

```markdown
---
type: BigQuery Table            # REQUIRED — the only mandatory field
title: Orders
description: One row per completed customer order.
resource: https://console.cloud.google.com/bigquery?p=acme&d=sales&t=orders
tags: [sales, orders]
timestamp: 2026-05-28T14:30:00Z
---

# Schema

| Column        | Type    | Description                              |
|---------------|---------|-------------------------------------------|
| `order_id`    | STRING  | Unique order identifier.                  |
| `customer_id` | STRING  | FK to [customers](/tables/customers.md).  |

# Joins

Joined with [customers](/tables/customers.md) on `customer_id`.
```

Frontmatter rules that matter:

- `type` is the only required field. Pick descriptive, self-explanatory
  values (`BigQuery Table`, `Metric`, `Playbook`, `API Endpoint`,
  `Reference`) — there is no central registry.
- Recommended, in priority order: `title`, `description` (one sentence —
  index generators and search snippets use it), `resource` (canonical URI of
  the underlying asset; omit for abstract concepts), `tags` (YAML list),
  `timestamp` (ISO 8601).
- Extra producer-defined keys are allowed; don't strip them when editing an
  existing bundle.

Body rules: favor structural markdown (headings, tables, fenced code) over
prose — it aids both human reading and agent retrieval. Three headings have
conventional meaning; use them when applicable: `# Schema` (columns/fields),
`# Examples` (usage, fenced code), `# Citations` (numbered external sources,
at the bottom: `[1] [label](url)`).

### 4. Cross-link concepts

Link related concepts with normal markdown links. Prefer the
**bundle-relative absolute form** — starts with `/`, resolved from the bundle
root: `[customers](/tables/customers.md)`. It survives files moving between
subdirectories. The relationship kind (joins-with, depends-on, part-of) is
conveyed by surrounding prose, not the link. Linking to a not-yet-written
concept is fine — broken links are legal and represent future knowledge.

### 5. Generate index.md files

Add an `index.md` to the bundle root and each subdirectory for progressive
disclosure. Index files have **no frontmatter** (exception: the bundle-root
index may carry a frontmatter block with just `okf_version: "0.1"` — the
recommended way to declare the spec version). Format:

```markdown
# Tables

* [Orders](orders.md) - One row per completed customer order.
* [Customers](customers.md) - One row per registered customer.

# Subdirectories

* [Metrics](metrics/) - Business metric definitions.
```

Pull each entry's description from the linked concept's frontmatter so the
index stays consistent with the concepts.

### 6. Add log.md (when history matters)

For bundles that will evolve, add a root `log.md` — date-grouped entries,
newest first, ISO `YYYY-MM-DD` headings:

```markdown
# Directory Update Log

## 2026-07-11
* **Initialization**: Created bundle with [orders](/tables/orders.md) and [customers](/tables/customers.md).
```

Entry prefixes (`**Creation**`, `**Update**`, `**Deprecation**`) are
conventions, not requirements. Skip `log.md` for one-shot exports unless the
user asks.

### 7. Validate before delivering

Run the bundled conformance checker on the finished bundle:

(`scripts/validate_okf.py` lives under this skill's base directory —
use its absolute path, since the shell's working directory is elsewhere.)

```bash
python3 <skill-base-dir>/scripts/validate_okf.py <bundle-dir>
```

It checks the three conformance rules (every non-reserved `.md` has parseable
frontmatter; every frontmatter has a non-empty `type`; reserved files are
structured correctly) and warns on soft issues like broken internal links and
missing descriptions. Fix errors; use judgment on warnings (broken links may
be intentional). Tell the user the validation result.

## Judgment calls

- **Codebase bundles**: OKF documents a codebase, it does not replace it.
  Create one concept per service/module (`type: Service`), API endpoint,
  data model, architecture decision (`type: ADR`), and runbook; point
  `resource` at the file, spec, or console URL; cross-link service ->
  endpoints -> tables -> runbooks. Keep the bundle in the repo (e.g.
  `knowledge/`) so it versions with the code.

- **Granularity**: a 40-column table is still one concept; a dataset with 40
  tables is 40 concepts plus a dataset concept linking to them.
- **Don't subsume other schemas**: OKF references Avro/Protobuf/OpenAPI
  definitions via `resource` or citations; it doesn't replace them. Summarize
  the schema in a `# Schema` table, link to the authoritative source.
- **Consumers are permissive by spec** — missing optional fields, unknown
  types, and broken links must not break a bundle. So when converting messy
  source material, ship a partially-enriched bundle rather than blocking on
  completeness; note gaps in `log.md` or the concept body.
- **Editing an existing bundle**: preserve unknown frontmatter keys and
  unfamiliar directory conventions; update the relevant `index.md` and
  `log.md` entries to match your changes.
