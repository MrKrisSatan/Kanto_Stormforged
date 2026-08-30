#!/usr/bin/env python3
"""Refresh KANTO: STORMFORGED pins from upstream GitHub releases.

Only releases that are safe for a published .g1rcart are allowed into cart.json:
- release tag is semantic version (v1.2.3 or 1.2.3)
- release is not draft, and prereleases are excluded unless configured
- the tagged manifest id matches the configured mod id
- the manifest targets Yellow / Gen1 (or uses the legacy no-games = Gen1 rule)
- there is one unambiguous .zip release asset
- the release asset has a verified SHA-256 (GitHub digest or a streamed fallback)

Non-semver upstreams are tracked in COMPANIONS.md but are never forced into the
cart. If those projects later publish resolver-compatible semantic tags, move
them into the "cart" section of upstreams.json.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CART_PATH = ROOT / "cart.json"
CONFIG_PATH = ROOT / "upstreams.json"
SOURCES_PATH = ROOT / "SOURCES.md"
COMPANIONS_PATH = ROOT / "COMPANIONS.md"
RELEASE_NOTES_PATH = ROOT / "RELEASE_NOTES.md"

SEMVER_TAG = re.compile(r"^v?(\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?)$")
CORE = re.compile(r"^(\d+)\.(\d+)\.(\d+)")


def api_json(url: str, token: str | None):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "kanto-stormforged-pinbot/1.0",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=45) as resp:
        return json.load(resp)


def release_list(repo: str, token: str | None):
    owner, name = repo.split("/", 1)
    url = f"https://api.github.com/repos/{owner}/{name}/releases?per_page=100"
    return api_json(url, token)


def manifest_at(repo: str, tag: str, path: str, token: str | None):
    owner, name = repo.split("/", 1)
    safe_path = "/".join(urllib.parse.quote(part, safe="") for part in path.split("/"))
    ref = urllib.parse.quote(tag, safe="")
    url = f"https://api.github.com/repos/{owner}/{name}/contents/{safe_path}?ref={ref}"
    try:
        obj = api_json(url, token)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        raise
    if not isinstance(obj, dict) or obj.get("encoding") != "base64":
        return None
    body = base64.b64decode(obj.get("content", "")).decode("utf-8")
    return json.loads(body)


def semver_from_tag(tag: str):
    match = SEMVER_TAG.fullmatch(tag or "")
    return match.group(1) if match else None


def semver_key(version: str):
    match = CORE.match(version)
    if not match:
        return (-1, -1, -1)
    return tuple(int(x) for x in match.groups())


def supports_yellow(manifest: dict):
    games = manifest.get("games")
    if games is None:
        # Gen1Recomp legacy rule: no games key means Gen1.
        return True
    if not isinstance(games, list):
        return False
    tokens = {str(value).strip().lower() for value in games}
    return bool(tokens & {"all", "gen1", "yellow"})


def zip_asset(release: dict, config: dict):
    assets = [a for a in release.get("assets", []) if isinstance(a, dict)]
    pattern = config.get("asset_regex")
    if pattern:
        rx = re.compile(pattern, re.I)
        matches = [a for a in assets if rx.search(str(a.get("name", "")))]
    else:
        matches = [a for a in assets if str(a.get("name", "")).lower().endswith(".zip")]
    if len(matches) != 1:
        return None
    return matches[0]


def asset_sha256(asset: dict, token: str | None):
    digest = str(asset.get("digest") or "")
    if digest.startswith("sha256:") and len(digest) == 71:
        return digest.split(":", 1)[1].lower()

    url = asset.get("browser_download_url")
    if not url:
        raise RuntimeError("release asset has no browser_download_url")
    headers = {"User-Agent": "kanto-stormforged-pinbot/1.0"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    h = hashlib.sha256()
    with urllib.request.urlopen(req, timeout=120) as resp:
        while True:
            chunk = resp.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def candidate_cart_release(config: dict, global_config: dict, token: str | None):
    allow_pre = bool(config.get("allow_prerelease", global_config.get("check_prereleases", False)))
    valid = []
    rejected = []
    for release in release_list(config["repo"], token):
        if release.get("draft"):
            continue
        if release.get("prerelease") and not allow_pre:
            continue
        tag = str(release.get("tag_name") or "")
        version = semver_from_tag(tag)
        if not version:
            continue
        manifest = manifest_at(config["repo"], tag, config["manifest_path"], token)
        if not manifest:
            rejected.append((version, "tag has no readable configured manifest"))
            continue
        if manifest.get("id") != config["id"]:
            rejected.append((version, f"manifest id is {manifest.get('id')!r}"))
            continue
        if str(manifest.get("version") or "") != version:
            rejected.append((version, f"manifest version is {manifest.get('version')!r}"))
            continue
        if not supports_yellow(manifest):
            rejected.append((version, "manifest does not target Yellow/Gen1"))
            continue
        asset = zip_asset(release, config)
        if not asset:
            rejected.append((version, "release does not have one unambiguous ZIP asset"))
            continue
        valid.append((semver_key(version), version, tag, release, manifest, asset))
    if not valid:
        reason = "; ".join(f"{v}: {why}" for v, why in rejected[:6])
        raise RuntimeError(f"{config['name']}: no Yellow-safe cart release found. {reason}")
    valid.sort(key=lambda row: row[0], reverse=True)
    _, version, tag, release, manifest, asset = valid[0]
    return {
        "id": config["id"],
        "name": config["name"],
        "repo": config["repo"],
        "version": version,
        "tag": tag,
        "sha256": asset_sha256(asset, token),
        "asset": asset.get("name"),
        "published_at": release.get("published_at"),
        "manifest": manifest,
        "rejected": rejected,
    }


def latest_companion(config: dict, global_config: dict, token: str | None):
    allow_pre = bool(config.get("allow_prerelease", global_config.get("check_prereleases", False)))
    for release in release_list(config["repo"], token):
        if release.get("draft") or (release.get("prerelease") and not allow_pre):
            continue
        tag = str(release.get("tag_name") or "")
        manifest = manifest_at(config["repo"], tag, config["manifest_path"], token)
        if not manifest or manifest.get("id") != config["id"] or not supports_yellow(manifest):
            continue
        asset = zip_asset(release, config)
        if not asset:
            continue
        return {
            "id": config["id"],
            "name": config["name"],
            "repo": config["repo"],
            "version": str(manifest.get("version") or "unknown"),
            "tag": tag,
            "sha256": asset_sha256(asset, token),
            "asset": asset.get("name"),
            "published_at": release.get("published_at"),
            "cart_compatible_tag": semver_from_tag(tag) is not None,
        }
    raise RuntimeError(f"{config['name']}: no Yellow-safe companion release found")


def bump_patch(version: str):
    match = CORE.match(version)
    if not match:
        raise RuntimeError(f"cart version {version!r} is not a normal x.y.z version")
    major, minor, patch = (int(x) for x in match.groups())
    return f"{major}.{minor}.{patch + 1}"


def render_sources(cart: dict, names: dict):
    lines = [
        "# Source pins",
        "",
        "Every native cart mod is pinned to an exact GitHub release and SHA-256. "
        "The scheduled pin bot only accepts resolver-compatible, Yellow-safe releases.",
        "",
        "| Mod | Repository | Version | SHA-256 |",
        "| --- | --- | ---: | --- |",
    ]
    for mod in cart["mods"]:
        lines.append(
            f"| {names.get(mod['id'], mod['id'])} | {mod['repo']} | {mod['version']} | `{mod['sha256']}` |"
        )
    lines += [
        "",
        "## Automatic update safety",
        "",
        "A newer GitHub release is not automatically considered safe. The updater checks the tagged "
        "`manifest.json`, requires the expected mod ID, requires Yellow/Gen1 support, requires a "
        "semantic release tag the cart resolver can fetch, and verifies the ZIP SHA-256.",
        "",
        "Battle Art is intentionally governed by this rule. Gen2-only releases are ignored even when "
        "GitHub marks them newer.",
        "",
    ]
    return "\n".join(lines)


def render_companions(rows: list[dict]):
    lines = [
        "# Tracked companion mods",
        "",
        "These projects are part of the intended STORMFORGED setup, but their current upstream release "
        "tags are not semantic versions, so Gen1Recomp's cart resolver cannot pin them directly. "
        "The pin bot still tracks and hashes their latest Yellow-safe releases.",
        "",
        "| Mod | Repository | Manifest version | Release tag | SHA-256 |",
        "| --- | --- | ---: | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row['name']} | {row['repo']} | {row['version']} | `{row['tag']}` | `{row['sha256']}` |"
        )
    lines += [
        "",
        "Once an upstream publishes the same mod under a normal `vX.Y.Z` or `X.Y.Z` release tag, it can "
        "be moved into the native cart list and will then participate in automatic cart updates.",
        "",
    ]
    return "\n".join(lines)


def update_cart(cart: dict, resolved: list[dict]):
    by_id = {row["id"]: row for row in resolved}
    changes = []
    for mod in cart["mods"]:
        row = by_id.get(mod["id"])
        if not row:
            continue
        old = (mod["version"], mod["sha256"])
        new = (row["version"], row["sha256"])
        if old != new:
            changes.append((mod["id"], mod["version"], row["version"]))
            mod["version"], mod["sha256"] = new
    return changes


def render_release_notes(cart: dict, changes: list[tuple[str, str, str]], names: dict):
    lines = [
        f"# KANTO: STORMFORGED v{cart['version']} ⚡🌧️",
        "",
        "Automated upstream refresh for the Pokémon Yellow STORMFORGED cart.",
        "",
        "## Updated pins",
        "",
    ]
    if changes:
        for mod_id, old, new in changes:
            lines.append(f"- {names.get(mod_id, mod_id)}: {old} → {new}")
    else:
        lines.append("- Initial Yellow-safe automatic-update baseline.")
    lines += [
        "",
        "Every native pin was rechecked for manifest identity, Yellow/Gen1 targeting, release-tag "
        "compatibility and archive SHA-256 before publication.",
        "",
        "Wilds of Kanto and Modern PC UI remain excluded to avoid the compatibility problems flagged "
        "by Battle Art. Dramaless Shape remains replaced by Battle Art.",
        "",
    ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write refreshed pins and docs")
    parser.add_argument("--github-token", default=os.getenv("GITHUB_TOKEN"))
    args = parser.parse_args()

    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    cart = json.loads(CART_PATH.read_text(encoding="utf-8"))
    names = {row["id"]: row["name"] for row in config["cart"]}
    names.update({row["id"]: row["name"] for row in config.get("companions", [])})

    resolved = []
    for mod in config["cart"]:
        row = candidate_cart_release(mod, config, args.github_token)
        resolved.append(row)
        print(f"CART {row['name']}: {row['version']} {row['sha256'][:12]}…")
        for version, reason in row.get("rejected", [])[:3]:
            print(f"  rejected {version}: {reason}")

    companions = []
    for mod in config.get("companions", []):
        row = latest_companion(mod, config, args.github_token)
        companions.append(row)
        suffix = " (cart-compatible tag)" if row["cart_compatible_tag"] else ""
        print(f"COMPANION {row['name']}: {row['version']} tag={row['tag']}{suffix}")

    changes = update_cart(cart, resolved)
    if changes:
        old_cart_version = cart["version"]
        cart["version"] = bump_patch(old_cart_version)
        print(f"Stormforged: {old_cart_version} -> {cart['version']}")
    else:
        print("No native cart pin changes.")

    if args.write:
        CART_PATH.write_text(json.dumps(cart, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        SOURCES_PATH.write_text(render_sources(cart, names), encoding="utf-8")
        COMPANIONS_PATH.write_text(render_companions(companions), encoding="utf-8")
        if changes:
            RELEASE_NOTES_PATH.write_text(render_release_notes(cart, changes, names), encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
