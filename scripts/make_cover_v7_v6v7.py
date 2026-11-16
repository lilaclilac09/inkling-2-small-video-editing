"""Build v7 cover combos v6/v7 — v2 base + STICKER-BORDER cutouts.

Per Aileen 2026-11-16 08:50 (replying to the v2/v3/v4/v5 comparison):
  (go with V1 [the rectangular v2]; top-left featured NOT cut out, make it
   the main image; the bottom-right girls cutout is good; pick more cutout
   options to show; add cute sticker borders to cutouts; brighten dark ones.)

Layout (canvas 1920x1080, cream #F7F1E5) — v2 structure:
  - FEATURED frame-0003 FULL-FRAME (NOT cut out), warm-graded:
    x=40, y=40, w=1080, h=608 (16:9).
  - Two right panels = CUTOUTS with cute sticker borders:
    top slot (1144, 40, 736, 491), bottom slot (1144, 555, 736, 485).
  - Title block under the featured photo: "Cursor Cafe" / "Shanghai"
    (Montserrat 72pt) + bronze rule + "2026.07.19" (28pt, tracked).

Combos:
  v6: top HM5A1900 (banner + 2 girls — the cutout she liked)
      + bottom HM5A1923 (white-haired man speaking)
  v7: top HM5A1900 (banner + 2 girls)
      + bottom HM5A1413 (black-dress girl + group, NEW cutout)

Sticker border: white die-cut outline ~12px around the silhouette
(dilated alpha), soft drop shadow following the sticker shape.
Brightening (measured mean luminance of opaque pixels):
  HM5A1900 lum 74 — NOT brightened: the low mean is the black Cursor
    banner, the girls themselves are bright outdoor; lifting would
    blow out their white dresses.
  HM5A1923 lum 141 — no brightening needed.
  HM5A1413 lum 87 (indoor) — brightness x1.18 + color x1.05.

Cutouts reused from the v3/v4/v5 work (rembg full u2net, cleaned);
HM5A1413 cut fresh with cutout_one.py (800px, own process).
Outputs: v7-cover-v6.jpg, v7-cover-v7.jpg + comparison
v7-cover-compare-v2v6v7.jpg. Does NOT overwrite v2/v3/v4/v5.
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance, ImageFilter
import numpy as np

W, H = 1920, 1080
BG = (247, 241, 229)          # cream #F7F1E5
INK = (58, 44, 32)
TAUPE = (120, 100, 78)
BRONZE = (150, 125, 90)

CUT = "cutouts"
# (cutout path, brighten factor, color factor)
COMBOS = {
    "v6": [(f"{CUT}/c2-HM5A1900.png", 1.00, 1.00, "top"),
           (f"{CUT}/c2-HM5A1923.png", 1.00, 1.00, "bottom")],
    "v7": [(f"{CUT}/c2-HM5A1900.png", 1.00, 1.00, "top"),
           (f"{CUT}/c2-HM5A1413.png", 1.18, 1.05, "bottom")],
}
FEATURED = "frames-dense/DJI_20260719104432_0054_D/frame-0003.jpg"

TOP_SLOT = (1144, 40, 736, 491)
BOTTOM_SLOT = (1144, 555, 736, 485)


def grade(im):
    """Unified warm/vivid grade, copied from make_cover_v7.py."""
    im = im.convert("RGB")
    im = ImageEnhance.Color(im).enhance(1.15)
    im = ImageEnhance.Contrast(im).enhance(1.08)
    im = ImageEnhance.Brightness(im).enhance(1.05)
    r, g, b = im.split()
    r = r.point(lambda v: min(255, int(v * 1.04)))
    b = b.point(lambda v: int(v * 0.96))
    return Image.merge("RGB", (r, g, b))


def build_featured():
    """frame-0003 full-frame, graded, 1080 wide (16:9 -> h=608)."""
    im = ImageOps.exif_transpose(Image.open(FEATURED))
    ow, oh = im.size
    h = round(1080 / (ow / oh))
    im = grade(im).resize((1080, h), Image.LANCZOS)
    print(f"  featured {FEATURED}: {ow}x{oh} -> {im.size}")
    return im


def prep_cutout(path, max_w, max_h, brighten=1.0, color=1.0):
    """Trim transparent borders, brighten, scale to fit. Returns RGBA."""
    im = Image.open(path).convert("RGBA")
    alpha = im.split()[3]
    bbox = alpha.getbbox()
    if bbox:
        l, t, r, b = bbox
        l = max(0, l - 4); t = max(0, t - 4)
        r = min(im.size[0], r + 4); b = min(im.size[1], b + 4)
        im = im.crop((l, t, r, b))
    if brighten != 1.0 or color != 1.0:
        rgb = im.convert("RGB")
        if brighten != 1.0:
            rgb = ImageEnhance.Brightness(rgb).enhance(brighten)
        if color != 1.0:
            rgb = ImageEnhance.Color(rgb).enhance(color)
        a = im.split()[3]
        im = rgb.convert("RGBA")
        im.putalpha(a)
        print(f"  {path}: brightened x{brighten}, color x{color}")
    w, h = im.size
    scale = min(max_w / w, max_h / h)
    if scale != 1.0:
        im = im.resize((round(w * scale), round(h * scale)), Image.LANCZOS)
    print(f"  {path}: trimmed+fit -> {im.size} (slot {max_w}x{max_h})")
    return im


def paste_sticker(canvas, im, slot):
    """Paste a cutout as a die-cut sticker: white outline (~12px) around
    the silhouette + soft drop shadow following the sticker shape."""
    sx, sy, sw, sh = slot
    px = sx + (sw - im.size[0]) // 2
    py = sy + (sh - im.size[1]) // 2
    alpha = im.split()[3]
    # Dilate alpha ~12px for the white sticker border (MaxFilter(9) ~4px/pass).
    dil = alpha
    for _ in range(3):
        dil = dil.filter(ImageFilter.MaxFilter(9))
    # Shadow from the sticker silhouette: black 25%, offset (6,8), blur 10.
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    sh_im = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sh_im.putalpha(dil.point(lambda v: int(v * 0.25)))
    shadow.paste(sh_im, (px + 6, py + 8), sh_im)
    shadow = shadow.filter(ImageFilter.GaussianBlur(10))
    canvas.alpha_composite(shadow)
    # White sticker outline.
    sticker = Image.new("RGBA", im.size, (255, 255, 255, 255))
    sticker.putalpha(dil)
    canvas.alpha_composite(sticker, (px, py))
    # The cutout itself on top.
    canvas.alpha_composite(im, (px, py))
    print(f"  sticker pasted at ({px},{py}) {im.size[0]}x{im.size[1]}")


def draw_tracked(d, xy, text, font, fill, tracking=6):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill)
        x += font.getlength(ch) + tracking
    return x


def build_combo(name, right_panels):
    canvas = Image.new("RGBA", (W, H), BG + (255,))
    feat = build_featured()
    canvas.alpha_composite(feat.convert("RGBA"), (40, 40))
    for (path, brighten, color, slot_name) in right_panels:
        slot = TOP_SLOT if slot_name == "top" else BOTTOM_SLOT
        panel = prep_cutout(path, *slot[2:], brighten=brighten, color=color)
        paste_sticker(canvas, panel, slot)
    # Title block under the featured photo (same as v2).
    d = ImageDraw.Draw(canvas)
    title_font = ImageFont.truetype("fonts/Montserrat.ttf", 72)
    date_font = ImageFont.truetype("fonts/Montserrat.ttf", 28)
    tx, ty = 40, 680
    d.text((tx, ty), "Cursor Cafe", font=title_font, fill=INK)
    lh = title_font.getbbox("Cursor Cafe")[3] + 12
    d.text((tx, ty + lh), "Shanghai", font=title_font, fill=INK)
    lh2 = title_font.getbbox("Shanghai")[3] + 12
    rule_y = ty + lh + lh2 + 18
    d.line([(tx + 4, rule_y), (tx + 336, rule_y)], fill=BRONZE, width=2)
    draw_tracked(d, (tx + 4, rule_y + 20), "2026.07.19", date_font, TAUPE, tracking=6)
    out = f"v7-cover-{name}.jpg"
    canvas.convert("RGB").save(out, quality=92)
    print(f"Wrote {out} {canvas.size}")


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)) or ".")
    for name, right_panels in COMBOS.items():
        print(f"== {name} (v2 base + sticker cutouts) ==")
        build_combo(name, right_panels)

    # Comparison image: 1x3 row (v2 rectangular, v6, v7 sticker).
    names = [("v7-cover-preview-v2.jpg", "v2 — rectangular (1893 + 0042-f12)"),
             ("v7-cover-v6.jpg", "v6 sticker — 1900 + 1923"),
             ("v7-cover-v7.jpg", "v7 sticker — 1900 + 1413")]
    tw, th = 960, 540
    comp = Image.new("RGB", (tw * 3 + 60, th + 45), (255, 255, 255))
    dd = ImageDraw.Draw(comp)
    labelfont = ImageFont.truetype("fonts/Montserrat.ttf", 26)
    for i, (path, label) in enumerate(names):
        im = Image.open(path).convert("RGB").resize((tw, th), Image.LANCZOS)
        x = i * (tw + 30)
        comp.paste(im, (x, 0))
        dd.text((x + 8, th + 8), label, font=labelfont, fill=(30, 30, 30))
    comp.save("v7-cover-compare-v2v6v7.jpg", quality=92)
    print(f"Wrote v7-cover-compare-v2v6v7.jpg {comp.size}")


if __name__ == "__main__":
    main()
