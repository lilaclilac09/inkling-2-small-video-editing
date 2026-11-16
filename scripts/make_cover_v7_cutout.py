"""Build v7 cover combos v3/v4/v5 WITH SLIGHT CUTOUTS (v2 of the combos).

Per Aileen 2026-11-15 22:12: apply a SLIGHT cutout to
the cover photos. This supersedes the rectangular v3/v4/v5 built minutes
earlier (never shown to her) and the old "no cutouts" rule.

Cutout findings (rembg full u2net, feathered edges):
  CLEAN: frame-0003 (4 people), HM5A1923 (solo man speaker),
         HM5A1789 (solo man at laptop).
  CLEANED: HM5A1900 (right edge cropped to drop a partial 3rd person),
           0042-f12 (floating paper lantern painted out of the alpha).
  FAILED (model drops most people — unusable as cutouts): HM5A1478
  (big group, kept 1 of 9 people), HM5A1424 (7-person group, kept
  fragments). Per the task, swapped for photos that cut cleanly.
  The rectangular v3/v4 (with 1478/1424) are superseded; the build
  script make_cover_v7_v3v4v5.py can rebuild them if ever needed.

Combos (frame-0003 featured in all, cut out):
  v3: top HM5A1923 + bottom HM5A1789
  v4: top HM5A1900-clean + bottom 0042-f12-clean
  v5: top HM5A1789 + bottom HM5A1900-clean

Treatment: trim transparent borders, scale to fit the same slots,
centre in slot, subtle drop shadow (offset 6,8, blur 10, black ~25%
opacity) so the cutouts sit on the cream instead of floating flat.
Layout / title / fonts / cream #F7F1E5 unchanged from
make_cover_v7_preview_v2.py. Overwrites v7-cover-v3/4/5.jpg and
rebuilds the comparison image.
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter

W, H = 1920, 1080
BG = (247, 241, 229)          # cream #F7F1E5
INK = (58, 44, 32)
TAUPE = (120, 100, 78)
BRONZE = (150, 125, 90)

CUT = "cutouts"
COMBOS = {
    "v3": [(f"{CUT}/c2-HM5A1923.png", "top"),
           (f"{CUT}/c2-HM5A1789.png", "bottom")],
    "v4": [(f"{CUT}/c2-HM5A1900.png", "top"),
           (f"{CUT}/c2-0042-f12.png", "bottom")],
    "v5": [(f"{CUT}/c2-HM5A1789.png", "top"),
           (f"{CUT}/c2-HM5A1900.png", "bottom")],
}
FEATURED = f"{CUT}/c2-frame-0003.png"

# Slots: (x, y, max_w, max_h)
FEATURED_SLOT = (40, 40, 1080, 608)
TOP_SLOT = (1144, 40, 736, 491)
BOTTOM_SLOT = (1144, 555, 736, 485)


def prep_cutout(path, max_w, max_h):
    """Trim transparent borders, scale to fit (max_w, max_h), return RGBA."""
    im = Image.open(path).convert("RGBA")
    alpha = im.split()[3]
    bbox = alpha.getbbox()
    if bbox:
        # Trim where alpha is essentially transparent, with 4px padding.
        l, t, r, b = bbox
        l = max(0, l - 4); t = max(0, t - 4)
        r = min(im.size[0], r + 4); b = min(im.size[1], b + 4)
        im = im.crop((l, t, r, b))
    # Scale to fit (upscaling allowed: cutouts were made from 800px
    # downscales of 1280px frames / 6000px photos, so scaling up to the
    # slot stays at or below the original resolution).
    w, h = im.size
    scale = min(max_w / w, max_h / h)
    if scale != 1.0:
        im = im.resize((round(w * scale), round(h * scale)), Image.LANCZOS)
    print(f"  {path}: trimmed+fit -> {im.size} (slot {max_w}x{max_h})")
    return im


def paste_cutout(canvas, im, slot):
    """Paste a cutout centred in its slot, with a subtle drop shadow."""
    sx, sy, sw, sh = slot
    # Shadow: alpha silhouette, offset (6,8), blurred, black at ~25%.
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    sh_im = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sh_im.putalpha(im.split()[3].point(lambda v: int(v * 0.25)))
    px = sx + (sw - im.size[0]) // 2
    py = sy + (sh - im.size[1]) // 2
    shadow.paste(sh_im, (px + 6, py + 8), sh_im)
    shadow = shadow.filter(ImageFilter.GaussianBlur(10))
    canvas.alpha_composite(shadow)
    canvas.alpha_composite(im, (px, py))
    print(f"  pasted at ({px},{py}) {im.size[0]}x{im.size[1]}")


def draw_tracked(d, xy, text, font, fill, tracking=6):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill)
        x += font.getlength(ch) + tracking
    return x


def build_combo(name, right_panels):
    canvas = Image.new("RGBA", (W, H), BG + (255,))
    feat = prep_cutout(FEATURED, *FEATURED_SLOT[2:])
    paste_cutout(canvas, feat, FEATURED_SLOT)
    for (path, slot_name) in right_panels:
        slot = TOP_SLOT if slot_name == "top" else BOTTOM_SLOT
        panel = prep_cutout(path, *slot[2:])
        paste_cutout(canvas, panel, slot)
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
        print(f"== {name} (cutout) ==")
        build_combo(name, right_panels)

    # Comparison image: 2x2 grid (v2 rectangular, v3, v4, v5 cutout).
    names = [("v7-cover-preview-v2.jpg", "v2 — rectangular (1893 + 0042-f12)"),
             ("v7-cover-v3.jpg", "v3 cutout — 1923 + 1789"),
             ("v7-cover-v4.jpg", "v4 cutout — 1900 + 0042-f12"),
             ("v7-cover-v5.jpg", "v5 cutout — 1789 + 1900")]
    tw, th = 960, 540
    comp = Image.new("RGB", (tw * 2 + 30, th * 2 + 90), (255, 255, 255))
    dd = ImageDraw.Draw(comp)
    labelfont = ImageFont.truetype("fonts/Montserrat.ttf", 26)
    for i, (path, label) in enumerate(names):
        im = Image.open(path).convert("RGB").resize((tw, th), Image.LANCZOS)
        x = (i % 2) * (tw + 30)
        y = (i // 2) * (th + 45)
        comp.paste(im, (x, y))
        dd.text((x + 8, y + th + 8), label, font=labelfont, fill=(30, 30, 30))
    comp.save("v7-cover-compare-v2v3v4v5.jpg", quality=92)
    print(f"Wrote v7-cover-compare-v2v3v4v5.jpg {comp.size}")


if __name__ == "__main__":
    main()
