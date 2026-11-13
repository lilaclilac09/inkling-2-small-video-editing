#!/usr/bin/env python3
"""Assemble a finished vlog: opening card -> body -> closing credits.

All three segments must be 1920x1080, 30fps, H.264 + AAC (the templates in
this folder produce exactly that). Joins are 0.5s dissolves (xfade +
acrossfade), so the opening melts into the first shot and the last shot melts
into the credits — a film opening and ending, not hard cuts.

Music: each segment carries its own audio. The body usually already has its
music mixed in (see the recut scripts); the opening and closing take --music
when you build them. If you want one continuous bed across the whole video
instead, mix it over the finished file afterwards (one-liner in README.md).

Usage:
  python3 assemble_vlog.py --opening opening.mp4 --body recap-v3.mp4 \
      --closing closing-scroll.mp4 --out my-vlog.mp4
  python3 assemble_vlog.py --body recap-v3.mp4 --closing closing-card.mp4 \
      --out my-vlog.mp4        # opening is optional, closing is optional
"""

import argparse
import json
import subprocess
import sys

XFADE = 0.5


def probe_duration(path):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "json", path],
        capture_output=True, text=True, check=True)
    return float(json.loads(r.stdout)["format"]["duration"])


def run(cmd):
    print(" ".join(cmd))
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-2000:])
        raise SystemExit(f"ffmpeg failed ({r.returncode})")
    return r


def main():
    ap = argparse.ArgumentParser(description="Assemble opening + body + closing.")
    ap.add_argument("--opening", default=None)
    ap.add_argument("--body", required=True)
    ap.add_argument("--closing", default=None)
    ap.add_argument("--xfade", type=float, default=XFADE)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    segs = [s for s in [args.opening, args.body, args.closing] if s]
    if len(segs) < 2:
        print("Need at least two segments to assemble (e.g. --body + --closing).")
        return 1
    durs = [probe_duration(s) for s in segs]
    print(f"segments: {list(zip(segs, [round(d, 2) for d in durs]))}")

    inputs = []
    for s in segs:
        inputs += ["-i", s]
    vf, af = [], []
    prev_v, prev_a = "0:v", "0:a"
    offset = durs[0] - args.xfade
    for k in range(1, len(segs)):
        vf.append(f"[{prev_v}][{k}:v]xfade=transition=fade:duration={args.xfade}:offset={offset:.3f}[v{k}]")
        af.append(f"[{prev_a}][{k}:a]acrossfade=d={args.xfade}[a{k}]")
        prev_v, prev_a = f"v{k}", f"a{k}"
        offset += durs[k] - args.xfade
    fc = ";".join(vf + af)
    total = sum(durs) - args.xfade * (len(segs) - 1)
    run(["ffmpeg", "-y"] + inputs +
        ["-filter_complex", fc, "-map", f"[{prev_v}]", "-map", f"[{prev_a}]",
         "-c:v", "libx264", "-preset", "medium", "-crf", "20",
         "-c:a", "aac", args.out])
    print(f"assembled: {args.out} ({total:.1f}s, {len(segs)} segments, "
          f"{args.xfade}s dissolves)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
