"""Build the v7 sticker overlay PNGs (rain + coffee).

Why overlays: measured on the v6 black-bg renders, the libass
BorderStyle=4 box stays axis-aligned (top/bottom edges 0.00 deg)
while the \\frz text tilts ~4 deg (rain) / ~3 deg (coffee). The user
is right: slanted text inside a straight box looks strange. The only
way to tilt text AND box together is to render the sticker as an
image and rotate the whole image.

Method (text identical to v6, same renderer):
  * The sticker text (both lines, emoji included) is rendered by
    libass onto a black mask (text-rain-mask.png / text-coffee-mask.png,
    white text, no box) -- so fonts, sizes, emoji and layout are
    byte-identical to what v6 showed.
  * In PIL the mask luminance becomes the alpha of black text, pasted
    onto a WHITE box (the user asked for white, strong contrast).
  * Box size: 5% narrower horizontally and 2% narrower vertically
    than the v6 box (rain 893x138 -> 848x135; coffee 801x129 ->
    761x126), padding symmetric top/bottom and left/right.
  * Soft drop shadow behind the white box, then the whole sticker is
    rotated (rain -4 deg, coffee -3 deg, same tilt direction as v6)
    and saved as a transparent PNG for ffmpeg overlay.
  * Overlay centre targets are the v6 box centres (rain (515,110),
    coffee (469,96)) so the position on screen does not move.

Outputs:
  scratch-v7/sticker-rain-v7.png, scratch-v7/sticker-coffee-v7.png
  scratch-v7/sticker-overlay.json  (overlay x,y + enable ranges)
"""
import json
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

BASE = "scratch-v7"

# v6 measured box sizes (black-bg renders) and centres.
SPECS = {
    "rain": {
        "mask": f"{BASE}/text-rain-mask.png",
        "angle": -4,          # PIL rotate: negative = clockwise (matches v6 text tilt)
        "target_w": 848,      # 893 * 0.95 = 848.4
        "target_h": 135,      # 138 * 0.98 = 135.2
        "centre": (515, 110),  # v6 box centre (x[69,961], y[42,179])
        "t0": 99, "t1": 104,  # ASS event 1:39.00-1:44.00
    },
    "coffee": {
        "mask": f"{BASE}/text-coffee-mask.png",
        "angle": -3,
        "target_w": 761,      # 801 * 0.95 = 761.0
        "target_h": 126,      # 129 * 0.98 = 126.4
        "centre": (469, 96),   # v6 box centre (x[69,869], y[32,160])
        "t0": 80, "t1": 84,   # ASS event 1:20.00-1:24.00
    },
}

SHADOW_OFF = (4, 5)
SHADOW_BLUR = 6
SHADOW_ALPHA = 90


def text_layer(mask_path):
    """Black text RGBA from the libass white-on-black mask."""
    lum = np.asarray(Image.open(mask_path).convert("L"))
    ys, xs = np.where(lum > 30)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    crop = lum[y0:y1 + 1, x0:x1 + 1]
    rgba = np.zeros((crop.shape[0], crop.shape[1], 4), dtype=np.uint8)
    rgba[..., 3] = crop  # luminance -> alpha, black text
    return Image.fromarray(rgba, "RGBA"), (x1 - x0 + 1, y1 - y0 + 1)


def build(name, spec):
    text, (tw, th) = text_layer(spec["mask"])
    W, H = spec["target_w"], spec["target_h"]
    pad_x = (W - tw) / 2
    pad_y = (H - th) / 2
    assert pad_x >= 8 and pad_y >= 8, f"{name}: padding too small ({pad_x:.1f},{pad_y:.1f})"
    print(f"{name}: text {tw}x{th} -> box {W}x{H}, "
          f"pad L/R {pad_x:.1f}, T/B {pad_y:.1f}")

    # Sticker (white box + text) on a transparent canvas with room
    # for the shadow offset + blur.
    m = 24
    canvas = Image.new("RGBA", (W + 2 * m, H + 2 * m), (0, 0, 0, 0))
    # Shadow: black copy of the box, offset down-right, blurred.
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rectangle([m + SHADOW_OFF[0], m + SHADOW_OFF[1],
                  m + W + SHADOW_OFF[0], m + H + SHADOW_OFF[1]],
                 fill=(0, 0, 0, SHADOW_ALPHA))
    shadow = shadow.filter(ImageFilter.GaussianBlur(SHADOW_BLUR))
    canvas = Image.alpha_composite(canvas, shadow)
    # White box.
    d = ImageDraw.Draw(canvas)
    d.rectangle([m, m, m + W, m + H], fill=(255, 255, 255, 255))
    # Text centred in the box.
    tx = m + int(round(pad_x))
    ty = m + int(round(pad_y))
    canvas.alpha_composite(text, (tx, ty))

    # Rotate the whole sticker (box + text together).
    rot = canvas.rotate(spec["angle"], resample=Image.BICUBIC, expand=True)
    out_path = f"{BASE}/sticker-{name}-v7.png"
    rot.save(out_path)

    # White-box centre in the rotated image (for overlay placement).
    arr = np.asarray(rot)
    white = (arr[..., 0] > 235) & (arr[..., 1] > 235) & (arr[..., 2] > 235) & (arr[..., 3] > 200)
    ys, xs = np.where(white)
    bcx = (xs.min() + xs.max()) / 2
    bcy = (ys.min() + ys.max()) / 2
    # White box bbox (unrotated axes) for the report.
    bw = xs.max() - xs.min() + 1
    bh = ys.max() - ys.min() + 1
    cx, cy = spec["centre"]
    ox = int(round(cx - bcx))
    oy = int(round(cy - bcy))
    print(f"  rotated {rot.size}, white bbox {bw}x{bh} centre "
          f"({bcx:.1f},{bcy:.1f}) -> overlay x={ox} y={oy} "
          f"(target centre {cx},{cy})")
    return {
        "png": out_path,
        "overlay_x": ox, "overlay_y": oy,
        "enable": f"between(t,{spec['t0']},{spec['t1']})",
        "box_w": W, "box_h": H,
        "angle": spec["angle"],
    }


def main():
    out = {}
    for name, spec in SPECS.items():
        out[name] = build(name, spec)
    with open(f"{BASE}/sticker-overlay.json", "w") as f:
        json.dump(out, f, indent=2)
    print("wrote sticker PNGs + sticker-overlay.json")


if __name__ == "__main__":
    main()
