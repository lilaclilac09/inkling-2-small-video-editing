#!/usr/bin/env python3
"""Build the categorized photo database from photo-index.jsonl.

Creates ~/workspace/inkling-recap/photo-categories/ with symlinks:
  by-scene/<scene>/          one link per photo
  best-of-burst/             one representative per burst + all singletons
  needs-rotation/            the 69 photos shot rotated 90 degrees
  headshots-men/             portrait-scene photos of men
  headshots-women/           portrait-scene photos of women
  delete-candidates/         the 4 bad/obstructed/accidental shots
Also writes photo-index.md (human summary) next to the jsonl.
"""
import json, os, collections, shutil

BASE = "/home/hatch/workspace/inkling-recap"
PHOTOS = os.path.join(BASE, "photos")
CAT = os.path.join(BASE, "photo-categories")

rows = [json.loads(l) for l in open(os.path.join(BASE, "photo-index.jsonl"))]
by_file = {r["file"]: r for r in rows}

if os.path.exists(CAT):
    shutil.rmtree(CAT)

def link(sub, fname):
    d = os.path.join(CAT, sub)
    os.makedirs(d, exist_ok=True)
    os.symlink(os.path.join(PHOTOS, fname), os.path.join(d, fname))

for r in rows:
    link(os.path.join("by-scene", r["scene"]), r["file"])
    if "ROTATED" in r["note"]:
        link("needs-rotation", r["file"])
    if r["scene"] == "bad":
        link("delete-candidates", r["file"])

# headshots split (portrait scene only; by the main subject, not background people)
for r in rows:
    if r["scene"] != "portrait":
        continue
    if "woman in black sleeveless top" in r["note"] or "same woman" in r["note"]:
        link("headshots-women", r["file"])
    else:
        link("headshots-men", r["file"])

# best-of-burst: first non-rotated file per burst, else first; singletons all in
bursts = collections.defaultdict(list)
for r in rows:
    if r.get("burst"):
        bursts[r["burst"]].append(r)
best = []
for name, members in sorted(bursts.items()):
    members = sorted(members, key=lambda r: r["file"])
    pick = next((m for m in members if "ROTATED" not in m["note"]), members[0])
    pick = dict(pick)
    pick["burst_size"] = len(members)
    best.append(pick)
    link("best-of-burst", pick["file"])
for r in rows:
    if not r.get("burst"):
        link("best-of-burst", r["file"])

scenes = collections.Counter(r["scene"] for r in rows)
rot = sum(1 for r in rows if "ROTATED" in r["note"])
print("scenes:", dict(scenes))
print("bursts:", len(bursts), "| best-of-burst files:", len(best) + sum(1 for r in rows if not r.get("burst")))
print("rotated:", rot, "| bad:", sum(1 for r in rows if r["scene"] == "bad"))

# markdown summary
lines = []
lines.append("# Cafe Cursor meetup — photo classification (300 photos)")
lines.append("")
lines.append("Classified by eye from labeled contact sheets, 2026-11-13. One row per photo in `photo-index.jsonl`;")
lines.append("symlinked folders in `photo-categories/`. Counts of men/women are approximate, read from thumbnails —")
lines.append("appearance only, no names attached. A second batch of photos is expected tomorrow; this index covers")
lines.append("only the 300 files downloaded so far (4 DJI + 296 Canon HM5A).")
lines.append("")
lines.append("## Counts by scene")
for scene, n in sorted(scenes.items(), key=lambda kv: -kv[1]):
    lines.append(f"- **{scene}**: {n}")
lines.append("")
lines.append(f"- **Rotated 90° (need rotating back)**: {rot} — see `photo-categories/needs-rotation/`")
lines.append(f"- **Bad / obstructed / accidental (delete candidates)**: {sum(1 for r in rows if r['scene']=='bad')} — HM5A1332, HM5A1357, HM5A1539, HM5A1614")
lines.append(f"- **Burst groups**: {len(bursts)} groups covering {sum(len(v) for v in bursts.values())} photos; {sum(1 for r in rows if not r.get('burst'))} singletons")
lines.append(f"- **Best-of-burst set**: {len(best) + sum(1 for r in rows if not r.get('burst'))} files in `photo-categories/best-of-burst/` — one representative per burst plus every singleton")
lines.append("")
lines.append("## Headshots (portrait scene, 21 total)")
lines.append("")
lines.append("Men (19): grey-haired man with glasses behind MacBook — HM5A1397–1401 (1397/1398 upright, 1400/1401 rotated);")
lines.append("two men posing by the banner — HM5A1428–1435; man in white tee thumbs-up by the banner — HM5A1488–1493 (1490–1493 rotated).")
lines.append("Women (2): woman in black sleeveless top smiling at camera — HM5A1412–1413.")
lines.append("Folders: `photo-categories/headshots-men/` and `photo-categories/headshots-women/`.")
lines.append("")
lines.append("## Group photos")
lines.append("")
lines.append("Eight men lined up by the banner outdoors — HM5A1478–1484 (7 near-identical shots, keep 1478).")
lines.append("")
lines.append("## Talks / demos worth pulling stills from")
lines.append("")
lines.append("- Woman in white tee, first talk — DJI 0005/0006 (09:20)")
lines.append("- Man in dark shirt presenting — DJI 0071/0072 (11:39/11:50)")
lines.append("- Man in white graphic tee, long burst — HM5A1334–1345")
lines.append("- Remote talk, woman on screen — HM5A1369–1374")
lines.append("- Grey-haired man with glasses, dashboard demo — HM5A1391–1399")
lines.append("- Young man in cream tee — HM5A1404, HM5A1416–1419")
lines.append("- Man in white tee + black shorts — HM5A1436–1450 (1436–1446 rotated)")
lines.append("- Man in navy polo + cap, code on screen — HM5A1506–1511, 1522–1523")
lines.append("- Man in light blue shirt, Pairoa demo — HM5A1528, HM5A1544–1556")
lines.append("- Man in beige tee, 'Your agents work.' — HM5A1604–1620")
lines.append("- Man in black tee, phone demo — HM5A1499–1505")
lines.append("")
lines.append("## Best-of-burst picks (representative per burst)")
lines.append("")
for b in sorted(best, key=lambda b: b["file"]):
    lines.append(f"- {b['file']} — {b['note']} (burst of {b['burst_size']})")
lines.append("")
lines.append("## Method note")
lines.append("")
lines.append("No face-recognition or naming was used: people are described by clothing/role only, and nobody is")
lines.append("identified by name. Gender splits are thumbnail reads and will be wrong on some wide shots — treat")
lines.append("the men/women counts as rough. If a burst's representative looks off, the whole burst is in")
lines.append("`photo-categories/by-scene/<scene>/` under its filenames.")

with open(os.path.join(BASE, "photo-index.md"), "w") as f:
    f.write("\n".join(lines) + "\n")
print("wrote photo-index.md")
