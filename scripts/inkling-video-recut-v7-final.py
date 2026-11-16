"""Build the full v7 recap (cover + main body + flash + credits + progress bar).

v7-final = the v6 main body (20 picks + 3 photos, 127.5s) with:
  - subtitles scan/captions-v11-singlebox-v10.ass (49 events, 2 lines each)
  - dim-scene brightening eq=brightness=0.10:contrast=1.05:saturation=1.03
    on the video pick segments (not the still photos)
  - music mix room 1.4 / music 0.30 (music up slightly from v6's 0.22),
    room ramp 0.5 -> 1.4 over t=22-26s, voices quiet at the opening
  - cover v7-cover-v26.jpg prepended (3s)
  - speaker flash montage appended (17 talks A-Q, one middle frame each,
    0.5s hard cuts = 8.5s)
  - rolling credits credits-audio.mp4 appended (40.0s)
  - progress-bar ruler over the whole video (Overview, Timelapse, Talks,
    Photos, Flashback, Credits; ticks from the real section boundaries)
  - extended music bed (Stay Useless 24s hook + main track, 177.5s,
    fade out 173.5-177.5s) mixed under the room audio

Structure: cover(3.0) + main(127.5) + flash(8.5) + credits(40.0),
xfade 0.5s between the four big pieces -> 177.5s total, 1920x1080.

Grades: another-season = silicon, funk = korean (same as v5/v6).
Picks/music/bed are fixed; --grade and --bed select the version.

  python3 inkling-video-recut-v7-final.py --grade silicon \
      --bed music/v7-main-bed.mp3 --out recap-v7-another-season.mp4
  python3 inkling-video-recut-v7-final.py --grade korean \
      --bed music/v7-funk-bed.mp3 --out recap-v7-just-used-music-again.mp4
"""

import argparse
import json
import os
import subprocess
import sys

XFADE = 0.5
# Audio mix (v7): music up slightly from v6 (0.22 -> 0.30); room 1.4.
# Voices stay louder: room 1.4 + compressor >> music 0.30.
MUSIC_VOL = 0.30
ROOM_VOL = 1.4
ROOM_COMP = "acompressor=threshold=-18dB:ratio=3:attack=5:release=100:makeup=4"
# Opening room ramp: 0.5 for the first 22s (Stay Useless hook), ramping
# smoothly back to 1.4 by 26s. Voices quiet at the opening (arrival /
# timelapse), full volume once the talks start at ~29s.
ROOM_VOL_RAMP = "volume='0.5+0.9*min(max((t-22)/4,0),1)':eval=frame"
# Dim-scene brightening DISABLED 2026-11-16 (user: whole video overexposed).
# Was eq=brightness=0.10:contrast=1.05:saturation=1.03. Do not re-enable
# without her say-so.
DIM_BRIGHT = ""

GRADES = {
    "korean": "scale=1920:1080,fps=30,eq=saturation=1.32:contrast=1.12:brightness=0,colorbalance=rs=0.12:gs=0.03:bs=-0.10",
    "silicon": "scale=1920:1080,fps=30,eq=saturation=1.22:contrast=1.12:brightness=0,colorbalance=rs=0.08:gs=0.02:bs=-0.06",
}

# (photo path, duration, after pick index 0-based) — same as v6.
PHOTOS = [
    ("frames-dense/DJI_20260719104432_0054_D/frame-0003.jpg", 3.0, 2),
    ("photos/HM5A1822.JPG", 3.0, 3),
    ("photos/HM5A1478.JPG", 4.0, 19),
]

COVER = "v7-cover-v26.jpg"
COVER_DUR = 3.0
CREDITS = "credits-audio.mp4"   # credits-preview.mp4 + silent audio
PICKS = "scan/inkling-video-picks-v5.jsonl"
ASS = "scan/captions-v11-singlebox-v10.ass"
MEDIA_DIR = "media/DJI_001"

# Speaker flash: one middle frame per talk A-Q (verified on a contact
# sheet: 14 show the speaker clearly; H/I/Q are wide room shots where
# the speaker is small/far, kept as the talk's representative frame).
FLASH_FRAMES = [
    ("A", "frames-dense/DJI_20260719072352_0033_D/frame-0033.jpg"),
    ("B", "frames-dense/DJI_20260719073634_0037_D/frame-0028.jpg"),
    ("C", "frames-dense/DJI_20260719082251_0039_D/frame-0022.jpg"),
    ("D", "frames-dense/DJI_20260719082925_0040_D/frame-0038.jpg"),
    ("E", "frames-dense/DJI_20260719084815_0042_D/frame-0038.jpg"),
    ("F", "frames-dense/DJI_20260719091529_0043_D/frame-0031.jpg"),
    ("G", "frames-dense/DJI_20260719092424_0044_D/frame-0032.jpg"),
    ("H", "frames-dense/DJI_20260719095849_0028_D/frame-0007.jpg"),
    ("I", "frames-dense/DJI_20260719101206_0036_D/frame-0008.jpg"),
    ("J", "frames-dense/DJI_20260719101751_0040_D/frame-0003.jpg"),
    ("K", "frames-dense/DJI_20260719102228_0044_D/frame-0003.jpg"),
    ("L", "frames-dense/DJI_20260719103250_0048_D/frame-0003.jpg"),
    ("M", "frames-dense/DJI_20260719110516_0059_D/frame-0005.jpg"),
    ("N", "frames-dense/DJI_20260719113019_0067_D/frame-0003.jpg"),
    ("O", "frames-dense/DJI_20260719115203_0073_D/frame-0004.jpg"),
    ("P", "frames-dense/DJI_20260719120831_0075_D/frame-0004.jpg"),
    ("Q", "frames-dense/DJI_20260719121456_0077_D/frame-0003.jpg"),
]
FLASH_DUR = 0.5          # per speaker
FLASH_TOTAL = len(FLASH_FRAMES) * FLASH_DUR   # 8.5s

# Final timeline (cover 3.0 + main 127.5 + flash 8.5 + credits 40.0,
# minus 3 x 0.5s crossfades) = 177.5s.
TOTAL_DUR = 177.5
MAIN_DUR = 127.5
# Progress-bar section boundaries (final-video seconds).
# main body starts at 2.5 (cover 3.0 - 0.5 xfade); pick 2 (timelapse)
# starts at main-body 5.5; pick 5 (Talk 1) at main-body 29.0; Photo C
# at main-body 123.5; flash starts at 129.5; credits at 137.5.
SECTIONS = [
    ("Overview", 2.5),
    ("Timelapse", 8.0),
    ("Talks", 31.5),
    ("Photos", 126.0),
    ("Flashback", 129.5),
    ("Credits", 137.5),
]
BAR_X0, BAR_X1, BAR_Y = 60, 1860, 1062
BAR_W = BAR_X1 - BAR_X0
FONT = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"


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


def progress_bar_filters():
    """drawbox/drawtext chain for the chapter ruler (t = final time)."""
    T = TOTAL_DUR
    parts = []
    # base ruler
    parts.append(f"drawbox=x={BAR_X0}:y={BAR_Y}:w={BAR_W}:h=2:color=white@0.35:t=fill")
    # progress fill (brighter, thicker) + head dot, both move with t
    parts.append(
        f"drawbox=x={BAR_X0}:y={BAR_Y - 1}:w='min({BAR_W}*t/{T},{BAR_W})':h=4"
        f":color=white@0.9:t=fill")
    parts.append(
        f"drawbox=x='min({BAR_X0}+{BAR_W}*t/{T}-4,1852)':y={BAR_Y - 4}:w=8:h=10"
        f":color=white:t=fill")
    # tick marks + labels, one per section
    for name, ts in SECTIONS:
        tx = BAR_X0 + (ts / T) * BAR_W
        parts.append(
            f"drawbox=x={tx - 1:.0f}:y={BAR_Y - 6}:w=2:h=12:color=white@0.6:t=fill")
        if name == "Photos":
            # right-align so it does not collide with Flashback (35px away)
            lx = f"{tx:.0f}-text_w"
        else:
            lx = f"{tx:.0f}"
        parts.append(
            f"drawtext=fontfile={FONT}:text='{name}':fontsize=14"
            f":fontcolor=white@0.6:x={lx}:y=1036")
    return ",".join(parts)


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
    for (_, f) in FLASH_FRAMES:
        if not os.path.exists(f):
            print(f"Flash frame not found: {f}")
            return 1

    tmp = args.tmpdir or os.path.join("render-tmp", f"v7-{args.grade}")
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

    def add_photo(photo, dur):
        durations.append(dur)
        nframes = int(round(dur * 30))
        seg = os.path.join(tmp, f"seg-{len(seg_files):02d}.mp4")
        seg_files.append(seg)
        if os.path.exists(seg):
            print(f"  (photo {os.path.basename(photo)} cached)")
            return True
        vf = (f"scale=3840:2160:force_original_aspect_ratio=decrease,"
              f"pad=3840:2160:(ow-iw)/2:(oh-ih)/2:color=0xF7F1E5,"
              f"zoompan=z='1+0.10*on/{nframes - 1}':"
              f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={nframes}:"
              f"s=1920x1080:fps=30,format=yuv420p")
        cmd = ["ffmpeg", "-y", "-loop", "1", "-i", photo,
               "-f", "lavfi", "-t", str(dur), "-i", "anullsrc",
               "-filter_complex", f"[0:v]{vf}[v]",
               "-map", "[v]", "-map", "1:a", "-t", str(dur),
               "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
               "-c:a", "aac", seg]
        return run(cmd, f"photo {os.path.basename(photo)}")

    for i, p in enumerate(picks):
        if not add_video(i, p):
            return 1
        for (photo, dur, after_idx) in PHOTOS:
            if after_idx == i:
                print(f"Inserting photo {photo} ({dur}s) after pick #{i + 1}")
                if not add_photo(photo, dur):
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
    # (afftdn + compressor + opening ramp). NO music yet.
    main_body = os.path.join(tmp, "main-body.mp4")
    if not os.path.exists(main_body):
        print("Main-body join (groups + v10 subtitles + room audio)...")
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
        af_parts.append(f"[{prev_a}]afftdn=nr=8:nf=-30[adn];[adn]{ROOM_COMP}[acomp];[acomp]{ROOM_VOL_RAMP}[aout]")
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

    # Flash montage: 17 frames x 0.5s, hard cuts, silent.
    flash_seg = os.path.join(tmp, "flash.mp4")
    if not os.path.exists(flash_seg):
        inputs = []
        vparts = []
        for idx, (_, frame) in enumerate(FLASH_FRAMES):
            inputs += ["-loop", "1", "-t", str(FLASH_DUR), "-i", frame]
            vparts.append(
                f"[{idx}:v]scale=1920:1080:force_original_aspect_ratio=decrease,"
                f"pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=black,"
                f"fps=30,format=yuv420p[v{idx}]")
        inputs += ["-f", "lavfi", "-t", str(FLASH_TOTAL), "-i", "anullsrc"]
        concat_in = "".join(f"[v{i}]" for i in range(len(FLASH_FRAMES)))
        fc = ";".join(vparts) + f";{concat_in}concat=n={len(FLASH_FRAMES)}:v=1:a=0[vout]"
        cmd = ["ffmpeg", "-y"] + inputs + [
            "-filter_complex", fc,
            "-map", "[vout]", "-map", f"{len(FLASH_FRAMES)}:a",
            "-c:v", "libx264", "-c:a", "aac", flash_seg,
        ]
        if not run(cmd, "flash montage"):
            return 1
    else:
        print("  (flash cached)")

    # Final assembly: cover + main + flash + credits (xfade 0.5s),
    # progress-bar overlay, music bed mixed under the room audio.
    print("Final assembly (cover+main+flash+credits, progress bar, music)...")
    inputs = ["-i", cover_seg, "-i", main_body, "-i", flash_seg,
              "-i", CREDITS, "-i", args.bed]
    # xfade chain: cover(3.0)->main offset 2.5; ->flash offset 129.5;
    # ->credits offset 137.5. Final duration 177.5s.
    # NOTE: the four video inputs have different timebases/fps
    # (main/cover/flash 30fps tb 1/15360; credits 24fps tb 1/12288),
    # which makes xfade fail with "timebase do not match" (-22).
    # Normalize each input to AVTB + 30fps before the xfade chain.
    vf = (
        "[0:v]settb=AVTB,fps=30[v0];"
        "[1:v]settb=AVTB,fps=30[v1];"
        "[2:v]settb=AVTB,fps=30[v2];"
        "[3:v]settb=AVTB,fps=30[v3];"
        "[v0][v1]xfade=transition=fade:duration=0.5:offset=2.5[x1];"
        "[x1][v2]xfade=transition=fade:duration=0.5:offset=129.5[x2];"
        "[x2][v3]xfade=transition=fade:duration=0.5:offset=137.5[x3];"
        f"[x3]{progress_bar_filters()}[vout]"
    )
    af = (
        "[0:a][1:a]acrossfade=d=0.5[a01];"
        "[a01][2:a]acrossfade=d=0.5[a012];"
        "[a012][3:a]acrossfade=d=0.5[aroom];"
        f"[4:a]volume={MUSIC_VOL}[bed];"
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
