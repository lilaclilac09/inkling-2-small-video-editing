"""Build v7 cover v25 — v24 with three user fixes (2026-11-16 12:20-12:21,
replying to v24; she said v24 is "还不错" / pretty good):
1. Main image (frame-0003): NO drop shadow ("主图不要有投影").
2. Bottom-left photo (HM5A1413): the man in white clothes on the left —
   do NOT crop the table ("左边白色衣服的不要裁掉桌子"). The photo is
   3:2 and the v24 slot was exactly 3:2, so the full frame was shown,
   but the table sits on the photo's very bottom edge and the 2-degree
   tilt pushed the left (table) side down, so it read as cut off.
   Fix: angle 0 (flat) + a TALLER slot with a "contain" fit, so the
   whole photo sits inside with white margin above and below — the
   table now has clear white space under it and reads as fully visible.
3. Chinese flag: use it ONCE only ("用这个，用一次"). The four
   scattered extra flags are removed; only the one after "shanghai"
   in the title remains.

Everything else kept from v24 (title "cursor cafe shanghai" one line,
main centred on top, top-left speaker stickers brightened/enlarged,
HM5A1413, white-shirt speaker, cup photo, date 2026.07.19, logo
stickers, HM5A1478 out, no fake logos).

Output: v7-cover-v25.jpg + v7-cover-compare-v24v25.jpg.
Does NOT overwrite v2-v24.
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
# (1086x611). Rescaled in code to the v24 placement.
HEADS_REF = [
    (195, 130, 345, 310),    # H1 man left
    (475, 275, 605, 440),    # H2 woman centre
    (625, 285, 715, 420),    # H3 man white behind
    (720, 150, 895, 345),    # H4 girl right
]
HEAD_PAD = 8

# ---- v24 geometry ----
# Main CENTERED horizontally (photo x 410 -> centre 960), top y 55
# (same as v23), drawn LAST (on top of all photo layers).
FRAME_MAIN = ("frames-dense/DJI_20260719104432_0054_D/frame-0003.jpg",
              410, 55, 1100, 619, 0)
# v25: HM1413 slot is TALLER (440 vs 413) and FLAT (angle 0) so the
# table has white margin under it; the photo is fitted with
# "contain" (whole frame, letterboxed on white) instead of "cover".
HM1413 = ("photos/HM5A1413.JPG", 60, 586, 620, 440, 0)
SPEAKER = ("speaker-white-shirt-man.jpg", 1160, 600, 680, 453, -1.5)
CUP = ("cup-hand-logo.jpg", 800, 672, 270, 360, -3)

# Top-left speaker stickers (die-cut). Blue man wide across the
# top of the left column; duck man bottom-left (portrait);
# green-cap woman bottom-right, BRIGHTENED + ENLARGED (v23: 150).
# (path, centre x, bottom y, width px, angle deg, brighten)
PERSON_STICKERS = [
    ("cutouts/blue-shirt-man-trim.png", 205, 230, 260, -3, 1.0),
    ("cutouts/duck-shirt-man-trim.png", 105, 470, 160, -4, 1.0),
    ("cutouts/green-cap-woman-f11-clean.png", 285, 590, 175, -3, 1.18),
]

# Logo stickers: hex + pill moved to the right margin (the men
# take the left column); white/black squares stay as v23.
# (tile, center x, center y, max-size px, angle deg)
STICKERS = [
    ("cutouts/sticker-hex-black-large.png", 1600, 100, 110, -8),
    ("cutouts/sticker-pill-cursor.png", 1700, 420, 280, -3),
    ("cutouts/sticker-square-white-large.png", 1750, 230, 120, 5),
    ("cutouts/sticker-square-black-small.png", 1852, 88, 85, 6),
]

# Title: ONE line, Caveat 140pt (measured ~1008px wide), centred
# on the main (centre x 960), top y 28. Flag drawn right after.
TITLE = "cursor cafe shanghai"
TITLE_SIZE = 140
TITLE_Y = 28
TITLE_CENTRE_X = 960
# Date: same relative spot on the main as v23 (photo coords
# (80,510) -> canvas (490,565)).
DATE = ("2026.07.19", 490, 565, 4, 54)
CAVEAT_STROKE = 3

# v25: ONE flag only — the one next to the title. The four scattered
# extra flags are REMOVED per the user ("用这个，用一次").
TITLE_FLAG_W = 55


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


def prep_photo(path, w, h, crop_top=None, fit="cover"):
    """Grade + resize to slot width, crop vertically to fill
    (cover), or fit the WHOLE frame inside the slot letterboxed on
    white (contain) — contain is used for HM5A1413 in v25 so the
    table at the photo's bottom edge gets white margin under it."""
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    ow, oh = im.size
    im = grade(im)
    if fit == "contain":
        scale = min(w / ow, h / oh)
        nw, nh = max(1, round(ow * scale)), max(1, round(oh * scale))
        im = im.resize((nw, nh), Image.LANCZOS)
        canvas = Image.new("RGB", (w, h), WHITE)
        canvas.paste(im, ((w - nw) // 2, (h - nh) // 2))
        return canvas
    nh = round(w * oh / ow)
    im = im.resize((w, nh), Image.LANCZOS)
    if nh <= h:
        return im
    top = crop_top if crop_top is not None else max(0, (nh - h) // 2)
    return im.crop((0, top, w, top + h))


def framed_card(photo, frame=14, angle=0, radius=10):
    """White-framed card with soft drop shadow."""
    w, h = photo.size
    card = Image.new("RGBA", (w + frame * 2, h + frame * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle([0, 0, card.size[0] - 1, card.size[1] - 1],
                        radius=radius, fill=(255, 255, 255, 255))
    card.alpha_composite(photo.convert("RGBA"), (frame, frame))
    if angle:
        card = card.rotate(angle, expand=True, resample=Image.BICUBIC)
    alpha = card.split()[3]
    sh = Image.new("RGBA", card.size, (0, 0, 0, 0))
    sh.putalpha(alpha.point(lambda v: int(v * 0.32)))
    sh = sh.filter(ImageFilter.GaussianBlur(9))
    return card, sh


def paste_card(canvas, photo, x, y, frame=14, angle=0, shadow=True):
    card, sh = framed_card(photo, frame=frame, angle=angle)
    cx, cy = x + photo.size[0] // 2, y + photo.size[1] // 2
    px, py = cx - card.size[0] // 2, cy - card.size[1] // 2
    if shadow:
        canvas.alpha_composite(sh, (px + 8, py + 10))
    canvas.alpha_composite(card, (px, py))
    print(f"  card {photo.size} at centre ({cx},{cy}) rot {angle}deg "
          f"shadow={shadow} -> tile {card.size}")
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


def heads_v24():
    """frame-0003 head boxes in v24 canvas coords."""
    px, py, pw, ph = FRAME_MAIN[1], FRAME_MAIN[2], FRAME_MAIN[3], FRAME_MAIN[4]
    sx, sy = pw / 1086.0, ph / 611.0
    out = []
    for (x0, y0, x1, y1) in HEADS_REF:
        out.append((round(px + x0 * sx), round(py + y0 * sy),
                    round(px + x1 * sx), round(py + y1 * sy)))
    return out


def paste_cutout(canvas, path, cx, bottom, width, angle,
                 outline=12, brighten=1.0):
    """Person cutout as a die-cut sticker: white outline (dilated
    alpha) + soft drop shadow, pasted so its bottom sits at `bottom`
    and its horizontal centre at `cx`. `brighten` lifts a dark
    cutout (green-cap woman)."""
    cut = Image.open(path).convert("RGBA")
    if brighten != 1.0:
        cut = ImageEnhance.Brightness(cut).enhance(brighten)
        cut = ImageEnhance.Color(cut).enhance(1.10)
    scale = width / cut.size[0]
    cut = cut.resize((width, max(1, round(cut.size[1] * scale))),
                     Image.LANCZOS)
    alpha = cut.split()[3]
    dil = alpha.filter(ImageFilter.MaxFilter(outline * 2 + 1))
    pad = outline + 6
    tile = Image.new("RGBA", (cut.size[0] + pad * 2,
                              cut.size[1] + pad * 2), (0, 0, 0, 0))
    sh = Image.new("RGBA", tile.size, (0, 0, 0, 0))
    sh_im = Image.new("RGBA", dil.size, (0, 0, 0, 0))
    sh_im.putalpha(dil.point(lambda v: int(v * 0.30)))
    sh.alpha_composite(sh_im, (pad, pad))
    sh = sh.filter(ImageFilter.GaussianBlur(5))
    tile.alpha_composite(sh, (4, 5))
    outl = Image.new("RGBA", dil.size, (255, 255, 255, 255))
    outl.putalpha(dil)
    tile.alpha_composite(outl, (pad, pad))
    tile.alpha_composite(cut, (pad, pad))
    if angle:
        tile = tile.rotate(angle, expand=True, resample=Image.BICUBIC)
    px = cx - tile.size[0] // 2
    py = bottom - tile.size[1] + 4
    canvas.alpha_composite(tile, (px, py))
    print(f"  cutout {os.path.basename(path)} {cut.size} at centre "
          f"x {cx}, bottom {bottom} rot {angle}deg brighten "
          f"{brighten} -> tile {tile.size} at ({px},{py})")
    return (px, py, px + tile.size[0], py + tile.size[1])


def _star_points(cx, cy, r_outer, r_inner, rotation=-90):
    pts = []
    for i in range(10):
        a = math.radians(rotation + i * 36)
        r = r_outer if i % 2 == 0 else r_inner
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def draw_china_flag(canvas, x, y, w):
    """Small Chinese flag, drawn (PIL cannot render colour emoji
    reliably): red field, one large yellow star + four small stars
    in an arc. Returns the flag's bbox."""
    h = round(w * 2 / 3)
    flag = Image.new("RGBA", (w, h), (222, 41, 16, 255))  # #DE2910
    d = ImageDraw.Draw(flag)
    yellow = (255, 222, 0, 255)
    # large star: centre (0.18w, 0.28h), outer r 0.28h
    lx, ly, lr = w * 0.18, h * 0.28, h * 0.28
    d.polygon(_star_points(lx, ly, lr, lr * 0.382), fill=yellow)
    # four small stars, one point facing the large star's centre
    small = [
        (w * 0.40, h * 0.12, h * 0.10),
        (w * 0.50, h * 0.24, h * 0.10),
        (w * 0.50, h * 0.40, h * 0.10),
        (w * 0.40, h * 0.52, h * 0.10),
    ]
    for (sx, sy, sr) in small:
        ang = math.degrees(math.atan2(ly - sy, lx - sx)) - 90
        d.polygon(_star_points(sx, sy, sr, sr * 0.382,
                               rotation=ang), fill=yellow)
    # thin white edge + soft shadow so it reads as a sticker
    edge = Image.new("RGBA", (w + 4, h + 4), (0, 0, 0, 0))
    ed = ImageDraw.Draw(edge)
    ed.rectangle([0, 0, w + 3, h + 3], outline=(255, 255, 255, 255),
                 width=2)
    sh = Image.new("RGBA", (w + 8, h + 8), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle([4, 4, w + 4, h + 4],
                                 fill=(0, 0, 0, 90))
    sh = sh.filter(ImageFilter.GaussianBlur(3))
    canvas.alpha_composite(sh, (x - 2, y - 1))
    canvas.alpha_composite(flag, (x, y))
    canvas.alpha_composite(edge, (x - 2, y - 2))
    print(f"  flag {w}x{h} at ({x},{y})")
    return (x, y, x + w, y + h)


def build_v25():
    canvas = Image.new("RGBA", (W, H), (247, 241, 229, 255))
    # 1-3. bottom row (same as v24) — drawn FIRST, main goes on top.
    # HM1413 uses the "contain" fit in its taller slot so the table
    # gets white margin under it; the others keep the cover fit.
    for (path, x, y, w, h, ang) in [HM1413, SPEAKER, CUP]:
        fit = "contain" if path == HM1413[0] else "cover"
        photo = prep_photo(path, w, h, fit=fit)
        print(f"  {os.path.basename(path)}: {photo.size} fit={fit}")
        paste_card(canvas, photo, x, y, frame=12, angle=ang)
    # 4. logo stickers (hex + pill moved to the right margin)
    for (tile, cx, cy, size, ang) in STICKERS:
        paste_sticker(canvas, tile, cx, cy, size, ang)
    # 5. top-left speaker stickers (die-cut)
    for (path, cx, bottom, width, ang, br) in PERSON_STICKERS:
        paste_cutout(canvas, path, cx, bottom, width, ang,
                     brighten=br)
    # 6. MAIN, centred horizontally, drawn LAST (on top of all
    #    photo layers) — v25: NO drop shadow.
    path, x, y, w, h, ang = FRAME_MAIN
    photo = prep_photo(path, w, h)
    print(f"  main {path}: {photo.size}")
    main_box = paste_card(canvas, photo, x, y, frame=14, angle=ang,
                          shadow=False)
    print(f"  main card box: {main_box} (centre "
          f"{(main_box[0] + main_box[2]) // 2},"
          f"{(main_box[1] + main_box[3]) // 2})")
    # 7. title ONE LINE + the ONE flag, then date. No scattered flags.
    heads = heads_v24()
    print(f"  heads v24 canvas: {heads}")
    font = ImageFont.truetype(CAVEAT, TITLE_SIZE)
    tmp = Image.new("RGBA", (10, 10), (0, 0, 0, 0))
    bb = ImageDraw.Draw(tmp).textbbox(
        (0, 0), TITLE, font=font, stroke_width=CAVEAT_STROKE)
    tw = bb[2] - bb[0]
    group_w = tw + 15 + TITLE_FLAG_W
    title_x = TITLE_CENTRE_X - group_w // 2
    bbox = draw_word(canvas, TITLE, title_x, TITLE_Y, 0, TITLE_SIZE,
                     CAVEAT, stroke=CAVEAT_STROKE, heads=heads)
    # flag right after the title, vertically centred on the text
    fy = int((bbox[1] + bbox[3]) / 2 - (TITLE_FLAG_W * 2 // 3) / 2)
    draw_china_flag(canvas, int(bbox[2]) + 15, fy, TITLE_FLAG_W)
    # date, same relative spot on the main as v23
    d_word, d_x, d_y, d_ang, d_size = DATE
    draw_word(canvas, d_word, d_x, d_y, d_ang, d_size, CAVEAT,
              stroke=CAVEAT_STROKE, heads=heads)
    canvas.convert("RGB").save("v7-cover-v25.jpg", quality=92)
    print("Wrote v7-cover-v25.jpg 1920x1080 (v24 + no main shadow, "
          "HM1413 table fully visible, one flag only)")


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)) or ".")
    print("== v25 (v24 + no main shadow, HM1413 table visible, "
          "one flag only) ==")
    build_v25()

    # Comparison: v24 vs v25 side by side.
    cells = [("v7-cover-v24.jpg", "v24"),
             ("v7-cover-v25.jpg", "v25 · 主图无投影, 左下桌子完整, 只留一面国旗 (新)")]
    cw, ch, lab_h, gap = 940, 529, 34, 10
    cols = 2
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
    grid.save("v7-cover-compare-v24v25.jpg", quality=92)
    print(f"Wrote v7-cover-compare-v24v25.jpg {gw}x{gh}")


if __name__ == "__main__":
    main()
