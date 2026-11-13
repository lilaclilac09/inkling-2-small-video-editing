#!/usr/bin/env python3
"""Build a reusable opening title card for a vlog, then a short video clip of it.

The card is a 1920x1080 still built from a wide base photo (your best exterior
or establishing shot), darkened with a bottom gradient so the text stays
legible. Text sits in the lower half on purpose: the top quarter of the frame
is kept clear, so a banner or logo in the photo (e.g. a Cursor banner) is
never covered by text.

Inputs (all plain text, nothing hardcoded to one event):
  --title     e.g. "Cursor Cafe Shanghai"
  --date      e.g. "2026.07.19"
  --location  e.g. "Shanghai · Yanqing Road"
  --image     base wide shot (any photo; cropped to 16:9)
  --duration  seconds the card holds (default 3.0)
  --out       output mp4 (1920x1080, 30fps, silent audio so it joins cleanly)

The card slowly zooms in (Ken Burns) and fades in from black, so the cut into
the first footage clip can be a dissolve rather than a hard cut — see
assemble_vlog.py, which xfades card -> body -> closing.

Fonts: Caveat for Latin titles, Ma Shan Zheng for Chinese titles,
DejaVu Sans for the date/location line. All are installed on this machine.

Usage:
  python3 make_opening.py --title "Cursor Cafe Shanghai" --date "2026.07.19" \
      --location "Shanghai · Yanqing Road" --image base.jpg --out opening.mp4
  python3 make_opening.py --title "My Berlin Vlog" --date "2026.10.12" \
      --location "Berlin" --image base.jpg --out opening.mp4 --keep-png card.png
"""

import argparse
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
    "noto_bold": "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
}

WARM_WHITE = (255, 248, 231, 255)
SOFT_WHITE = (255, 255, 255, 230)


def has_cjk(text):
    return any("\u4e00" <= ch <= "\u9fff" for ch in text)


def font(path, size):
    return ImageFont.truetype(path, size)


def fit_font(draw, text, path, start_size, max_width, min_size=40):
    """Largest size (<= start_size) at which text fits max_width."""
    size = start_size
    while size > min_size:
        f = font(path, size)
        if draw.textlength(text, font=f) <= max_width:
            return f, size
        size -= 4
    return font(path, min_size), min_size


def wrap_title(draw, title, path, start_size, max_width):
    """Wrap a title to at most two lines; returns (font, [line, ...])."""
    f, size = fit_font(draw, title, path, start_size, max_width)
    if draw.textlength(title, font=f) <= max_width:
        return f, [title]
    words = title.split()
    if len(words) < 2:
        return f, [title]
    # Split into two balanced lines.
    best = None
    for i in range(1, len(words)):
        l1, l2 = " ".join(words[:i]), " ".join(words[i:])
        w1 = draw.textlength(l1, font=f)
        w2 = draw.textlength(l2, font=f)
        if w1 <= max_width and w2 <= max_width:
            score = abs(w1 - w2)
            if best is None or score < best[0]:
                best = (score, [l1, l2])
    if best:
        return f, best[1]
    return f, [title]


def build_card(title, date, location, image_path):
    base = Image.open(image_path).convert("RGB")
    # Center-crop to 16:9, resize to 1920x1080.
    tw, th = base.size
    target = W / H
    if tw / th > target:
        nw = int(th * target)
        x0 = (tw - nw) // 2
        base = base.crop((x0, 0, x0 + nw, th))
    else:
        nh = int(tw / target)
        y0 = (th - nh) // 2
        base = base.crop((0, y0, tw, y0 + nh))
    base = base.resize((W, H), Image.LANCZOS)

    # Darken overall, then a stronger gradient at the bottom for text legibility.
    dark = Image.new("RGB", (W, H), (0, 0, 0))
    img = Image.blend(base, dark, 0.25)
    grad = Image.new("L", (1, H))
    grad.putdata([int(255 * (max(0, (y - H * 0.45) / (H * 0.55)) ** 1.5) * 0.55) for y in range(H)])
    grad = grad.resize((W, H))
    black = Image.new("RGB", (W, H), (0, 0, 0))
    img = Image.composite(black, img, grad)
    img = img.convert("RGBA")

    draw = ImageDraw.Draw(img)
    title_font_path = FONTS["ma_shan"] if has_cjk(title) else FONTS["caveat"]
    title_start = 150 if has_cjk(title) else 170
    title_font, lines = wrap_title(draw, title, title_font_path, title_start, W - 240)
    line_h = int(title_font.size * 1.05)

    sub = " · ".join(p for p in [date, location] if p)
    sub_font, _ = fit_font(draw, sub, FONTS["dejavu"], 44, W - 320)

    # Layout: title block sits in the lower half (logo zone at top stays clear).
    total_h = line_h * len(lines) + 30 + sub_font.size
    y = H - 130 - total_h
    for line in lines:
        draw.text((W / 2, y), line, font=title_font, fill=WARM_WHITE, anchor="ma",
                  stroke_width=2, stroke_fill=(0, 0, 0, 160))
        y += line_h
    y += 30
    draw.text((W / 2, y), sub, font=sub_font, fill=SOFT_WHITE, anchor="ma",
              stroke_width=1, stroke_fill=(0, 0, 0, 160))
    return img.convert("RGB")


def run(cmd):
    print(" ".join(cmd))
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-2000:])
        raise SystemExit(f"ffmpeg failed ({r.returncode})")
    return r


def main():
    ap = argparse.ArgumentParser(description="Build a vlog opening title card clip.")
    ap.add_argument("--title", required=True)
    ap.add_argument("--date", default="")
    ap.add_argument("--location", default="")
    ap.add_argument("--image", required=True, help="base wide shot")
    ap.add_argument("--duration", type=float, default=3.0)
    ap.add_argument("--music", default=None,
                    help="optional music bed under the card (volume 0.3)")
    ap.add_argument("--out", required=True, help="output mp4")
    ap.add_argument("--keep-png", default=None, help="also save the card still")
    args = ap.parse_args()

    card = build_card(args.title, args.date, args.location, args.image)
    png = args.keep_png or os.path.splitext(args.out)[0] + "-card.png"
    card.save(png, quality=95)
    print(f"card still: {png}")

    frames = max(1, int(round(args.duration * 30)))
    vf = (
        f"zoompan=z='min(zoom+0.0007,1.07)':d={frames}:s=1920x1080:fps=30,"
        f"fade=t=in:st=0:d=0.5,format=yuv420p"
    )
    if args.music:
        cmd = ["ffmpeg", "-y", "-loop", "1", "-i", png, "-i", args.music,
               "-filter_complex",
               f"[0:v]{vf}[v];[1:a]volume=0.3,afade=t=out:st={args.duration - 1.0:.2f}:d=1.0[a]",
               "-map", "[v]", "-map", "[a]", "-t", str(args.duration),
               "-c:v", "libx264", "-preset", "medium", "-crf", "20",
               "-c:a", "aac", args.out]
    else:
        cmd = ["ffmpeg", "-y", "-loop", "1", "-i", png,
               "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
               "-vf", vf, "-t", str(args.duration),
               "-c:v", "libx264", "-preset", "medium", "-crf", "20",
               "-c:a", "aac", "-shortest", args.out]
    run(cmd)
    print(f"opening clip: {args.out} ({args.duration}s, 1920x1080, 30fps)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
