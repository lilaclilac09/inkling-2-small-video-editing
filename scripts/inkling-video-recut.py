"""Build the vlog-style re-cut (v2 picks) with crossfade transitions,
music mixed low, and burned-in subtitles.

Takes the picks file (one JSON object per line, in order), cuts each
segment from its source video, joins them with 0.5 s crossfades (xfade
video + acrossfade audio), mixes the music file low underneath, and
burns in a short caption per segment (the pick title).

  python3 inkling-video-recut.py --media-dir media/DJI_001 \
      --picks scan/inkling-video-picks-v2.jsonl \
      --music music/koyo-timing.mp3 --out recap-v2.mp4

--music is optional. Without it the recap has only the room audio.
--xfade sets the crossfade duration in seconds (default 0.5).
--dry-run prints every ffmpeg command without running anything.
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile

FILTER = "scale=1920:1080,fps=30,eq=saturation=0.88:contrast=0.96:brightness=0.02"
# The source clips have mixed resolution/fps (2688x1512 @ 59.94, 2688x1512
# @ 29.97, 1920x1080 @ 29.97). xfade requires identical inputs, so the
# segment cut normalizes everything to 1920x1080 @ 30 fps here.
MUSIC_VOL = 0.15


def parse_ts(value):
    """Accept seconds (number) or HH:MM:SS / MM:SS strings."""
    if isinstance(value, (int, float)):
        return float(value)
    parts = [float(p) for p in str(value).split(":")]
    total = 0.0
    for p in parts:
        total = total * 60 + p
    return total


def srt_time(t):
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = int(t % 60)
    ms = int(round((t - int(t)) * 1000))
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def run(cmd, dry_run):
    print("  $ " + " ".join(cmd))
    if dry_run:
        return None
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr.strip()[-800:])
    return r


def resolve_source(pick, media_dir):
    clip = pick.get("clip", pick)
    name = clip.get("file") or pick.get("file")
    if name:
        if os.path.isabs(name):
            return name
        return os.path.join(media_dir, name)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--media-dir", default=".")
    ap.add_argument("--picks", default="inkling-video-picks.jsonl")
    ap.add_argument("--music", default=None)
    ap.add_argument("--out", default="recap-v2.mp4")
    ap.add_argument("--xfade", type=float, default=0.5)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not os.path.exists(args.picks):
        print(f"Picks not found: {args.picks}")
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
        print("No picks")
        return 1
    print(f"{len(picks)} segments, in order:")
    for i, p in enumerate(picks):
        clip = p.get("clip", p)
        src = resolve_source(p, args.media_dir) or ""
        print(f"  {i + 1}. {clip.get('start')}–{clip.get('end')}  {clip.get('title', '')}  [{os.path.basename(src)}]")

    tmp = tempfile.mkdtemp(prefix="recut-")
    seg_files = []
    durations = []
    for i, p in enumerate(picks):
        clip = p.get("clip", p)
        start = parse_ts(clip["start"])
        end = parse_ts(clip["end"])
        dur = end - start
        durations.append(dur)
        src = resolve_source(p, args.media_dir)
        if not src or not os.path.exists(src):
            print(f"Source not found for segment {i + 1}: {src}")
            return 1
        seg = os.path.join(tmp, f"seg-{i:02d}.mp4")
        seg_files.append(seg)
        # Cut the segment (video + audio), apply the vintage grade.
        # Keep audio (room sound) for the acrossfade.
        cmd = ["ffmpeg", "-y", "-ss", str(start), "-to", str(end),
               "-i", src, "-vf", FILTER,
               "-c:v", "libx264", "-c:a", "aac", seg]
        r = run(cmd, args.dry_run)
        if r is not None and r.returncode != 0:
            print(f"Failed cutting segment {i + 1}")
            return 1

    # --- Build the subtitle file (one caption per segment, the pick title).
    # With xfade of X seconds, segment i starts at (sum of durations before
    # it) - i*X. Caption shows for the segment's on-screen span.
    xfade = args.xfade
    srt_path = os.path.join(tmp, "captions.srt")
    if not args.dry_run:
        with open(srt_path, "w", encoding="utf-8") as f:
            t = 0.0
            for i, p in enumerate(picks):
                clip = p.get("clip", p)
                title = (clip.get("title") or "").strip()
                if title:
                    start_t = t
                    end_t = t + durations[i]
                    f.write(f"{i + 1}\n{srt_time(start_t)} --> {srt_time(end_t)}\n{title}\n\n")
                t += durations[i] - (xfade if i < len(picks) - 1 else 0.0)
    else:
        print(f"  (dry run: would write captions to {srt_path})")

    # --- Build the xfade / acrossfade chain.
    # Inputs: 0..N-1 are the segments, N is the music (if any).
    n = len(seg_files)
    inputs = []
    for seg in seg_files:
        inputs += ["-i", seg]
    music_idx = None
    if args.music:
        music_idx = n
        inputs += ["-i", args.music]

    # Video chain: [0:v][1:v]xfade=transition=fade:duration=X:offset=O1[v1];
    # [v1][2:v]xfade=...:offset=O2[v2]; ... ; final [vN-1] -> [vout].
    # offset for the k-th xfade (0-based) = (sum of durations of segments
    # 0..k) - (k+1)*X.
    vf_parts = []
    af_parts = []
    # Video
    prev_v = "0:v"
    offset = durations[0] - xfade
    for k in range(1, n):
        out_v = f"v{k}"
        vf_parts.append(f"[{prev_v}][{k}:v]xfade=transition=fade:duration={xfade}:offset={offset:.3f}[{out_v}]")
        prev_v = out_v
        offset += durations[k] - xfade
    # Audio (room sound): same chaining with acrossfade.
    prev_a = "0:a"
    offset_a = durations[0] - xfade
    for k in range(1, n):
        out_a = f"a{k}"
        af_parts.append(f"[{prev_a}][{k}:a]acrossfade=d={xfade}[{out_a}]")
        prev_a = out_a
        offset_a += durations[k] - xfade
    # Subtitles on the final video.
    vf_parts.append(f"[{prev_v}]subtitles={srt_path}:force_style='FontSize=20,PrimaryColour=&HFFFFFF,OutlineColour=&H80000000,BorderStyle=1,Outline=1,Shadow=0,MarginV=30'[vsub]")
    # Mix music low under the room audio.
    if args.music:
        af_parts.append(f"[{prev_a}]volume=1.0[a0];[{music_idx}:a]volume={MUSIC_VOL}[a1];[a0][a1]amix=inputs=2:duration=first:dropout_transition=0[aout]")
        final_a = "[aout]"
    else:
        final_a = f"[{prev_a}]"

    filter_complex = ";".join(vf_parts + af_parts)
    cmd = ["ffmpeg", "-y"] + inputs + [
        "-filter_complex", filter_complex,
        "-map", "[vsub]", "-map", final_a,
        "-c:v", "libx264", "-c:a", "aac",
        "-shortest", args.out,
    ]
    print(f"Joining {n} segments with {xfade}s crossfades"
          + (" + music" if args.music else "") + " + subtitles.")
    r = run(cmd, args.dry_run)
    if r is not None and r.returncode != 0:
        print("Failed joining segments")
        return 1
    print(f"Done: {args.out}" if not args.dry_run else f"(dry run: would write {args.out})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
