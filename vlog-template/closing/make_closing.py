#!/usr/bin/env python3
"""Build a movie-style closing for a vlog: rolling credits or a static end card.

Credits JSON (nothing hardcoded to one event):
  {
    "title": "Cursor Cafe Shanghai",
    "sections": [
      {"heading": "Thanks to", "lines": ["The Cursor team", "All our speakers"]},
      {"heading": "Music", "lines": ["KOYO — Timing (demo use only)"]}
    ],
    "footer": "Shot with Inkling 2 Small · Cut by Inkling 2 Small on Tinker"
  }

Two modes:
  scroll — classic rolling credits: a tall credit roll scrolls up from below
           the screen over a black background, fades in and out.
  card   — one elegant static card: "Thanks for watching" + a few credit
           lines, fades in, holds, fades out.

Music: pass --music to mix a track underneath (volume 0.3, faded out at the
end). The tracks in this project are commercial songs used for demo only —
say so in the credits (see credits.example.json) and clear the licence
before publishing anywhere public.

Usage:
  python3 make_closing.py --credits credits.json --mode scroll --duration 12 \
      --music ../music/koyo-timing.mp3 --out closing-scroll.mp4
  python3 make_closing.py --credits credits.json --mode card --duration 5 \
      --music ../music/koyo-timing.mp3 --out closing-card.mp4
"""

import argparse
import json
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080

FONTS = {
    "caveat": os.path.expanduser("~/.fonts/Caveat.ttf"),
    "ma_shan": os.path.expanduser("~/.fonts/MaShanZheng.ttf"),
    "dejavu": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "dejavu_bold": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
}

WHITE = (255, 255, 255)
WARM = (255, 248, 231)
GREY = (200, 200, 200)
GOLD = (212, 175, 105)


def has_cjk(text):
    return any("\u4e00" <= ch <= "\u9fff" for ch in text)


def font(path, size):
    return ImageFont.truetype(path, size)


def load_credits(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def draw_centered(draw, y, text, fnt, fill, spacing=0):
    draw.text((W / 2, y), text, font=fnt, fill=fill, anchor="ma")
    return y + fnt.size + spacing


def fit_font(draw, text, path, start_size, max_width, min_size=24):
    """Largest size (<= start_size) at which text fits max_width."""
    size = start_size
    while size > min_size:
        f = font(path, size)
        if draw.textlength(text, font=f) <= max_width:
            return f
        size -= 2
    return font(path, min_size)


def build_roll(credits):
    """Render the tall scrolling image. Returns a PIL image (1920 x H)."""
    title = credits.get("title", "")
    sections = credits.get("sections", [])
    footer = credits.get("footer", "")

    # Measure height first.
    tmp = Image.new("RGB", (W, 10))
    d = ImageDraw.Draw(tmp)
    y = 120
    if title:
        y += 120
    for sec in sections:
        y += 90  # heading
        for _ in sec.get("lines", []):
            y += 66
        y += 50
    if footer:
        y += 140
    img = Image.new("RGB", (W, y + 120), (0, 0, 0))
    d = ImageDraw.Draw(img)

    y = 120
    if title:
        f = font(FONTS["ma_shan"] if has_cjk(title) else FONTS["caveat"], 110)
        y = draw_centered(d, y, title, f, WARM, 30)
    for sec in sections:
        heading = sec.get("heading", "")
        if heading:
            f = fit_font(d, heading.upper(), FONTS["dejavu_bold"], 46, W - 160)
            y = draw_centered(d, y, heading.upper(), f, GOLD, 24)
        for line in sec.get("lines", []):
            f = fit_font(d, line, FONTS["dejavu"], 44, W - 160)
            y = draw_centered(d, y, line, f, WHITE, 14)
        y += 50
    if footer:
        y += 40
        f = fit_font(d, footer, FONTS["dejavu"], 36, W - 160)
        y = draw_centered(d, y, footer, f, GREY, 0)
    return img


def build_card(credits):
    """Render one static 1920x1080 end card."""
    img = Image.new("RGB", (W, H), (8, 8, 10))
    d = ImageDraw.Draw(img)
    # Subtle warm vignette: a soft radial glow behind the centre.
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([-500, -300, W + 500, H + 500], fill=(24, 20, 14))
    img = Image.blend(img, glow, 0.5)
    d = ImageDraw.Draw(img)

    y = 300
    f = font(FONTS["caveat"], 130)
    y = draw_centered(d, y, "Thanks for watching", f, WARM, 40)
    title = credits.get("title", "")
    if title:
        f = font(FONTS["dejavu"], 44)
        y = draw_centered(d, y, title, f, GREY, 60)
    for sec in credits.get("sections", [])[:2]:
        for line in sec.get("lines", [])[:3]:
            f = font(FONTS["dejavu"], 38)
            y = draw_centered(d, y, line, f, GREY, 8)
    footer = credits.get("footer", "")
    if footer:
        f = fit_font(d, footer, FONTS["dejavu"], 34, W - 160)
        draw_centered(d, H - 140, footer, f, GOLD, 0)
    return img


def run(cmd):
    print(" ".join(cmd))
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-2000:])
        raise SystemExit(f"ffmpeg failed ({r.returncode})")
    return r


def music_args(music, duration, audio_index=1):
    """Return ffmpeg input + filter args to mix music under the closing."""
    if not music:
        return [], []
    return (["-i", music],
            [f"[{audio_index}:a]volume=0.3,afade=t=in:st=0:d=0.8,afade=t=out:st={duration - 1.2:.2f}:d=1.2[a]"])


def make_scroll(credits, duration, music, out):
    roll = build_roll(credits)
    roll_path = os.path.splitext(out)[0] + "-roll.png"
    roll.save(roll_path)
    rh = roll.height
    # Scroll speed: the roll travels from fully below the screen to fully above.
    speed = (rh + H) / duration
    vf = (
        f"[0:v][1:v]overlay=y='H-t*{speed:.4f}':x=0,"
        f"fade=t=in:st=0:d=0.8,fade=t=out:st={duration - 1.0:.2f}:d=1.0,format=yuv420p[v]"
    )
    inputs = ["-f", "lavfi", "-i", f"color=c=black:s=1920x1080:r=30:d={duration}",
              "-loop", "1", "-i", roll_path]
    m_in, m_f = music_args(music, duration, audio_index=2)
    if m_in:
        cmd = (["ffmpeg", "-y"] + inputs + m_in +
               ["-filter_complex", ";".join([vf] + m_f),
                "-map", "[v]", "-map", "[a]", "-t", str(duration),
                "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                "-c:a", "aac", out])
    else:
        cmd = (["ffmpeg", "-y"] + inputs +
               ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
                "-filter_complex", vf,
                "-map", "[v]", "-map", "2:a", "-t", str(duration),
                "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                "-c:a", "aac", "-shortest", out])
    run(cmd)
    print(f"scrolling credits: {out} ({duration}s, roll height {rh}px)")


def make_card(credits, duration, music, out):
    card = build_card(credits)
    card_path = os.path.splitext(out)[0] + "-card.png"
    card.save(card_path, quality=95)
    vf = (f"fade=t=in:st=0:d=0.8,fade=t=out:st={duration - 0.8:.2f}:d=0.8,"
          f"format=yuv420p")
    m_in, m_f = music_args(music, duration)
    if m_in:
        cmd = (["ffmpeg", "-y", "-loop", "1", "-i", card_path] + m_in +
               ["-filter_complex", f"[0:v]{vf}[v];" + m_f[0],
                "-map", "[v]", "-map", "[a]", "-t", str(duration),
                "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                "-c:a", "aac", out])
    else:
        cmd = (["ffmpeg", "-y", "-loop", "1", "-i", card_path,
                "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
                "-vf", vf, "-t", str(duration),
                "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                "-c:a", "aac", "-shortest", out])
    run(cmd)
    print(f"end card: {out} ({duration}s)")


def main():
    ap = argparse.ArgumentParser(description="Build a movie-style vlog closing.")
    ap.add_argument("--credits", required=True, help="credits JSON")
    ap.add_argument("--mode", choices=["scroll", "card"], default="scroll")
    ap.add_argument("--duration", type=float, default=12.0,
                    help="scroll: 12s; card: 5s (default 12)")
    ap.add_argument("--music", default=None)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    credits = load_credits(args.credits)
    if args.mode == "scroll":
        make_scroll(credits, args.duration, args.music, args.out)
    else:
        make_card(credits, args.duration, args.music, args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
