"""Build cover-v5.jpg — mood board layout (NO cutouts).

Design (per Aileen 2026-11-13 19:19, supersedes the cutout direction):
  - STOP CUTTING OUT PEOPLE ENTIRELY. The cutouts look weird and the
    group's legs still did not come back.
  - MOOD BOARD: rectangular photo panels placed on the cream canvas with a
    little space/gap between them. No masks, no rembg, no feathered edges,
    no rounded corners — just the photos as they are.
  - Same photos/layout as v5b (text top-left, interior top-centre, hero
    top-right, black-hat girl bottom-left, group bottom-centre).
  - Hero girl (green trees) is now a PHOTO PANEL (full 0054 frame-0003,
    no crop) — her green-trees background stays, no cut faces.
  - Group HM5A1478 is BIGGER (810 wide), full legs + background.
  - Black-hat girl HM5A1822 panel keeps her background + banner text legible.
  - Interior speaking shot (Talk L, 0051 frame-0008) top-centre.
  - Text top-left, same refined typography as v5b (Playfair Bold +
    Playfair Bold Italic, thin bronze rule, letterspaced Montserrat date).
  - No cut-off heads, no black bar, no overlapping panels.
"""
from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080
BG = (247, 241, 229)
INK = (58, 44, 32)
TAUPE = (120, 100, 78)
BRONZE = (150, 125, 90)
FONTS = "fonts"


def load_font(name, size, weight):
    f = ImageFont.truetype(f"{FONTS}/{name}", size)
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        pass
    return f


def sharp_panel(im, size):
    """Resize to an exact size and return a plain RGB panel (no rounding,
    no feather, no mask — the photo as it is)."""
    return im.convert("RGB").resize(size, Image.LANCZOS)


def crop_frac(im, x0, y0, x1, y1):
    w, h = im.size
    return im.crop((round(x0 * w), round(y0 * h), round(x1 * w), round(y1 * h)))


def draw_tracked(d, xy, text, font, fill, tracking=6):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill)
        x += font.getlength(ch) + tracking
    return x


def main():
    canvas = Image.new("RGB", (W, H), BG)

    # (d) interior speaking shot — Talk L, clip 0051 frame-0008 (1280x720)
    interior = Image.open("frames-dense/DJI_20260719103816_0051_D/frame-0008.jpg")
    interior_panel = sharp_panel(interior, (640, 360))
    canvas.paste(interior_panel, (560, 30))
    print("interior:", interior_panel.size, "at (560, 30)")

    # (a) hero girl — FULL photo panel, no crop (0054 frame-0003, 1280x720).
    # Everyone whole, no cut faces; girl + green trees + drink + tablet.
    hero = Image.open("frames-dense/DJI_20260719104432_0054_D/frame-0003.jpg")
    hero_panel = sharp_panel(hero, (610, 343))
    canvas.paste(hero_panel, (1230, 30))
    print("hero:", hero_panel.size, "at (1230, 30)")

    # (b) black-hat girl + banner — photo panel, HM5A1822.
    # Crop x 0.10-0.76 (verified in v5b): full "CURSOR / Cursor Café ×
    # Sunset Shanghai" + Chinese lines + drawing legible.
    girl = Image.open("photos/HM5A1822.JPG")
    girl_crop = crop_frac(girl, 0.10, 0.04, 0.76, 1.0)
    print("girl crop:", girl_crop.size, "aspect",
          round(girl_crop.size[0] / girl_crop.size[1], 3))
    girl_panel = sharp_panel(girl_crop, (520, 504))
    canvas.paste(girl_panel, (80, 546))
    print("girl panel:", girl_panel.size, "at (80, 546)")

    # (c) group + banner + street, FULL LEGS — photo panel, HM5A1478.
    # Crop right edge x1=0.84 (verified in v5b): man 7 ends ~0.826, man 8's
    # foot starts ~0.855. Keeps all 7 men whole, head to toe.
    group = Image.open("photos/HM5A1478.JPG")
    group_crop = crop_frac(group, 0.015, 0.20, 0.84, 0.97)
    print("group crop:", group_crop.size, "aspect",
          round(group_crop.size[0] / group_crop.size[1], 3))
    group_panel = sharp_panel(group_crop, (810, 504))
    canvas.paste(group_panel, (630, 546))
    print("group panel:", group_panel.size, "at (630, 546)")

    # ---- refined typography, top-left (same as v5b) ----
    d = ImageDraw.Draw(canvas)
    title_font = load_font("PlayfairDisplay.ttf", 78, 700)
    title_it = load_font("PlayfairDisplay-Italic.ttf", 78, 700)
    date_font = load_font("Montserrat.ttf", 34, 600)
    d.text((80, 78), "Cursor Cafe", font=title_font, fill=INK)
    d.text((80, 170), "Shanghai", font=title_it, fill=INK)
    d.line([(84, 302), (420, 302)], fill=BRONZE, width=2)
    draw_tracked(d, (84, 322), "2026.07.19", date_font, TAUPE, tracking=6)

    canvas.save("cover-v5.jpg", quality=92)
    print("Wrote cover-v5.jpg", canvas.size)


if __name__ == "__main__":
    main()
