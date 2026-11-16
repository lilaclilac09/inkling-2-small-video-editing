"""Build v7 cover v13 — same as v12 but the logo stickers use the
REAL official Cursor logo (extracted from logo-cursor-official.jpg,
the file the user sent) instead of the banner-cropped cube.
Everything else (layout, panels, scattered title, cup positions)
is identical to v12.

Build v7 cover v12 — redesign (2026-11-16 09:19, user).

Her directions, in order:
  1. CONTRAST / MORNING PHOTOS: contrast too weak; pick MORNING
     photos, they'd look better. All four panels are morning shots:
     HM5A1478 10:27, HM5A1413 10:05, frame-0003 (clip 0054) 10:44,
     0042-f52 (clip 0042) 08:48. Grade boosted a touch more
     (contrast 1.12) for extra pop.
  2. CAFE INTERIOR + CROWD: cover shows the hall and the crowd.
     0042-f52 is a wide interior shot (speaker + screen + shelves +
     lantern + audience); HM5A1413 is the main room with the audience
     behind the seated woman.
  3. CUP CUTOUTS KEEP THE TABLE: for the seated cup shots, do NOT
     cut the table out. A rembg cutout removes the table by
     definition, so the cup panels are RECTANGULAR full-frame shots
     instead — the table stays fully visible. (All four panels are
     rectangular in v12 for the same reason: interior + table.)
  4. LOGO ON EVERY COFFEE CUP: 6 cups get the logo sticker, not just
     the one in frame-0003: frame-0003 man's tall cup + woman's small
     cup; HM5A1413's 3 table cups; HM5A1478's small cup in the man's
     hand. Positions measured by zooming each cup (see CUP_LOGOS).
  5. WHITE LOGO, BIGGER: white Cursor cube (on a black rounded-square
     backing so it reads on light-brown coffee), 30-32px (v10 was
     24px); the tiny HM5A1478 cup gets 18px (the cup itself is only
     ~16px wide in the panel).
  6. SCATTERED TITLE: the title words are NOT in neat rows; they are
     scattered playfully ON the main image (frame-0003) at varied
     positions/rotations, like a sticker collage. Same big bold
     outlined floating style (DejaVu Sans Bold, white/yellow + black
     outline, drop shadow). No faces covered (verified).
  7. LAYOUT FLIP: roll-up-banner group photo LEFT, visual center
     RIGHT. HM5A1478 (8 guys posing with thumbs up around the black
     "Cursor Cafe x Sunset Shanghai" roll-up banner, storefront,
     morning 10:27) is the left panel; frame-0003 (two girls) is the
     visual center on the right.

Layout (1920x1080, cream #F7F1E5):
  Left column  x=40 w=730:  HM5A1478 (40,40) 730x487
                           HM5A1413 (40,551) 730x487
  Right column x=794 w=1086: frame-0003 (794,40) 1086x611 (visual center)
                           0042-f52   (794,675) 1086x365 (wide, crop y 90-455)
  Title scattered on frame-0003. Logo stickers on all 6 cups.
Output: v7-cover-v12.jpg + comparison v7-cover-compare-v10v12.jpg.
Does NOT overwrite v2-v11.
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance, ImageFilter
import numpy as np

W, H = 1920, 1080
BG = (247, 241, 229)          # cream #F7F1E5
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
PALEYELLOW = (255, 243, 176)

LOGO_ART = "cutouts/logo-cursor-official.png"  # white cube RGBA, extracted from the OFFICIAL logo file the user sent

# Panels: (source, x, y, w, h, crop_top_or_None)
# crop_top: for the speaker wide shot, vertical crop offset in the
# resized image (keeps speaker head + screen + partial audience).
PANELS = [
    ("photos/HM5A1478.JPG", 40, 40, 730, 487, None),
    ("photos/HM5A1413.JPG", 40, 551, 730, 487, None),
    ("frames-dense/DJI_20260719104432_0054_D/frame-0003.jpg", 794, 40, 1086, 611, None),
    ("frames-dense/DJI_20260719084815_0042_D/frame-0052.jpg", 794, 675, 1086, 365, 90),
]

# Logo stickers: (panel_index, cx, cy, size) in CANVAS coordinates.
# Measured by zooming each cup:
#  A1 HM5A1478: man in white tee holds a small dark cup, full-photo
#     centre (1480,2095) -> panel (180,255) -> canvas (220,295).
#     Cup only ~16px wide in the panel -> 18px logo.
#  B1 HM5A1413 left cup (short glass, light-brown): table-crop centre
#     -> panel (32,412) -> canvas (72,963). 32px.
#  B2 HM5A1413 middle cup (clear, mostly empty): panel (99,407)
#     -> canvas (139,958). 30px.
#  B3 HM5A1413 right cup (tall iced coffee): panel (222,405)
#     -> canvas (262,956). 32px.
#  C1 frame-0003 man's tall cup: orig centre (490,645) -> panel
#     (416,547) -> canvas (1210,587). 32px.
#  C2 frame-0003 woman's small dark cup: orig centre (695,595) ->
#     panel (589,505) -> canvas (1383,545). 30px.
CUP_LOGOS = [
    (220, 295, 18),    # A1 HM5A1478 small cup
    (72, 963, 32),     # B1 HM5A1413 left cup
    (139, 958, 30),    # B2 HM5A1413 middle cup
    (262, 956, 32),    # B3 HM5A1413 right cup
    (1210, 587, 32),   # C1 frame-0003 man's tall cup
    (1383, 545, 30),   # C2 frame-0003 woman's small cup
]

# Scattered title words on frame-0003 (panel origin (794,40);
# positions below are CANVAS coords). Faces (display coords):
# man left x 227-415 y 227-415; woman centre x 632-731 y 326-472;
# girl right x 909-1064 y 276-473; man white behind x 789-868 y 365-473.
# All words clear of faces; words sit on trees / dark clothing.
# (word, x, y, angle_deg, font_size, fill)
SCATTER = [
    ("Cursor", 819, 55, -8, 92, WHITE),
    ("Cafe", 1574, 130, 10, 92, PALEYELLOW),
    ("Shanghai", 854, 180, -5, 78, WHITE),
    ("2026.07.19", 1594, 600, 4, 38, PALEYELLOW),
]
TITLE_FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def grade(im):
    """Warm/vivid grade, slightly stronger than v10/v11 for contrast."""
    im = im.convert("RGB")
    im = ImageEnhance.Color(im).enhance(1.15)
    im = ImageEnhance.Contrast(im).enhance(1.12)
    im = ImageEnhance.Brightness(im).enhance(1.06)
    r, g, b = im.split()
    r = r.point(lambda v: min(255, int(v * 1.04)))
    b = b.point(lambda v: int(v * 0.96))
    return Image.merge("RGB", (r, g, b))


def prep_rect(path, w, h, crop_top=None):
    """Full-frame shot: grade, resize to slot width, crop vertically
    to fill the slot. crop_top overrides the centred crop."""
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    ow, oh = im.size
    im = grade(im)
    nh = round(w * oh / ow)
    im = im.resize((w, nh), Image.LANCZOS)
    if crop_top is not None:
        top = crop_top
    else:
        top = max(0, (nh - h) // 2)
    im = im.crop((0, top, w, top + h))
    print(f"  {path}: {ow}x{oh} -> {w}x{nh}, cropped y {top}-{top + h}")
    return im


def make_logo_sticker(logo, size):
    """White cube on a black rounded-square backing + white die-cut
    outline + drop shadow baked into an RGBA tile of `size` px.
    Returns (tile, outline_alpha) ready to paste centred at (cx, cy)."""
    cube = logo.copy()
    bbox = cube.split()[3].getbbox()
    cube = cube.crop(bbox)
    S = size
    backing = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    bd = ImageDraw.Draw(backing)
    bd.rounded_rectangle([0, 0, S - 1, S - 1], radius=max(3, S // 5),
                         fill=(20, 20, 20, 255))
    cw = round(S * 0.72)
    ch = round(cw * cube.size[1] / cube.size[0])
    cube = cube.resize((cw, ch), Image.LANCZOS)
    backing.alpha_composite(cube, ((S - cw) // 2, (S - ch) // 2))
    alpha = backing.split()[3]
    dil = alpha.filter(ImageFilter.MaxFilter(5))
    # Tile with room for outline + shadow.
    pad = 6
    tile = Image.new("RGBA", (S + pad * 2, S + pad * 2), (0, 0, 0, 0))
    # Shadow (offset down-right, blurred).
    sh = Image.new("RGBA", (S + pad * 2, S + pad * 2), (0, 0, 0, 0))
    sh_im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    sh_im.putalpha(dil.point(lambda v: int(v * 0.30)))
    sh.paste(sh_im, (pad + 2, pad + 2), sh_im)
    sh = sh.filter(ImageFilter.GaussianBlur(2))
    tile.alpha_composite(sh)
    # White die-cut outline.
    outline = Image.new("RGBA", (S, S), (255, 255, 255, 255))
    outline.putalpha(dil)
    tile.alpha_composite(outline, (pad, pad))
    tile.alpha_composite(backing, (pad, pad))
    return tile, pad


def paste_logo(canvas, logo, cx, cy, size):
    tile, pad = make_logo_sticker(logo, size)
    px = cx - tile.size[0] // 2
    py = cy - tile.size[1] // 2
    canvas.alpha_composite(tile, (px, py))
    print(f"  logo sticker {size}px at canvas ({cx},{cy})")


def draw_scattered_word(canvas, word, x, y, angle, font_size, fill):
    """One title word as a floating outlined sticker, rotated and
    pasted at canvas (x, y) (top-left of the unrotated tile)."""
    font = ImageFont.truetype(TITLE_FONT, font_size)
    stroke_w = 10 if font_size >= 78 else 5
    tmp = Image.new("RGBA", (10, 10), (0, 0, 0, 0))
    td = ImageDraw.Draw(tmp)
    bb = td.textbbox((0, 0), word, font=font, stroke_width=stroke_w)
    tw = bb[2] - bb[0]
    th = bb[3] - bb[1]
    pad = 30
    layer = Image.new("RGBA", (tw + pad * 2, th + pad * 2), (0, 0, 0, 0))
    ox, oy = pad - bb[0], pad - bb[1]
    # Drop shadow (offset, blurred).
    sh = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.text((ox + 5, oy + 7), word, font=font, fill=(0, 0, 0, 115),
            stroke_width=stroke_w, stroke_fill=(0, 0, 0, 115))
    sh = sh.filter(ImageFilter.GaussianBlur(6))
    layer.alpha_composite(sh)
    d = ImageDraw.Draw(layer)
    d.text((ox, oy), word, font=font, fill=fill + (255,),
           stroke_width=stroke_w, stroke_fill=BLACK + (255,))
    layer = layer.rotate(angle, expand=True, resample=Image.BICUBIC)
    canvas.alpha_composite(layer, (x, y))
    print(f"  scattered '{word}' at ({x},{y}) rot {angle}deg {font_size}pt "
          f"-> tile {layer.size}")


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)) or ".")
    logo = Image.open(LOGO_ART).convert("RGBA")
    print(f"logo art {LOGO_ART} {logo.size}")

    canvas = Image.new("RGBA", (W, H), (247, 241, 229, 255))
    for (path, x, y, w, h, crop_top) in PANELS:
        panel = prep_rect(path, w, h, crop_top=crop_top)
        canvas.alpha_composite(panel.convert("RGBA"), (x, y))
        print(f"  panel pasted at ({x},{y}) {w}x{h}")

    # Scattered title on the main image (frame-0003, right column).
    for (word, x, y, angle, size, fill) in SCATTER:
        draw_scattered_word(canvas, word, x, y, angle, size, fill)

    # Logo sticker on every coffee cup.
    for (cx, cy, size) in CUP_LOGOS:
        paste_logo(canvas, logo, cx, cy, size)

    canvas.convert("RGB").save("v7-cover-v13.jpg", quality=92)
    print("Wrote v7-cover-v13.jpg 1920x1080")

    # Comparison: v10 vs v12 side by side.
    tw, th = 960, 540
    comp = Image.new("RGB", (tw * 2 + 30, th + 45), (255, 255, 255))
    dd = ImageDraw.Draw(comp)
    labelfont = ImageFont.truetype("fonts/Montserrat.ttf", 26)
    for i, (path, label) in enumerate([
            ("v7-cover-v12.jpg", "v12 (banner-crop cube logos)"),
            ("v7-cover-v13.jpg", "v13 (OFFICIAL Cursor logo)")]):
        im = Image.open(path).convert("RGB").resize((tw, th), Image.LANCZOS)
        x = i * (tw + 30)
        comp.paste(im, (x, 0))
        dd.text((x + 8, th + 8), label, font=labelfont, fill=(30, 30, 30))
    comp.save("v7-cover-compare-v12v13.jpg", quality=92)
    print("Wrote v7-cover-compare-v12v13.jpg")


if __name__ == "__main__":
    main()
