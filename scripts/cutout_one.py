"""Cut out ONE photo with the full u2net model. Run once per photo as
its own process so memory is freed between runs.

Usage: cutout_one.py <input> <output> [max_dim]
"""
import os
import sys
from PIL import Image, ImageOps, ImageFilter
from rembg import new_session, remove

inp, outp = sys.argv[1], sys.argv[2]
max_dim = int(sys.argv[3]) if len(sys.argv) > 3 else 800

os.environ.setdefault("OMP_NUM_THREADS", "2")
session = new_session("u2net")
im = ImageOps.exif_transpose(Image.open(inp)).convert("RGB")
im.thumbnail((max_dim, max_dim), Image.LANCZOS)
print(f"{inp}: {im.size} -> removing bg...", flush=True)
cut = remove(im, session=session)
r, g, b, a = cut.split()
a = a.filter(ImageFilter.GaussianBlur(1.0))
cut = Image.merge("RGBA", (r, g, b, a))
cut.save(outp)
print(f"saved {outp} {cut.size}", flush=True)
