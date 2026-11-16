"""Build captions-v11-singlebox-v10.ass from v9.

User (2026-11-16 12:21, replying to the v9 rain preview): "每次字幕保持
在两行，一行中文一行英文" -- every subtitle must stay at exactly TWO
lines: one line Chinese, one line English.

Problem: v9 folded the rain and coffee notes into the talk caption box,
making 4-line boxes. That violates the 2-line rule.

Fix in v10:
  1. Un-fold the 2 v9 events: restore them to 2-line talk-only captions
     (CN + EN), same text as v7/v9.
  2. The notes become their own SEPARATE regular caption events in the
     same single-box cream style (SINGLE, CN fs40 + EN fs36, bottom
     centre, L/R ~5% and T/B ~2% narrowing), NOT stickers, NOT folded
     into the talk box.
  3. No two boxes on screen at once: the note and the talk SEQUENCE
     inside the same window -- talk first, then note. Talk stays synced
     to speech onset; the note follows as an aside:
       * Coffee: talk  1:20.50-1:21.75, note 1:21.75-1:23.00 (1.25s each)
       * Rain:   talk  1:39.00-1:41.50, note 1:41.50-1:44.00 (2.5s each)
  4. The other 45 events are BYTE-IDENTICAL to v9 (and to v7).
     Total: 47 + 2 new note events = 49 events.

Preview frames (ffmpeg -copyts, -ss before -i, ass filter, over
recap-v6-another-season.mp4):
  Talk 1 @ 0:33 (a normal 2-line caption);
  rain NOTE @ 1:42 -- inside the note window 1:41.50-1:44.00, so the
    frame shows the note as its own 2-line caption (1:41 would still
    show the talk, which ends 1:41.50);
  coffee NOTE @ 1:22 -- inside the note window 1:21.75-1:23.00.
"""
import re

SRC = "scan/captions-v11-singlebox-v9.ass"
DST = "scan/captions-v11-singlebox-v10.ass"

PAD = "\\h" * 9  # side padding per side (v7/v9 narrowing, kept)

# (talk_start, talk_snippet, note_cn, note_en, talk_new_end, note_start,
#  note_end)
SPLITS = [
    ("0:01:20.50", "你的护肤柜，记住你的皮肤",
     "这是咖啡机的声音", "This is the coffee machine sound",
     "0:01:21.75", "0:01:21.75", "0:01:23.00"),
    ("0:01:39.00", "信息雷达，创业情报全在这",
     "外面在下暴雨，所以光线比较暗",
     "It's pouring rain outside, so the light is dim",
     "0:01:41.50", "0:01:41.50", "0:01:44.00"),
]

BOTTOM_BLANK = "{\\fnLiberation Sans\\fs25}\\h"
TOP_BLANK = "{\\fnLiberation Sans\\fs18}\\h"


def to_cs(t):
    h, m, s = t.split(":")
    return int(h) * 360000 + int(m) * 6000 + int(round(float(s) * 100))


def parse_events(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    events = [ln for ln in text.split("\n") if ln.startswith("Dialogue:")]
    return text, events


def fields(line):
    return line.split(",", 9)


def note_event(start, end, cn, en):
    text = (TOP_BLANK
            + "\\N{\\fnNoto Sans CJK SC\\fs40\\b0}" + PAD + cn + PAD
            + "\\N{\\fnLiberation Sans\\fs36\\b1}" + PAD + en + PAD
            + "\\N" + BOTTOM_BLANK)
    return f"Dialogue: 0,{start},{end},SINGLE,,0,0,0,,{text}"


def main():
    src_text, src_events = parse_events(SRC)
    assert len(src_events) == 47, f"expected 47 v9 events, got {len(src_events)}"

    new_events = []
    notes_made = []
    for start, snippet, note_cn, note_en, talk_end, n_start, n_end in SPLITS:
        hits = [e for e in src_events
                if fields(e)[1] == start and snippet in e]
        assert len(hits) == 1, f"expected 1 event at {start} with {snippet!r}"
        old = hits[0]
        # Un-fold: the note block starts at the second CN override carrying
        # the note text; everything before it is the talk-only event.
        block_start = ("\\N{\\fnNoto Sans CJK SC\\fs40\\b0}" + PAD + note_cn)
        idx = old.find(block_start)
        assert idx > 0, f"note block not found in {start} event"
        assert old.endswith("\\N" + BOTTOM_BLANK), "unexpected event tail"
        talk = old[:idx] + BOTTOM_BLANK
        # Talk keeps its text, ends early; note follows in the same window.
        f = fields(talk)
        assert f[2] != talk_end, "talk end already split?"
        f[2] = talk_end
        talk = ",".join(f)
        new_events.append(talk)
        notes_made.append(note_event(n_start, n_end, note_cn, note_en))
        print(f"split {start}: talk -> {talk_end}, note {n_start}-{n_end}")

    # The other 45 events pass through unchanged.
    split_starts = {s[0] for s in SPLITS}
    rest = [e for e in src_events if fields(e)[1] not in split_starts]
    assert len(rest) == 45, f"expected 45 untouched events, got {len(rest)}"
    all_events = rest + new_events + notes_made
    # Chronological order (stable; no ties).
    all_events.sort(key=lambda e: to_cs(fields(e)[1]))
    assert len(all_events) == 49, f"expected 49 v10 events, got {len(all_events)}"

    head, sep, tail = src_text.partition("[Events]\n")
    assert sep, "no [Events] section"
    fmt_line, _, _ = tail.partition("\n")
    out = head + sep + fmt_line + "\n" + "\n".join(all_events) + "\n"
    with open(DST, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"wrote {DST}")

    # --- Fidelity checks. ---
    dst_text, dst_events = parse_events(DST)
    assert len(dst_events) == 49, f"expected 49 v10 events, got {len(dst_events)}"
    # 45 events byte-identical to v9.
    src_by_start = {fields(e)[1]: e for e in src_events}
    identical = sum(1 for e in dst_events
                    if e == src_by_start.get(fields(e)[1], None))
    assert identical == 45, f"expected 45 byte-identical events, got {identical}"
    # Every event is exactly 2 visible text lines (1 CN + 1 EN).
    for e in dst_events:
        text = fields(e)[9]
        plain = re.sub(r"\{[^}]*\}", "", text).replace("\\h", "")
        lines = [ln for ln in plain.split("\\N") if ln.strip()]
        assert len(lines) == 2, (
            f"event {fields(e)[1]} has {len(lines)} visible lines: {lines}")
    # No two events overlap in time.
    spans = sorted((to_cs(fields(e)[1]), to_cs(fields(e)[2])) for e in dst_events)
    for (s1, e1), (s2, e2) in zip(spans, spans[1:]):
        assert e1 <= s2, f"overlap: {s1}-{e1} vs {s2}-{e2}"
    # The notes exist as their own events with the right text/timing.
    for start, snippet, note_cn, note_en, talk_end, n_start, n_end in SPLITS:
        ne = [e for e in dst_events if fields(e)[1] == n_start]
        assert len(ne) == 1 and note_cn in ne[0] and note_en in ne[0]
        assert fields(ne[0])[2] == n_end
        te = [e for e in dst_events if fields(e)[1] == start]
        assert len(te) == 1 and snippet in te[0] and note_cn not in te[0]
        assert fields(te[0])[2] == talk_end
    print("OK: 49 events; 45 byte-identical to v9; 2 talks restored to 2 lines")
    print("    + 2 notes as their own 2-line events; every event exactly 2 lines;")
    print("    no overlaps; single-box cream style kept (L/R ~5%, T/B ~2%).")
    print()
    print("Preview method: ffmpeg -copyts, -ss before -i, ass filter,")
    print("one frame each (over recap-v6-another-season.mp4):")
    print("  Talk 1 @ 0:33, rain NOTE @ 1:42, coffee NOTE @ 1:22.")


if __name__ == "__main__":
    main()
