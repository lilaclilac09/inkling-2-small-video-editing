"""Build captions-v11-singlebox-v5.ass from v4: annotation cards -> stickers.

User (2026-11-16 10:16, replying to the v4 previews): "加的这行字要么
放在顶上，不要遮住人脸，不要放最下面，不要重新单开一行字幕，就是
斜着放或者随意摆一下，像贴纸一样，加粗一点字体，emoji 还可以。"
Translation: the added annotation lines go at the TOP, must not cover
any face, not at the very bottom, NOT as a separate subtitle row --
instead placed at a slight angle / casually, like a sticker, with a
bolder font. The emoji is fine as-is (monochrome Noto Color Emoji is
acceptable, no color needed).

What changes (ONLY the two annotation events; the other 47 v11 events
must be byte-identical to v4):
  1. TOP placement via \\pos (new styles use Alignment 8 = top-center,
     so \\pos(x,y) is the box's top-center point).
  2. STICKER STYLE: \\frz rotation (-4 deg rain, -3 deg coffee), cream
     box kept (BorderStyle=4) so it reads as a sticker, Shadow=3 for a
     soft drop shadow.
  3. BOLDER font: rain fs40 -> fs42, coffee fs40 -> fs44 (both already
     \\b1). Rain cannot go to fs44: its EN line would make the box
     ~1064px wide, which hits the paper lantern (left edge x~1042) in
     the Talk 8 frame. Coffee fits fs44 easily.
  4. TIGHTER side padding so the boxes fit the face-free top zones:
     rain 13\\h -> 6\\h per side (~990px box), coffee 13\\h -> 8\\h
     (~860px box). Emoji unchanged (same glyph, same position at the
     front of each line).

Placement evidence (frames read 2026-11-16, 1920x1080):
  - RAIN (Talk 8 @ 1:41): speaker face ~x390-510, y630-770; screen
    top y~310; picture frame x870-1670, y0-110 (wall art, NOT a face);
    lantern left edge x~1042. Sticker: \\pos(515,45), box ~990x135,
    rotated -4 deg -> spans x~19-1017, lowest corner ~(11,215) on the
    shelf unit (cups, no faces). Clears the lantern by ~25px. It DOES
    overlap the picture frame's bottom-left corner (x870-1017, y~10-110)
    -- that is wall art, not a face; unavoidable at this width, and
    reported honestly. No face is covered.
  - COFFEE (Talk 5 @ 1:22): speaker (green cap) face ~x200-420,
    y300-500, cap top y~230; screen top y~200 (x590-1460); lantern
    left edge x~1171. Sticker: \\pos(470,35), box ~860x140, rotated
    -3 deg -> spans x~34-906, lowest corner ~(34,197), clears the cap
    top (y230) by ~33px and the screen top (y200) by ~47px. No face
    is covered; nothing else is touched.
"""
import re

SRC = "scan/captions-v11-singlebox-v4.ass"
DST = "scan/captions-v11-singlebox-v5.ass"

RAIN_EMOJI = "\U0001F327\uFE0F"   # 🌧️ (unchanged from v4)
COFFEE_EMOJI = "\u2615"           # ☕ (unchanged from v4)
RAIN_CN = "外面在下暴雨，所以光线比较暗"
RAIN_EN = "It's pouring rain outside, so the light is dim"
COFFEE_CN = "这是咖啡机的声音"
COFFEE_EN = "This is the coffee machine sound"


def parse_events(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    events = [ln for ln in text.split("\n") if ln.startswith("Dialogue:")]
    return text, events


def plain_text(line):
    p = line[len("Dialogue:"):].split(",", 9)
    t = re.sub(r"\{[^}]*\}", "", p[9]).replace("\\h", "").replace("\\N", "|")
    return (p[1], p[2], p[3], t)


def sticker_event(start, end, style, pos, frz, fs, pad, emoji, cn, en):
    """One two-line sticker event: \\pos + \\frz, top blank fs21, CN fs,
    EN fs, bottom blank fs15. Same cream box (BorderStyle=4) as v4."""
    pad_h = "\\h" * pad
    return (
        f"Dialogue: 0,{start},{end},{style},,0,0,0,,"
        f"{{\\pos{pos}\\frz{frz}}}{{\\fnLiberation Sans\\fs21}}\\h\\N"
        f"{{\\fnNoto Sans CJK SC\\fs{fs}\\b1}}{pad_h}"
        f"{{\\fnNoto Color Emoji\\fs{fs}}}{emoji}"
        f"\\h{{\\fnNoto Sans CJK SC\\fs{fs}\\b1}}{cn}{pad_h}\\N"
        f"{{\\fnLiberation Sans\\fs{fs}\\b1}}{pad_h}"
        f"{{\\fnNoto Color Emoji\\fs{fs}}}{emoji}"
        f"\\h{{\\fnLiberation Sans\\fs{fs}\\b1}}{en}{pad_h}\\N"
        f"{{\\fnLiberation Sans\\fs15}}\\h"
    )


def main():
    src_text, src_events = parse_events(SRC)
    assert len(src_events) == 49, f"expected 49 v4 events, got {len(src_events)}"

    # --- 1. Add the two sticker styles (Alignment 8 = top-center so
    #        \\pos(x,y) is the box's top-center; Shadow=3 soft shadow;
    #        same deeper cream BackColour as v4). ---
    base_style = ("Style: SINGLE,Liberation Sans,40,&H00000000,&H000000FF,"
                  "&H00FFFFFF,&H00A3B8C4,1,0,0,0,100,100,0,0,4,0,0,2,60,60,50,1")
    assert base_style in src_text, "SINGLE style line not found!"
    rain_style = ("Style: SINGLE_RAIN_STK,Liberation Sans,42,&H00000000,&H000000FF,"
                  "&H00FFFFFF,&H00A3B8C4,1,0,0,0,100,100,0,0,4,0,3,8,60,60,50,1")
    coffee_style = ("Style: SINGLE_COFFEE_STK,Liberation Sans,44,&H00000000,&H000000FF,"
                    "&H00FFFFFF,&H00A3B8C4,1,0,0,0,100,100,0,0,4,0,3,8,60,60,50,1")
    out = src_text.replace(base_style,
                           base_style + "\n" + rain_style + "\n" + coffee_style, 1)

    # --- 2. Replace the rain event (1:39-1:44) with the sticker version. ---
    rain_old = [e for e in src_events if "0:01:39.00,0:01:44.00,SINGLE_RAIN" in e]
    assert len(rain_old) == 1, "rain event not found!"
    rain_new = sticker_event("0:01:39.00", "0:01:44.00", "SINGLE_RAIN_STK",
                             "(515,45)", -4, 42, 6,
                             RAIN_EMOJI, RAIN_CN, RAIN_EN)
    out = out.replace(rain_old[0], rain_new, 1)

    # --- 3. Replace the coffee event (1:20-1:24) with the sticker version. ---
    coffee_old = [e for e in src_events if "0:01:20.00,0:01:24.00,SINGLE_COFFEE" in e]
    assert len(coffee_old) == 1, "coffee event not found!"
    coffee_new = sticker_event("0:01:20.00", "0:01:24.00", "SINGLE_COFFEE_STK",
                               "(470,35)", -3, 44, 8,
                               COFFEE_EMOJI, COFFEE_CN, COFFEE_EN)
    out = out.replace(coffee_old[0], coffee_new, 1)

    with open(DST, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"wrote {DST}")

    # --- 4. Fidelity check: 49 events; the other 47 byte-identical. ---
    _, dst_events = parse_events(DST)
    assert len(dst_events) == 49, f"expected 49 v5 events, got {len(dst_events)}"
    changed_src = {plain_text(e) for e in (rain_old[0], coffee_old[0])}
    kept = [e for e in src_events if plain_text(e) not in changed_src]
    assert len(kept) == 47, f"expected 47 untouched events, got {len(kept)}"
    kept_plain = {plain_text(e) for e in kept}
    dst_plain = {plain_text(e) for e in dst_events}
    missing = kept_plain - dst_plain
    assert not missing, f"{len(missing)} pre-existing events changed/lost!"
    # The two new events must carry the sticker markup and the same text.
    rain = [e for e in dst_events if "0:01:39.00,0:01:44.00,SINGLE_RAIN_STK" in e]
    coffee = [e for e in dst_events if "0:01:20.00,0:01:24.00,SINGLE_COFFEE_STK" in e]
    assert len(rain) == 1 and len(coffee) == 1
    for ev, emoji, cn, en in ((rain[0], RAIN_EMOJI, RAIN_CN, RAIN_EN),
                              (coffee[0], COFFEE_EMOJI, COFFEE_CN, COFFEE_EN)):
        assert "\\pos" in ev and "\\frz" in ev, "sticker markup missing!"
        assert ev.count(emoji) == 2, "emoji should appear twice (CN+EN)"
        assert cn in ev and en in ev, "annotation text changed!"
    assert out.count("Style: SINGLE_RAIN_STK") == 1
    assert out.count("Style: SINGLE_COFFEE_STK") == 1
    print("OK: 49 events; 47 untouched byte-identical; rain+coffee restyled")
    print("    as top stickers (rain fs42 \\pos(515,45) \\frz-4; coffee fs44")
    print("    \\pos(470,35) \\frz-3; emoji unchanged).")


if __name__ == "__main__":
    main()
