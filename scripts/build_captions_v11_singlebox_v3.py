"""Build captions-v11-singlebox-v3.ass from v2: narrower side padding + deeper cream.

User adjustments (2026-11-16 09:11, on the v2 previews):
  1. NARROWER left/right margins by ~0.5 inch per side: the cream box should
     hug the text more tightly, but KEEP some padding (text must not touch
     the box edge). Measured on the v2 renders: the widest line (EN) has
     165px of \\h padding per side; one \\h at fs36 Liberation Sans is
     ~9.2px, so 0.5 inch (~48px at 96dpi) = ~5 \\h. Change: 18 -> 13 \\h
     per side on every line (NOTE and CAP alike). New EN padding ~119px.
     Vertical padding (blank lines) UNCHANGED.
  2. BACKGROUND 20% MORE OPAQUE: the box fill was measured on the v2
     renders as RGB (246,230,202) = the ASS BackColour &H00CCE6F5 with
     alpha 00, i.e. the box is ALREADY fully opaque — there is no alpha
     left to remove. What reads as "see-through" is the very pale cream.
     Faithful equivalent: deepen the cream 20% (scale each channel by
     0.8) so the box reads as more solid: (245,230,204) -> (196,184,163),
     BackColour &H00CCE6F5 -> &H00A3B8C4, on all three styles. Text,
     timing, fonts, vertical padding unchanged.
"""
import re
import sys

SRC = "scan/captions-v11-singlebox-v2.ass"
DST = "scan/captions-v11-singlebox-v3.ass"

OLD_PAD = 18
NEW_PAD = 13
OLD_BG = "&H00CCE6F5"
NEW_BG = "&H00A3B8C4"  # RGB (196,184,163) = 0.8 * (245,230,204)


def main():
    with open(SRC, encoding="utf-8") as f:
        src = f.read()

    # 1. Side padding: runs of exactly 18 \h -> 13 \h. Single \h (blank
    #    lines) are untouched: the regex requires exactly 18 in a row.
    out, n_pad = re.subn(r"(?:\\h){18}", lambda m: "\\h" * NEW_PAD, src)
    # 2. Box background: deepen cream 20% on all styles.
    out, n_bg = re.subn(re.escape(OLD_BG), NEW_BG, out)

    with open(DST, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"padding runs changed: {n_pad}, BackColour changed: {n_bg} -> {DST}")

    # 3. Fidelity check: strip overrides + \h, compare text/timing v2 vs v3.
    def plain(path):
        pairs = []
        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.startswith("Dialogue:"):
                    p = line[len("Dialogue:"):].split(",", 9)
                    t = re.sub(r"\{[^}]*\}", "", p[9]).replace("\\h", "").replace("\\N", "|")
                    pairs.append((p[1], p[2], p[3], t))
        return pairs

    a, b = plain(SRC), plain(DST)
    assert len(a) == len(b), f"event count differs: {len(a)} vs {len(b)}"
    mism = [(x, y) for x, y in zip(a, b) if x != y]
    print(f"Text/timing fidelity: {len(a)} events, {len(mism)} mismatches")
    if mism:
        for x, y in mism[:5]:
            print("  V2:", x)
            print("  V3:", y)
        sys.exit(1)

    # 4. Structural checks.
    with open(DST, encoding="utf-8") as f:
        dst = f.read()
    assert OLD_BG not in dst, "old BackColour still present!"
    assert dst.count(NEW_BG) == 3, f"expected 3 new BackColours, got {dst.count(NEW_BG)}"
    assert not re.search(r"(?:\\h){18}", dst), "an 18-\\h run survived!"
    # every event must still have its blank-line single \h top and bottom
    n_events = dst.count("Dialogue:")
    assert dst.count("\\N") == 3 * n_events, "line-break structure changed!"
    # padding runs of 13: 4 per event (CN left/right, EN left/right)
    runs13 = len(re.findall(r"(?:\\h){13}", dst))
    assert runs13 == 4 * n_events, f"expected {4*n_events} 13-\\h runs, got {runs13}"
    print(f"OK: {n_events} events, 13-\\h side padding everywhere, cream deepened 20%")
    print("NOTE: v2 box was already fully opaque (alpha 00); 20% applied as colour deepening.")


if __name__ == "__main__":
    main()
