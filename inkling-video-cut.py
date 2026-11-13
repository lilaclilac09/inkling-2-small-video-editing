"""Cut the Cafe Cursor clips once the video and the picks exist.

Reads inkling-video-picks.jsonl (one JSON object per line, each with
clip.start / clip.end / clip.title) and cuts each clip out of the source
video with ffmpeg, applying the light vintage faded filter from the edit
plan (slightly desaturated, slightly soft — no heavy effects).

Usage:
  python3 inkling-video-cut.py --video cafe-cursor.mp4 --picks inkling-video-picks.jsonl --out clips/
  python3 inkling-video-cut.py --video cafe-cursor.mp4 --picks inkling-video-picks.jsonl --out clips/ --dry-run

The picks file is written by the scan step (Inkling's picks, corrected by
Aileen). Timestamps are HH:MM:SS or MM:SS. Clip files are named
01-<slug>.mp4 in pick order.

Music is mixed separately: the music file (not downloadable from Spotify)
has to be supplied, or the mix happens in CapCut. This script only cuts
the picture; the audio stays as recorded, music low under voices at mix.
"""

import argparse
import json
import os
import re
import subprocess
import sys

# Light vintage faded filter only: a touch less saturation, a touch less
# contrast. No grain, no light leak, no 4:3 — those come later, only for
# the flashback ending.
VIDEO_FILTER = "eq=saturation=0.88:contrast=0.96:brightness=0.02"


def slugify(title):
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug or "clip"


def parse_time(t):
    parts = [float(x) for x in str(t).split(":")]
    seconds = 0.0
    for p in parts:
        seconds = seconds * 60 + p
    return seconds


def load_picks(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--picks", default="inkling-video-picks.jsonl")
    ap.add_argument("--out", default="clips")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not os.path.exists(args.video):
        print(f"Video not found: {args.video}")
        print("Send the Cafe Cursor recording first — the cut starts from it.")
        return 1
    if not os.path.exists(args.picks):
        print(f"Picks not found: {args.picks}")
        print("Run the scan first (transcript + keyframes + Inkling picks),")
        print("then cut. One approved pick = one clip.")
        return 1

    rows = load_picks(args.picks)
    if not rows:
        print("Picks file is empty — nothing to cut yet.")
        return 1

    os.makedirs(args.out, exist_ok=True)
    print(f"Cutting {len(rows)} clips from {args.video} into {args.out}/")

    for i, row in enumerate(rows, 1):
        clip = row.get("clip", {})
        start = clip.get("start")
        end = clip.get("end")
        title = clip.get("title", f"clip {i}")
        if not start or not end:
            print(f"  [{i}] skip {title!r}: missing start/end")
            continue
        duration = parse_time(end) - parse_time(start)
        if duration <= 0:
            print(f"  [{i}] skip {title!r}: end is not after start")
            continue
        out = os.path.join(args.out, f"{i:02d}-{slugify(title)}.mp4")
        cmd = [
            "ffmpeg", "-y",
            "-ss", str(start), "-to", str(end),
            "-i", args.video,
            "-vf", VIDEO_FILTER,
            "-c:a", "aac", "-b:a", "192k",
            out,
        ]
        print(f"  [{i}] {title} ({start} -> {end}, {duration:.1f}s) -> {out}")
        if args.dry_run:
            print("      " + " ".join(cmd))
            continue
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"      ffmpeg failed: {result.stderr.strip().splitlines()[-1:]}")
            return 1

    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
