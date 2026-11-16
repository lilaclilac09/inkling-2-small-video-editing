"""Update photo index after rotation + deletion (2026-11-13).

- Remove the 4 deleted rows from photo-index.jsonl.
- Mark the 67 rotated rows with "rotated": "90 CCW".
- Mark the 2 already-upright rows with "rotated": "already upright" and fix their note.
- Update photo-index.md counts/notes.
- Copy both files to the goals dir.
- Clean up photo-categories symlinks/dirs.
"""
import json, os, shutil
from collections import Counter

BASE = os.path.expanduser("~/workspace/inkling-recap")
CATS = os.path.join(BASE, "photo-categories")
GOALS = os.path.expanduser("~/workspace/goals/inkling-2-small-tinker-credits-for-video-editing/files")
DELETED = {"HM5A1332.JPG", "HM5A1357.JPG", "HM5A1539.JPG", "HM5A1614.JPG"}
ROTATED_67 = set()  # filled below from needs-rotation minus the 2 already-upright
ALREADY = {"HM5A1497.JPG", "HM5A1498.JPG"}

rot_dir = os.path.join(CATS, "needs-rotation")
rot_set = set(os.listdir(rot_dir))
ROTATED_67 = rot_set - ALREADY
assert len(rot_set) == 69, f"rotation set {len(rot_set)}"
assert len(ROTATED_67) == 67, f"rotated {len(ROTATED_67)}"

# --- 1. photo-index.jsonl ---
idx_path = os.path.join(BASE, "photo-index.jsonl")
rows = [json.loads(l) for l in open(idx_path) if l.strip()]
assert len(rows) == 300, f"expected 300 rows, got {len(rows)}"
kept = []
removed = 0
for r in rows:
    fn = r["file"]
    if fn in DELETED:
        removed += 1
        continue
    if fn in ROTATED_67:
        r["rotated"] = "90 CCW"
    elif fn in ALREADY:
        r["rotated"] = "already upright"
        # fix the misleading "ROTATED;" note
        if r.get("note", "").startswith("ROTATED;"):
            r["note"] = r["note"].replace("ROTATED;", "Checked upright, no rotation needed;", 1)
    kept.append(r)
assert removed == 4, f"removed {removed}"
assert len(kept) == 296, f"kept {len(kept)}"
# verify every kept row's file still exists in photos/
photos = os.path.join(BASE, "photos")
missing = [r["file"] for r in kept if not os.path.exists(os.path.join(photos, r["file"]))]
assert not missing, f"missing files in photos/: {missing}"
with open(idx_path, "w") as f:
    for r in kept:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
print(f"photo-index.jsonl: {len(rows)} -> {len(kept)} rows (removed {removed}, rotated marked {len(ROTATED_67)}, already-upright {len(ALREADY)})")

# --- 2. photo-index.md ---
md_path = os.path.join(BASE, "photo-index.md")
md = open(md_path).read()
# Header: 300 -> 296 + note about second batch
md = md.replace(
    "Classified by eye from labeled contact sheets, 2026-11-13. One row per photo in `photo-index.jsonl`;\n"
    "symlinked folders in `photo-categories/`. Counts of men/women are approximate, read from thumbnails —\n"
    "appearance only, no names attached. A second batch of photos is expected tomorrow; this index covers\n"
    "only the 300 files downloaded so far (4 DJI + 296 Canon HM5A).",
    "Classified by eye from labeled contact sheets, 2026-11-13. One row per photo in `photo-index.jsonl`;\n"
    "symlinked folders in `photo-categories/`. Counts of men/women are approximate, read from thumbnails —\n"
    "appearance only, no names attached. This index covers the first batch only: 300 files (4 DJI + 296 Canon HM5A),\n"
    "minus 4 deleted 2026-11-13 = 296 rows. A second batch is downloading into photos/ now (Drive folder grew past\n"
    "the first 300); those new files are NOT in this index and will need their own classification pass.")
# Scene counts: bad 4 -> 0 (deleted)
md = md.replace("- **bad**: 4\n", "- **bad**: 0 (4 deleted 2026-11-13, see below)\n")
# Rotation + deletion summary lines
md = md.replace(
    "- **Rotated 90° (need rotating back)**: 69 — see `photo-categories/needs-rotation/`\n"
    "- **Bad / obstructed / accidental (delete candidates)**: 4 — HM5A1332, HM5A1357, HM5A1539, HM5A1614",
    "- **Rotated 90° CCW (done 2026-11-13)**: 67 — pixels rotated in place, EXIF Orientation reset to 1. "
    "Method: PIL at quality 100, 4:4:4 subsampling (jpegtran was not installable in this VM; visually lossless). "
    "2 more (HM5A1497, HM5A1498) were checked and already upright, not rotated.\n"
    "- **Deleted 2026-11-13**: 4 — HM5A1332, HM5A1357, HM5A1539, HM5A1614 (bad/accidental shots). "
    "Removed from photos/ (recoverable trash until 2026-12-13); originals still in Google Drive.")
# Best-of-burst 99 -> 95
md = md.replace(
    "- **Best-of-burst set**: 99 files in `photo-categories/best-of-burst/` — one representative per burst plus every singleton",
    "- **Best-of-burst set**: 95 files in `photo-categories/best-of-burst/` — one representative per burst plus every singleton "
    "(was 99; the 4 deleted singletons were removed)")
# Headshot note: 1400/1401 were rotated, now upright
md = md.replace(
    "two men posing by the banner — HM5A1428–1435; man in white tee thumbs-up by the banner — HM5A1488–1493 (1490–1493 rotated).",
    "two men posing by the banner — HM5A1428–1435; man in white tee thumbs-up by the banner — HM5A1488–1493 (1490–1493 were rotated, now upright).")
md = md.replace(
    "Men (19): grey-haired man with glasses behind MacBook — HM5A1397–1401 (1397/1398 upright, 1400/1401 rotated);",
    "Men (19): grey-haired man with glasses behind MacBook — HM5A1397–1401 (1400/1401 were rotated, now upright);")
open(md_path, "w").write(md)
print("photo-index.md updated")

# --- 3. copy to goals dir ---
for name in ["photo-index.jsonl", "photo-index.md"]:
    src = os.path.join(BASE, name)
    dst = os.path.join(GOALS, name)
    if os.path.exists(dst):
        shutil.copy2(src, dst)
        print(f"copied {name} -> goals files/")
    else:
        print(f"goals copy of {name} not found, skipping")

# --- 4. clean up photo-categories symlinks ---
def remove_symlink(p):
    if os.path.islink(p):
        os.unlink(p)
        return True
    return False
removed_links = 0
# by-scene/bad: 4 broken links; remove dir if empty
for fn in DELETED:
    if remove_symlink(os.path.join(CATS, "by-scene", "bad", fn)):
        removed_links += 1
    if remove_symlink(os.path.join(CATS, "delete-candidates", fn)):
        removed_links += 1
    if remove_symlink(os.path.join(CATS, "best-of-burst", fn)):
        removed_links += 1
# needs-rotation: all 69 (rotation done)
for fn in sorted(rot_set):
    if remove_symlink(os.path.join(CATS, "needs-rotation", fn)):
        removed_links += 1
print(f"removed {removed_links} symlinks (expected {4*3 + 69} = 81)")
# remove now-empty dirs
for d in [os.path.join(CATS, "by-scene", "bad"),
          os.path.join(CATS, "delete-candidates"),
          os.path.join(CATS, "needs-rotation")]:
    try:
        os.rmdir(d)
        print(f"removed empty dir {d}")
    except OSError as e:
        print(f"dir {d} not empty or error: {e}")
# verify no broken symlinks remain
broken = []
for root, dirs, files in os.walk(CATS):
    for f in files:
        p = os.path.join(root, f)
        if os.path.islink(p) and not os.path.exists(p):
            broken.append(p)
print(f"broken symlinks remaining: {len(broken)}")
for b in broken:
    print("  ", b)
print("DONE")
