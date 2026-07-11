#!/usr/bin/env python3
"""Conformance checker for OKF (Open Knowledge Format) v0.1 bundles.

Usage: python3 validate_okf.py <bundle-dir>

Exit code 0 = conformant (warnings allowed), 1 = errors found.
No dependencies required; uses PyYAML if available for stricter parsing.
"""
import os
import re
import sys

RESERVED = {"index.md", "log.md"}

try:
    import yaml  # type: ignore
except ImportError:
    yaml = None

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*(\n|\Z)", re.DOTALL)
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
DATE_HEADING_RE = re.compile(r"^## \d{4}-\d{2}-\d{2}\s*$", re.MULTILINE)
FENCE_RE = re.compile(r"^(```|~~~).*?^\1\s*$", re.DOTALL | re.MULTILINE)


def strip_code_blocks(text):
    """Remove fenced code blocks and inline code spans so example links inside them are not scanned."""
    return re.sub(r"`[^`\n]*`", "", FENCE_RE.sub("", text))


def parse_frontmatter(text):
    """Return (dict_or_None, error_or_None)."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None, "no frontmatter block delimited by --- lines"
    block = m.group(1)
    if yaml is not None:
        try:
            data = yaml.safe_load(block)
        except yaml.YAMLError as e:
            return None, f"unparseable YAML: {e}"
        if not isinstance(data, dict):
            return None, "frontmatter is not a YAML mapping"
        return data, None
    # Fallback: naive key: value parse (top-level keys only)
    data = {}
    for line in block.splitlines():
        if line and not line[0].isspace() and ":" in line:
            k, _, v = line.partition(":")
            data[k.strip()] = v.strip()
    return data, None


def check_concept(path, text, errors, warnings, rel):
    fm, err = parse_frontmatter(text)
    if err:
        errors.append(f"{rel}: {err}")
        return
    t = fm.get("type")
    if not t or (isinstance(t, str) and not t.strip()):
        errors.append(f"{rel}: missing or empty required 'type' field")
    if not fm.get("description"):
        warnings.append(f"{rel}: no 'description' (recommended)")
    if not fm.get("title"):
        warnings.append(f"{rel}: no 'title' (recommended)")


def check_index(text, errors, warnings, rel, is_root):
    m = FRONTMATTER_RE.match(text)
    if m:
        if not is_root:
            errors.append(f"{rel}: index.md may only carry frontmatter at the bundle root")
        else:
            fm, err = parse_frontmatter(text)
            if err:
                errors.append(f"{rel}: {err}")
            elif set(fm.keys()) - {"okf_version"}:
                warnings.append(f"{rel}: root index frontmatter should only declare okf_version")
    if not LINK_RE.search(strip_code_blocks(text)):
        warnings.append(f"{rel}: index.md contains no links")


def check_log(text, errors, warnings, rel):
    if FRONTMATTER_RE.match(text):
        warnings.append(f"{rel}: frontmatter in log.md is not part of the spec's log format")
    if not DATE_HEADING_RE.search(text):
        warnings.append(f"{rel}: log.md has no ISO-dated '## YYYY-MM-DD' headings")


def main():
    if len(sys.argv) != 2 or not os.path.isdir(sys.argv[1]):
        print(__doc__)
        sys.exit(2)
    root = os.path.abspath(sys.argv[1])
    errors, warnings = [], []
    md_files = []
    for dirpath, _, filenames in os.walk(root):
        for fn in sorted(filenames):
            if fn.endswith(".md"):
                md_files.append(os.path.join(dirpath, fn))

    all_rel = {os.path.relpath(p, root).replace(os.sep, "/") for p in md_files}
    concepts = 0
    for path in md_files:
        rel = os.path.relpath(path, root).replace(os.sep, "/")
        try:
            with open(path, encoding="utf-8") as f:
                text = f.read()
        except (UnicodeDecodeError, OSError) as e:
            errors.append(f"{rel}: unreadable as UTF-8 markdown ({e.__class__.__name__})")
            continue
        name = os.path.basename(path)
        if name == "index.md":
            check_index(text, errors, warnings, rel, is_root=(rel == "index.md"))
        elif name == "log.md":
            check_log(text, errors, warnings, rel)
        else:
            concepts += 1
            check_concept(path, text, errors, warnings, rel)
        # Broken internal links (warning only — legal per spec §5.3)
        for target in LINK_RE.findall(strip_code_blocks(text)):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            t = target.split("#")[0]
            if not t.endswith(".md"):
                continue
            if t.startswith("/"):
                resolved = t.lstrip("/")
            else:
                resolved = os.path.normpath(
                    os.path.join(os.path.dirname(rel), t)
                ).replace(os.sep, "/")
            if resolved not in all_rel:
                warnings.append(f"{rel}: link target not in bundle: {target}")

    print(f"Bundle: {root}")
    print(f"Concept documents: {concepts}, total .md files: {len(md_files)}")
    for e in errors:
        print(f"ERROR   {e}")
    for w in warnings:
        print(f"warning {w}")
    if errors:
        print(f"\nRESULT: NOT CONFORMANT ({len(errors)} error(s), {len(warnings)} warning(s))")
        sys.exit(1)
    print(f"\nRESULT: CONFORMANT with OKF v0.1 ({len(warnings)} warning(s))")
    sys.exit(0)


if __name__ == "__main__":
    main()
