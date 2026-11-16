"""Test rembg cutouts with the lightweight u2netp model (low memory).

u2netp is ~4MB vs u2net ~170MB — much smaller memory footprint.
Images downscaled to max 800px. One photo at a time, explicit gc.
"""
import os
import gc
from PIL import Image, ImageOps, ImageFilter
from rembg import new_session, remove

os.chdir(os.path.dirname(os.path.abspath(__file__)) or ".")

CANDIDATES = {
    "frame-0003": "frames-dense/DJI_20260719104432_0054_D/frame-0003.jpg",
    "HM5A1478": "photos/HM5A1478.JPG",
    "HM5A1923": "photos/HM5A1923.JPG",
    "HM5A1424": "photos/HM5A1424.JPG",
    "HM5A1900": "photos/HM5A1900.JPG",
    "HM5A1789": "photos/HM5A1789.JPG",
    "0042-f12": "frames-dense/DJI_20260719084815_0042_D/frame-0012.jpg",
}

os.makedirs("cutouts", exist_ok=True)
session = new_session("u2netp")
print("session ready", flush=True)

for name, path in CANDIDATES.items():
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    im.thumbnail((800, 800), Image.LANCZOS)
    print(f"{name}: {im.size} -> removing bg...", flush=True)
    cut = remove(im, session=session)
    r, g, b, a = cut.split()
    a = a.filter(ImageFilter.GaussianBlur(1.0))
    cut = Image.merge("RGBA", (r, g, b, a))
    out = f"cutouts/{name}.png"
    cut.save(out)
    print(f"  saved {out} {cut.size}", flush=True)
    del im, cut, r, g, b, a
    gc.collect()

print("done")
