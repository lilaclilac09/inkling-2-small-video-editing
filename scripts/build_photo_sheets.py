#!/usr/bin/env python3
"""Build labeled contact sheets for the 300 Cafe Cursor meetup photos.

12 photos per sheet (4 cols x 3 rows), each cell 480x320 with the
filename on a label bar. Sheets go to photo-sheets/sheet-NN.jpg.
Also writes photo-sheets/manifest.json: sheet -> [filenames].
"""
import json
import os
from PIL import Image, ImageDraw, ImageFont

PHOTOS = "/home/hatch/workspace/inkling-recap/photos"
OUT = "/home/hatch/workspace/inkling-recap/photo-sheets"
os.makedirs(OUT, exist_ok=True)

COLS, ROWS = 4, 3
CELL_W, CELL_H, LABEL_H = 480, 320, 28
PER_SHEET = COLS * ROWS

try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
    small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
except Exception:
    font = ImageFont.load_default()
    small = font

files = sorted(f for f in os.listdir(PHOTOS) if f.lower().endswith((".jpg", ".jpeg")))
print(f"{len(files)} photos")

manifest = {}
for s in range(0, len(files), PER_SHEET):
    batch = files[s:s + PER_SHEET]
    rows = (len(batch) + COLS - 1) // COLS
    sheet = Image.new("RGB", (COLS * CELL_W, rows * (CELL_H + LABEL_H)), "white")
    draw = ImageDraw.Draw(sheet)
    for i, name in enumerate(batch):
        r, c = divmod(i, COLS)
        x, y = c * CELL_W, r * (CELL_H + LABEL_H)
        try:
            im = Image.open(os.path.join(PHOTOS, name)).convert("RGB")
        except Exception as e:
            print("skip", name, e)
            continue
        # center-crop to 3:2 then resize
        w, h = im.size
        target = CELL_W / CELL_H
        if w / h > target:
            nw = int(h * target)
            x0 = (w - nw) // 2
            im = im.crop((x0, 0, x0 + nw, h))
        else:
            nh = int(w / target)
            y0 = (h - nh) // 2
            im = im.crop((0, y0, w, y0 + nh))
        im = im.resize((CELL_W, CELL_H), Image.LANCZOS)
        sheet.paste(im, (x, y))
        draw.rectangle([x, y + CELL_H, x + CELL_W, y + CELL_H + LABEL_H], fill=(20, 20, 20))
        draw.text((x + 8, y + CELL_H + 4), f"{i+1:02d} {name}", fill="white", font=font)
    n = s // PER_SHEET + 1
    path = os.path.join(OUT, f"sheet-{n:02d}.jpg")
    sheet.save(path, quality=82)
    manifest[f"sheet-{n:02d}"] = batch
    print(f"sheet-{n:02d}: {len(batch)} photos -> {path}")

with open(os.path.join(OUT, "manifest.json"), "w") as f:
    json.dump(manifest, f, indent=1)
print("sheets:", len(manifest))
