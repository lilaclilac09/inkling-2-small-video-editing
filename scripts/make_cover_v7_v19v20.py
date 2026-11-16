"""Build v7 covers v19 (sticker collage) + v20 (v18 audience shrink).

v19 — LAYERED STICKER COLLAGE (user direction 2026-11-16 09:51-09:52).
NOT a flat grid. Cream background shows between elements; photos sit
as white-framed cards at slight rotations, overlapping deliberately;
Cursor logo stickers from the production sheet are scattered around
with fat white die-cut borders + soft shadows.
  * HM5A1478 (banner group photo) is OUT of the top-left and NOT a
    main panel — the user says it doesn't look good there.
  * frame-0003 is the BIGGEST element (visual center).
  * HM5A1413 (black-dress girl + group) is prominent, FULLY visible.
  * Speaker = white-shirt man, WHOLE person + screen: the panel is
    3:2 (680x453), the full frame, no crop — head, hands, MacBook
    and the big screen (voice-app UI) all in frame.
  * Cup photo (real printed logo) as a small framed portrait card.
  * TITLE: Caveat (handwriting — the cutest font on the system; NO
    true crayon font is installed), white, NO black outline, slightly
    thickened with a white stroke, soft drop shadow. No word covers
    any head (checked programmatically, same head boxes as v14,
    rescaled to the new frame-0003 placement).
  * NO fake logo stickers on cups next to people (the cup photo
    carries the real printed logo).

v20 — v18 flat layout, audience panel (HM5A1652) zoomed OUT ~17%
(crop a taller window, then scale down to the slot) so the people
read smaller and more of the scene shows. Everything else = v18
(incl. Noto Sans Black title).

Outputs: v7-cover-v19.jpg, v7-cover-v20.jpg,
v7-cover-compare-v14v19v20.jpg. Does NOT overwrite v2-v18.
"""
import os
import math
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance, ImageFilter

W, H = 1920, 1080
BG = (247, 241, 229)          # cream #F7F1E5
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

CAVEAT = "/home/hatch/.fonts/Caveat.ttf"
NOTO_BLACK = "/usr/share/fonts/truetype/noto/NotoSans-Black.ttf"
LABEL_FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"

# frame-0003 head boxes, PANEL coords at the v14 reference size
# (1086x611). Rescaled in code to the v19 placement.
HEADS_REF = [
    (195, 130, 345, 310),    # H1 man left
    (475, 275, 605, 440),    # H2 woman centre
    (625, 285, 715, 420),    # H3 man white behind
    (720, 150, 895, 345),    # H4 girl right
]
HEAD_PAD = 8

# ---- v19 geometry (photo boxes, before the white frame) ----
FRAME_MAIN = ("frames-dense/DJI_20260719104432_0054_D/frame-0003.jpg",
              760, 30, 1100, 619, 0)      # BIGGEST, anchor, no rotation
HM1413 = ("photos/HM5A1413.JPG", 60, 600, 620, 413, 2)
SPEAKER = ("speaker-white-shirt-man.jpg", 1160, 600, 680, 453, -1.5)
CUP = ("cup-hand-logo.jpg", 800, 640, 270, 360, -3)

# stickers: (tile, center x, center y, max-size px, angle deg)
STICKERS = [
    ("cutouts/sticker-hex-black-large.png", 135, 130, 150, -8),
    ("cutouts/sticker-pill-cursor.png", 235, 300, 330, -3),
    ("cutouts/sticker-square-white-large.png", 130, 480, 120, 5),
    ("cutouts/sticker-square-black-small.png", 1852, 88, 85, 6),
]

# Title, Caveat, scattered on frame-0003's dark patches.
# (word, x, y, angle_deg, font_size) — canvas coords, top-left of tile.
SCATTER_V19 = [
    ("Cursor", 770, 28, -4, 125),
    ("Cafe", 1500, 30, 6, 125),
    ("Shanghai", 775, 465, -5, 95),
    ("2026.07.19", 780, 550, 3, 46),
]
CAVEAT_STROKE = 2

# v14 title (Noto Black), reused for v20 (same positions as v14).
SCATTER_V14 = [
    ("Cursor", 810, 24, -4, 120),
    ("Cafe", 1504, 20, 6, 120),
    ("Shanghai", 814, 510, -5, 100),
    ("2026.07.19", 1590, 580, 4, 48),
]
# v14 frame-0003 head boxes, CANVAS coords (panel origin 794,40).
HEADS_V14 = [
    (989, 170, 1139, 350),
    (1269, 315, 1399, 480),
    (1419, 325, 1509, 460),
    (1514, 190, 1689, 385),
]


def grade(im):
    """Warm/vivid grade, same as v12/v13."""
    im = im.convert("RGB")
    im = ImageEnhance.Color(im).enhance(1.15)
    im = ImageEnhance.Contrast(im).enhance(1.12)
    im = ImageEnhance.Brightness(im).enhance(1.06)
    r, g, b = im.split()
    r = r.point(lambda v: min(255, int(v * 1.04)))
    b = b.point(lambda v: int(v * 0.96))
    return Image.merge("RGB", (r, g, b))


def prep_photo(path, w, h, crop_top=None):
    """Grade + resize to slot width, crop vertically to fill.
    No crop if the aspect already matches (full frame kept)."""
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    ow, oh = im.size
    im = grade(im)
    nh = round(w * oh / ow)
    im = im.resize((w, nh), Image.LANCZOS)
    if nh <= h:
        # aspect matches the slot (within rounding): full frame kept
        return im
    top = crop_top if crop_top is not None else max(0, (nh - h) // 2)
    return im.crop((0, top, w, top + h))


def framed_card(photo, frame=14, angle=0, radius=10):
    """White-framed card with soft drop shadow. Returns (card, shadow)
    as RGBA layers (shadow is black, offset baked in by the caller)."""
    w, h = photo.size
    card = Image.new("RGBA", (w + frame * 2, h + frame * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle([0, 0, card.size[0] - 1, card.size[1] - 1],
                        radius=radius, fill=(255, 255, 255, 255))
    card.alpha_composite(photo.convert("RGBA"), (frame, frame))
    if angle:
        card = card.rotate(angle, expand=True, resample=Image.BICUBIC)
    # shadow from the card's alpha
    alpha = card.split()[3]
    sh = Image.new("RGBA", card.size, (0, 0, 0, 0))
    sh.putalpha(alpha.point(lambda v: int(v * 0.32)))
    sh = sh.filter(ImageFilter.GaussianBlur(9))
    return card, sh


def paste_card(canvas, photo, x, y, frame=14, angle=0):
    card, sh = framed_card(photo, frame=frame, angle=angle)
    # rotation with expand shifts the top-left; centre the card on the
    # intended photo centre instead of the raw (x, y)
    cx, cy = x + photo.size[0] // 2, y + photo.size[1] // 2
    px, py = cx - card.size[0] // 2, cy - card.size[1] // 2
    canvas.alpha_composite(sh, (px + 8, py + 10))
    canvas.alpha_composite(card, (px, py))
    print(f"  card {photo.size} at centre ({cx},{cy}) rot {angle}deg "
          f"-> tile {card.size}")
    return (px, py, px + card.size[0], py + card.size[1])


def paste_sticker(canvas, path, cx, cy, size, angle):
    tile = Image.open(path).convert("RGBA")
    scale = size / max(tile.size)
    tile = tile.resize((max(1, round(tile.size[0] * scale)),
                        max(1, round(tile.size[1] * scale))),
                       Image.LANCZOS)
    if angle:
        tile = tile.rotate(angle, expand=True, resample=Image.BICUBIC)
    alpha = tile.split()[3]
    sh = Image.new("RGBA", tile.size, (0, 0, 0, 0))
    sh.putalpha(alpha.point(lambda v: int(v * 0.30)))
    sh = sh.filter(ImageFilter.GaussianBlur(4))
    px, py = cx - tile.size[0] // 2, cy - tile.size[1] // 2
    canvas.alpha_composite(sh, (px + 4, py + 5))
    canvas.alpha_composite(tile, (px, py))
    print(f"  sticker {os.path.basename(path)} {tile.size} "
          f"at centre ({cx},{cy}) rot {angle}deg")


def _intersects(a, b):
    return not (a[2] <= b[0] or a[0] >= b[2] or a[3] <= b[1] or a[1] >= b[3])


def _rotated_glyph_bbox(layer_size, glyph_rect, angle):
    w, h = layer_size
    cx, cy = w / 2.0, h / 2.0
    a = math.radians(angle)
    ca, sa = math.cos(a), math.sin(a)
    pts = []
    for (gx, gy) in [(glyph_rect[0], glyph_rect[1]),
                     (glyph_rect[2], glyph_rect[1]),
                     (glyph_rect[0], glyph_rect[3]),
                     (glyph_rect[2], glyph_rect[3])]:
        dx, dy = gx - cx, gy - cy
        pts.append((cx + dx * ca - dy * sa, cy + dx * sa + dy * ca))
    corners = [(0, 0), (w, 0), (0, h), (w, h)]
    allx, ally = [], []
    for (gx, gy) in corners:
        dx, dy = gx - cx, gy - cy
        allx.append(cx + dx * ca - dy * sa)
        ally.append(cy + dx * sa + dy * ca)
    minx, miny = min(allx), min(ally)
    xs = [p[0] - minx for p in pts]
    ys = [p[1] - miny for p in pts]
    return (min(xs), min(ys), max(xs), max(ys))


def draw_word(canvas, word, x, y, angle, font_size, font_path,
              stroke=0, heads=None):
    """Title word: white fill, NO black stroke, soft drop shadow.
    Raises if the glyph bbox touches any head box."""
    font = ImageFont.truetype(font_path, font_size)
    tmp = Image.new("RGBA", (10, 10), (0, 0, 0, 0))
    td = ImageDraw.Draw(tmp)
    bb = td.textbbox((0, 0), word, font=font, stroke_width=stroke)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    pad = 24
    layer = Image.new("RGBA", (tw + pad * 2, th + pad * 2), (0, 0, 0, 0))
    ox, oy = pad - bb[0], pad - bb[1]
    sh = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.text((ox + 6, oy + 8), word, font=font, fill=(0, 0, 0, 150),
            stroke_width=stroke, stroke_fill=(0, 0, 0, 150))
    sh = sh.filter(ImageFilter.GaussianBlur(7))
    layer.alpha_composite(sh)
    d = ImageDraw.Draw(layer)
    d.text((ox, oy), word, font=font, fill=WHITE + (255,),
           stroke_width=stroke, stroke_fill=WHITE + (255,))
    glyph_rect = (ox, oy, ox + tw, oy + th)
    layer = layer.rotate(angle, expand=True, resample=Image.BICUBIC)
    canvas.alpha_composite(layer, (x, y))
    gb = _rotated_glyph_bbox(layer.size, glyph_rect, angle)
    bbox = (x + gb[0], y + gb[1], x + gb[2], y + gb[3])
    print(f"  word '{word}' {font_size}pt at ({x},{y}) rot {angle} -> "
          f"glyph bbox {[round(v) for v in bbox]}")
    if heads:
        for i, hb in enumerate(heads):
            padded = (hb[0] - HEAD_PAD, hb[1] - HEAD_PAD,
                      hb[2] + HEAD_PAD, hb[3] + HEAD_PAD)
            if _intersects(bbox, padded):
                raise SystemExit(
                    f"ABORT: word '{word}' glyph bbox "
                    f"{[round(v) for v in bbox]} touches head H{i+1} "
                    f"{padded} — move it before saving.")
    return bbox


def heads_v19():
    """frame-0003 head boxes in v19 canvas coords."""
    px, py, pw, ph = FRAME_MAIN[1], FRAME_MAIN[2], FRAME_MAIN[3], FRAME_MAIN[4]
    sx, sy = pw / 1086.0, ph / 611.0
    out = []
    for (x0, y0, x1, y1) in HEADS_REF:
        out.append((round(px + x0 * sx), round(py + y0 * sy),
                    round(px + x1 * sx), round(py + y1 * sy)))
    return out


def build_v19():
    canvas = Image.new("RGBA", (W, H), (247, 241, 229, 255))
    # 1. frame-0003, biggest, anchor (no rotation)
    path, x, y, w, h, ang = FRAME_MAIN
    photo = prep_photo(path, w, h)
    print(f"  main {path}: {photo.size}")
    paste_card(canvas, photo, x, y, frame=14, angle=ang)
    # 2. HM5A1413, prominent, full frame
    path, x, y, w, h, ang = HM1413
    photo = prep_photo(path, w, h)
    print(f"  HM5A1413: {photo.size}")
    paste_card(canvas, photo, x, y, frame=12, angle=ang)
    # 3. speaker, full 3:2 frame — whole person + screen
    path, x, y, w, h, ang = SPEAKER
    photo = prep_photo(path, w, h)
    print(f"  speaker: {photo.size}")
    paste_card(canvas, photo, x, y, frame=12, angle=ang)
    # 4. cup photo, full portrait
    path, x, y, w, h, ang = CUP
    photo = prep_photo(path, w, h)
    print(f"  cup: {photo.size}")
    paste_card(canvas, photo, x, y, frame=12, angle=ang)
    # 5. scattered logo stickers (on top of the cream + photo corners)
    for (tile, cx, cy, size, ang) in STICKERS:
        paste_sticker(canvas, tile, cx, cy, size, ang)
    # 6. title, Caveat, no black outline
    heads = [(a, b, c, d) for (a, b, c, d) in heads_v19()]
    print(f"  heads v19 canvas: {heads}")
    for (word, x, y, ang, size) in SCATTER_V19:
        draw_word(canvas, word, x, y, ang, size, CAVEAT,
                  stroke=CAVEAT_STROKE, heads=heads)
    canvas.convert("RGB").save("v7-cover-v19.jpg", quality=92)
    print("Wrote v7-cover-v19.jpg 1920x1080 (sticker collage, "
          "no fake logo stickers)")


def prep_rect_zoom(path, w, h, crop_top, zoom=0.83):
    """v18 panel, zoomed OUT: crop a taller window (h/zoom) from the
    resized image, then scale down to the slot — people read smaller,
    more of the scene shows."""
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    ow, oh = im.size
    im = grade(im)
    nh = round(w * oh / ow)
    im = im.resize((w, nh), Image.LANCZOS)
    win_h = round(h / zoom)
    top = int(crop_top + (h - win_h) / 2)
    top = max(0, min(top, nh - win_h))
    crop = im.crop((0, top, w, top + win_h))
    crop = crop.resize((w, h), Image.LANCZOS)
    print(f"  {path}: {ow}x{oh} -> {w}x{nh}, zoom-out window "
          f"y {top}-{top + win_h} -> {w}x{h}")
    return crop


def build_v20():
    """v18 flat layout, audience panel zoomed out."""
    canvas = Image.new("RGBA", (W, H), (247, 241, 229, 255))
    panels = [
        ("photos/HM5A1478.JPG", 40, 40, 730, 487, None, False),
        ("cup-hand-logo.jpg", 40, 551, 730, 487, 235, False),
        ("frames-dense/DJI_20260719104432_0054_D/frame-0003.jpg",
         794, 40, 1086, 611, None, False),
    ]
    for (path, x, y, w, h, crop_top, _) in panels:
        panel = prep_photo(path, w, h, crop_top=crop_top)
        canvas.alpha_composite(panel.convert("RGBA"), (x, y))
        print(f"  panel pasted at ({x},{y}) {w}x{h}")
    aud = prep_rect_zoom("photos/HM5A1652.JPG", 1086, 365, 700, zoom=0.83)
    canvas.alpha_composite(aud.convert("RGBA"), (794, 675))
    print("  audience panel pasted at (794,675) 1086x365 (zoomed out)")
    for (word, x, y, ang, size) in SCATTER_V14:
        draw_word(canvas, word, x, y, ang, size, NOTO_BLACK,
                  stroke=0, heads=HEADS_V14)
    canvas.convert("RGB").save("v7-cover-v20.jpg", quality=92)
    print("Wrote v7-cover-v20.jpg 1920x1080 (v18 + shrunk audience)")


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)) or ".")
    print("== v19 sticker collage ==")
    build_v19()
    print("== v20 v18 shrink fix ==")
    build_v20()

    # Comparison: v14 vs v19 vs v20, 1 row x 3 cols.
    cells = [("v7-cover-v14.jpg", "v14 · 旧版 (白衣男生)"),
             ("v7-cover-v19.jpg", "v19 · 贴纸拼贴 (新)"),
             ("v7-cover-v20.jpg", "v20 · v18 观众缩小")]
    cw, ch, lab_h, gap = 620, 349, 34, 10
    cols = 3
    gw = cols * cw + (cols + 1) * gap
    gh = (ch + lab_h) + 2 * gap
    grid = Image.new("RGB", (gw, gh), (255, 255, 255))
    dd = ImageDraw.Draw(grid)
    labelfont = ImageFont.truetype(LABEL_FONT, 24, index=0)
    for i, (path, label) in enumerate(cells):
        x = gap + i * (cw + gap)
        im = Image.open(path).convert("RGB").resize((cw, ch), Image.LANCZOS)
        grid.paste(im, (x, gap))
        dd.text((x + 6, gap + ch + 4), label, font=labelfont,
                fill=(30, 30, 30))
    grid.save("v7-cover-compare-v14v19v20.jpg", quality=92)
    print(f"Wrote v7-cover-compare-v14v19v20.jpg {gw}x{gh}")


if __name__ == "__main__":
    main()
