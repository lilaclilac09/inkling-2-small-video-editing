"""Convert captions-v11.ass (two-box) to single-box format.

Mechanical conversion only: merge each CN+EN pair (same Start/End) into ONE
Dialogue event with a single cream box (BorderStyle=4). CN on top (Ma Shan
Zheng), EN below (DejaVu Sans Bold), separated by \\N, with blank-line
padding top/bottom and \\h side padding. Timings, positions and text are
kept exactly as in v11 — nothing is reworded.

Sizes follow the approved mockup (subtitle-style-mockup.png, v9 text):
  NOTE:   CN Ma Shan Zheng fs40, EN DejaVu Sans Bold fs36
  CAP:    CN Ma Shan Zheng fs48, EN DejaVu Sans Bold fs56 (v11 CAP sizes)
  COFFEE: CN Noto Sans CJK SC fs40 Bold, EN DejaVu Sans Bold fs40 (v11 sizes)
Positions: NOTE/CAP box bottom at MarginV 50 (v11 CN position);
COFFEE box bottom at MarginV 205 (v11 COFFEE_CN position).
"""
import re
import sys

SRC = "scan/captions-v11.ass"
DST = "scan/captions-v11-singlebox.ass"

# (card kind, cn font, cn size, cn bold, en font, en size, en bold, style name)
SPECS = {
    "NOTE": ("Ma Shan Zheng", 40, 0, "DejaVu Sans", 36, 1, "SINGLE"),
    "CAP": ("Ma Shan Zheng", 48, 0, "DejaVu Sans", 56, 1, "SINGLE_CAP"),
    "COFFEE": ("Noto Sans CJK SC", 40, 1, "DejaVu Sans", 40, 1, "SINGLE_COFFEE"),
}

HEADER = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: SINGLE,DejaVu Sans,40,&H00000000,&H000000FF,&H00FFFFFF,&H00CCE6F5,1,0,0,0,100,100,0,0,4,0,0,2,60,60,50,1
Style: SINGLE_CAP,DejaVu Sans,48,&H00000000,&H000000FF,&H00FFFFFF,&H00CCE6F5,1,0,0,0,100,100,0,0,4,0,0,2,60,60,50,1
Style: SINGLE_COFFEE,DejaVu Sans,40,&H00000000,&H000000FF,&H00FFFFFF,&H00CCE6F5,1,0,0,0,100,100,0,0,4,0,0,2,60,60,205,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def strip_h(text):
    """Remove leading/trailing \\h padding, return plain text."""
    return text.replace("\\h", "")


def main():
    with open(SRC, encoding="utf-8") as f:
        lines = f.read().splitlines()

    events = []  # (start, end, style, text)
    for line in lines:
        if not line.startswith("Dialogue:"):
            continue
        # Dialogue: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
        parts = line[len("Dialogue:"):].split(",", 9)
        layer, start, end, style = parts[0], parts[1], parts[2], parts[3]
        text = parts[9]
        events.append((start, end, style, text))

    # Group into pairs by (start, end): one _CN and one _EN per pair,
    # order may be CN-first (CAP/NOTE) or EN-first (COFFEE).
    pairs = []
    i = 0
    while i < len(events):
        start, end, style, text = events[i]
        kind = style.rsplit("_", 1)[0]  # CAP / NOTE / COFFEE
        assert i + 1 < len(events), f"unpaired event at {start}"
        s2, e2, style2, text2 = events[i + 1]
        assert (s2, e2) == (start, end), f"pair timing mismatch at {start}"
        assert style2.rsplit("_", 1)[0] == kind, f"pair kind mismatch at {start}"
        by_lang = {style.rsplit("_", 1)[1]: text,
                   style2.rsplit("_", 1)[1]: text2}
        assert set(by_lang) == {"CN", "EN"}, f"pair not CN+EN at {start}: {style}, {style2}"
        pairs.append((start, end, kind, strip_h(by_lang["CN"]), strip_h(by_lang["EN"])))
        i += 2

    print(f"Parsed {len(events)} events -> {len(pairs)} pairs")
    kinds = {}
    for _, _, kind, _, _ in pairs:
        kinds[kind] = kinds.get(kind, 0) + 1
    print("Pairs by kind:", kinds)

    out = [HEADER.rstrip("\n")]
    PAD = "\\h" * 18
    for start, end, kind, cn, en in pairs:
        cn_font, cn_size, cn_bold, en_font, en_size, en_bold, sty = SPECS[kind]
        cb = "\\b1" if cn_bold else "\\b0"
        eb = "\\b1" if en_bold else "\\b0"
        # Blank line top + bottom for vertical padding inside the box.
        text = (
            f"\\N{{\\fn{cn_font}\\fs{cn_size}{cb}}}{PAD}{cn}{PAD}"
            f"\\N{{\\fn{en_font}\\fs{en_size}{eb}}}{PAD}{en}{PAD}\\N"
        )
        out.append(f"Dialogue: 0,{start},{end},{sty},,0,0,0,,{text}")

    with open(DST, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print(f"Wrote {DST} with {len(pairs)} single-box events")


if __name__ == "__main__":
    main()
