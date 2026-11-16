"""Build captions-v11-singlebox-v8.ass from v7.

User (2026-11-16 11:00, replying to the v7 previews): "不要放米白色的框，
就用白色的字体在上半部分或者是居中的位置写一个就行了"
Translation: do NOT put a cream/beige box; just use WHITE TEXT, in the
upper half or in a centered position.

What changes in THIS file (regular captions only):
  1. NO background box: BorderStyle 4 -> 1 (outline+shadow, no box).
     PrimaryColour black -> WHITE (&H00FFFFFF); OutlineColour white ->
     BLACK (&H00000000) so the text reads on bright backgrounds.
     Outline 0 -> 2, Shadow 0 -> 2 (subtle dark halo, legibility only --
     NOT a box). BackColour set to black (unused for BorderStyle=1).
  2. POSITION: Alignment 2 (bottom-center) -> 8 (top-center), MarginV
     50 -> 250. The caption block now sits in the UPPER HALF
     (y ~250-400), horizontally centered.
  3. STICKER CLEARANCE (measured): the v7 sticker PNGs' visible
     content (incl. shadow) spans rain x 78-962 / y 5-226 and coffee
     x 76-871 / y 5-198. MarginV=250 puts the caption top 24px below
     the rain sticker's lowest pixel (226), so NO regular caption
     collides with either sticker -- nothing is shifted to the bottom.
  4. The two sticker overlays (sticker-rain-v7.png /
     sticker-coffee-v7.png + sticker-overlay-v7.json) are UNCHANGED.
  5. All 47 Dialogue lines are BYTE-IDENTICAL to v7 (text + timings).
     Only the [V4+ Styles] SINGLE / SINGLE_CAP lines change.
     (SINGLE_COFFEE / SINGLE_RAIN / SINGLE_*_STK styles are unused in
     v7 -- no Dialogue event references them -- and are left as-is.)

Preview method (same as v7): ffmpeg -copyts, -ss before -i, ass filter
+ overlay filter, one frame each:
  Talk 1 @ 0:33, Talk 8 @ 1:41 (rain sticker + regular caption),
  Talk 5 @ 1:22 (coffee sticker + regular caption).
"""
import re  # noqa: F401 (kept for parity)

SRC = "scan/captions-v11-singlebox-v7.ass"
DST = "scan/captions-v11-singlebox-v8.ass"

# Style fields (V4+ Styles format):
# Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour,
# BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing,
# Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR,
# MarginV, Encoding
NEW_STYLE = {
    # name: (PrimaryColour, OutlineColour, BackColour, BorderStyle,
    #        Outline, Shadow, Alignment, MarginV)
    "SINGLE":     ("&H00FFFFFF", "&H00000000", "&H00000000", 1, 2, 2, 8, 250),
    "SINGLE_CAP": ("&H00FFFFFF", "&H00000000", "&H00000000", 1, 2, 2, 8, 250),
}


def parse_events(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    events = [ln for ln in text.split("\n") if ln.startswith("Dialogue:")]
    return text, events


def restyle_line(line, pri, outl, back, bs, ol, sh, al, mv):
    """Rewrite one V4+ Style line by field index (robust, no regex)."""
    f = line.split(",")
    assert len(f) == 23, f"unexpected Style field count {len(f)}: {line}"
    # 0 Name, 1 Fontname, 2 Fontsize, 3 Primary, 4 Secondary, 5 Outline,
    # 6 Back, 7 Bold, 8 Italic, 9 Underline, 10 StrikeOut, 11 ScaleX,
    # 12 ScaleY, 13 Spacing, 14 Angle, 15 BorderStyle, 16 Outline,
    # 17 Shadow, 18 Alignment, 19 MarginL, 20 MarginR, 21 MarginV,
    # 22 Encoding
    f[3] = pri
    f[5] = outl
    f[6] = back
    f[15] = str(bs)
    f[16] = str(ol)
    f[17] = str(sh)
    f[18] = str(al)
    f[21] = str(mv)
    return ",".join(f)


def main():
    src_text, src_events = parse_events(SRC)
    assert len(src_events) == 47, f"expected 47 v7 events, got {len(src_events)}"

    lines = src_text.split("\n")
    for i, ln in enumerate(lines):
        for name, (pri, outl, back, bs, ol, sh, al, mv) in NEW_STYLE.items():
            if ln.startswith(f"Style: {name},"):
                lines[i] = restyle_line(ln, pri, outl, back, bs, ol, sh, al, mv)
                print(f"restyled {name}: white text, BorderStyle=1, "
                      f"outline={ol} shadow={sh}, align={al} top, MarginV={mv}")
    out = "\n".join(lines)

    with open(DST, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"wrote {DST}")

    # --- Fidelity checks. ---
    dst_text, dst_events = parse_events(DST)
    assert len(dst_events) == 47, f"expected 47 v8 events, got {len(dst_events)}"
    assert src_events == dst_events, "Dialogue lines changed! (must be byte-identical)"
    # Style checks.
    for name in NEW_STYLE:
        line = [ln for ln in dst_text.split("\n")
                if ln.startswith(f"Style: {name},")][0]
        f = line.split(",")
        assert f[3] == "&H00FFFFFF", f"{name} PrimaryColour not white: {f[3]}"
        assert f[5] == "&H00000000", f"{name} OutlineColour not black: {f[5]}"
        assert f[15] == "1", f"{name} BorderStyle not 1: {f[15]}"
        assert f[16] == "2" and f[17] == "2", f"{name} outline/shadow: {f[16]}/{f[17]}"
        assert f[18] == "8", f"{name} Alignment not 8 (top-center): {f[18]}"
        assert f[21] == "250", f"{name} MarginV not 250: {f[21]}"
    print("OK: 47 events byte-identical to v7; SINGLE/SINGLE_CAP now white "
          "text, no box, top-center, MarginV=250.")
    print()
    print("Sticker clearance: rain sticker content ends y=226, coffee y=198;")
    print("caption top at MarginV=250 -> 24px clear of the rain sticker,")
    print("no collision, no caption shifted. Stickers unchanged (v7 PNGs).")


if __name__ == "__main__":
    main()
