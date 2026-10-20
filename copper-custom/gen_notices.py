#!/usr/bin/env python3
"""gen_notices.py <assets-dir> <custom-dir> <source-url> [extra-output]

Writes assets/THIRD_PARTY_NOTICES.txt: the static notices plus a table of the mods really bundled in this build, with the
license and source each jar declares in its own fabric.mod.json.
"""
import glob
import json
import os
import sys
import zipfile

assets, custom, source_url = sys.argv[1:4]
extra = sys.argv[4] if len(sys.argv) > 4 else None

mods = {}
for jar in sorted(glob.glob(os.path.join(assets, "custom", "mods", "*", "*.jar"))):
    game = os.path.basename(os.path.dirname(jar))
    try:
        meta = json.loads(zipfile.ZipFile(jar).read("fabric.mod.json"))
    except Exception:
        continue
    license_ = meta.get("license", "not declared")
    if isinstance(license_, list):
        license_ = ", ".join(license_)
    contact = meta.get("contact") or {}
    link = contact.get("sources") or contact.get("homepage") or contact.get("issues") or ""
    entry = mods.setdefault(meta.get("id", os.path.basename(jar)), {
        "name": meta.get("name", os.path.basename(jar)), "license": license_, "link": link, "versions": {}})
    entry["versions"].setdefault(meta.get("version", "?"), []).append(game)

rows = []
for mod_id, entry in sorted(mods.items(), key=lambda kv: kv[1]["name"].lower()):
    versions = "; ".join(f"{v} (for {', '.join(games)})" for v, games in entry["versions"].items())
    rows.append(f"* {entry['name']} - {entry['license']}\n    {versions}\n    {entry['link'] or 'see the mod page'}")
table = "\n".join(rows) if rows else "(no mods bundled in this build)"

text = open(os.path.join(custom, "NOTICES.txt"), encoding="utf-8").read()
text = text.replace("@SOURCE_URL@", source_url).replace("@MODS@", table)
open(os.path.join(assets, "THIRD_PARTY_NOTICES.txt"), "w", encoding="utf-8").write(text)
if extra:
    open(extra, "w", encoding="utf-8").write(text)
print(f"notices written: {len(mods)} mods listed")
