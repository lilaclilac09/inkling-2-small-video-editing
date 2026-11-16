"""Build captions-v11-singlebox-v7.ass from v6.

User (2026-11-16 10:48): "字是斜的，整个背景也斜啊，你用白对比
强烈一点的吧，你怎么字斜这个框不斜呢？哇很奇怪，而且这个盒子
左右再收窄百分之五，上下收窄百分之二，上下要对齐"
Translation: the sticker text is slanted but its background box is
NOT slanted (that is the strange part); the whole sticker (text AND
box) must tilt together; use WHITE with stronger contrast for the
sticker background; narrow the box left/right by 5% and top/bottom
by 2%; top and bottom padding must be aligned (symmetric).

VERIFIED ROOT CAUSE (measured on v6 black-bg renders): the libass
BorderStyle=4 box stays axis-aligned (top/bottom edges 0.00 deg)
while the \\frz text tilts ~4 deg (rain) / ~3 deg (coffee). No ASS
tweak can tilt that box -- so the two stickers leave the ASS and
become image overlays (see build_stickers_v7.py):
  * sticker-rain-v7.png / sticker-coffee-v7.png -- white box + black
    text rendered as one image, rotated -4 deg / -3 deg, so box and
    text tilt together. Text itself is rendered by libass (same
    renderer/fonts/emoji as v6), so it looks identical.
  * Overlay: ffmpeg overlay filter, enable='between(t,99,104)' (rain)
    / 'between(t,80,84)' (coffee); positions in sticker-overlay-v7.json
    (rain x=62 y=-14, coffee x=61 y=-13; centres match the v6 boxes).

What changes in THIS file (regular captions only):
  1. The 2 sticker Dialogue events are REMOVED (they live in the PNGs
     now). 49 events -> 47. All 47 remaining events' text/timings are
     byte-identical to v6.
  2. NARROWER HORIZONTALLY (~5%): side-padding \\h runs 11 -> 9 per
     side on all 47 regular events. (v6 measured ~9.2 px per \\h, so
     -2 \\h/side is ~37 px off a ~770-880 px box, ~4.7-4.8%.)
  3. NARROWER VERTICALLY (~2%): top/bottom blank-line font sizes -1
     each -- CAP top fs17 -> 16, bottom fs28 -> 27; NOTE top fs19 ->
     18, bottom fs26 -> 25. Same delta top and bottom, so the
     rendered top/bottom padding stays symmetric (aligned).
  4. Regular boxes keep the v6 pale cream BackColour &H00CCE6F5.
     Only the stickers go white (in the PNGs).
"""
import re
import shutil

SRC = "scan/captions-v11-singlebox-v6.ass"
DST = "scan/captions-v11-singlebox-v7.ass"

# Side-padding \\h runs: old count -> new count (per side).
PAD_MAP = {11: 9}

# Top/bottom blank-line font sizes: old -> new.
PAD_FS = [(17, 16), (28, 27), (19, 18), (26, 25)]

STICKER_STYLES = ("SINGLE_COFFEE_STK", "SINGLE_RAIN_STK")


def parse_events(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    events = [ln for ln in text.split("\n") if ln.startswith("Dialogue:")]
    return text, events


def plain_text(line):
    p = line[len("Dialogue:"):].split(",", 9)
    t = re.sub(r"\{[^}]*\}", "", p[9]).replace("\\h", "").replace("\\N", "|")
    return (p[1], p[2], p[3], t)


def h_runs(text):
    from collections import Counter
    c = Counter()
    for m in re.finditer(r"(?:\\h)+", text):
        c[len(m.group(0)) // 2] += 1
    return c


def main():
    src_text, src_events = parse_events(SRC)
    assert len(src_events) == 49, f"expected 49 v6 events, got {len(src_events)}"

    # --- 1. Drop the 2 sticker events (now image overlays). ---
    kept, dropped = [], []
    for e in src_events:
        style = e.split(",", 4)[3]
        (dropped if style in STICKER_STYLES else kept).append(e)
    assert len(dropped) == 2, f"expected 2 sticker events, got {len(dropped)}"
    assert len(kept) == 47
    print("dropped sticker events:",
          [plain_text(e)[3][:30] for e in dropped])

    out = src_text
    for e in dropped:
        assert out.count(e) == 1
        out = out.replace(e + "\n", "")

    # --- 2. Narrower horizontally: side-padding \\h runs 11 -> 9. ---
    def shrink_run(m):
        n = len(m.group(0)) // 2
        assert n in PAD_MAP, f"unexpected \\h run length {n}"
        return "\\h" * PAD_MAP[n]

    # Only runs of >= 2 are side padding (blank lines hold a single \h).
    out = re.sub(r"(?:\\h){2,}", shrink_run, out)

    # --- 3. Narrower vertically: top/bottom blank-line font sizes -1. ---
    for old_fs, new_fs in PAD_FS:
        old = "{\\fnLiberation Sans\\fs%d}\\h" % old_fs
        new = "{\\fnLiberation Sans\\fs%d}\\h" % new_fs
        n = out.count(old)
        assert n > 0, f"padding pattern fs{old_fs} not found!"
        out = out.replace(old, new)
        print(f"  padding fs{old_fs} -> fs{new_fs}: {n} occurrences")

    with open(DST, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"wrote {DST}")

    # --- 4. Copy the sticker overlays to their deliverable locations. ---
    shutil.copy("scratch-v7/sticker-rain-v7.png", "sticker-rain-v7.png")
    shutil.copy("scratch-v7/sticker-coffee-v7.png", "sticker-coffee-v7.png")
    shutil.copy("scratch-v7/sticker-overlay.json", "sticker-overlay-v7.json")
    print("copied sticker-rain-v7.png, sticker-coffee-v7.png, "
          "sticker-overlay-v7.json to the top level")

    # --- 5. Fidelity checks. ---
    _, dst_events = parse_events(DST)
    assert len(dst_events) == 47, f"expected 47 v7 events, got {len(dst_events)}"
    src_plain = {plain_text(e) for e in kept}
    dst_plain = {plain_text(e) for e in dst_events}
    assert src_plain == dst_plain, "regular event text/timings changed!"
    runs = h_runs(out)
    assert runs.get(11, 0) == 0, f"old \\h runs of 11 survive: {dict(runs)}"
    assert runs.get(9, 0) == 47 * 4, f"expected 188 runs of 9, got {runs.get(9)}"
    assert 6 not in runs and 4 not in runs, f"sticker runs survive: {dict(runs)}"
    print("OK: 47 events, text/timings identical to v6 regular events; "
          "side padding 11->9; pad fs -1 top+bottom; sticker events removed.")
    print()
    print("Overlay commands for the v7 render (previews use the same):")
    print("  rain:   overlay=62:-14:enable='between(t,99,104)'")
    print("  coffee: overlay=61:-13:enable='between(t,80,84)'")
    print("  (inputs: sticker-rain-v7.png, sticker-coffee-v7.png)")


if __name__ == "__main__":
    main()
