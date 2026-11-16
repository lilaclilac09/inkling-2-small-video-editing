#!/usr/bin/env python3
"""Build labeled contact sheets of keyframes for clips not yet viewed."""
import os
import sys
from PIL import Image, ImageDraw, ImageFont

SCAN = "/home/hatch/workspace/inkling-recap/scan"
OUT = "/home/hatch/workspace/inkling-recap/contact-sheets"
os.makedirs(OUT, exist_ok=True)

# clips already viewed by eye (skip these)
VIEWED = {
    "0001", "0002", "0007", "0011", "0020", "0021", "0022", "0023",
    "0025", "0026", "0027", "0028", "0029", "0031", "0034", "0035",
    "0037", "0039", "0040", "0044", "0046", "0049", "0050", "0053",
    "0054", "0055", "0056", "0059",
}

# collect frame-0001.jpg for every clip folder, excluding viewed
items = []
for name in sorted(os.listdir(SCAN)):
    if not name.startswith("DJI_"):
        continue
    num = name.split("_")[2]  # DJI_20260719091607_0001_D -> 0001
    if num in VIEWED:
        continue
    f = os.path.join(SCAN, name, "frames", "frame-0001.jpg")
    if os.path.exists(f):
        items.append((num, name, f))

print(f"{len(items)} unseen clips with frames")
for num, name, f in items:
    print(" ", num, name)

# build sheets: 4 cols, 320px wide cells, label bar on top of each cell
COLS = 4
CELL_W = 320
CELL_H = 200  # image area
LABEL_H = 22
CELL_TOTAL_H = CELL_H + LABEL_H

try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
except Exception:
    font = ImageFont.load_default()

per_sheet = 12  # 4 cols x 3 rows
for s in range(0, len(items), per_sheet):
    batch = items[s:s + per_sheet]
    rows = (len(batch) + COLS - 1) // COLS
    sheet = Image.new("RGB", (COLS * CELL_W, rows * CELL_TOTAL_H), "white")
    d = ImageDraw.Draw(sheet)
    for i, (num, name, f) in enumerate(batch):
        r, c = divmod(i, COLS)
        x, y = c * CELL_W, r * CELL_TOTAL_H
        try:
            im = Image.open(f).convert("RGB")
            im.thumbnail((CELL_W, CELL_H))
            # paste centered in cell
            ox = x + (CELL_W - im.width) // 2
            oy = y + (CELL_H - im.height) // 2
            sheet.paste(im, (ox, oy))
        except Exception as e:
            print("ERR", f, e)
        d.rectangle([x, y + CELL_H, x + CELL_W, y + CELL_TOTAL_H], fill="black")
        d.text((x + 6, y + CELL_H + 3), f"{num}  {name[4:12]} {name[12:16]}", fill="white", font=font)
    out = os.path.join(OUT, f"sheet-{s//per_sheet+1}.jpg")
    sheet.save(out, quality=85)
    print("wrote", out, sheet.size)
