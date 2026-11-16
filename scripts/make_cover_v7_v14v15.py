"""Build v7 covers v14-v18 — speaker swap + real cup photo, new title style.

Base = v13 layout (1920x1080, cream #F7F1E5):
  Left column  x=40 w=730:  HM5A1478 (40,40) 730x487
                           CUP PHOTO (40,551) 730x487  [replaces HM5A1413]
  Right column x=794 w=1086: frame-0003 (794,40) 1086x611 (visual center)
                           SPEAKER (794,675) 1086x365 (varies per version)

User rules applied (2026-11-16 09:34-09:38):
  * Speaker panel: one of the men she picked (v14/v15) + more combos
    (v16/v17/v18). Rectangular full-frame, warm grade.
  * LOGO: where there's a person, NO fake logo sticker on a cup.
    The cup photo (cup-hand-logo.jpg, IMG_7918) carries the REAL
    printed white Cursor cube on the cup — no sticker needed. All
    other panels have people in them, so NO fake stickers at all
    in v14-v18. (v13's 6 stickers are all removed.)
  * TITLE: NO black outline. Bigger + bolder WHITE text (Noto Sans
    Black, weight 900 — the heaviest on the system, heavier than
    DejaVu Bold). Soft drop shadow kept so it floats. Every word
    placed on a darker patch of the photo so white reads clearly.
  * TITLE must NOT cover anyone's HEAD. Head boxes (panel coords,
    frame-0003, measured from the graded panel) are checked
    programmatically before saving; any overlap aborts that version.

Head boxes, frame-0003 panel coords (1086x611), padded 10px:
  H1 man left (glasses, navy polo):   (195, 130, 345, 310)
  H2 woman centre (glasses, white):   (475, 275, 605, 440)
  H3 man white behind (white tee):     (625, 285, 715, 420)
  H4 girl right (black top, ponytail): (720, 150, 895, 345)
Canvas coords = panel + (794, 40).

Speaker sources + vertical crop (slot 1086x365, resized width 1086):
  v14 white-shirt man  speaker-white-shirt-man.jpg  crop_top=30
      (cream shirt, glasses, smiling; head + screen edge in frame)
  v15 glasses man      speaker-blue-shirt-man.jpg   crop_top=100
      (dark blue shirt, big smile; head + laptop top + screen in frame)
  v16 duck-shirt man   speaker-duck-shirt-man.jpg   crop_top=70
      (white Donald Duck tee, holds a real cup; head + cup top in frame)
  v17 HM5A1710 man     photos/HM5A1710.JPG          crop_top=110
      (CORRECTED 2026-11-16: NOT the woman with long black hair —
      that ID was a misattributed read. Correctly oriented (EXIF 8)
      it is a MAN, dark hair + glasses, cream t-shirt + grey pants,
      standing by the shelves holding a tablet, laptop in foreground.
      A standing presenter-type shot; portrait 4000x6000.)
  v18 HM5A1652 audience photos/HM5A1652.JPG          crop_top=500
      (CORRECTED 2026-11-16: NOT the white-polo + black-cap speaker —
      that ID was a misattributed read. Correctly oriented (EXIF 8)
      it is an AUDIENCE scene, portrait 4000x6000: people seated at
      tables with laptops/drinks, green-polo man with sunglasses
      left, white-t-shirt man cut off at right edge. Built as an
      audience-energy variant in the slot, NOT labelled a speaker.)

Cup photo panel: cup-hand-logo.jpg is portrait 1536x2048. Resized to
730 wide -> 973 tall; crop_top=235 keeps lid (y~271), real logo
(y~499-589) and cup bottom (y~727) inside the 487px slot; the hand
is cut at the bottom edge (acceptable — the cup + logo are intact).

Outputs: v7-cover-v14.jpg ... v7-cover-v18.jpg + comparison grid
v7-cover-compare-v14v15v16v17v18.jpg (2 rows x 3 cols, v13 as
reference in the last cell). Does NOT overwrite v2-v13.
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance, ImageFilter

W, H = 1920, 1080
BG = (247, 241, 229)          # cream #F7F1E5
WHITE = (255, 255, 255)

# frame-0003 head boxes, CANVAS coords (panel origin 794,40).
HEADS = [
    (989, 170, 1139, 350),    # H1 man left
    (1269, 315, 1399, 480),   # H2 woman centre
    (1419, 325, 1509, 460),   # H3 man white behind
    (1514, 190, 1689, 385),   # H4 girl right
]
HEAD_PAD = 8

# Scattered title, NEW style: Noto Sans Black, ALL WHITE, NO stroke,
# bigger than v13 (92/92/78/38 -> 120/120/100/48), stronger shadow.
# (word, x, y, angle_deg, font_size) — canvas coords, top-left of the
# unrotated tile. Positions chosen on dark patches, clear of heads.
SCATTER = [
    ("Cursor", 810, 24, -4, 120),
    ("Cafe", 1504, 20, 6, 120),
    ("Shanghai", 814, 510, -5, 100),
    ("2026.07.19", 1590, 580, 4, 48),
]
TITLE_FONT = "/usr/share/fonts/truetype/noto/NotoSans-Black.ttf"
LABEL_FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"

PANEL_FRAME = "frames-dense/DJI_20260719104432_0054_D/frame-0003.jpg"
PANEL_GROUP = "photos/HM5A1478.JPG"
PANEL_CUP = "cup-hand-logo.jpg"

VARIANTS = [
    ("v14", "speaker-white-shirt-man.jpg", 30, "v14 · 白衣男生", True),
    ("v15", "speaker-blue-shirt-man.jpg", 100, "v15 · 眼镜男生", True),
    ("v16", "speaker-duck-shirt-man.jpg", 70, "v16 · 唐老鸭T恤男生", True),
    ("v17", "photos/HM5A1710.JPG", 180, "v17 · HM5A1710 男生 (白T恤+平板)", True),
    ("v18", "photos/HM5A1652.JPG", 700, "v18 · HM5A1652 观众席 (非演讲者)", True),
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


def prep_rect(path, w, h, crop_top=None, transpose=True):
    """Full-frame shot: grade, resize to slot width, crop vertically.
    EXIF orientation is applied (transpose=True) — HM5A1710/HM5A1652
    carry orientation 8 and the tag is CORRECT: their stored pixels
    are sideways, transposing gives the upright portrait image.
    (An earlier no-transpose attempt proved this: raw pixels show
    the person lying sideways.)"""
    im = Image.open(path)
    if transpose:
        im = ImageOps.exif_transpose(im)
    im = im.convert("RGB")
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


def _intersects(a, b):
    return not (a[2] <= b[0] or a[0] >= b[2] or a[3] <= b[1] or a[1] >= b[3])


def _rotated_glyph_bbox(layer_size, glyph_rect, angle):
    """Bounding box of `glyph_rect` (in layer coords) after PIL
    rotate(angle, expand=True). PIL rotates counter-clockwise around
    the layer centre; the expanded canvas is then shifted so its
    minimum x/y is 0."""
    import math
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
    # PIL's expand canvas: size = bbox of the rotated full layer.
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


def draw_scattered_word(canvas, word, x, y, angle, font_size):
    """One title word, NEW style: Noto Sans Black, white fill, NO
    black stroke, soft drop shadow. The head check uses the GLYPH
    bbox (not the transparent tile) so padding/shadow don't count
    as covering a head; raises if glyphs touch any head box."""
    font = ImageFont.truetype(TITLE_FONT, font_size)
    tmp = Image.new("RGBA", (10, 10), (0, 0, 0, 0))
    td = ImageDraw.Draw(tmp)
    bb = td.textbbox((0, 0), word, font=font)
    tw = bb[2] - bb[0]
    th = bb[3] - bb[1]
    pad = 22
    layer = Image.new("RGBA", (tw + pad * 2, th + pad * 2), (0, 0, 0, 0))
    ox, oy = pad - bb[0], pad - bb[1]
    # Drop shadow (offset, blurred, stronger than v13 so white pops
    # on mid-tone green without an outline).
    sh = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.text((ox + 6, oy + 8), word, font=font, fill=(0, 0, 0, 150))
    sh = sh.filter(ImageFilter.GaussianBlur(7))
    layer.alpha_composite(sh)
    d = ImageDraw.Draw(layer)
    d.text((ox, oy), word, font=font, fill=WHITE + (255,))
    glyph_rect = (ox, oy, ox + tw, oy + th)
    layer = layer.rotate(angle, expand=True, resample=Image.BICUBIC)
    canvas.alpha_composite(layer, (x, y))
    gb = _rotated_glyph_bbox(layer.size, glyph_rect, angle)
    bbox = (x + gb[0], y + gb[1], x + gb[2], y + gb[3])
    print(f"  word '{word}' {font_size}pt at ({x},{y}) rot {angle} -> "
          f"glyph bbox {[round(v) for v in bbox]}")
    for i, hb in enumerate(HEADS):
        padded = (hb[0] - HEAD_PAD, hb[1] - HEAD_PAD,
                  hb[2] + HEAD_PAD, hb[3] + HEAD_PAD)
        if _intersects(bbox, padded):
            raise SystemExit(
                f"ABORT: word '{word}' glyph bbox "
                f"{[round(v) for v in bbox]} touches head H{i+1} "
                f"{padded} — move it before saving.")
    return bbox


def build_cover(speaker_path, speaker_crop, out_name, transpose=True):
    canvas = Image.new("RGBA", (W, H), (247, 241, 229, 255))
    panels = [
        (PANEL_GROUP, 40, 40, 730, 487, None, True),
        (PANEL_CUP, 40, 551, 730, 487, 235, True),
        (PANEL_FRAME, 794, 40, 1086, 611, None, True),
        (speaker_path, 794, 675, 1086, 365, speaker_crop, transpose),
    ]
    for (path, x, y, w, h, crop_top, tr) in panels:
        panel = prep_rect(path, w, h, crop_top=crop_top, transpose=tr)
        canvas.alpha_composite(panel.convert("RGBA"), (x, y))
        print(f"  panel pasted at ({x},{y}) {w}x{h}")
    for (word, x, y, angle, size) in SCATTER:
        draw_scattered_word(canvas, word, x, y, angle, size)
    canvas.convert("RGB").save(out_name, quality=92)
    print(f"Wrote {out_name} 1920x1080 (no fake logo stickers)")


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)) or ".")
    built = []
    for (ver, spath, crop, label, tr) in VARIANTS:
        print(f"== {ver} speaker={spath} crop_top={crop} transpose={tr} ==")
        out = f"v7-cover-{ver}.jpg"
        build_cover(spath, crop, out, transpose=tr)
        built.append((out, label))

    # Comparison grid 2 rows x 3 cols: v14-v18 + v13 reference.
    cells = built + [("v7-cover-v13.jpg", "v13 · 对照 (旧版，有黑边+假贴纸)")]
    cw, ch, lab_h, gap = 620, 349, 34, 10
    cols, rows = 3, 2
    gw = cols * cw + (cols + 1) * gap
    gh = rows * (ch + lab_h) + (rows + 1) * gap
    grid = Image.new("RGB", (gw, gh), (255, 255, 255))
    dd = ImageDraw.Draw(grid)
    labelfont = ImageFont.truetype(LABEL_FONT, 24, index=0)
    for i, (path, label) in enumerate(cells):
        r, c = divmod(i, cols)
        x = gap + c * (cw + gap)
        y = gap + r * (ch + lab_h + gap)
        im = Image.open(path).convert("RGB").resize((cw, ch), Image.LANCZOS)
        grid.paste(im, (x, y))
        dd.text((x + 6, y + ch + 4), label, font=labelfont,
                fill=(30, 30, 30))
    grid.save("v7-cover-compare-v14v15v16v17v18.jpg", quality=92)
    print("Wrote v7-cover-compare-v14v15v16v17v18.jpg "
          f"{gw}x{gh} (2x3, v14-v18 + v13 ref)")


if __name__ == "__main__":
    main()
