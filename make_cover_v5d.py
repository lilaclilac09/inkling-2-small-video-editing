"""Build cover-v5.jpg — mood board, ORIGINAL FULL PHOTOS, no cropping (v5d).

Per Aileen 2026-11-13 19:42 (logged in requirements-log.md):
  - The mood-board direction is right, BUT the v5c photos were still CROPS
    (black-hat girl 0.76 width, group 0.84 width) — she can tell they are
    not the full pictures.
  - FIX: use the ORIGINAL full photos and place them AT PROPORTIONAL SCALE
    (keep each photo's native aspect ratio, just scale to fit the slot).
    NO cropping, NO cutting out, NO masks, NO rembg, NO feathering.
  - ADD MORE PHOTOS: interior speaking close-ups (dàtóu) + people
    interacting/chatting.
  - Still a mood board on the cream canvas with gaps between panels.
    Same text ("Cursor Cafe Shanghai" / "2026.07.19"), same refined
    typography (Playfair Bold + Italic, bronze rule, letterspaced date).

Panels (8 photos, all full-frame, native aspect ratio):
  R1: text | black-hat girl HM5A1822 (full, 3:2) | hero 0054 frame-0003
        (full, 16:9, green-trees girl)
  R2: Talk E hat girl 0042 frame-0012 (16:9) | Carl Yang 0047 frame-0008
        (16:9) | two women by drinks fridge 0049 frame-0012 (16:9)
  R3: interior Talk L 0051 frame-0008 (16:9) | group HM5A1478 (full, 3:2,
        all 8 men incl. the back-turned 8th) | listeners 0063 frame-0003
        (16:9)
Layout: canvas 1920x1080, cream #F7F1E5, margins 36 sides / 28 top-bottom,
gap 28. Row heights 320 / 315 / 333. Each row is centred horizontally.
Panel width = round(height * true_aspect) — proportional scale, no crop,
no stretch.
"""
from PIL import Image, ImageDraw, ImageFont, ImageOps

W, H = 1920, 1080
BG = (247, 241, 229)
INK = (58, 44, 32)
TAUPE = (120, 100, 78)
BRONZE = (150, 125, 90)
FONTS = "fonts"
MX, MY, GAP = 36, 28, 28


def load_font(name, size, weight):
    f = ImageFont.truetype(f"{FONTS}/{name}", size)
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        pass
    return f


def fit_panel(path, height):
    """Load a photo/frame, apply EXIF orientation, scale PROPORTIONALLY to
    the given height (width = height * true aspect). No crop, no stretch."""
    im = ImageOps.exif_transpose(Image.open(path))
    w, h = im.size
    aspect = w / h
    pw = round(height * aspect)
    panel = im.convert("RGB").resize((pw, height), Image.LANCZOS)
    print(f"  {path}: {w}x{h} aspect {aspect:.3f} -> panel {pw}x{height}")
    return panel


def draw_tracked(d, xy, text, font, fill, tracking=6):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill)
        x += font.getlength(ch) + tracking
    return x


def main():
    canvas = Image.new("RGB", (W, H), BG)
    usable_w = W - 2 * MX

    # ---- Row 1 (y=28, h=320): text | black-hat girl | hero ----
    h1 = 320
    y1 = MY
    girl = fit_panel("photos/HM5A1822.JPG", h1)          # full, 3:2
    hero = fit_panel("frames-dense/DJI_20260719104432_0054_D/frame-0003.jpg", h1)  # full, 16:9
    text_w = 620
    row1_w = text_w + girl.width + hero.width + 2 * GAP
    x1 = MX + (usable_w - row1_w) // 2
    print("row1 width", row1_w, "start x", x1)

    # ---- Row 2 (y=376, h=315): Talk E | Carl Yang | two women ----
    h2 = 315
    y2 = y1 + h1 + GAP
    talke = fit_panel("frames-dense/DJI_20260719084815_0042_D/frame-0012.jpg", h2)
    carl = fit_panel("frames-dense/DJI_20260719101632_0047_D/frame-0008.jpg", h2)
    twowomen = fit_panel("frames-dense/DJI_20260719103442_0049_D/frame-0012.jpg", h2)
    row2_w = talke.width + carl.width + twowomen.width + 2 * GAP
    x2 = MX + (usable_w - row2_w) // 2
    print("row2 width", row2_w, "start x", x2)

    # ---- Row 3 (y=719, h=333): interior | group | listeners ----
    h3 = 333
    y3 = y2 + h2 + GAP
    interior = fit_panel("frames-dense/DJI_20260719103816_0051_D/frame-0008.jpg", h3)
    group = fit_panel("photos/HM5A1478.JPG", h3)          # full, 3:2, all 8 men
    listeners = fit_panel("frames-dense/DJI_20260719111025_0063_D/frame-0003.jpg", h3)
    row3_w = interior.width + group.width + listeners.width + 2 * GAP
    x3 = MX + (usable_w - row3_w) // 2
    print("row3 width", row3_w, "start x", x3)
    print("bottom edge:", y3 + h3, "canvas H:", H)

    # ---- paste panels ----
    # R1: text block, then girl, then hero (hero top-right)
    canvas.paste(girl, (x1 + text_w + GAP, y1))
    canvas.paste(hero, (x1 + text_w + GAP + girl.width + GAP, y1))
    # R2
    canvas.paste(talke, (x2, y2))
    canvas.paste(carl, (x2 + talke.width + GAP, y2))
    canvas.paste(twowomen, (x2 + talke.width + GAP + carl.width + GAP, y2))
    # R3
    canvas.paste(interior, (x3, y3))
    canvas.paste(group, (x3 + interior.width + GAP, y3))
    canvas.paste(listeners, (x3 + interior.width + GAP + group.width + GAP, y3))

    # ---- typography in the R1 text block (same refined style as v5b) ----
    d = ImageDraw.Draw(canvas)
    tx, ty = x1, y1
    # Fit the title inside the text block width
    size = 102
    while size > 40:
        title_font = load_font("PlayfairDisplay.ttf", size, 700)
        if title_font.getlength("Cursor Cafe") <= text_w - 20:
            break
        size -= 4
    title_it = load_font("PlayfairDisplay-Italic.ttf", size, 700)
    date_font = load_font("Montserrat.ttf", 34, 600)
    print("title size:", size, "Cursor Cafe width:",
          round(title_font.getlength("Cursor Cafe")))
    d.text((tx, ty + 30), "Cursor Cafe", font=title_font, fill=INK)
    d.text((tx, ty + 30 + size + 18), "Shanghai", font=title_it, fill=INK)
    rule_y = ty + 30 + 2 * size + 60
    d.line([(tx + 4, rule_y), (tx + 336, rule_y)], fill=BRONZE, width=2)
    draw_tracked(d, (tx + 4, rule_y + 20), "2026.07.19", date_font, TAUPE, tracking=6)

    canvas.save("cover-v5.jpg", quality=92)
    print("Wrote cover-v5.jpg", canvas.size)


if __name__ == "__main__":
    main()
