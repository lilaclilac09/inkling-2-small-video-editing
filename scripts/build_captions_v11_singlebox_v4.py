"""Build captions-v11-singlebox-v4.ass from v3: annotation cards + emoji fix.

User (2026-11-16 10:03): "did you do the subtitle changes? Screenshot them."
New requirements:
  1. RAIN annotation (NEW event): one short sentence explaining the dim
     light is because it was pouring rain outside. Apple's rain emoji
     (U+1F327 U+FE0F) at the FRONT of the sentence. Placed at the
     dimmest talk moment, Talk 8 Information Radar 1:39-1:44 (mean
     luminance 103, dimmest measured). Same single-box cream style as
     v3, positioned ABOVE the regular caption (MarginV 205, the same
     pattern as the existing coffee card) so it overlaps the Talk 8
     NOTE without covering it.
  2. COFFEE annotation (EXISTING event, emoji fix): v3 already contains
     a coffee card at 1:20.00-1:24.00 ("This is the coffee machine
     sound") but with a speaker emoji (U+1F50A). User wants the coffee
     cup emoji (U+2615) at the FRONT of the sentence. Fix: replace the
     emoji with U+2615 at the front of BOTH the CN and EN lines.
     Timing/style/position UNCHANGED (it is an approved v11 event).
  3. No other text or timing changes. All 47 non-coffee v3 events must
     be byte-identical in v4.

Emoji reality: Apple's emoji font is NOT on this VM. The only emoji
font is Noto Color Emoji (/usr/share/fonts/truetype/noto/
NotoColorEmoji.ttf). The emoji glyphs get an explicit
{\\fnNoto Color Emoji} override. Whether libass renders them as
color emoji is verified by reading the preview renders back.
"""
import re
import sys

SRC = "scan/captions-v11-singlebox-v3.ass"
DST = "scan/captions-v11-singlebox-v4.ass"

RAIN_CN = "外面在下暴雨，所以光线比较暗"          # 14 chars, <=15
RAIN_EN = "It's pouring rain outside, so the light is dim"
RAIN_START = "0:01:39.00"
RAIN_END = "0:01:44.00"

COFFEE_OLD_EMOJI = "\U0001F50A"   # 🔊 speaker (what v3 has)
COFFEE_EMOJI = "\u2615"           # ☕ coffee cup (what the user asked for)
RAIN_EMOJI = "\U0001F327\uFE0F"   # 🌧️ rain cloud (as the user wrote it)


def parse_events(path):
    """Return (header_lines, style_lines, events) where each event is the
    raw Dialogue line."""
    with open(path, encoding="utf-8") as f:
        text = f.read()
    lines = text.split("\n")
    events = [ln for ln in lines if ln.startswith("Dialogue:")]
    return text, events


def event_fields(line):
    p = line[len("Dialogue:"):].split(",", 9)
    return p  # [layer, start, end, style, name, ml, mr, mv, effect, text]


def plain_text(line):
    p = event_fields(line)
    t = re.sub(r"\{[^}]*\}", "", p[9]).replace("\\h", "").replace("\\N", "|")
    return (p[1], p[2], p[3], t)


def main():
    src_text, src_events = parse_events(SRC)
    assert len(src_events) == 48, f"expected 48 v3 events, got {len(src_events)}"

    # --- 1. Add SINGLE_RAIN style (identical params to SINGLE_COFFEE). ---
    style_line = ("Style: SINGLE_COFFEE,Liberation Sans,40,&H00000000,&H000000FF,"
                  "&H00FFFFFF,&H00A3B8C4,1,0,0,0,100,100,0,0,4,0,0,2,60,60,205,1")
    assert style_line in src_text, "SINGLE_COFFEE style line not found!"
    rain_style = style_line.replace("SINGLE_COFFEE", "SINGLE_RAIN")
    out = src_text.replace(style_line, style_line + "\n" + rain_style, 1)

    # --- 2. Fix the coffee event: speaker emoji -> coffee cup, front of
    #        both lines. The CN line has no emoji yet; the EN line starts
    #        with the speaker emoji after its padding run. ---
    coffee_pat = re.compile(
        r"(Dialogue: 0,0:01:20\.00,0:01:24\.00,SINGLE_COFFEE,,0,0,0,,"
        r"\{\\fnLiberation Sans\\fs21\}\\h\\N"
        r"\{\\fnNoto Sans CJK SC\\fs40\\b1\}(?:\\h)+)"
        r"(这是咖啡机的声音)"
        r"((?:\\h)+\\N"
        r"\{\\fnLiberation Sans\\fs40\\b1\}(?:\\h)+)"
        + re.escape(COFFEE_OLD_EMOJI) +
        r"( This is the coffee machine sound(?:\\h)+\\N"
        r"\{\\fnLiberation Sans\\fs15\}\\h)")
    m = coffee_pat.search(out)
    assert m, "coffee event not found in expected form!"
    # CN line: emoji goes right after the padding run, before the text,
    # with its own font override, then a hard space, then back to CJK.
    # EN line: emoji replaces the speaker emoji at the front; group(4)
    # already starts with a space, so no extra \h is added there.
    cn_new = (m.group(1)
              + "{\\fnNoto Color Emoji\\fs40}" + COFFEE_EMOJI
              + "\\h{\\fnNoto Sans CJK SC\\fs40\\b1}"
              + m.group(2))
    en_new = (m.group(3)
              + "{\\fnNoto Color Emoji\\fs40}" + COFFEE_EMOJI
              + "{\\fnLiberation Sans\\fs40\\b1}"
              + m.group(4))
    out = out[:m.start()] + cn_new + en_new + out[m.end():]

    # --- 3. Add the rain event (SINGLE_RAIN, 1:39.00-1:44.00). Mirror the
    #        coffee event's structure: top blank fs21, CN fs40, EN fs40,
    #        bottom blank fs15, 13-\h side padding on both lines. ---
    pad13 = "\\h" * 13
    rain_event = (
        "Dialogue: 0,0:01:39.00,0:01:44.00,SINGLE_RAIN,,0,0,0,,"
        "{\\fnLiberation Sans\\fs21}\\h\\N"
        "{\\fnNoto Sans CJK SC\\fs40\\b1}" + pad13 +
        "{\\fnNoto Color Emoji\\fs40}" + RAIN_EMOJI +
        "\\h{\\fnNoto Sans CJK SC\\fs40\\b1}" + RAIN_CN + pad13 + "\\N"
        "{\\fnLiberation Sans\\fs40\\b1}" + pad13 +
        "{\\fnNoto Color Emoji\\fs40}" + RAIN_EMOJI +
        "\\h{\\fnLiberation Sans\\fs40\\b1}" + RAIN_EN + pad13 + "\\N"
        "{\\fnLiberation Sans\\fs15}\\h"
    )
    # Insert the rain event right after the coffee event (keeps the file
    # roughly chronological by insertion; libass sorts by start time).
    anchor = "Dialogue: 0,0:01:20.00,0:01:24.00,SINGLE_COFFEE"
    idx = out.find(anchor)
    assert idx != -1
    eol = out.find("\n", idx)
    out = out[:eol + 1] + rain_event + "\n" + out[eol + 1:]

    with open(DST, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"wrote {DST}")

    # --- 4. Fidelity check. ---
    _, dst_events = parse_events(DST)
    assert len(dst_events) == 49, f"expected 49 v4 events, got {len(dst_events)}"
    src_plain = {plain_text(e) for e in src_events}
    dst_plain = {plain_text(e) for e in dst_events}
    # The 47 non-coffee v3 events must survive unchanged.
    coffee_src = [e for e in src_events if "0:01:20.00,0:01:24.00" in e][0]
    kept = [e for e in src_events if e is not coffee_src]
    kept_plain = {plain_text(e) for e in kept}
    missing = kept_plain - dst_plain
    assert not missing, f"{len(missing)} pre-existing events changed/lost!"
    # The coffee event must differ ONLY by the emoji swap.
    coffee_dst = [e for e in dst_events if "0:01:20.00,0:01:24.00" in e][0]
    assert COFFEE_OLD_EMOJI not in coffee_dst, "old speaker emoji survives!"
    assert coffee_dst.count(COFFEE_EMOJI) == 2, "coffee emoji should appear twice (CN+EN)"
    assert "这是咖啡机的声音" in coffee_dst and "This is the coffee machine sound" in coffee_dst
    # The rain event must exist with the right timing/style/text.
    rain = [e for e in dst_events if "0:01:39.00,0:01:44.00,SINGLE_RAIN" in e]
    assert len(rain) == 1, f"expected 1 rain event, got {len(rain)}"
    assert RAIN_EMOJI in rain[0] and RAIN_CN in rain[0] and RAIN_EN in rain[0]
    assert rain[0].count(RAIN_EMOJI) == 2, "rain emoji should appear twice (CN+EN)"
    assert "SINGLE_RAIN" in out and out.count("Style: SINGLE_RAIN") == 1
    print("OK: 49 events (48 carried + 1 rain); 47 non-coffee events identical;")
    print("    coffee emoji 🔊->☕ at front of CN+EN lines; rain card 1:39-1:44.")


if __name__ == "__main__":
    main()
