"""Build the full v10 recap (cover + main body + credits, NO flashback).

v10 = v9 rebuilt per the user's 2026-11-16 18:52-18:55 notes:
  1. Caption 06 (thousand-women hackathon) MOVED OFF the pick-6
     skincare girl and ONTO pick 20 — the banner girl (short dark
     hair, glasses, black t-shirt + black pants, black headband,
     thumbs up by the Cursor x Sunset Shanghai banner, closing
     clip DJI_20260719122116_0079_D). She is the ONLY match: the
     "black hat" was her headband. New timing main 114.7-116.7.
  2. DYNAMIC GROUP-PHOTO ENDING: the 8s static freeze hold is
     GONE. Replaced by moving clips of people posing by the banner:
     END1 = DJI_20260719122153_0080_D (white-dress woman posing,
     3.75s) + END2 = DJI_20260719115456_0074_D 0:00-0:08 (people
     gathering by the entrance, 8.0s). Captions re-timed: 26 on
     END1, 27 + 28 on END2. No caption straddles a cut.
  3. FLASHBACK DELETED (user 18:54, supersedes "闪回不要去掉"):
     the 8.5s speaker-frame flash montage is gone entirely.
     Structure is now cover + main + credits only.
  4. CREDITS TRIMMED: the scroll freezes at ~27.1s (clamp hit)
     and holds a frozen frame for the last ~4.8s. Credits cut to
     27.2s (credits-v10.mp4) — the video ends when the text stops.

Structure: cover(3.0) + main(128.75) + credits(27.2),
xfade 0.5s between the three pieces -> 157.95s total, 1920x1080.
Main body = picks 127.5 + END1 3.75 + END2 8.0 - 21 x 0.5s
crossfades = 128.75s.

Silicon grade only (Another Season). Do NOT build the korean version.

  python3 inkling-video-recut-v10-final.py --grade silicon \
      --bed music/v9-main-bed.mp3 --out recap-v7-another-season.mp4
"""

import argparse
import json
import os
import subprocess
import sys

XFADE = 0.5
# Audio mix (v8): music 0.30 / room 1.4.
# Voices stay louder: room 1.4 + compressor >> music 0.30.
MUSIC_VOL = 0.30
ROOM_VOL = 1.4
ROOM_COMP = "acompressor=threshold=-18dB:ratio=3:attack=5:release=100:makeup=4"
# Noise gate (v8): suppress quiet audience chatter/noise so only the
# background music + the mic'd on-stage speaker are heard. Talk mean was
# measured ~-19 dB; audience is quieter. Threshold -25 dB, ratio 10,
# range -20 dB: below-threshold sound is pushed down hard, the speaker
# (above threshold) passes through. Attack 5ms, release 100ms.
ROOM_GATE = "agate=threshold=-25dB:ratio=10:attack=5:release=100:range=-20dB"
# Music bed fade-out (v10): total is ~158.0s, bed is 170s. Fade the bed
# out over the last 4.5s of the video (153.4-157.9) so the music ends
# smoothly instead of cutting off; the final 0.5s is silent credits.
BED_FADE = "afade=t=out:st=153.4:d=4.5"
# Opening room ramp: 0.5 for the first 22s (Stay Useless hook), ramping
# smoothly back to 1.4 by 26s. Voices quiet at the opening (arrival /
# timelapse), full volume once the talks start at ~29s.
ROOM_VOL_RAMP = "volume='0.5+0.9*min(max((t-22)/4,0),1)':eval=frame"
# Dim-scene brightening DISABLED 2026-11-16 (user: whole video overexposed).
# Was eq=brightness=0.10:contrast=1.05:saturation=1.03. Do not re-enable
# without her say-so.
DIM_BRIGHT = ""

# Shadows-only lift (v8, 2026-11-16): the global brightness boost was
# crude and blew out the highlights. Instead lift ONLY the dark end
# with a curves point-lift: input 0 -> 0.05, input 0.25 -> 0.30, input
# 1.0 -> 1.0. Dark areas get a little brighter; bright areas are
# untouched; no overall overexposure. Do NOT re-add eq brightness.
SHADOW_LIFT = "curves=all='0/0.05 0.25/0.30 1/1'"

GRADES = {
    "korean": "scale=1920:1080,fps=30,eq=saturation=1.32:contrast=1.12:brightness=0," + SHADOW_LIFT + ",colorbalance=rs=0.12:gs=0.03:bs=-0.10",
    "silicon": "scale=1920:1080,fps=30,eq=saturation=1.22:contrast=1.12:brightness=0," + SHADOW_LIFT + ",colorbalance=rs=0.08:gs=0.02:bs=-0.06",
}

# v10: NO PHOTOS (unchanged from v9) and NO HOLD. The 8s freeze hold
# is replaced by two DYNAMIC ending clips (moving video of people
# posing by the banner at closing) — see ENDING below.
PHOTOS = []

# Dynamic group-photo ending (v10, replaces the v9 8s freeze hold):
# END1 = the other closing banner clip (white-dress woman posing,
# 3.75s); END2 = people gathering by the entrance/banner at 11:54
# (first 8.0s: entrance + banner, then camera moves inside).
ENDING = [
    ("DJI_20260719122153_0080_D.MP4", 0.0, 3.75),
    ("DJI_20260719115456_0074_D.MP4", 0.0, 8.0),
]

COVER = "v7-cover-v26.jpg"
COVER_DUR = 3.0
CREDITS = "credits-v10.mp4"   # smooth-scroll credits, TRIMMED to 27.2s (scroll freezes ~27.1s) + silent audio
PICKS = "scan/inkling-video-picks-v8.jsonl"
ASS = "scan/captions-v10-final.ass"
MEDIA_DIR = "media/DJI_001"

# FLASHBACK DELETED (v10, user 2026-11-16 18:54): the 17-frame speaker
# flash montage is gone entirely. No FLASH_FRAMES, no flash segment.

# Final timeline (v10): cover 3.0 + main 128.75 + credits 27.2,
# minus 2 x 0.5s crossfades = 157.95s.
# Main body = picks 127.5 + END1 3.75 + END2 8.0 - 21 x 0.5s
# crossfades = 128.75s.
# Xfade offsets (final-video seconds): cover->main 2.5 (=3.0-0.5);
# main->credits 130.75 (=3.0+128.75-0.5-0.5).
TOTAL_DUR = 157.95
MAIN_DUR = 128.75
CREDITS_OFF = COVER_DUR + MAIN_DUR - 2 * XFADE   # 130.75


def parse_ts(value):
    if isinstance(value, (int, float)):
        return float(value)
    parts = [float(p) for p in str(value).split(":")]
    total = 0.0
    for p in parts:
        total = total * 60 + p
    return total


def run(cmd, label):
    print(f"  $ {' '.join(cmd[:5])} ... [{label}]", flush=True)
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr.strip()[-1200:])
        print(f"FAILED: {label}")
        return False
    return True


def has_audio(path):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "stream=codec_type",
         "-of", "csv=p=0", path],
        capture_output=True, text=True)
    return "audio" in r.stdout.split()


def join_group(seg_files, durations, out):
    n = len(seg_files)
    if n == 1:
        # Single segment (v9 group 3 = the group photo alone): nothing
        # to crossfade — copy it as the group file.
        import shutil
        shutil.copyfile(seg_files[0], out)
        print(f"  (group {os.path.basename(out)} = single segment, copied)")
        return True
    inputs = []
    for seg in seg_files:
        inputs += ["-i", seg]
    vf_parts, af_parts = [], []
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
    return run(cmd, f"join group -> {os.path.basename(out)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--grade", choices=["korean", "silicon"], required=True)
    ap.add_argument("--bed", required=True, help="extended music bed mp3 (180s)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--tmpdir", default=None)
    args = ap.parse_args()

    grade_filter = GRADES[args.grade]  # no extra brightening (overexposure fix)
    print(f"grade={args.grade}  bed={args.bed}  out={args.out}")
    print(f"music vol {MUSIC_VOL}, room vol {ROOM_VOL} (ramp 0.5->1.4)")

    for path in [PICKS, ASS, args.bed, COVER, CREDITS]:
        if not os.path.exists(path):
            print(f"Not found: {path}")
            return 1
    for (photo, _, _) in PHOTOS:
        if not os.path.exists(photo):
            print(f"Photo not found: {photo}")
            return 1

    tmp = args.tmpdir or os.path.join("render-tmp", f"v10-{args.grade}")
    os.makedirs(tmp, exist_ok=True)
    print(f"tmpdir: {tmp}")

    picks = []
    with open(PICKS, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                picks.append(json.loads(line))
    print(f"{len(picks)} video picks + {len(PHOTOS)} photos = "
          f"{len(picks) + len(PHOTOS)} segments")

    seg_files, durations = [], []

    def add_video(i, p):
        clip = p.get("clip", p)
        start = parse_ts(clip["start"])
        end = parse_ts(clip["end"])
        durations.append(end - start)
        src = os.path.join(MEDIA_DIR, clip.get("file", ""))
        if not os.path.exists(src):
            print(f"Source not found for segment {i + 1}: {src}")
            return False
        seg = os.path.join(tmp, f"seg-{len(seg_files):02d}.mp4")
        seg_files.append(seg)
        if os.path.exists(seg):
            print(f"  (segment {i + 1} cached)")
            return True
        if has_audio(src):
            cmd = ["ffmpeg", "-y", "-ss", str(start), "-to", str(end),
                   "-i", src, "-vf", grade_filter,
                   "-c:v", "libx264", "-c:a", "aac", seg]
        else:
            print(f"  (segment {i + 1} source has no audio; adding silent track)")
            cmd = ["ffmpeg", "-y", "-ss", str(start), "-to", str(end),
                   "-i", src, "-f", "lavfi", "-t", str(end - start),
                   "-i", "anullsrc",
                   "-filter_complex", f"[0:v]{grade_filter}[v]",
                   "-map", "[v]", "-map", "1:a",
                   "-c:v", "libx264", "-c:a", "aac", seg]
        return run(cmd, f"cut segment {i + 1}")

    def add_ending_clip(fname, start, end):
        """A dynamic ending clip (moving video, not a still). Same cut
        + grade pipeline as a pick segment."""
        durations.append(end - start)
        src = os.path.join(MEDIA_DIR, fname)
        if not os.path.exists(src):
            print(f"Ending source not found: {src}")
            return False
        seg = os.path.join(tmp, f"seg-{len(seg_files):02d}.mp4")
        seg_files.append(seg)
        if os.path.exists(seg):
            print(f"  (ending segment {fname} cached)")
            return True
        if has_audio(src):
            cmd = ["ffmpeg", "-y", "-ss", str(start), "-to", str(end),
                   "-i", src, "-vf", grade_filter,
                   "-c:v", "libx264", "-c:a", "aac", seg]
        else:
            cmd = ["ffmpeg", "-y", "-ss", str(start), "-to", str(end),
                   "-i", src, "-f", "lavfi", "-t", str(end - start),
                   "-i", "anullsrc",
                   "-filter_complex", f"[0:v]{grade_filter}[v]",
                   "-map", "[v]", "-map", "1:a",
                   "-c:v", "libx264", "-c:a", "aac", seg]
        return run(cmd, f"cut ending segment {fname}")

    for i, p in enumerate(picks):
        if not add_video(i, p):
            return 1
    # Dynamic group-photo ending after pick 20 (replaces the v9 hold).
    for (fname, start, end) in ENDING:
        if not add_ending_clip(fname, start, end):
            return 1

    print(f"Main body raw: {sum(durations):.1f}s -> "
          f"{sum(durations) - (len(durations) - 1) * XFADE:.1f}s after crossfades")

    # Join in groups of 7.
    GROUP = 7
    groups = []
    for g in range(0, len(seg_files), GROUP):
        chunk_files = seg_files[g:g + GROUP]
        chunk_durs = durations[g:g + GROUP]
        group_out = os.path.join(tmp, f"group-{g // GROUP}.mp4")
        if not os.path.exists(group_out):
            print(f"Joining group {g // GROUP} (seg {g}-{g + len(chunk_files) - 1})...")
            if not join_group(chunk_files, chunk_durs, group_out):
                return 1
        else:
            print(f"  (group {g // GROUP} cached)")
        groups.append((group_out, sum(chunk_durs) - (len(chunk_durs) - 1) * XFADE))

    # Main body: chain the groups, burn v10 ASS, process room audio
    # (afftdn + compressor + NOISE GATE + opening ramp). NO music yet.
    main_body = os.path.join(tmp, "main-body.mp4")
    if not os.path.exists(main_body):
        print("Main-body join (groups + v9 subtitles + room audio)...")
        inputs = []
        for group_out, _ in groups:
            inputs += ["-i", group_out]
        vf_parts, af_parts = [], []
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
        ass_path = os.path.abspath(ASS)
        vf_parts.append(f"[{prev_v}]subtitles={ass_path}[vsub]")
        af_parts.append(f"[{prev_a}]afftdn=nr=8:nf=-30[adn];[adn]{ROOM_COMP}[acomp];[acomp]{ROOM_GATE}[agate];[agate]{ROOM_VOL_RAMP}[aout]")
        fc = ";".join(vf_parts + af_parts)
        cmd = ["ffmpeg", "-y"] + inputs + [
            "-filter_complex", fc,
            "-map", "[vsub]", "-map", "[aout]",
            "-c:v", "libx264", "-c:a", "aac", main_body,
        ]
        if not run(cmd, "main-body join"):
            return 1
    else:
        print("  (main body cached)")

    # Cover segment (3s, silent).
    cover_seg = os.path.join(tmp, "cover.mp4")
    if not os.path.exists(cover_seg):
        cmd = ["ffmpeg", "-y", "-loop", "1", "-i", COVER,
               "-f", "lavfi", "-t", str(COVER_DUR), "-i", "anullsrc",
               "-filter_complex",
               "[0:v]scale=1920:1080,fps=30,format=yuv420p[v]",
               "-map", "[v]", "-map", "1:a", "-t", str(COVER_DUR),
               "-c:v", "libx264", "-c:a", "aac", cover_seg]
        if not run(cmd, "cover segment"):
            return 1
    else:
        print("  (cover cached)")

    # Final assembly: cover + main + credits (xfade 0.5s),
    # NO flashback, NO progress bar, music bed (with fade-out)
    # mixed under the room audio.
    print("Final assembly (cover+main+credits, music)...")
    inputs = ["-i", cover_seg, "-i", main_body,
              "-i", CREDITS, "-i", args.bed]
    # xfade chain: cover(3.0)->main offset 2.5;
    # ->credits offset 130.75. Final duration 157.95s.
    # NOTE: the three video inputs have different timebases/fps
    # (main/cover 30fps tb 1/15360; credits 30fps tb 1/12288),
    # which makes xfade fail with "timebase do not match" (-22).
    # Normalize each input to AVTB + 30fps before the xfade chain.
    vf = (
        "[0:v]settb=AVTB,fps=30[v0];"
        "[1:v]settb=AVTB,fps=30[v1];"
        "[2:v]settb=AVTB,fps=30[v2];"
        "[v0][v1]xfade=transition=fade:duration=0.5:offset=2.5[x1];"
        f"[x1][v2]xfade=transition=fade:duration=0.5:offset={CREDITS_OFF:.1f}[vout]"
    )
    af = (
        "[0:a][1:a]acrossfade=d=0.5[a01];"
        "[a01][2:a]acrossfade=d=0.5[aroom];"
        f"[3:a]volume={MUSIC_VOL},{BED_FADE}[bed];"
        "[aroom][bed]amix=inputs=2:duration=first:dropout_transition=0[aout]"
    )
    fc = vf + ";" + af
    cmd = ["ffmpeg", "-y"] + inputs + [
        "-filter_complex", fc,
        "-map", "[vout]", "-map", "[aout]",
        "-c:v", "libx264", "-c:a", "aac", args.out,
    ]
    if not run(cmd, "final assembly"):
        return 1
    print(f"Done: {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
