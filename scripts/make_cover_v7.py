"""Build cover-v7 (A/B/C) — mood board, ORIGINAL FULL PHOTOS, no cutouts.

Per Aileen 2026-11-15 16:55-16:56 (logged in requirements-log.md):
  - MOOD BOARD, NO CUTOUTS. Do NOT cut out / mask / rembg anyone.
  - Scale each photo down PROPORTIONALLY (original aspect ratio, smaller).
    No cropping, no stretching.
  - UNIFY the color tone across the three photos (warm, vivid — like the
    v6 "korean" grade).
  - THREE photos, one per category: (1) OUTDOOR, (2) INDOOR, (3) SPEAKER.
  - Feature the PRETTY GIRLS, incl. the girl in BLACK CLOTHES with LONG
    HAIR (three-girls photo, middle girl in a black dress).
  - TEXT/FONT must look NICER. Make MULTIPLE versions with different
    fonts; she picks first. ONLY the font changes between versions.

Photos (full-frame, native aspect ratio, no crop/stretch):
  INDOOR / FEATURED  HM5A1413.JPG (3:2) — the girl in BLACK CLOTHES with
           LONG HAIR: black sleeveless top, long dark hair, front-facing,
           smiling at the camera, at a table indoors. This is the girl
           the user named. FEATURED (largest panel). (HM5A1412 is the
           same woman mid-blink; 1413 has her eyes open.)
  OUTDOOR  HM5A1893.JPG (3:2) — three girls at the storefront; the girl
           in the white dress making a peace sign, front-facing, at the
           Cursor banner. (The HM5A1892-1899 burst is all this same
           peace-sign scene, verified by contact sheet — NOT a separate
           three-girls-with-black-dress photo; the black-dress girl the
           user remembers is HM5A1413 above.)
  SPEAKER  frames-dense/DJI_20260719084815_0042_D/frame-0012.jpg (16:9) —
           Talk E woman (green t-shirt + cap) presenting at the screen,
           speaking into the mic, gesturing, front-facing. A video frame
           (no suitable female-speaker PHOTO exists in the library: the
           at-screen photos HM5A1725-1729 are all the same man, and
           HM5A1879/1880 show a woman from behind). Using a frame is
           consistent with the v5d cover, which mixed photos + frames.

Layout (canvas 1920x1080, cream #F7F1E5, margin 40, gap 24):
  - HM5A1413 (indoor, featured): x=40, y=40, w=1080, h=720.
  - HM5A1893 (outdoor):   x=1144, y=40, w=736, h=491.
  - 0042-f12 (speaker):   x=1144, y=555, w=736, h=414 (16:9).
  - Text block under the featured photo: x=40, y=780.
    "Cursor Cafe" / "Shanghai" + bronze rule + "2026.07.19".
  No cut-off heads (full photos), tones unified, text does not cover faces.

Fonts:
  A: Montserrat (fonts/Montserrat.ttf) — clean, refined, normal sans.
  B: Caveat (/home/hatch/.fonts/Caveat.ttf) — handwritten.
  C: Playfair Display (fonts/PlayfairDisplay.ttf + Italic) — elegant serif.
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance

W, H = 1920, 1080
BG = (247, 241, 229)          # cream #F7F1E5
INK = (58, 44, 32)            # dark brown ink
TAUPE = (120, 100, 78)
BRONZE = (150, 125, 90)
PHOTOS = "photos"

# (path, x, y, w) — height computed from the image's true aspect ratio
# (proportional scale, no crop/stretch). Layout: featured left, two stacked right.
PANELS = [
    (f"{PHOTOS}/HM5A1413.JPG", 40, 40, 1080),    # indoor, featured (3:2 -> h=720)
    (f"{PHOTOS}/HM5A1893.JPG", 1144, 40, 736),   # outdoor (3:2 -> h=491)
    ("frames-dense/DJI_20260719084815_0042_D/frame-0012.jpg", 1144, 555, 736),  # speaker (16:9 -> h=414)
]


def grade(im):
    """Unified warm/vivid grade (korean-style): saturation up, contrast up,
    brightness slightly up, warm tint (red up, blue down)."""
    im = im.convert("RGB")
    im = ImageEnhance.Color(im).enhance(1.15)
    im = ImageEnhance.Contrast(im).enhance(1.08)
    im = ImageEnhance.Brightness(im).enhance(1.05)
    # warm tint: R *1.04, G *1.0, B *0.96
    r, g, b = im.split()
    r = r.point(lambda v: min(255, int(v * 1.04)))
    b = b.point(lambda v: int(v * 0.96))
    return Image.merge("RGB", (r, g, b))


def build_panel(path, w):
    """Load a photo/frame, apply EXIF orientation, scale PROPORTIONALLY to
    the given width (height = width / true aspect). No crop, no stretch."""
    im = ImageOps.exif_transpose(Image.open(path))
    ow, oh = im.size
    aspect = ow / oh
    h = round(w / aspect)
    im = grade(im)
    panel = im.resize((w, h), Image.LANCZOS)
    print(f"  {path}: {ow}x{oh} aspect {aspect:.3f} -> panel {w}x{h}")
    return panel


def draw_tracked(d, xy, text, font, fill, tracking=6):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill)
        x += font.getlength(ch) + tracking
    return x


def load(path, size):
    return ImageFont.truetype(path, size)


def build(fonts, out_name):
    """fonts: dict with keys title, title_it (or None), date."""
    canvas = Image.new("RGB", (W, H), BG)
    for path, x, y, w in PANELS:
        panel = build_panel(path, w)
        canvas.paste(panel, (x, y))
        print(f"  pasted {path} at ({x},{y}) {panel.size[0]}x{panel.size[1]}")
    d = ImageDraw.Draw(canvas)
    tx, ty = 40, 780
    # Title: two lines "Cursor Cafe" / "Shanghai", then bronze rule, then date.
    # Fit the title width to the featured-photo width (1080).
    title_font = fonts["title"]
    title_it = fonts.get("title_it") or title_font
    date_font = fonts["date"]
    d.text((tx, ty), "Cursor Cafe", font=title_font, fill=INK)
    # second line y: use title font bbox height
    lh = title_font.getbbox("Cursor Cafe")[3] + 12
    d.text((tx, ty + lh), "Shanghai", font=title_it, fill=INK)
    lh2 = title_it.getbbox("Shanghai")[3] + 12
    rule_y = ty + lh + lh2 + 18
    d.line([(tx + 4, rule_y), (tx + 336, rule_y)], fill=BRONZE, width=2)
    draw_tracked(d, (tx + 4, rule_y + 20), "2026.07.19", date_font, TAUPE, tracking=6)
    canvas.save(out_name, quality=92)
    print(f"Wrote {out_name} {canvas.size}")


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)) or ".")
    # Version A: Montserrat (normal, refined sans)
    build({
        "title": load("fonts/Montserrat.ttf", 72),
        "title_it": load("fonts/Montserrat.ttf", 72),
        "date": load("fonts/Montserrat.ttf", 28),
    }, "cover-v7-A.jpg")
    # Version B: Caveat (handwritten) — smaller than A/C: Caveat's line
    # height runs tall, so 96pt pushed the date off the canvas; 76pt fits.
    build({
        "title": load("/home/hatch/.fonts/Caveat.ttf", 76),
        "title_it": load("/home/hatch/.fonts/Caveat.ttf", 76),
        "date": load("/home/hatch/.fonts/Caveat.ttf", 32),
    }, "cover-v7-B.jpg")
    # Version C: Playfair Display (elegant serif)
    build({
        "title": load("fonts/PlayfairDisplay.ttf", 76),
        "title_it": load("fonts/PlayfairDisplay-Italic.ttf", 76),
        "date": load("fonts/Montserrat.ttf", 28),
    }, "cover-v7-C.jpg")

    # ---- comparison image: 2x2 grid (A, B, C, previous cover-v5.jpg) ----
    prev = Image.open("cover-v5.jpg").convert("RGB")
    names = [("cover-v7-A.jpg", "A — Montserrat (normal)"),
             ("cover-v7-B.jpg", "B — Caveat (handwritten)"),
             ("cover-v7-C.jpg", "C — Playfair (serif)"),
             ("cover-v5.jpg", "Previous — v5d mood board")]
    tw, th = 960, 540
    comp = Image.new("RGB", (tw * 2 + 30, th * 2 + 90), (255, 255, 255))
    dd = ImageDraw.Draw(comp)
    labelfont = ImageFont.truetype("fonts/Montserrat.ttf", 28)
    for i, (path, label) in enumerate(names):
        im = Image.open(path).convert("RGB").resize((tw, th), Image.LANCZOS)
        x = (i % 2) * (tw + 30)
        y = (i // 2) * (th + 45)
        comp.paste(im, (x, y))
        dd.text((x + 8, y + th + 8), label, font=labelfont, fill=(30, 30, 30))
    comp.save("cover-compare.jpg", quality=92)
    print("Wrote cover-compare.jpg", comp.size)


if __name__ == "__main__":
    main()
