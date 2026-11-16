"""Build contact sheets: 3 frames per clip (first, middle, last), 3 clips per sheet."""
import glob, os
from PIL import Image, ImageDraw, ImageFont
root = os.path.expanduser('~/workspace/inkling-recap/frames-dense')
out_root = os.path.expanduser('~/workspace/inkling-recap/contact-sheets-dense')
os.makedirs(out_root, exist_ok=True)
clips = sorted(os.listdir(root))
# font
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22)
    small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
except Exception:
    font = ImageFont.load_default(); small = font
CELL_W, CELL_H = 640, 360
LABEL_H = 34
cols, rows = 3, 3
sheet_w = cols * CELL_W
sheet_h = rows * (CELL_H + LABEL_H)
sheet_idx = 0
for start in range(0, len(clips), 3):
    group = clips[start:start+3]
    sheet = Image.new('RGB', (sheet_w, sheet_h), (20, 20, 20))
    d = ImageDraw.Draw(sheet)
    for ci, clip in enumerate(group):
        frames = sorted(glob.glob(os.path.join(root, clip, 'frame-*.jpg')))
        if not frames:
            continue
        picks = [frames[0], frames[len(frames)//2], frames[-1]]
        for fi, fp in enumerate(picks):
            idx = ci * 3 + fi
            r, c = divmod(idx, cols)
            x, y = c * CELL_W, r * (CELL_H + LABEL_H)
            try:
                im = Image.open(fp).convert('RGB')
                im.thumbnail((CELL_W, CELL_H))
            except Exception as e:
                continue
            sheet.paste(im, (x, y))
            ts = os.path.basename(fp).replace('frame-','').replace('.jpg','')
            # frame number -> seconds (fps=1, frame-0001 = 0s)
            sec = int(ts) - 1
            label = f"{clip}  t={sec}s"
            d.rectangle([x, y + CELL_H, x + CELL_W, y + CELL_H + LABEL_H], fill=(0,0,0))
            d.text((x + 6, y + CELL_H + 5), label, fill=(255,255,0), font=small)
    out = os.path.join(out_root, f"sheet-{sheet_idx+1:02d}.jpg")
    sheet.save(out, quality=88)
    print(f"sheet {sheet_idx+1}: clips {group}", flush=True)
    sheet_idx += 1
print(f"TOTAL sheets: {sheet_idx}")
