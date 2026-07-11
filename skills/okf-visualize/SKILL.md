---
name: okf-visualize
description: Render an Open Knowledge Format (OKF) bundle as a self-contained interactive HTML knowledge-graph — nodes colored by concept type, directed edges from cross-links, click-through detail panel, search. Use this skill whenever the user wants to visualize, graph, map, or "see" an OKF bundle or knowledge base, asks what a bundle looks like as a diagram, or wants a shareable browsable view of their knowledge bundle.
---

# Visualizing OKF Bundles

Generate the graph with the bundled zero-dependency script:

```bash
python3 <skill-base-dir>/scripts/okf_visualize.py <bundle-dir> [-o out.html] [--name "Title"]
```

Default output is `viz.html` inside the bundle. The file is fully
self-contained (bundle embedded as JSON; Cytoscape.js and marked loaded
from cdnjs) — no backend, no install for viewers, no data leaves the
page. It can be committed next to the bundle, emailed, or hosted
statically.

What viewers get: a force-directed graph of every concept (colored by
`type`), directed edges for each cross-link, a search box (title/id/tags),
and a click-through panel showing frontmatter, rendered markdown body
with in-graph link navigation, and "Cited by" backlinks.

After generating, tell the user the concept/link counts the script
prints and present the HTML file to them. If the bundle fails to render
sensibly (0 concepts), it's probably not an OKF bundle — suggest
`okf-validate` to diagnose. Very large bundles (>2,000 concepts) will
render slowly; offer to visualize a subdirectory instead.
