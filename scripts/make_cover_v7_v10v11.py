"""Build v7 cover combos v10/v11 — FINAL revision (2026-11-16 09:08-09:10).

Changes in this revision (user, 2026-11-16):
  1. TITLE restyle (09:10, ref: "SOM's BANGKOK VLOG" thumbnail):
     big bold letters, FLOATING (strong drop shadow) and HOLLOW/
     OUTLINE (thick black outline around each letter). Replaces the
     Montserrat + bronze rule look. "Cursor Cafe" white fill +
     black outline; "Shanghai" pale-yellow fill + black outline;
     "2026.07.19" smaller, same outlined style. Font: DejaVu Sans
     Bold (heaviest rounded bold on the system; no Montserrat
     Black/ExtraBold available). No bronze rule anymore.
  2. CURSOR LOGO STICKER ON THE CUP (09:09): the Cursor Cafe logo
     made into a sticker and stuck on the coffee cup the woman with
     glasses holds in featured frame-0003. Logo source: the event
     banner in HM5A1901 (white cube + CURSOR on black). The cup is
     SMALL (~33px wide in the 1280px frame, ~28px on the cover)
     and her thumb crosses its middle, so only the CUBE icon fits
     legibly (the CURSOR text would be ~3px tall at this size).
     Cube kept WHITE (the cup liquid is dark brown — white reads,
     black would not). The cube sits on a BLACK rounded-square
     backing with a white die-cut outline + small drop shadow:
     a white cube + white outline alone merged into an unreadable
     white blob (first attempt). The cup is SMALL (~33px wide in
     the 1280px frame) and her thumb crosses its middle, so the
     sticker is 24px on the upper cup (lid) above the thumb — a
     small cute detail, as asked. Only the CUBE fits legibly (the
     CURSOR text would be ~3px tall at this size).

Layout: 1920x1080 cream #F7F1E5. Featured frame-0003 full-frame
(1080x608, NOT cut out, warm-graded, logo sticker on the cup).
Right column x=1144 w=736, three slots 736x322 at y=40/378/716:
top HM5A1900 sticker cutout, middle speaker RECTANGULAR wide shot
(cafe interior visible — NOT a cutout, per 09:08: wide shot showing
the cafe hall interior), bottom HM5A1413 sticker cutout.
  v10 middle: clip 0042 frame-0052 — green-cap woman, side profile,
      pointing at the phone-UI screen, LONG STRAIGHT BLACK HAIR.
  v11 middle: clip 0043 frame-0020 — Saraeal woman, front-facing,
      gesturing at her agents slide, dark straight hair to shoulders.
Title block below the featured photo (y~680): "Cursor Cafe" /
"Shanghai" / "2026.07.19", outlined + floating, no faces covered.
Outputs: v7-cover-v10.jpg, v7-cover-v11.jpg + comparison
v7-cover-compare-v8v10v11.jpg. Does NOT overwrite v2-v9.
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageEnhance, ImageFilter
import numpy as np

W, H = 1920, 1080
BG = (247, 241, 229)          # cream #F7F1E5
INK = (58, 44, 32)
BRONZE = (150, 125, 90)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
PALEYELLOW = (255, 243, 176)  # pale yellow emphasis

CUT = "cutouts"
COMBOS = {
    # (kind, path, brighten, color, slot)
    "v10": [("sticker", f"{CUT}/c2-HM5A1900.png", 1.00, 1.00, "top"),
            ("rect", "frames-dense/DJI_20260719084815_0042_D/frame-0052.jpg", 1.00, 1.00, "middle"),
            ("sticker", f"{CUT}/c2-HM5A1413.png", 1.18, 1.05, "bottom")],
    "v11": [("sticker", f"{CUT}/c2-HM5A1900.png", 1.00, 1.00, "top"),
            ("rect", "frames-dense/DJI_20260719091529_0043_D/frame-0020.jpg", 1.00, 1.00, "middle"),
            ("sticker", f"{CUT}/c2-HM5A1413.png", 1.18, 1.05, "bottom")],
}
FEATURED = "frames-dense/DJI_20260719104432_0054_D/frame-0003.jpg"
LOGO_SRC = "/tmp/logo-full.jpg"   # cube + CURSOR crop from HM5A1901
LOGO_OUT = "cutouts/logo-cursor-cube.png"

SLOTS = {
    "top": (1144, 40, 736, 322),
    "middle": (1144, 378, 736, 322),
    "bottom": (1144, 716, 736, 322),
}
# Cup in the featured photo (1080x608, built from the 1280x720 frame):
# original-frame cup bbox x 657-690, y 563-627 -> featured x 554-582,
# y 475-529; her THUMB crosses the cup at featured y ~489-515, so the
# only clean spot is the UPPER cup (lid) above the thumb.
# Sticker is a BLACK rounded square with the white cube on it (a white
# cube + white outline merged into an unreadable white blob in the
# first attempt — the black backing is what makes the white cube read).
LOGO_CX, LOGO_CY = 575, 484   # centre of the logo sticker, featured coords
LOGO_W = 24                    # sticker width on the featured photo


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


def extract_cube_logo():
    """Extract the white Cursor cube from the banner crop -> solid-white
    RGBA sticker art (transparent background). Returns the RGBA image."""
    src = Image.open(LOGO_SRC).convert("RGB")
    # Cube region inside the 850x300 crop (measured from the crop image).
    cube = src.crop((40, 40, 290, 270))
    g = np.asarray(cube.convert("L"), dtype=np.float32)
    # White/silver cube (bright, incl. grey facets) vs black banner.
    mask = np.clip((g - 70) / 60.0, 0, 1)
    mask = np.asarray(Image.fromarray((mask * 255).astype(np.uint8))
                      .filter(ImageFilter.GaussianBlur(0.6)), dtype=np.float32) / 255.0
    rgba = np.zeros((cube.size[1], cube.size[0], 4), dtype=np.uint8)
    rgba[..., 0] = 255
    rgba[..., 1] = 255
    rgba[..., 2] = 255
    rgba[..., 3] = (mask * 255).astype(np.uint8)
    out = Image.fromarray(rgba, "RGBA")
    out.save(LOGO_OUT)
    print(f"  logo cube extracted -> {LOGO_OUT} {out.size}")
    return out


def paste_logo_sticker(feat, logo):
    """Paste the cube logo as a tiny sticker on the cup in the featured
    photo (feat is 1080x608 RGB). The cube is WHITE, so it sits on a
    BLACK rounded-square backing (white cube + white outline alone
    merged into an unreadable white blob). White die-cut outline +
    small drop shadow around the black square."""
    cube = logo.copy()
    bbox = cube.split()[3].getbbox()
    cube = cube.crop(bbox)
    # Black rounded-square backing, LOGO_W wide; cube ~75% of it.
    S = LOGO_W
    backing = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    bd = ImageDraw.Draw(backing)
    bd.rounded_rectangle([0, 0, S - 1, S - 1], radius=6, fill=(20, 20, 20, 255))
    cw = round(S * 0.72)
    ch = round(cw * cube.size[1] / cube.size[0])
    cube = cube.resize((cw, ch), Image.LANCZOS)
    backing.alpha_composite(cube, ((S - cw) // 2, (S - ch) // 2))
    canvas = feat.convert("RGBA")
    px = LOGO_CX - S // 2
    py = LOGO_CY - S // 2
    alpha = backing.split()[3]
    # White die-cut outline (~2px at this scale).
    dil = alpha.filter(ImageFilter.MaxFilter(5))
    # Small drop shadow following the sticker shape.
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    sh = Image.new("RGBA", backing.size, (0, 0, 0, 0))
    sh.putalpha(dil.point(lambda v: int(v * 0.30)))
    shadow.paste(sh, (px + 2, py + 2), sh)
    shadow = shadow.filter(ImageFilter.GaussianBlur(2))
    canvas.alpha_composite(shadow)
    sticker = Image.new("RGBA", backing.size, (255, 255, 255, 255))
    sticker.putalpha(dil)
    canvas.alpha_composite(sticker, (px, py))
    canvas.alpha_composite(backing, (px, py))
    print(f"  logo sticker pasted at ({px},{py}) {S}x{S}")
    return canvas.convert("RGB")


def build_featured(logo):
    """frame-0003 full-frame, graded, 1080 wide, logo sticker on cup."""
    im = ImageOps.exif_transpose(Image.open(FEATURED))
    ow, oh = im.size
    h = round(1080 / (ow / oh))
    im = grade(im).resize((1080, h), Image.LANCZOS)
    print(f"  featured {FEATURED}: {ow}x{oh} -> {im.size}")
    return paste_logo_sticker(im, logo)


def prep_rect(path, max_w, max_h):
    """Full-frame wide shot: grade, resize to slot width, center-crop
    vertically to fill the slot (keeps the speaker, shows interior)."""
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    ow, oh = im.size
    im = grade(im)
    nw = max_w
    nh = round(max_w * oh / ow)
    im = im.resize((nw, nh), Image.LANCZOS)
    top = max(0, (nh - max_h) // 2)
    im = im.crop((0, top, nw, top + max_h))
    print(f"  {path}: {ow}x{oh} -> {im.size} (rect, cropped y {top}-{top + max_h})")
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
    dil = alpha
    for _ in range(3):
        dil = dil.filter(ImageFilter.MaxFilter(9))
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    sh_im = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sh_im.putalpha(dil.point(lambda v: int(v * 0.25)))
    shadow.paste(sh_im, (px + 6, py + 8), sh_im)
    shadow = shadow.filter(ImageFilter.GaussianBlur(10))
    canvas.alpha_composite(shadow)
    sticker = Image.new("RGBA", im.size, (255, 255, 255, 255))
    sticker.putalpha(dil)
    canvas.alpha_composite(sticker, (px, py))
    canvas.alpha_composite(im, (px, py))
    print(f"  sticker pasted at ({px},{py}) {im.size[0]}x{im.size[1]}")


def draw_outlined_floating(canvas, xy, text, font, fill, stroke_w,
                           shadow_dx=5, shadow_dy=7, shadow_blur=6,
                           shadow_alpha=115):
    """Draw text with a thick black outline and a strong drop shadow so
    the letters float. Shadow on its own layer, blurred, then the
    outlined text on top."""
    x, y = xy
    # Shadow layer: black text, offset, blurred.
    sh_layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    sh_d = ImageDraw.Draw(sh_layer)
    sh_d.text((x + shadow_dx, y + shadow_dy), text, font=font,
              fill=(0, 0, 0, shadow_alpha), stroke_width=stroke_w,
              stroke_fill=(0, 0, 0, shadow_alpha))
    sh_layer = sh_layer.filter(ImageFilter.GaussianBlur(shadow_blur))
    canvas.alpha_composite(sh_layer)
    # Main text: fill + thick black outline.
    d = ImageDraw.Draw(canvas)
    d.text((x, y), text, font=font, fill=fill + (255,),
           stroke_width=stroke_w, stroke_fill=BLACK + (255,))
    return d.textbbox((x, y), text, font=font,
                      stroke_width=stroke_w)


def draw_title(canvas):
    """Big bold outlined floating title below the featured photo.
    'Cursor Cafe' white + black outline; 'Shanghai' pale yellow +
    black outline; date smaller, same style. No bronze rule."""
    title_font = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 100)
    date_font = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
    tx = 40
    # Line 1: Cursor Cafe
    bb = draw_outlined_floating(canvas, (tx, 672), "Cursor Cafe",
                                title_font, WHITE, stroke_w=10)
    # Line 2: Shanghai
    bb2 = draw_outlined_floating(canvas, (tx, 800), "Shanghai",
                                 title_font, PALEYELLOW, stroke_w=10)
    # Date
    draw_outlined_floating(canvas, (tx + 4, 928), "2026.07.19",
                           date_font, WHITE, stroke_w=5,
                           shadow_dx=3, shadow_dy=4, shadow_blur=4)
    print(f"  title: 'Cursor Cafe' bbox {bb}, 'Shanghai' bbox {bb2}")


def build_combo(name, right_panels, logo):
    canvas = Image.new("RGBA", (W, H), BG + (255,))
    feat = build_featured(logo)
    canvas.alpha_composite(feat.convert("RGBA"), (40, 40))
    for (kind, path, brighten, color, slot_name) in right_panels:
        slot = SLOTS[slot_name]
        if kind == "rect":
            panel = prep_rect(path, *slot[2:])
            canvas.alpha_composite(panel.convert("RGBA"), (slot[0], slot[1]))
            print(f"  rect pasted at ({slot[0]},{slot[1]}) {panel.size}")
        else:
            panel = prep_cutout(path, *slot[2:], brighten=brighten, color=color)
            paste_sticker(canvas, panel, slot)
    draw_title(canvas)
    out = f"v7-cover-{name}.jpg"
    canvas.convert("RGB").save(out, quality=92)
    print(f"Wrote {out} {canvas.size}")


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)) or ".")
    logo = extract_cube_logo()
    for name, right_panels in COMBOS.items():
        print(f"== {name} ==")
        build_combo(name, right_panels, logo)

    # Comparison image: 1x3 row (v8, v10, v11).
    names = [("v7-cover-v8.jpg", "v8 (old title, cutout speaker)"),
             ("v7-cover-v10.jpg", "v10 wide speaker + new title + logo cup"),
             ("v7-cover-v11.jpg", "v11 wide speaker + new title + logo cup")]
    tw, th = 960, 540
    comp = Image.new("RGB", (tw * 3 + 60, th + 45), (255, 255, 255))
    dd = ImageDraw.Draw(comp)
    labelfont = ImageFont.truetype("fonts/Montserrat.ttf", 26)
    for i, (path, label) in enumerate(names):
        im = Image.open(path).convert("RGB").resize((tw, th), Image.LANCZOS)
        x = i * (tw + 30)
        comp.paste(im, (x, 0))
        dd.text((x + 8, th + 8), label, font=labelfont, fill=(30, 30, 30))
    comp.save("v7-cover-compare-v8v10v11.jpg", quality=92)
    print(f"Wrote v7-cover-compare-v8v10v11.jpg {comp.size}")


if __name__ == "__main__":
    main()
