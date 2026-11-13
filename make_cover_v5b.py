"""Build cover-v5.jpg — v6 layout (photo panels + hero cutout + refined type).

Design (per Aileen 2026-11-13 19:07 + 19:08):
  - Warm cream solid background.
  - (a) Hero girl (green trees) — cutout, BIGGEST, TOP-RIGHT, unchanged
      position/size; edges cleaned (erode + defringe + feather).
  - (b) Black-hat girl HM5A1822 — PHOTO PANEL (not a cutout): her background
      (the Cursor banner, text legible) stays visible. Bottom-left.
  - (c) Group HM5A1478 — PHOTO PANEL (not a cutout): full background, FULL
      LEGS, bigger. Bottom-centre.
  - (d) Interior speaking shot (Talk L, clip 0051 frame-0008: presenter at
      laptop, screen, audience listening) — photo panel, top-centre.
  - Text top-left, same words, refined typography: Playfair Bold "Cursor
      Cafe" + Playfair Bold Italic "Shanghai", thin bronze rule, letterspaced
      Montserrat SemiBold date.
  - All panels: rounded corners + feathered edge, soft on cream.
  - No overlapping elements; no one has their head cut off.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

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

def clean_cutout_edges(im):
    """Remove background-colour fringe from an RGBA cutout: defringe the RGB
    (edge pixels take the nearest fully-opaque colour), erode alpha 1px,
    feather 0.8px."""
    im = im.convert("RGBA")
    rgb = np.array(im.convert("RGB")).astype(np.uint8)
    a = np.array(im.split()[3])
    try:
        from scipy import ndimage
        opaque = a > 200
        # nearest opaque pixel index for every pixel
        _, inds = ndimage.distance_transform_edt(~opaque, return_indices=True)
        nearest_rgb = rgb[tuple(inds)]
        edge = (a > 0) & (a <= 200)
        rgb[edge] = nearest_rgb[edge]
    except Exception as e:
        print("defringe skipped:", e)
    out = Image.fromarray(rgb, "RGB").convert("RGBA")
    alpha = Image.fromarray(a, "L")
    alpha = alpha.filter(ImageFilter.MinFilter(3))          # erode 1px
    alpha = alpha.filter(ImageFilter.GaussianBlur(0.8))     # feather
    out.putalpha(alpha)
    return out

def soft_panel(im, size, radius=24, feather=5):
    """Resize to size, round the corners, feather the edge into the cream."""
    im = im.convert("RGB").resize(size, Image.LANCZOS)
    mask = Image.new("L", size, 0)
    d = ImageDraw.Draw(mask)
    d.rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], radius=radius, fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(feather))
    out = Image.new("RGBA", size, (0, 0, 0, 0))
    out.paste(im, (0, 0))
    out.putalpha(mask)
    return out

def crop_frac(im, x0, y0, x1, y1):
    w, h = im.size
    return im.crop((round(x0 * w), round(y0 * h), round(x1 * w), round(y1 * h)))

def draw_tracked(d, xy, text, font, fill, tracking=6):
    """Draw text with letter tracking (px between chars)."""
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill)
        x += font.getlength(ch) + tracking
    return x

def main():
    canvas = Image.new("RGB", (W, H), BG)

    # (d) interior speaking shot — Talk L, clip 0051 frame-0008 (1280x720)
    interior = Image.open("frames-dense/DJI_20260719103816_0051_D/frame-0008.jpg")
    interior_panel = soft_panel(interior, (700, 394))
    canvas.paste(interior_panel, (640, 70), interior_panel)
    print("interior:", interior_panel.size, "at (640, 70)")

    # (b) black-hat girl + banner — photo panel, HM5A1822.
    # Crop widened to x1=0.76 (verified): the banner text "Sunset Shanghai"
    # runs to ~x=0.74, so 0.72 clipped it. Full text now visible.
    girl = Image.open("photos/HM5A1822.JPG")
    girl_crop = crop_frac(girl, 0.10, 0.04, 0.76, 1.0)
    print("girl crop:", girl_crop.size, "aspect", round(girl_crop.size[0] / girl_crop.size[1], 3))
    girl_panel = soft_panel(girl_crop, (520, 504))
    canvas.paste(girl_panel, (80, 546), girl_panel)
    print("girl panel:", girl_panel.size, "at (80, 546)")

    # (c) group + banner + street, FULL LEGS — photo panel, HM5A1478.
    # Crop right edge x1=0.84 (verified by reading crops): man 7 (white tee,
    # far right) ends ~x=0.826; man 8's foot starts ~x=0.855. 0.84 keeps all
    # 7 men whole and excludes man 8 entirely. 0.86 caught his foot.
    group = Image.open("photos/HM5A1478.JPG")
    group_crop = crop_frac(group, 0.015, 0.20, 0.84, 0.97)
    print("group crop:", group_crop.size, "aspect", round(group_crop.size[0] / group_crop.size[1], 3))
    gw = 730
    gh = round(gw * group_crop.size[1] / group_crop.size[0])
    group_panel = soft_panel(group_crop, (gw, gh))
    gx, gy = 620, H - gh - 30
    canvas.paste(group_panel, (gx, gy), group_panel)
    print("group panel:", group_panel.size, f"at ({gx}, {gy})")

    # (a) hero girl — cleaned cutout, SAME size/position as v5
    hero = Image.open("cover-v5/girl-trees-cutout.png")
    hero = clean_cutout_edges(hero)
    bbox = hero.split()[3].getbbox()
    hero = hero.crop(bbox)
    hero = hero.resize((712, 680), Image.LANCZOS)
    canvas.paste(hero, (W - hero.width - 50, 30), hero)
    print("hero:", hero.size, "at", (W - hero.width - 50, 30))

    # ---- refined typography, top-left ----
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
