"""Extract Cursor logo stickers from the production sheet
(logo-cursor-stickers.jpg, 1200x682) as transparent RGBA tiles with a
fat white die-cut border baked in.

Sheet layout (approx, from viewing it):
  top row:    large white rounded-square, large black rounded-square,
              black hexagon
  bottom row: small white rounded-square, small black rounded-square,
              small black hexagon, horizontal white pill "cube + CURSOR"
Red dimension lines/numbers surround each sticker; crops stay inside
them. Masks are built by luminance threshold + red-exclusion, holes
filled, largest component kept; the fat white border is the mask
dilated ~10px. Saved to cutouts/sticker-*.png.
"""
import os
import numpy as np
from PIL import Image
from scipy import ndimage

os.chdir(os.path.dirname(os.path.abspath(__file__)) or ".")

SHEET = "logo-cursor-stickers.jpg"

# (name, crop box (x0,y0,x1,y1), kind) — kind: 'white' | 'black'
STICKERS = [
    ("hex-black-large",   (788, 100, 1005, 345), "black"),
    ("square-black-large", (413, 90, 667, 345), "black"),
    ("square-white-large", (75, 90, 330, 345), "white"),
    ("pill-cursor",        (744, 460, 1044, 568), "white"),
    ("square-black-small", (294, 443, 434, 585), "black"),
    ("square-white-small", (70, 443, 210, 585), "white"),
    ("hex-black-small",    (526, 446, 647, 582), "black"),
]


def extract(name, box, kind):
    im = Image.open(SHEET).convert("RGB").crop(box)
    a = np.asarray(im).astype(np.int16)
    lum = a.mean(axis=2)
    # red dimension lines / numbers: strong R, weak G/B
    red = (a[:, :, 0] > 140) & (a[:, :, 1] < 110) & (a[:, :, 2] < 110)
    if kind == "white":
        mask = (lum > 222) & (~red)
    else:
        mask = (lum < 115) & (~red)
    # keep largest connected component (the sticker body)
    lab, n = ndimage.label(mask)
    if n == 0:
        raise SystemExit(f"{name}: no mask found")
    sizes = ndimage.sum_labels(mask, lab, range(1, n + 1))
    mask = lab == (int(np.argmax(sizes)) + 1)
    # fill interior holes (white chevron inside black stickers, cube
    # shading inside white ones, black CURSOR text inside the pill)
    mask = ndimage.binary_fill_holes(mask)
    # trim to bbox with a small margin
    ys, xs = np.where(mask)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    m = 6
    y0, y1 = max(0, y0 - m), min(mask.shape[0], y1 + m + 1)
    x0, x1 = max(0, x0 - m), min(mask.shape[1], x1 + m + 1)
    mask = mask[y0:y1, x0:x1]
    rgb = np.asarray(im)[y0:y1, x0:x1].astype(np.uint8)
    # fat white die-cut border: dilate the mask ~10px
    border = ndimage.binary_dilation(mask, iterations=10)
    out = np.zeros((*mask.shape, 4), dtype=np.uint8)
    out[..., 0:3] = 255  # white border base
    out[..., 3] = (border * 255).astype(np.uint8)
    inner = mask
    out[inner, 0:3] = rgb[inner]
    tile = Image.fromarray(out, "RGBA")
    path = f"cutouts/sticker-{name}.png"
    tile.save(path)
    print(f"{name}: crop {box} -> tile {tile.size}, "
          f"mask px {int(mask.sum())}")
    return path


def main():
    made = []
    for (name, box, kind) in STICKERS:
        made.append(extract(name, box, kind))
    # contact sheet: stickers on cream + on dark, to verify extraction
    # (thumbnails sized to fit their columns, no overlap)
    names = [n for (n, _, _) in STICKERS]
    sheet = Image.new("RGBA", (1240, 460), (247, 241, 229, 255))
    dark = Image.new("RGBA", (1240, 460), (40, 40, 48, 255))
    from PIL import ImageDraw, ImageFont
    labelfont = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
    for i, p in enumerate(made):
        t = Image.open(p)
        t.thumbnail((160, 160))
        x = 12 + i * 176
        sheet.alpha_composite(t.convert("RGBA"), (x, 20))
        dark.alpha_composite(t.convert("RGBA"), (x, 250))
        ImageDraw.Draw(sheet).text((x, 190), names[i], font=labelfont,
                                    fill=(30, 30, 30))
        ImageDraw.Draw(dark).text((x, 420), names[i], font=labelfont,
                                   fill=(255, 255, 255))
    sheet.convert("RGB").save("cutouts/sticker-check.jpg", quality=90)
    dark.convert("RGB").save("cutouts/sticker-check-dark.jpg", quality=90)
    print("Wrote cutouts/sticker-check.jpg + sticker-check-dark.jpg")


if __name__ == "__main__":
    main()
