"""Extract Cursor logo stickers v2 — SHARPER edges.

v1 problem (measured 2026-11-16): the tile alpha is fully binary
(0/255, zero semi-transparent pixels), so the die-cut border edge
renders stair-stepped/jaggy, especially on the hexagon diagonals and
rounded corners. v2 keeps the same masks but:
  * cleans the mask (binary opening to drop specks, closing to fill
    notches),
  * erodes 1px to cut the JPEG fringe clinging to the sticker edge,
  * smooths the contour (Gaussian sigma 0.8 + re-threshold) so the
    outline is a smooth curve, not a threshold staircase,
  * gives the fat white border a 1-2px anti-aliased ramp (Gaussian
    sigma 0.8 on the border alpha) so the outer edge looks crisp and
    smooth instead of pixelated.
Same crop boxes as v1; overwrites cutouts/sticker-*.png in place.
"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

os.chdir(os.path.dirname(os.path.abspath(__file__)) or ".")

SHEET = "logo-cursor-stickers.jpg"

STICKERS = [
    ("hex-black-large",   (788, 100, 1005, 345), "black"),
    ("square-black-large", (413, 90, 667, 345), "black"),
    ("square-white-large", (75, 90, 330, 345), "white"),
    ("pill-cursor",        (744, 460, 1044, 568), "white"),
    ("square-black-small", (294, 443, 434, 585), "black"),
    ("square-white-small", (70, 443, 210, 585), "white"),
    ("hex-black-small",    (526, 446, 647, 582), "black"),
]


def smooth_mask(mask, sigma=0.8):
    """Gaussian-smooth a binary mask and re-threshold: removes the
    threshold staircase while keeping the contour location."""
    blurred = ndimage.gaussian_filter(mask.astype(np.float64), sigma)
    return blurred >= 0.5


def extract(name, box, kind):
    im = Image.open(SHEET).convert("RGB").crop(box)
    a = np.asarray(im).astype(np.int16)
    lum = a.mean(axis=2)
    red = (a[:, :, 0] > 140) & (a[:, :, 1] < 110) & (a[:, :, 2] < 110)
    if kind == "white":
        mask = (lum > 222) & (~red)
    else:
        mask = (lum < 115) & (~red)
    lab, n = ndimage.label(mask)
    if n == 0:
        raise SystemExit(f"{name}: no mask found")
    sizes = ndimage.sum_labels(mask, lab, range(1, n + 1))
    mask = lab == (int(np.argmax(sizes)) + 1)
    mask = ndimage.binary_fill_holes(mask)
    # clean: drop specks, fill notches
    mask = ndimage.binary_opening(mask, structure=np.ones((3, 3)))
    mask = ndimage.binary_closing(mask, structure=np.ones((3, 3)))
    mask = ndimage.binary_fill_holes(mask)
    # cut the 1px JPEG fringe clinging to the edge
    mask = ndimage.binary_erosion(mask, iterations=1)
    # smooth the contour (anti-staircase)
    mask = smooth_mask(mask, sigma=0.8)
    mask = ndimage.binary_fill_holes(mask)
    # trim to bbox with a small margin
    ys, xs = np.where(mask)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    m = 6
    y0, y1 = max(0, y0 - m), min(mask.shape[0], y1 + m + 1)
    x0, x1 = max(0, x0 - m), min(mask.shape[1], x1 + m + 1)
    mask = mask[y0:y1, x0:x1]
    rgb = np.asarray(im)[y0:y1, x0:x1].astype(np.uint8)
    # fat white die-cut border: dilate ~10px, then a 1-2px
    # anti-aliased ramp on the border alpha (crisp, smooth edge)
    border = ndimage.binary_dilation(mask, iterations=10)
    border_a = ndimage.gaussian_filter(border.astype(np.float64), 0.8)
    border_a = np.clip(border_a * 255, 0, 255).astype(np.uint8)
    out = np.zeros((*mask.shape, 4), dtype=np.uint8)
    out[..., 0:3] = 255
    out[..., 3] = border_a
    # interior: full opacity, original pixels
    out[mask, 3] = 255
    out[mask, 0:3] = rgb[mask]
    tile = Image.fromarray(out, "RGBA")
    path = f"cutouts/sticker-{name}.png"
    tile.save(path)
    # edge stats: semi-transparent pixels = the anti-aliased ramp
    fringe = int(((border_a > 0) & (border_a < 255)).sum())
    print(f"{name}: tile {tile.size}, mask px {int(mask.sum())}, "
          f"ramp px {fringe}")
    return path


def main():
    made = []
    for (name, box, kind) in STICKERS:
        made.append(extract(name, box, kind))
    # 4x zoom contact sheet: each sticker's top-left corner region,
    # so the edge smoothness can be judged at a glance.
    names = [n for (n, _, _) in STICKERS]
    cell = 300
    sheet = Image.new("RGB", (cell * 4, cell * 2 + 40), (247, 241, 229))
    dd = ImageDraw.Draw(sheet)
    labelfont = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
    for i, p in enumerate(made):
        t = Image.open(p)
        # crop the top-left corner (has a diagonal/rounded edge) and
        # upscale 4x with LANCZOS (shows the real edge, not blocks)
        cw, ch = min(75, t.size[0]), min(75, t.size[1])
        corner = t.crop((0, 0, cw, ch)).resize((cell, cell), Image.LANCZOS)
        bg = Image.new("RGBA", (cell, cell), (247, 241, 229, 255))
        bg.alpha_composite(corner, (0, 0))
        x, y = (i % 4) * cell, (i // 4) * (cell + 20)
        sheet.paste(bg.convert("RGB"), (x, y))
        dd.text((x + 6, y + cell + 2), names[i] + " 4x corner",
                font=labelfont, fill=(30, 30, 30))
    sheet.save("cutouts/sticker-check-v2-zoom.jpg", quality=92)
    print("Wrote cutouts/sticker-check-v2-zoom.jpg")


if __name__ == "__main__":
    main()
