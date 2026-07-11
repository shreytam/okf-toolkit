#!/usr/bin/env python3
"""CI check: verify the okf-toolkit plugin is structurally valid.

Runs in GitHub Actions on every push and pull request. No third-party
dependencies. Fails (non-zero exit) if any of the following break:

  1. .claude-plugin/plugin.json and marketplace.json are valid JSON.
  2. Every bundled Python script under skills/ compiles.
  3. Every skills/*/SKILL.md has `name` and `description` frontmatter.
"""
import glob
import json
import os
import py_compile
import sys

errors = []

# 1. Manifests are present and valid JSON.
for manifest in (".claude-plugin/plugin.json", ".claude-plugin/marketplace.json"):
    if not os.path.exists(manifest):
        errors.append(f"missing manifest: {manifest}")
        continue
    try:
        json.load(open(manifest, encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON in {manifest}: {exc}")

# 2. Every bundled script compiles.
for script in sorted(glob.glob("skills/**/*.py", recursive=True)):
    try:
        py_compile.compile(script, doraise=True)
    except py_compile.PyCompileError as exc:
        errors.append(f"does not compile: {script}: {exc}")

# 3. Every SKILL.md carries name + description frontmatter.
skills = sorted(glob.glob("skills/*/SKILL.md"))
if not skills:
    errors.append("no skills found under skills/*/SKILL.md")
for skill in skills:
    text = open(skill, encoding="utf-8").read()
    if not text.startswith("---"):
        errors.append(f"{skill}: missing YAML frontmatter")
        continue
    frontmatter = text.split("---", 2)[1]
    for key in ("name:", "description:"):
        if key not in frontmatter:
            errors.append(f"{skill}: frontmatter missing '{key}'")

if errors:
    print("Plugin validation FAILED:")
    for err in errors:
        print(f"  - {err}")
    sys.exit(1)

print(f"Plugin validation passed: {len(skills)} skills, manifests OK, scripts compile.")
