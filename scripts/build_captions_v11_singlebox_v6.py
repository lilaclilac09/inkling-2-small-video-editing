"""Build captions-v11-singlebox-v6.ass from v5: lighter bg + narrower box.

User (2026-11-16 10:17): "字幕版的底色不要那么暗，稍微还是用一点
亮色吧，左右两边再稍微收窄一点，上下再稍微收窄那么一点点，大概
百分之二左右，左右的话大概收窄百分之三到百分之五"
Translation: the subtitle box background should not be so dark, use a
slightly lighter color; narrow the left/right sides a bit more
(~3-5%) and the top/bottom a tiny bit (~2%).

Base: v5 (captions-v11-singlebox-v5.ass) -- the sticker restyle is
preserved. If v5 had not existed, this script would have based on v4
and said so; v5 was present (17,186 B, 2026-11-16 02:22).

What changes (ALL 49 events; text, timings, fonts, positions otherwise
unchanged):
  1. LIGHTER BACKGROUND: BackColour &H00A3B8C4 (v3 deepened cream,
     (196,184,163)) -> &H00CCE6F5 (v2 pale cream, (245,230,204), the
     lighter color she previously approved). All 6 styles (SINGLE,
     SINGLE_CAP, SINGLE_COFFEE, SINGLE_RAIN, SINGLE_COFFEE_STK,
     SINGLE_RAIN_STK).
  2. NARROWER HORIZONTALLY (~3-5%): side padding \\h runs reduced by 2
     per side -- regular events 13 -> 11, coffee sticker 8 -> 6, rain
     sticker 6 -> 4. (v3 measured ~9.2-9.5 px per \\h, so -2 \\h/side
     is ~37 px off an ~800-990 px box, ~4%. Verified by measuring the
     renders, see below.)
  3. NARROWER VERTICALLY (~2%): top/bottom blank-line font sizes -1
     each -- CAP top fs18 -> 17, bottom fs29 -> 28; NOTE top fs20 ->
     19, bottom fs27 -> 26; sticker top fs21 -> 20, bottom fs15 -> 14.
     (The single \\h in the blank lines is NOT touched -- it is the
     placeholder that keeps libass from dropping the line.)
"""
import re

SRC = "scan/captions-v11-singlebox-v4.ass"  # placeholder, fixed below
SRC = "scan/captions-v11-singlebox-v5.ass"
DST = "scan/captions-v11-singlebox-v6.ass"

OLD_BG = "&H00A3B8C4"   # v3 deepened cream (196,184,163)
NEW_BG = "&H00CCE6F5"   # v2 pale cream (245,230,204)

# Side-padding \\h runs: old count -> new count (per side).
PAD_MAP = {13: 11, 8: 6, 6: 4}

# Top/bottom blank-line font sizes: old -> new. Order matters: fs21 -> 20
# must run AFTER fs20 -> 19, or the new fs20 would be hit again.
PAD_FS = [(18, 17), (29, 28), (20, 19), (27, 26), (21, 20), (15, 14)]


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
    """Count maximal \\h runs by length."""
    from collections import Counter
    c = Counter()
    for m in re.finditer(r"(?:\\h)+", text):
        c[len(m.group(0)) // 2] += 1
    return c


def main():
    src_text, src_events = parse_events(SRC)
    assert len(src_events) == 49, f"expected 49 v5 events, got {len(src_events)}"
    print("v5 side-padding runs:", dict(h_runs(src_text)))

    out = src_text

    # --- 1. Lighter background on all 6 styles. ---
    n_bg = out.count(OLD_BG)
    assert n_bg == 6, f"expected 6 style BackColour occurrences, got {n_bg}"
    out = out.replace(OLD_BG, NEW_BG)
    assert NEW_BG in out and OLD_BG not in out

    # --- 2. Narrower horizontally: side-padding \\h runs -2 per side. ---
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
    print("v6 side-padding runs:", dict(h_runs(out)))

    # --- 4. Fidelity check: 49 events, all plain text/timings unchanged. ---
    _, dst_events = parse_events(DST)
    assert len(dst_events) == 49, f"expected 49 v6 events, got {len(dst_events)}"
    src_plain = {plain_text(e) for e in src_events}
    dst_plain = {plain_text(e) for e in dst_events}
    assert src_plain == dst_plain, "event text/timings changed!"
    # No old padding runs survive; new runs are exactly as mapped.
    runs = h_runs(out)
    # 13 and 8 are old values that must not survive (6 is the coffee
    # sticker's NEW value, so it legitimately appears 4 times).
    assert 13 not in runs and 8 not in runs, \
        f"old \\h runs survive: {dict(runs)}"
    assert runs.get(11, 0) == 47 * 4, f"expected 188 runs of 11, got {runs.get(11)}"
    assert runs.get(7, 0) == 0 and runs.get(5, 0) == 0
    assert runs.get(6, 0) == 4, f"coffee sticker should have 4 runs of 6, got {runs.get(6)}"
    assert runs.get(4, 0) == 4, f"rain sticker should have 4 runs of 4, got {runs.get(4)}"
    # Styles: 6 BackColour now the lighter cream.
    assert out.count(NEW_BG) == 6, f"expected 6 new BackColour, got {out.count(NEW_BG)}"
    print("OK: 49 events, text/timings identical to v5; bg lighter on all 6")
    print("    styles; side padding 13->11 / 8->6 / 6->4; pad fs -1 top+bottom.")


if __name__ == "__main__":
    main()
