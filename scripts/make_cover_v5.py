"""Build cover-v5.jpg — cutout poster, 1920x1080 (v2 layout).

Design (per Aileen 2026-11-13 15:39-15:40):
  - Warm cream solid background. Cutout people arranged on it.
  - (a) Green-trees girl — BIGGEST cutout, TOP-RIGHT.
  - (b) Black-hat girl HM5A1822 (waist-up crop; her legs fade in the
      cutout, so only head + torso + crossed arms are used) — bottom-left.
  - (c) Group at the door HM5A1478 — bottom-centre.
  - Text top-left in Playfair Display Bold / Montserrat SemiBold
    (NOT Caveat), dark warm brown. No text touches any head.
  - No overlapping cutouts; no one has their head cut off.
"""
from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080
BG = (247, 241, 229)

def load_cutout(path, target_h):
    im = Image.open(path).convert("RGBA")
    bbox = im.split()[3].getbbox()
    if bbox:
        im = im.crop(bbox)
    w, h = im.size
    return im.resize((round(w * target_h / h), target_h), Image.LANCZOS)

def main():
    canvas = Image.new("RGB", (W, H), BG)
    # (a) hero girl — biggest, top-right (trimmed 420x401 -> 712x680)
    hero = load_cutout("cover-v5/girl-trees-cutout.png", 680)
    canvas.paste(hero, (W - hero.width - 50, 30), hero)
    print("hero:", hero.size, "at", (W - hero.width - 50, 30))
    # (b) black-hat girl, waist-up — bottom-left (trimmed 558x1216 -> 266x580)
    hat = load_cutout("cover-v5/girl-hat-cutout-waistup.png", 580)
    canvas.paste(hat, (110, H - hat.height - 30), hat)
    print("hat:", hat.size, "at", (110, H - hat.height - 30))
    # (c) group — bottom-centre, BELOW the hero (trimmed 1480x770 -> 692x360).
    # Placed at y=720 so it sits fully below the hero (hero ends y=710);
    # x-range 650-1342 stays clear of the hat girl (ends x=376).
    group = load_cutout("cover-v5/group-cutout-clean.png", 360)
    canvas.paste(group, (650, 720), group)
    print("group:", group.size, "at", (650, 720))

    d = ImageDraw.Draw(canvas)
    title_font = ImageFont.truetype("/tmp/fonts-v4/PlayfairDisplay-Bold.ttf", 84)
    date_font = ImageFont.truetype("/tmp/fonts-v4/Montserrat-SemiBold.ttf", 46)
    ink = (58, 44, 32)
    d.text((80, 70), "Cursor Cafe", font=title_font, fill=ink)
    d.text((80, 160), "Shanghai", font=title_font, fill=ink)
    d.text((84, 280), "2026.07.19", font=date_font, fill=(120, 100, 78))
    d.line([(84, 350), (340, 350)], fill=(120, 100, 78), width=3)

    canvas.save("cover-v5.jpg", quality=92)
    print("Wrote cover-v5.jpg", canvas.size)

if __name__ == "__main__":
    main()
