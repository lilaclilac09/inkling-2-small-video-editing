"""Resume a v5 render from already-cut segments in a tmp dir.

Use when the segment cutting finished but a group join failed (e.g. the
timelapse had no audio and seg-01 had to be re-cut with a silent track).
Re-does only the group joins + final join; does NOT re-cut segments.

  python3 resume_v5_join.py --tmpdir /tmp/recutv5-XXXX \
      --ass scan/captions-v5.ass --music music/v5-main-bed.mp3 \
      --out recap-v5-another-season.mp4
"""
import argparse
import glob
import json
import os
import subprocess
import sys

XFADE = 0.5
MUSIC_VOL = 0.30
ROOM_VOL = 1.4
PHOTOS = [(2, 3.0), (3, 3.0), (19, 4.0)]  # (after pick idx, duration)


def parse_ts(value):
    parts = [float(p) for p in str(value).split(":")]
    total = 0.0
    for p in parts:
        total = total * 60 + p
    return total


def run(cmd):
    print("  $ " + " ".join(cmd[:6]) + (" ..." if len(cmd) > 6 else ""), flush=True)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr.strip()[-800:])
    return r


def join_group(seg_files, durations, out):
    n = len(seg_files)
    inputs = []
    for seg in seg_files:
        inputs += ["-i", seg]
    vf_parts, af_parts = [], []
    prev_v, offset = "0:v", durations[0] - XFADE
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
    r = run(cmd)
    return r.returncode == 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tmpdir", required=True)
    ap.add_argument("--picks", default="scan/inkling-video-picks-v5.jsonl")
    ap.add_argument("--ass", required=True)
    ap.add_argument("--music", default=None)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    picks = [json.loads(l) for l in open(args.picks, encoding="utf-8") if l.strip()]
    durations = []
    for i, p in enumerate(picks):
        c = p["clip"]
        durations.append(parse_ts(c["end"]) - parse_ts(c["start"]))
        for (after_idx, dur) in PHOTOS:
            if after_idx == i:
                durations.append(dur)
    seg_files = [os.path.join(args.tmpdir, f"seg-{k:02d}.mp4") for k in range(len(durations))]
    for s in seg_files:
        if not os.path.exists(s):
            print(f"Missing segment: {s}")
            return 1
    print(f"{len(seg_files)} segments, total {sum(durations):.1f}s raw")

    GROUP = 7
    groups = []
    for g in range(0, len(seg_files), GROUP):
        chunk_files = seg_files[g:g + GROUP]
        chunk_durs = durations[g:g + GROUP]
        group_out = os.path.join(args.tmpdir, f"group-{g // GROUP}.mp4")
        print(f"Joining group {g // GROUP} (seg {g}-{g + len(chunk_files) - 1})...", flush=True)
        if not join_group(chunk_files, chunk_durs, group_out):
            print(f"Failed joining group {g // GROUP}")
            return 1
        groups.append((group_out, sum(chunk_durs) - (len(chunk_durs) - 1) * XFADE))

    print(f"Final join ({len(groups)} groups) + subtitles + music...", flush=True)
    inputs = []
    for group_out, _ in groups:
        inputs += ["-i", group_out]
    music_idx = None
    if args.music:
        music_idx = len(groups)
        inputs += ["-i", args.music]
    vf_parts, af_parts = [], []
    prev_v, offset = "0:v", groups[0][1] - XFADE
    for k in range(1, len(groups)):
        out_v = f"gv{k}"
        vf_parts.append(f"[{prev_v}][{k}:v]xfade=transition=fade:duration={XFADE}:offset={offset:.3f}[{out_v}]")
        prev_v = out_v
        offset += groups[k][1] - XFADE
    prev_a = "0:a"
    for k in range(1, len(groups)):
        out_a = f"ga{k}"
        af_parts.append(f"[{prev_a}][{k}:a]acrossfade=d={XFADE}[{out_a}]")
        prev_a = out_a
    ass_path = os.path.abspath(args.ass)
    vf_parts.append(f"[{prev_v}]subtitles={ass_path}[vsub]")
    if args.music:
        af_parts.append(f"[{prev_a}]afftdn=nr=8:nf=-30[adn];[adn]volume={ROOM_VOL}[a0];[{music_idx}:a]volume={MUSIC_VOL}[a1];[a0][a1]amix=inputs=2:duration=first:dropout_transition=0[aout]")
        final_a = "[aout]"
    else:
        af_parts.append(f"[{prev_a}]afftdn=nr=8:nf=-30[adn];[adn]volume={ROOM_VOL}[aout]")
        final_a = "[aout]"
    fc = ";".join(vf_parts + af_parts)
    cmd = ["ffmpeg", "-y"] + inputs + [
        "-filter_complex", fc,
        "-map", "[vsub]", "-map", final_a,
        "-c:v", "libx264", "-c:a", "aac",
        "-shortest", args.out,
    ]
    r = run(cmd)
    if r.returncode != 0:
        print("Failed final join")
        return 1
    print(f"Done: {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
