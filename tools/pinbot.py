#!/usr/bin/env python3
from __future__ import annotations
import argparse, base64, hashlib, json, os, re, tempfile, urllib.error, urllib.parse, urllib.request, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CART = ROOT / "cart.json"
CFG = ROOT / "upstreams.json"
SOURCES = ROOT / "SOURCES.md"
COMPANIONS = ROOT / "COMPANIONS.md"
NOTES = ROOT / "RELEASE_NOTES.md"
TAG_RE = re.compile(r"^v?(\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?)$")
CORE_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)")

def request(url, token=None):
    headers={"Accept":"application/vnd.github+json","User-Agent":"stormforged-pinbot/1.1","X-GitHub-Api-Version":"2022-11-28"}
    if token: headers["Authorization"]=f"Bearer {token}"
    return urllib.request.Request(url,headers=headers)

def get_json(url, token=None):
    with urllib.request.urlopen(request(url,token),timeout=60) as r: return json.load(r)

def releases(repo, token):
    return get_json(f"https://api.github.com/repos/{repo}/releases?per_page=100",token)

def tag_version(tag):
    m=TAG_RE.fullmatch(str(tag or ""))
    return m.group(1) if m else None

def vkey(v):
    m=CORE_RE.match(v or "")
    return tuple(map(int,m.groups())) if m else (-1,-1,-1)

def supports_yellow(m):
    games=m.get("games")
    if games is None: return True
    if not isinstance(games,list): return False
    return bool({str(x).lower() for x in games}&{"yellow","gen1","all"})

def asset_for(rel,cfg):
    z=[a for a in rel.get("assets",[]) if str(a.get("name","")).lower().endswith(".zip")]
    pat=cfg.get("asset_regex")
    if pat: z=[a for a in z if re.search(pat,str(a.get("name","")),re.I)]
    return z[0] if len(z)==1 else None

def manifest_at_tag(cfg,tag,token):
    path=cfg.get("manifest_path","manifest.json")
    qp="/".join(urllib.parse.quote(x,safe="") for x in path.split("/"))
    ref=urllib.parse.quote(tag,safe="")
    url=f"https://api.github.com/repos/{cfg['repo']}/contents/{qp}?ref={ref}"
    try: obj=get_json(url,token)
    except urllib.error.HTTPError as e:
        if e.code==404: return None
        raise
    try:
        if obj.get("encoding")!="base64": return None
        return json.loads(base64.b64decode(obj["content"]).decode())
    except Exception: return None

def inspect_zip(cfg,asset,token):
    url=asset.get("browser_download_url")
    if not url: raise RuntimeError(f"{cfg['name']}: asset has no download URL")
    req=request(url,token)
    h=hashlib.sha256()
    with tempfile.NamedTemporaryFile(suffix=".zip") as tmp:
        with urllib.request.urlopen(req,timeout=240) as r:
            while True:
                b=r.read(1024*1024)
                if not b: break
                h.update(b); tmp.write(b)
        tmp.flush()
        with zipfile.ZipFile(tmp.name) as z:
            names=[n for n in z.namelist() if n.endswith("manifest.json")]
            wanted=cfg.get("manifest_path","manifest.json").replace("\\","/")
            names.sort(key=lambda n:(not(n==wanted or n.endswith("/"+wanted)),len(n)))
            for n in names:
                try: m=json.loads(z.read(n).decode())
                except Exception: continue
                if isinstance(m,dict) and m.get("id")==cfg["id"]: return m,h.hexdigest()
    return None,h.hexdigest()

def digest(asset,token):
    d=str(asset.get("digest") or "")
    if re.fullmatch(r"sha256:[0-9a-fA-F]{64}",d): return d.split(":",1)[1].lower()
    url=asset.get("browser_download_url")
    if not url: raise RuntimeError("asset has no download URL")
    h=hashlib.sha256()
    with urllib.request.urlopen(request(url,token),timeout=240) as r:
        while True:
            b=r.read(1024*1024)
            if not b: break
            h.update(b)
    return h.hexdigest()

def inspect_release(cfg,rel,version,token):
    asset=asset_for(rel,cfg)
    if not asset: return None,"not exactly one matching ZIP"
    m=manifest_at_tag(cfg,str(rel.get("tag_name") or ""),token); ziphash=None
    if not m or m.get("id")!=cfg["id"]:
        m,ziphash=inspect_zip(cfg,asset,token)
    if not m: return None,"no matching manifest"
    if m.get("id")!=cfg["id"]: return None,f"manifest id {m.get('id')!r}"
    if str(m.get("version") or "")!=version: return None,f"manifest version {m.get('version')!r}"
    if not supports_yellow(m): return None,"not for Yellow/Gen1"
    return {"version":version,"tag":rel.get("tag_name"),"sha256":ziphash or digest(asset,token),"asset":asset.get("name")},None

def best_cart(cfg,global_cfg,token):
    allow=bool(cfg.get("allow_prerelease",global_cfg.get("check_prereleases",False)))
    candidates=[]
    for rel in releases(cfg["repo"],token):
        if rel.get("draft") or (rel.get("prerelease") and not allow): continue
        v=tag_version(rel.get("tag_name"))
        if v: candidates.append((vkey(v),v,rel))
    candidates.sort(reverse=True,key=lambda x:x[0])
    rejected=[]
    for _,v,rel in candidates:
        row,why=inspect_release(cfg,rel,v,token)
        if row:
            row.update(id=cfg["id"],name=cfg["name"],repo=cfg["repo"],rejected=rejected)
            return row
        rejected.append((v,why))
    raise RuntimeError(f"{cfg['name']}: no Yellow-safe semantic release; "+ "; ".join(f"{v} {w}" for v,w in rejected[:6]))

def latest_companion(cfg,global_cfg,token):
    allow=bool(cfg.get("allow_prerelease",global_cfg.get("check_prereleases",False)))
    for rel in releases(cfg["repo"],token):
        if rel.get("draft") or (rel.get("prerelease") and not allow): continue
        asset=asset_for(rel,cfg)
        if not asset: continue
        tag=str(rel.get("tag_name") or "")
        m=manifest_at_tag(cfg,tag,token); zh=None
        if not m or m.get("id")!=cfg["id"]: m,zh=inspect_zip(cfg,asset,token)
        if not m or m.get("id")!=cfg["id"] or not supports_yellow(m): continue
        return {"id":cfg["id"],"name":cfg["name"],"repo":cfg["repo"],"version":str(m.get("version") or "unknown"),
                "tag":tag,"sha256":zh or digest(asset,token),"cart_tag":bool(tag_version(tag))}
    raise RuntimeError(f"{cfg['name']}: no Yellow-safe companion release")

def bump(v):
    m=CORE_RE.match(v)
    if not m: raise RuntimeError(f"bad cart version {v}")
    a,b,c=map(int,m.groups()); return f"{a}.{b}.{c+1}"

def render_sources(cart,names):
    out=["# Source pins","",
         "Every native cart mod is pinned to an exact GitHub release and SHA-256. The scheduled pin bot only accepts resolver-compatible, Yellow-safe releases.","",
         "| Mod | Repository | Version | SHA-256 |","| --- | --- | ---: | --- |"]
    for m in cart["mods"]: out.append(f"| {names.get(m['id'],m['id'])} | {m['repo']} | {m['version']} | `{m['sha256']}` |")
    out += ["","## Automatic update safety","",
            "A newer release is accepted only when its tag is semantic, its manifest ID matches, its manifest targets Yellow/Gen1, and its ZIP hash is verified.",
            "Battle Art prereleases may be examined, but Gen2-only manifests are rejected.",""]
    return "\n".join(out)

def render_comp(rows):
    out=["# Tracked companion mods","",
         "These requested mods are tracked but their current release tags are not semantic, so the Gen1Recomp cart resolver cannot pin them directly.","",
         "| Mod | Repository | Manifest version | Release tag | SHA-256 |","| --- | --- | ---: | --- | --- |"]
    for r in rows: out.append(f"| {r['name']} | {r['repo']} | {r['version']} | `{r['tag']}` | `{r['sha256']}` |")
    out += ["","When an upstream adopts a normal `vX.Y.Z` or `X.Y.Z` release tag, it can be promoted to the native cart list.",""]
    return "\n".join(out)

def render_notes(cart,changes,names):
    out=[f"# KANTO: STORMFORGED v{cart['version']} ⚡🌧️","","Automated Yellow-safe upstream refresh.","","## Updated pins",""]
    for mid,old,new in changes: out.append(f"- {names.get(mid,mid)}: {old} → {new}")
    out += ["","All candidate pins passed semantic-tag, manifest-ID, Yellow/Gen1 target and SHA-256 checks.",
            "Battle Art remains preferred; Wilds of Kanto and Modern PC UI remain excluded.",""]
    return "\n".join(out)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--write",action="store_true"); ap.add_argument("--github-token",default=os.getenv("GITHUB_TOKEN")); args=ap.parse_args()
    cfg=json.loads(CFG.read_text()); cart=json.loads(CART.read_text())
    names={x["id"]:x["name"] for x in cfg["cart"]+cfg.get("companions",[])}
    resolved=[]
    for c in cfg["cart"]:
        r=best_cart(c,cfg,args.github_token); resolved.append(r)
        print(f"CART {r['name']}: {r['version']}")
        for v,w in r["rejected"][:4]: print(f"  rejected {v}: {w}")
    comp=[]
    for c in cfg.get("companions",[]):
        r=latest_companion(c,cfg,args.github_token); comp.append(r); print(f"COMPANION {r['name']}: {r['version']} tag={r['tag']}")
    by={r["id"]:r for r in resolved}; changes=[]
    for m in cart["mods"]:
        r=by.get(m["id"])
        if r and (m["version"]!=r["version"] or m["sha256"]!=r["sha256"]):
            changes.append((m["id"],m["version"],r["version"])); m["version"]=r["version"]; m["sha256"]=r["sha256"]
    if changes: cart["version"]=bump(cart["version"]); print("Stormforged ->",cart["version"])
    else: print("No native pin changes.")
    if args.write:
        CART.write_text(json.dumps(cart,indent=2,ensure_ascii=False)+"\n")
        SOURCES.write_text(render_sources(cart,names))
        COMPANIONS.write_text(render_comp(comp))
        if changes: NOTES.write_text(render_notes(cart,changes,names))
    return 0

if __name__=="__main__": raise SystemExit(main())
