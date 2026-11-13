"""Build the ~2-minute recap video from the approved picks.

Takes the picks file (one JSON object per line, in order), cuts each
segment from its source video, joins them in order, and optionally mixes
the music file low underneath. Tinker does the thinking (which moments);
this script does the cutting, locally, with ffmpeg.

Each pick may name its own source file:
  {"clip": {"file": "DJI_20260719091607_0001_D.MP4",
            "start": "0:02", "end": "0:09", "title": "guitar", ...}}
Source files are resolved under --media-dir (default: current folder).
If a pick has no "file", it is cut from --video instead.

  python3 inkling-video-recap.py --media-dir media --picks inkling-video-picks.jsonl --music timing.mp3 --out recap.mp4
  python3 inkling-video-recap.py --video cafe-cursor.mp4 --picks inkling-video-picks.jsonl --out recap.mp4

--music is optional. Without it the recap has only the room audio.
--dry-run prints every ffmpeg command without running anything.
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile

FILTER = "eq=saturation=0.88:contrast=0.96:brightness=0.02"


def parse_ts(value):
    """Accept seconds (number) or HH:MM:SS / MM:SS strings."""
    if isinstance(value, (int, float)):
        return float(value)
    parts = str(value).split(":")
    parts = [float(p) for p in parts]
    total = 0.0
    for p in parts:
        total = total * 60 + p
    return total


def run(cmd, dry_run):
    print("  $ " + " ".join(cmd))
    if dry_run:
        return None
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr.strip()[-500:])
    return r


def resolve_source(pick, video, media_dir):
    """Return the source video file for one pick, or None."""
    clip = pick.get("clip", pick)
    name = clip.get("file") or pick.get("file")
    if name:
        if os.path.isabs(name):
            return name
        return os.path.join(media_dir, name)
    return video


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", default=None,
                    help="single source video (used when a pick has no file)")
    ap.add_argument("--media-dir", default=".",
                    help="folder holding the per-clip source files")
    ap.add_argument("--picks", default="inkling-video-picks.jsonl")
    ap.add_argument("--music", default=None)
    ap.add_argument("--out", default="recap.mp4")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.video and not os.path.exists(args.video):
        print(f"Video not found: {args.video}")
        return 1
    if not os.path.exists(args.picks):
        print(f"Picks not found: {args.picks}")
        print("Save Inkling's picks to this file first (one JSON object per line).")
        return 1
    if args.music and not os.path.exists(args.music):
        print(f"Music file not found: {args.music}")
        return 1

    picks = []
    with open(args.picks, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                picks.append(json.loads(line))
    if not picks:
        print(f"No picks in {args.picks}")
        return 1
    print(f"{len(picks)} segments, in order:")
    for i, p in enumerate(picks):
        clip = p.get("clip", p)
        src = resolve_source(p, args.video, args.media_dir) or ""
        print(f"  {i + 1}. {clip.get('start')}–{clip.get('end')}  {clip.get('title', '')}  [{os.path.basename(src)}]")

    tmp = tempfile.mkdtemp(prefix="recap-")
    seg_files = []
    for i, p in enumerate(picks):
        clip = p.get("clip", p)
        start = parse_ts(clip["start"])
        end = parse_ts(clip["end"])
        src = resolve_source(p, args.video, args.media_dir)
        if not src:
            print(f"No source for segment {i + 1} (no file in pick, no --video)")
            return 1
        if not os.path.exists(src):
            print(f"Source not found for segment {i + 1}: {src}")
            return 1
        seg = os.path.join(tmp, f"seg-{i:02d}.mp4")
        seg_files.append(seg)
        cmd = ["ffmpeg", "-y", "-ss", str(start), "-to", str(end),
               "-i", src, "-vf", FILTER,
               "-c:v", "libx264", "-c:a", "aac", seg]
        r = run(cmd, args.dry_run)
        if r is not None and r.returncode != 0:
            print(f"Failed cutting segment {i + 1}")
            return 1

    list_path = os.path.join(tmp, "concat.txt")
    if not args.dry_run:
        with open(list_path, "w", encoding="utf-8") as f:
            for seg in seg_files:
                f.write(f"file '{seg}'\n")
    else:
        print(f"  (dry run: would write concat list with {len(seg_files)} files)")

    if args.music:
        print("Mixing music low under the room audio (volume 0.15).")
        cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_path,
               "-i", args.music,
               "-filter_complex",
               "[0:a]volume=1.0[a0];[1:a]volume=0.15[a1];"
               "[a0][a1]amix=inputs=2:duration=first:dropout_transition=0[a]",
               "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-c:a", "aac",
               "-shortest", args.out]
    else:
        cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_path,
               "-c", "copy", args.out]
    r = run(cmd, args.dry_run)
    if r is not None and r.returncode != 0:
        print("Failed joining segments")
        return 1
    print(f"Done: {args.out}" if not args.dry_run else f"(dry run: would write {args.out})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
