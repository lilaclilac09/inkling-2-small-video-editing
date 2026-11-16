"""Join pre-cut segments into the vlog re-cut, in two groups to stay
under the VM memory limit (a single 18-input xfade graph OOM-killed).

Inputs: the segment files (seg-00..seg-16, already normalized to
1920x1080 @ 30 fps) and captions.srt in the temp dir, plus the music.

  python3 inkling-video-join.py --seg-dir /tmp/recut-XXXX \
      --music music/koyo-timing.mp3 --out recap-v2.mp4

Steps:
  1. Group A = seg 0-8 (9 segs), xfade chain -> groupA.mp4
  2. Group B = seg 9-16 (8 segs), xfade chain -> groupB.mp4
  3. Final: xfade groupA + groupB (0.5s), burn subtitles, mix music -> out
Each step keeps at most 9 video inputs open, so memory stays bounded.
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile

XFADE = 0.5
MUSIC_VOL = 0.15


def parse_ts(value):
    if isinstance(value, (int, float)):
        return float(value)
    parts = [float(p) for p in str(value).split(":")]
    total = 0.0
    for p in parts:
        total = total * 60 + p
    return total


def run(cmd, dry_run):
    print("  $ " + " ".join(cmd[:6]) + (" ..." if len(cmd) > 6 else ""))
    if dry_run:
        return None
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr.strip()[-800:])
    return r


def join_group(seg_files, durations, out, dry_run):
    """Join a list of segments with xfade (video) + acrossfade (audio)."""
    n = len(seg_files)
    inputs = []
    for seg in seg_files:
        inputs += ["-i", seg]
    vf_parts = []
    af_parts = []
    prev_v = "0:v"
    offset = durations[0] - XFADE
    for k in range(1, n):
        out_v = f"v{k}"
        vf_parts.append(f"[{prev_v}][{k}:v]xfade=transition=fade:duration={XFADE}:offset={offset:.3f}[{out_v}]")
        prev_v = out_v
        offset += durations[k] - XFADE
    prev_a = "0:a"
    for k in range(1, n):
        out_a = f"a{k}"
        af_parts.append(f"[{prev_a}][{k}:a]acrossfade=d={XFADE}[{out_a}]")
        prev_a = out_a
    fc = ";".join(vf_parts + af_parts)
    cmd = ["ffmpeg", "-y"] + inputs + [
        "-filter_complex", fc,
        "-map", f"[{prev_v}]", "-map", f"[{prev_a}]",
        "-c:v", "libx264", "-c:a", "aac", out,
    ]
    r = run(cmd, dry_run)
    if r is not None and r.returncode != 0:
        print(f"Failed joining group -> {out}")
        return False
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seg-dir", required=True)
    ap.add_argument("--picks", default="scan/inkling-video-picks-v2.jsonl")
    ap.add_argument("--music", default=None)
    ap.add_argument("--out", default="recap-v2.mp4")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    picks = []
    with open(args.picks, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                picks.append(json.loads(line))
    durations = []
    seg_files = []
    for i, p in enumerate(picks):
        clip = p.get("clip", p)
        durations.append(parse_ts(clip["end"]) - parse_ts(clip["start"]))
        seg_files.append(os.path.join(args.seg_dir, f"seg-{i:02d}.mp4"))
    for s in seg_files:
        if not os.path.exists(s):
            print(f"Missing segment: {s}")
            return 1
    print(f"{len(seg_files)} segments, durations sum {sum(durations):.1f}s")

    tmp = tempfile.mkdtemp(prefix="join-")
    group_a = os.path.join(tmp, "groupA.mp4")
    group_b = os.path.join(tmp, "groupB.mp4")

    # Group A: seg 0-8 (9 segments). Group B: seg 9-16 (8 segments).
    print("Joining group A (seg 0-8)...")
    if not join_group(seg_files[:9], durations[:9], group_a, args.dry_run):
        return 1
    print("Joining group B (seg 9-16)...")
    if not join_group(seg_files[9:], durations[9:], group_b, args.dry_run):
        return 1

    # Group durations after xfade: sum - (n-1)*XFADE each.
    dur_a = sum(durations[:9]) - 8 * XFADE
    dur_b = sum(durations[9:]) - 7 * XFADE
    print(f"Group A {dur_a:.1f}s, group B {dur_b:.1f}s")

    # Final: xfade A+B, burn subtitles, mix music.
    srt = os.path.join(args.seg_dir, "captions.srt")
    inputs = ["-i", group_a, "-i", group_b]
    music_idx = None
    if args.music:
        music_idx = 2
        inputs += ["-i", args.music]
    vf = (
        f"[0:v][1:v]xfade=transition=fade:duration={XFADE}:offset={dur_a - XFADE:.3f}[vx];"
        f"[vx]subtitles={srt}:force_style='FontSize=20,PrimaryColour=&HFFFFFF,OutlineColour=&H80000000,BorderStyle=1,Outline=1,Shadow=0,MarginV=30'[vsub]"
    )
    if args.music:
        af = (
            f"[0:a][1:a]acrossfade=d={XFADE}[a0];"
            f"[a0]volume=1.0[am0];[{music_idx}:a]volume={MUSIC_VOL}[am1];"
            f"[am0][am1]amix=inputs=2:duration=first:dropout_transition=0[aout]"
        )
        final_a = "[aout]"
    else:
        af = f"[0:a][1:a]acrossfade=d={XFADE}[aout]"
        final_a = "[aout]"
    fc = vf + ";" + af
    cmd = ["ffmpeg", "-y"] + inputs + [
        "-filter_complex", fc,
        "-map", "[vsub]", "-map", final_a,
        "-c:v", "libx264", "-c:a", "aac",
        "-shortest", args.out,
    ]
    print("Final join (A+B) + subtitles" + (" + music" if args.music else "") + "...")
    r = run(cmd, args.dry_run)
    if r is not None and r.returncode != 0:
        print("Failed final join")
        return 1
    print(f"Done: {args.out}" if not args.dry_run else f"(dry run: would write {args.out})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
