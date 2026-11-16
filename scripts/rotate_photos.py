"""Rotate the 67 Orientation=8 photos 90 deg CCW (lossless direction, PIL q100).

Method note: jpegtran was not installable in this VM (apt-get update stalls
on the mirror, package not locatable). Fallback per task: PIL at maximum
quality (quality=100, subsampling=0 / 4:4:4) which is visually lossless.
EXIF Orientation is reset to 1 after rotating the pixels so viewers do not
rotate a second time. The 2 Orientation=1 files (HM5A1497/1498) are already
upright and are NOT rotated.
"""
import os
import sys
from PIL import Image

PHOTOS = os.path.expanduser("~/workspace/inkling-recap/photos")
ROT_DIR = os.path.expanduser("~/workspace/inkling-recap/photo-categories/needs-rotation")
SKIP_UPRIGHT = {"HM5A1497.JPG", "HM5A1498.JPG"}  # already upright, verified visually

def main():
    files = sorted(os.listdir(ROT_DIR))
    to_rotate = []
    skipped = []
    for fn in files:
        if fn in SKIP_UPRIGHT:
            skipped.append(fn)
            continue
        to_rotate.append(fn)
    print(f"to rotate (Orientation=8, 90 CCW): {len(to_rotate)}")
    print(f"skipped (already upright): {skipped}")
    ok, fail, already = [], [], []
    for fn in to_rotate:
        src = os.path.realpath(os.path.join(ROT_DIR, fn))
        assert os.path.exists(src), f"missing {src}"
        tmp = src + ".rot.tmp.jpg"
        try:
            im = Image.open(src)
            w, h = im.size
            o = im.getexif().get(274)
            if (w, h) == (4000, 6000) and o == 1:
                already.append(fn)
                continue
            assert (w, h) == (6000, 4000), f"{fn} unexpected size {(w,h)}"
            assert o == 8, f"{fn} orient != 8"
            # Rotate 90 CCW
            out = im.transpose(Image.ROTATE_90)
            exif = im.getexif()
            exif[274] = 1  # Orientation normal
            out.save(tmp, format="JPEG", quality=100, subsampling=0, exif=exif)
            # Verify temp
            chk = Image.open(tmp)
            cw, ch = chk.size
            co = chk.getexif().get(274)
            assert (cw, ch) == (4000, 6000), f"{fn} bad out size {(cw,ch)}"
            assert co == 1, f"{fn} bad out orient {co}"
            os.replace(tmp, src)
            ok.append(fn)
        except Exception as e:
            fail.append((fn, str(e)))
            if os.path.exists(tmp):
                os.remove(tmp)
    print(f"rotated OK: {len(ok)}")
    print(f"already upright (skipped): {len(already)} {already}")
    if fail:
        print(f"FAILED: {len(fail)}")
        for fn, e in fail:
            print(f"  {fn}: {e}")
    return 0 if not fail else 1

if __name__ == "__main__":
    sys.exit(main())
