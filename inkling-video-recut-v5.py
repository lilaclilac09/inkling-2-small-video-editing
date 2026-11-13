"""Build one v5 story re-cut (cut + grouped join + bilingual subtitles).

v5 = the story cut (Aileen 2026-11-13 15:39-15:40): 20 Inkling story picks
re-ordered into a 5-beat arc (arrival -> hosts -> talks, important first ->
human moments -> closing) + 3 interleaved still photos (Ken Burns slow
zoom, 2-4s each).

Subtitle system v6 (Aileen 2026-11-13 17:09 + 17:14, see
build_captions_v6.py): cream/beige background, black text, max 2 lines
(1 EN + 1 CN), all cards at the same bottom position, cycling 2-3 cards
per scene at a comfortable reading pace (~2-3s each, never lingering),
coffee-machine label at t=80-84s. Pass --ass scan/captions-v6.ass.

Audio mix (17:09): music 0.22 (lowered so it never covers voices),
room 1.6 + acompressor so voices are louder and more solid/full,
afftdn denoise on the room bus (coffee-machine hum).
Grades (17:09): both pushed warmer + more vivid than v5;
korean = warm/glowy, silicon = clean (no longer cool/blue).

  python3 inkling-video-recut-v5.py --picks scan/inkling-video-picks-v5.jsonl \
      --ass scan/captions-v6.ass --grade korean \
      --music music/v5-main-bed.mp3 --out recap-v5-another-season.mp4

Grades: korean (glowy, warm) / silicon (crisp, warm).
Photo insertions (fixed, matching build_captions_v5.py):
  - Photo A: frames-dense/DJI_20260719104432_0054_D/frame-0003.jpg (3s),
    after pick #3 (walking in).
  - Photo B: photos/HM5A1822.JPG (3s), after pick #4 (hosts).
  - Photo C: photos/HM5A1478.JPG (4s), after pick #20 (sign-off), final frame.
Photo segments are Ken Burns zoompan (10% zoom-in) with silent audio so
the acrossfade join treats them like any other segment.
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile

XFADE = 0.5
# Audio mix (Aileen 2026-11-13 17:09): music must NOT cover the voices.
# Music lowered 0.30 -> 0.22; room/voices boosted 1.4 -> 1.6 and
# compressed (acompressor) so voices are louder and more solid/full.
MUSIC_VOL = 0.22
ROOM_VOL = 1.6
# acompressor on the room bus: gentle compression + makeup gain so
# speech sits solidly above the music instead of dipping under it.
ROOM_COMP = "acompressor=threshold=-18dB:ratio=3:attack=5:release=100:makeup=4"

# Grades (Aileen 2026-11-13 17:09): warmer, prettier, stronger/more
# vivid contrast, CUTER. Both grades pushed warmer + more saturated
# than v5; korean stays the warm/glowy one, silicon the clean one.
GRADES = {
    "korean": "scale=1920:1080,fps=30,eq=saturation=1.32:contrast=1.12:brightness=0.07,colorbalance=rs=0.12:gs=0.03:bs=-0.10",
    "silicon": "scale=1920:1080,fps=30,eq=saturation=1.22:contrast=1.12:brightness=0.05,colorbalance=rs=0.08:gs=0.02:bs=-0.06",
}

# (photo path, duration, after pick index 0-based)
PHOTOS = [
    ("frames-dense/DJI_20260719104432_0054_D/frame-0003.jpg", 3.0, 2),
    ("photos/HM5A1822.JPG", 3.0, 3),
    ("photos/HM5A1478.JPG", 4.0, 19),
]


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
    ap.add_argument("--media-dir", default="media/DJI_001")
    ap.add_argument("--picks", required=True)
    ap.add_argument("--ass", required=True, help="bilingual ASS subtitle file")
    ap.add_argument("--grade", choices=["korean", "silicon"], required=True)
    ap.add_argument("--music", default=None)
    ap.add_argument("--out", default="recap-v5.mp4")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    grade_filter = GRADES[args.grade]
    print(f"grade={args.grade}")
    print(f"music={args.music} (vol {MUSIC_VOL}), room vol {ROOM_VOL}")

    for path in [args.picks, args.ass] + ([args.music] if args.music else []):
        if not os.path.exists(path):
            print(f"Not found: {path}")
            return 1
    for (photo, _, _) in PHOTOS:
        if not os.path.exists(photo):
            print(f"Photo not found: {photo}")
            return 1

    picks = []
    with open(args.picks, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                picks.append(json.loads(line))
    print(f"{len(picks)} video picks + {len(PHOTOS)} photos = "
          f"{len(picks) + len(PHOTOS)} segments")

    tmp = tempfile.mkdtemp(prefix="recutv5-")
    seg_files = []
    durations = []

    def has_audio(path):
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "stream=codec_type",
             "-of", "csv=p=0", path],
            capture_output=True, text=True)
        return "audio" in r.stdout.split()

    def add_video(i, p):
        clip = p.get("clip", p)
        start = parse_ts(clip["start"])
        end = parse_ts(clip["end"])
        durations.append(end - start)
        src = os.path.join(args.media_dir, clip.get("file", ""))
        if not os.path.exists(src):
            print(f"Source not found for segment {i + 1}: {src}")
            return False
        seg = os.path.join(tmp, f"seg-{len(seg_files):02d}.mp4")
        seg_files.append(seg)
        # Some sources (e.g. the timelapse) have NO audio track; the
        # acrossfade join needs every segment to carry audio, so give those
        # a silent track instead of letting the join fail.
        if has_audio(src):
            cmd = ["ffmpeg", "-y", "-ss", str(start), "-to", str(end),
                   "-i", src, "-vf", grade_filter,
                   "-c:v", "libx264", "-c:a", "aac", seg]
        else:
            print(f"  (segment {i + 1} source has no audio; adding silent track)")
            # NOTE: use -filter_complex (not -vf) here — -vf with an
            # explicit -map of a second (lavfi) input fails in ffmpeg.
            cmd = ["ffmpeg", "-y", "-ss", str(start), "-to", str(end),
                   "-i", src, "-f", "lavfi", "-t", str(end - start),
                   "-i", "anullsrc",
                   "-filter_complex", f"[0:v]{grade_filter}[v]",
                   "-map", "[v]", "-map", "1:a",
                   "-c:v", "libx264", "-c:a", "aac", seg]
        r = run(cmd, args.dry_run)
        if r is not None and r.returncode != 0:
            print(f"Failed cutting segment {i + 1}")
            return False
        return True

    def add_photo(photo, dur):
        durations.append(dur)
        nframes = int(round(dur * 30))
        seg = os.path.join(tmp, f"seg-{len(seg_files):02d}.mp4")
        seg_files.append(seg)
        # Ken Burns: 10% slow zoom-in via zoompan; silent audio so the
        # acrossfade join treats this like any other segment.
        vf = (f"scale=3840:2160,zoompan=z='1+0.10*on/{nframes - 1}':"
              f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={nframes}:"
              f"s=1920x1080:fps=30,format=yuv420p")
        cmd = ["ffmpeg", "-y", "-loop", "1", "-i", photo,
               "-f", "lavfi", "-t", str(dur), "-i", "anullsrc",
               "-filter_complex", f"[0:v]{vf}[v]",
               "-map", "[v]", "-map", "1:a", "-t", str(dur),
               "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
               "-c:a", "aac", seg]
        r = run(cmd, args.dry_run)
        if r is not None and r.returncode != 0:
            print(f"Failed generating photo segment {photo}")
            return False
        return True

    for i, p in enumerate(picks):
        if not add_video(i, p):
            return 1
        for (photo, dur, after_idx) in PHOTOS:
            if after_idx == i:
                print(f"Inserting photo {photo} ({dur}s) after pick #{i + 1}")
                if not add_photo(photo, dur):
                    return 1

    print(f"Total timeline: {sum(durations):.1f}s raw -> "
          f"{sum(durations) - (len(durations) - 1) * XFADE:.1f}s after crossfades")

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
    ass_path = os.path.abspath(args.ass)
    vf_parts.append(f"[{prev_v}]subtitles={ass_path}[vsub]")
    if args.music:
        af_parts.append(f"[{prev_a}]afftdn=nr=8:nf=-30[adn];[adn]{ROOM_COMP}[acomp];[acomp]volume={ROOM_VOL}[a0];[{music_idx}:a]volume={MUSIC_VOL}[a1];[a0][a1]amix=inputs=2:duration=first:dropout_transition=0[aout]")
        final_a = "[aout]"
    else:
        af_parts.append(f"[{prev_a}]afftdn=nr=8:nf=-30[adn];[adn]{ROOM_COMP}[acomp];[acomp]volume={ROOM_VOL}[aout]")
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
