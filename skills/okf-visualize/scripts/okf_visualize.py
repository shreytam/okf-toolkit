#!/usr/bin/env python3
"""Render an OKF bundle as a self-contained interactive HTML graph.

Usage: python3 okf_visualize.py <bundle-dir> [-o out.html] [--name "Display Name"]

Zero dependencies. Output is one HTML file (Cytoscape.js + marked via CDN);
no backend, no data leaves the page.
"""
import argparse
import json
import os
import re
import sys

RESERVED = {"index.md", "log.md"}
FM = re.compile(r"\A---\s*\n(.*?)\n---\s*(\n|\Z)", re.DOTALL)
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
FENCE = re.compile(r"^(```|~~~).*?^\1\s*$", re.DOTALL | re.MULTILINE)


def parse_fm(block):
    data = {}
    try:
        import yaml  # type: ignore
        d = yaml.safe_load(block)
        return d if isinstance(d, dict) else {}
    except Exception:
        pass
    for line in block.splitlines():
        if line and not line[0].isspace() and ":" in line:
            k, _, v = line.partition(":")
            data[k.strip()] = v.strip().strip("'\"")
    return data


def load(root):
    concepts, edges = {}, []
    paths = []
    for dp, _, fns in os.walk(root):
        for fn in sorted(fns):
            if fn.endswith(".md") and fn not in RESERVED:
                paths.append(os.path.join(dp, fn))
    rels = {os.path.relpath(p, root).replace(os.sep, "/") for p in paths}
    for p in paths:
        rel = os.path.relpath(p, root).replace(os.sep, "/")
        try:
            text = open(p, encoding="utf-8").read()
        except (UnicodeDecodeError, OSError):
            continue
        m = FM.match(text)
        fm = parse_fm(m.group(1)) if m else {}
        body = text[m.end():] if m else text
        cid = rel[:-3]
        concepts[cid] = {
            "id": cid,
            "type": str(fm.get("type", "Unknown")),
            "title": str(fm.get("title") or os.path.basename(cid)),
            "description": str(fm.get("description", "")),
            "resource": str(fm.get("resource", "")),
            "tags": fm.get("tags") if isinstance(fm.get("tags"), list) else [],
            "body": body,
        }
        for t in LINK.findall(re.sub(r"`[^`\n]*`", "", FENCE.sub("", text))):
            t2 = t.split("#")[0]
            if t2.startswith(("http", "mailto")) or not t2.endswith(".md"):
                continue
            tgt = t2.lstrip("/") if t2.startswith("/") else os.path.normpath(
                os.path.join(os.path.dirname(rel), t2)).replace(os.sep, "/")
            if tgt in rels and os.path.basename(tgt) not in RESERVED:
                edges.append([cid, tgt[:-3]])
    return concepts, edges


TEMPLATE = r"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>__NAME__ — OKF graph</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.28.1/cytoscape.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/marked/12.0.2/marked.min.js"></script>
<style>
body{margin:0;font-family:system-ui,sans-serif;display:flex;height:100vh}
#cy{flex:1}
#panel{width:380px;border-left:1px solid #ddd;padding:16px;overflow:auto;background:#fafafa}
#panel h1{font-size:1.1em}#panel table{border-collapse:collapse;font-size:.85em}
#panel td,#panel th{border:1px solid #ccc;padding:3px 6px}
#search{position:fixed;top:10px;left:10px;z-index:9;padding:6px 10px;width:220px;border:1px solid #bbb;border-radius:6px}
.meta{color:#666;font-size:.85em}.tag{background:#e0e7ff;border-radius:4px;padding:1px 6px;margin-right:4px;font-size:.8em}
.bl{font-size:.85em;color:#444}#panel a{color:#3b5bdb}
</style></head><body>
<input id="search" placeholder="search concepts…">
<div id="cy"></div><div id="panel"><p class="meta">Click a node. __COUNT__ concepts, __ECOUNT__ links.</p></div>
<script>
const DATA=__DATA__;
const esc=x=>String(x).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const safeUrl=u=>/^https?:\/\//i.test(u)?u:null;
function sanitize(html){
 const t=document.createElement("template");t.innerHTML=html;
 t.content.querySelectorAll("script,style,iframe,object,embed,link,meta,form").forEach(n=>n.remove());
 t.content.querySelectorAll("*").forEach(n=>{
  [...n.attributes].forEach(a=>{
   if(/^on/i.test(a.name))n.removeAttribute(a.name);
   if((a.name==="href"||a.name==="src")&&/^\s*(javascript|data|vbscript):/i.test(a.value))n.removeAttribute(a.name);
  });});
 return t.innerHTML;}
const palette=["#4c6ef5","#f76707","#37b24d","#ae3ec9","#f59f00","#e64980","#0ca678","#845ef7"];
const types=[...new Set(Object.values(DATA.concepts).map(c=>c.type))];
const color=t=>palette[types.indexOf(t)%palette.length];
const backlinks={};DATA.edges.forEach(([s,t])=>{(backlinks[t]=backlinks[t]||[]).push(s)});
const cy=cytoscape({container:document.getElementById("cy"),
 elements:[...Object.values(DATA.concepts).map(c=>({data:{id:c.id,label:c.title,type:c.type}})),
           ...DATA.edges.map(([s,t],i)=>({data:{id:"e"+i,source:s,target:t}}))],
 style:[{selector:"node",style:{label:"data(label)","font-size":"10px","background-color":e=>color(e.data("type")),"text-valign":"bottom","text-margin-y":"4px"}},
        {selector:"edge",style:{width:1.2,"line-color":"#bbb","target-arrow-shape":"triangle","target-arrow-color":"#bbb","curve-style":"bezier","arrow-scale":.7}},
        {selector:".dim",style:{opacity:.15}}],
 layout:{name:"cose",animate:false}});
function show(id){const c=DATA.concepts[id];if(!c)return;
 let html=`<h1>${esc(c.title)}</h1><p class="meta">${esc(c.id)} · <b style="color:${color(c.type)}">${esc(c.type)}</b></p>`;
 if(c.description)html+=`<p>${esc(c.description)}</p>`;
 if(c.tags.length)html+=`<p>${c.tags.map(t=>`<span class="tag">${esc(t)}</span>`).join("")}</p>`;
 const ru=safeUrl(c.resource);
 if(c.resource)html+=`<p class="meta">resource: ${ru?`<a href="${esc(ru)}" target="_blank" rel="noopener noreferrer">${esc(c.resource)}</a>`:esc(c.resource)}</p>`;
 if(backlinks[id])html+=`<p class="bl">Cited by: ${backlinks[id].map(b=>`<a href="#" data-cid="${esc(b)}">${esc(b)}</a>`).join(", ")}</p>`;
 let body=sanitize(marked.parse(c.body));
 body=body.replace(/href="\/?([^"]+)\.md"/g,(m,p)=>`href="#" data-cid="${p}"`);
 html+=`<hr>${body}`;
 const panel=document.getElementById("panel");panel.innerHTML=html;
 panel.querySelectorAll("a[data-cid]").forEach(a=>a.addEventListener("click",e=>{e.preventDefault();show(a.dataset.cid);}));
 cy.elements().removeClass("dim");}
cy.on("tap","node",e=>show(e.target.id()));
document.getElementById("search").addEventListener("input",e=>{
 const q=e.target.value.toLowerCase();cy.elements().removeClass("dim");
 if(!q)return;cy.nodes().forEach(n=>{const c=DATA.concepts[n.id()];
 const hit=(c.title+c.id+c.tags.join(" ")).toLowerCase().includes(q);
 if(!hit)n.addClass("dim");});});
</script></script></body></html>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bundle")
    ap.add_argument("-o", "--out")
    ap.add_argument("--name")
    a = ap.parse_args()
    if not os.path.isdir(a.bundle):
        sys.exit(f"not a directory: {a.bundle}")
    concepts, edges = load(a.bundle)
    if not concepts:
        sys.exit("no concept documents found")
    name = a.name or os.path.basename(os.path.abspath(a.bundle))
    out = a.out or os.path.join(a.bundle, "viz.html")
    html = (TEMPLATE.replace("__DATA__", json.dumps({"concepts": concepts, "edges": edges}).replace("</", "<\\/"))
            .replace("__NAME__", name.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")).replace("__COUNT__", str(len(concepts)))
            .replace("__ECOUNT__", str(len(edges))))
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Wrote {out} ({len(concepts)} concepts, {len(edges)} links)")


if __name__ == "__main__":
    main()
