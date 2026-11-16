"""Build one v3 re-cut version (cut + grouped join + bilingual subtitles).

Parameterized by grade and music, so the two v3 versions share the pipeline:
  - Korean variety / dating-show (glowy, warm): --grade korean
  - Silicon Valley (crisp, cool, strong contrast): --grade silicon

  python3 inkling-video-recut-v3.py --picks scan/inkling-video-picks-v3.jsonl \
      --ass scan/captions-v3.ass --grade korean \
      --music music/just-used-music-again.mp3 \
      --out recap-v3-just-used-music-again.mp4

Steps:
  1. Cut each pick segment (1920x1080 @ 30fps, grade applied).
  2. Join in groups of 7 (xfade + acrossfade) to stay under the memory limit.
  3. Final join: groups + bilingual ASS subtitles + music (0.30) + room (1.4).
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile

XFADE = 0.5
MUSIC_VOL = 0.30
ROOM_VOL = 1.4

GRADES = {
    # Korean variety / dating-show: soft, glowy, warm, vivid but flattering.
    # Lifted blacks (brightness), warm tint, vivid color.
    "korean": "scale=1920:1080,fps=30,eq=saturation=1.10:contrast=1.05:brightness=0.05,colorbalance=rs=0.06:gs=0.02:bs=-0.06",
    # Silicon Valley: clean, crisp, strong contrast, cooler, deep blacks.
    "silicon": "scale=1920:1080,fps=30,eq=saturation=1.05:contrast=1.15:brightness=-0.02,colorbalance=rs=-0.04:gs=0.0:bs=0.05",
}


def parse_ts(value):
    if isinstance(value, (int, float)):
        return float(value)
    parts = [float(p) for p in str(value).split(":")]
    total = 0.0
    for p in parts:
        total = total * 60 + p
    return total


def run(cmd, dry_run):
    print("  $ " + " ".join(cmd[:5]) + (" ..." if len(cmd) > 5 else ""))
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
    ap.add_argument("--media-dir", default="media/DJI_001")
    ap.add_argument("--picks", required=True)
    ap.add_argument("--ass", required=True, help="bilingual ASS subtitle file")
    ap.add_argument("--grade", choices=["korean", "silicon"], required=True)
    ap.add_argument("--music", default=None)
    ap.add_argument("--out", default="recap-v3.mp4")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    grade_filter = GRADES[args.grade]
    print(f"grade={args.grade}: {grade_filter}")
    print(f"music={args.music} (vol {MUSIC_VOL}), room vol {ROOM_VOL}")

    if not os.path.exists(args.picks):
        print(f"Picks not found: {args.picks}")
        return 1
    if not os.path.exists(args.ass):
        print(f"ASS not found: {args.ass}")
        return 1
    if args.music and not os.path.exists(args.music):
        print(f"Music not found: {args.music}")
        return 1

    picks = []
    with open(args.picks, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                picks.append(json.loads(line))
    print(f"{len(picks)} segments")

    tmp = tempfile.mkdtemp(prefix="recutv3-")
    seg_files = []
    durations = []
    for i, p in enumerate(picks):
        clip = p.get("clip", p)
        start = parse_ts(clip["start"])
        end = parse_ts(clip["end"])
        durations.append(end - start)
        src = os.path.join(args.media_dir, clip.get("file", ""))
        if not os.path.exists(src):
            print(f"Source not found for segment {i + 1}: {src}")
            return 1
        seg = os.path.join(tmp, f"seg-{i:02d}.mp4")
        seg_files.append(seg)
        cmd = ["ffmpeg", "-y", "-ss", str(start), "-to", str(end),
               "-i", src, "-vf", grade_filter,
               "-c:v", "libx264", "-c:a", "aac", seg]
        r = run(cmd, args.dry_run)
        if r is not None and r.returncode != 0:
            print(f"Failed cutting segment {i + 1}")
            return 1

    # Join in groups of 7 to stay under the memory limit.
    GROUP = 7
    groups = []
    for g in range(0, len(seg_files), GROUP):
        chunk_files = seg_files[g:g + GROUP]
        chunk_durs = durations[g:g + GROUP]
        group_out = os.path.join(tmp, f"group-{g // GROUP}.mp4")
        print(f"Joining group {g // GROUP} (seg {g}-{g + len(chunk_files) - 1}, {len(chunk_files)} segs)...")
        if not join_group(chunk_files, chunk_durs, group_out, args.dry_run):
            return 1
        groups.append((group_out, sum(chunk_durs) - (len(chunk_durs) - 1) * XFADE))

    # Final join: chain the groups with xfade, burn ASS subtitles, mix audio.
    print(f"Final join ({len(groups)} groups) + subtitles + music...")
    inputs = []
    for group_out, _ in groups:
        inputs += ["-i", group_out]
    music_idx = None
    if args.music:
        music_idx = len(groups)
        inputs += ["-i", args.music]

    # Chain xfades across groups.
    vf_parts = []
    af_parts = []
    prev_v = "0:v"
    offset = groups[0][1] - XFADE
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
    # Subtitles (bilingual ASS, handwritten fonts) on the final video.
    ass_path = os.path.abspath(args.ass)
    vf_parts.append(f"[{prev_v}]subtitles={ass_path}[vsub]")
    # Audio: room louder (1.4), music at 0.30, mix.
    if args.music:
        af_parts.append(f"[{prev_a}]volume={ROOM_VOL}[a0];[{music_idx}:a]volume={MUSIC_VOL}[a1];[a0][a1]amix=inputs=2:duration=first:dropout_transition=0[aout]")
        final_a = "[aout]"
    else:
        af_parts.append(f"[{prev_a}]volume={ROOM_VOL}[aout]")
        final_a = "[aout]"
    fc = ";".join(vf_parts + af_parts)
    cmd = ["ffmpeg", "-y"] + inputs + [
        "-filter_complex", fc,
        "-map", "[vsub]", "-map", final_a,
        "-c:v", "libx264", "-c:a", "aac",
        "-shortest", args.out,
    ]
    r = run(cmd, args.dry_run)
    if r is not None and r.returncode != 0:
        print("Failed final join")
        return 1
    print(f"Done: {args.out}" if not args.dry_run else f"(dry run: would write {args.out})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
