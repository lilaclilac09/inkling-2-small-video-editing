"""Build captions-v11-singlebox-v9.ass from v7.

User (2026-11-16 11:41, replying to the v8 previews): "玩一会儿字幕就
简单的字幕就行了，就最开始的那个。今天最开始的，在我教你把左右
两边缩百分之五之后和上下再缩百分之一，百分之三就用那一版，然后
去掉其他的注释，把这个全部写到后面的字幕里面去。"
Translation: stop iterating on the subtitles -- go back to the SIMPLE
single-box style from the start of today (the version after narrowing
L/R 5% and T/B 1-3%), remove the separate annotations (stickers), and
fold all of that content into the regular subtitle track.

What changes in THIS file:
  1. Base = v7 (single-box cream, CN+EN together in one box,
     BorderStyle=4, BackColour &H00CCE6F5, Alignment 2 bottom-center).
     The v7 narrowing is KEPT as-is: side padding 9 \\h per side
     (L/R ~5%), top/bottom blank-line font sizes already -1 (T/B ~2%).
     The v8 white-text-no-box style is NOT used.
  2. The two v7 sticker overlays (sticker-rain-v7.png /
     sticker-coffee-v7.png) are REMOVED -- no overlays in v9.
  3. The two annotations are folded into the regular caption track as
     extra lines inside the SAME single-box cream caption at that
     timestamp (not separate events, not stickers):
       * Coffee note "这是咖啡机的声音 / This is the coffee machine
         sound" (was 1:20-1:24) is folded into the "你的护肤柜，记住
         你的皮肤" event (1:20.50-1:23.00) -- the main caption covering
         most of that window. The box now has 4 lines: talk CN+EN,
         then note CN+EN. The coffee note shows 1:20.50-1:23.00
         (2.5s of the 4s window); the neighbouring "分享 5" title
         (1:19-1:20.50) and "按实时天气" (1:23-1:25.50) are untouched.
       * Rain note "外面在下暴雨，所以光线比较暗 / It's pouring rain
         outside, so the light is dim" (was 1:39-1:44) is folded into
         the "信息雷达，创业情报全在这" event (1:39.00-1:44.00) --
         the EXACT same window. The box now has 4 lines: talk CN+EN,
         then note CN+EN.
     No emoji on the folded notes (kept simple, per the user's
     "simple" instruction; the v4/v5 emoji lived on the separate
     cards/stickers, which are gone).
  4. The other 45 events are BYTE-IDENTICAL to v7 (text + timings).
     Total stays 47 events.
"""
import re

SRC = "scan/captions-v11-singlebox-v7.ass"
DST = "scan/captions-v11-singlebox-v9.ass"

PAD = "\\h" * 9  # side padding per side (v7 narrowing, kept)

# (match_start, match_text_snippet, note_cn, note_en)
FOLDS = [
    ("0:01:20.50", "你的护肤柜，记住你的皮肤",
     "这是咖啡机的声音", "This is the coffee machine sound"),
    ("0:01:39.00", "信息雷达，创业情报全在这",
     "外面在下暴雨，所以光线比较暗",
     "It's pouring rain outside, so the light is dim"),
]

BOTTOM_BLANK = "{\\fnLiberation Sans\\fs25}\\h"


def parse_events(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    events = [ln for ln in text.split("\n") if ln.startswith("Dialogue:")]
    return text, events


def plain_text(line):
    p = line[len("Dialogue:"):].split(",", 9)
    t = re.sub(r"\{[^}]*\}", "", p[9]).replace("\\h", "").replace("\\N", "|")
    return (p[1], p[2], p[3], t)


def main():
    src_text, src_events = parse_events(SRC)
    assert len(src_events) == 47, f"expected 47 v7 events, got {len(src_events)}"

    out = src_text
    folded = []
    for start, snippet, note_cn, note_en in FOLDS:
        hits = [e for e in src_events
                if e.split(",", 3)[1] == start and snippet in e]
        assert len(hits) == 1, f"expected 1 event at {start} with {snippet!r}, got {len(hits)}"
        old = hits[0]
        assert old.endswith(BOTTOM_BLANK), "unexpected event tail"
        block = ("\\N{\\fnNoto Sans CJK SC\\fs40\\b0}" + PAD + note_cn + PAD
                 + "\\N{\\fnLiberation Sans\\fs36\\b1}" + PAD + note_en + PAD)
        new = old[: -len(BOTTOM_BLANK)] + block + "\\N" + BOTTOM_BLANK
        assert out.count(old) == 1
        out = out.replace(old, new)
        folded.append((start, snippet, note_cn))
        print(f"folded note into {start} ({snippet}): + {note_cn}")

    with open(DST, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"wrote {DST}")

    # --- Fidelity checks. ---
    dst_text, dst_events = parse_events(DST)
    assert len(dst_events) == 47, f"expected 47 v9 events, got {len(dst_events)}"
    # 45 events byte-identical to v7; the 2 folded ones differ only by the
    # added note lines (same start/end/style, same talk text).
    src_by_start = {}
    for e in src_events:
        src_by_start[e.split(",", 3)[1]] = e
    identical = 0
    for e in dst_events:
        start = e.split(",", 3)[1]
        if e == src_by_start[start]:
            identical += 1
    assert identical == 45, f"expected 45 byte-identical events, got {identical}"
    # The folded events still carry the original talk text and timing.
    for start, snippet, note_cn, note_en in FOLDS:
        e = [x for x in dst_events if x.split(",", 3)[1] == start][0]
        assert snippet in e and note_cn in e and note_en in e
        assert e.split(",", 3)[2] == [x for x in src_events
                                       if x.split(",", 3)[1] == start][0].split(",", 3)[2]
    # No sticker events, side padding still 9 per side.
    assert "SINGLE_RAIN_STK" not in dst_text.split("[Events]")[1]
    assert "SINGLE_COFFEE_STK" not in dst_text.split("[Events]")[1]
    from collections import Counter
    runs = Counter()
    for m in re.finditer(r"(?:\\h)+", dst_text.split("[Events]")[1]):
        runs[len(m.group(0)) // 2] += 1
    assert runs.get(11, 0) == 0, f"old \\h runs of 11 survive: {dict(runs)}"
    print("OK: 47 events; 45 byte-identical to v7; 2 folded with notes;")
    print("    side padding 9/side (L/R ~5%), pad fs -1 (T/B ~2%);")
    print("    no sticker events; single-box cream style kept.")
    print()
    print("Preview method: ffmpeg -copyts, -ss before -i, ass filter,")
    print("one frame each (over recap-v6-another-season.mp4):")
    print("  Talk 1 @ 0:33, Talk 8 @ 1:41, Talk 5 @ 1:22.")


if __name__ == "__main__":
    main()
