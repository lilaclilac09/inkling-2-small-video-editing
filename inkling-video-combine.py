#!/usr/bin/env python3
"""Combine per-clip scan outputs into one Playground pack.

After the per-clip loop finishes, each clip lives in
scan/<clip>/ with transcript.srt + frames/*.jpg. This walks all
clip folders and builds a single pack: master prompt + combined
transcript + keyframe inventory, so Inkling can pick across the
whole morning in one session instead of 64 separate ones.

Usage:
    python3 inkling-video-combine.py [--scan-dir ~/Downloads/scan]
                                     [--output <file>]
"""
import argparse
import os
import re
import sys

PROMPT_CANDIDATES = [
    "inkling-demo-master-prompt.txt",
    "inkling-demo-master-prompt-2.txt",
]

DJI_RE = re.compile(r"DJI_(\d{8})(\d{6})_\d+_D")


def find_prompt(scan_dir):
    places = [scan_dir, os.path.expanduser("~/Downloads"), os.getcwd()]
    for place in places:
        for name in PROMPT_CANDIDATES:
            p = os.path.join(place, name)
            if os.path.exists(p):
                return p
    return None


def clip_time(name):
    m = DJI_RE.match(name)
    if not m:
        return None
    hhmmss = m.group(2)
    return f"{hhmmss[0:2]}:{hhmmss[2:4]}:{hhmmss[4:6]}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan-dir", default=os.path.expanduser("~/Downloads/scan"))
    ap.add_argument("--output", default=None)
    args = ap.parse_args()
    scan_dir = args.scan_dir
    output = args.output or os.path.join(scan_dir, "inkling-video-playground-pack.txt")

    clip_dirs = sorted(
        d for d in os.listdir(scan_dir)
        if os.path.isdir(os.path.join(scan_dir, d))
    )
    if not clip_dirs:
        print(f"No clip folders in {scan_dir}")
        return 1

    prompt_path = find_prompt(scan_dir)
    lines = []
    if prompt_path:
        lines.append(open(prompt_path, encoding="utf-8").read().rstrip())
        lines.append("")
    else:
        print("(master prompt not found — pack will lack the prompt)")

    lines.append("---")
    lines.append(f"# COMBINED TRANSCRIPT — {len(clip_dirs)} clips")
    lines.append("")

    with_transcript = 0
    missing = []
    total_frames = 0
    frame_inventory = []

    for name in clip_dirs:
        d = os.path.join(scan_dir, name)
        t = clip_time(name)
        header = f"## {name}" + (f" ({t})" if t else "")
        lines.append(header)
        srt = os.path.join(d, "transcript.srt")
        if os.path.exists(srt):
            text = open(srt, encoding="utf-8").read().strip()
            if text:
                lines.append(text)
            else:
                lines.append("(no speech detected)")
            with_transcript += 1
        else:
            lines.append("(no transcript — scan failed or not run)")
            missing.append(name)
        lines.append("")

        frames_dir = os.path.join(d, "frames")
        frames = []
        if os.path.isdir(frames_dir):
            frames = sorted(f for f in os.listdir(frames_dir)
                            if f.lower().endswith(".jpg"))
        total_frames += len(frames)
        if frames:
            frame_inventory.append(
                (name, [os.path.join(name, "frames", f) for f in frames]))

    lines.append("---")
    lines.append(f"# KEYFRAMES — {total_frames} total")
    lines.append("Attach these images with the pack, in batches if needed.")
    lines.append("")
    for name, paths in frame_inventory:
        lines.append(f"## {name}")
        for p in paths:
            lines.append(f"- {p}")
        lines.append("")

    with open(output, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))

    print(f"clips: {len(clip_dirs)}, with transcript: {with_transcript}, "
          f"missing transcript: {len(missing)}, frames: {total_frames}")
    if missing:
        print("missing: " + ", ".join(missing))
    print(f"pack written to {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
