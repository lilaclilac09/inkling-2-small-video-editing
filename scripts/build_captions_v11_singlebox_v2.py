"""Build captions-v11-singlebox-v2.ass from v1: new fonts + symmetric padding.

Font changes (user 2026-11-15 22:05, on the Talk 8 preview):
  - CN: Ma Shan Zheng (calligraphic, "too complicated") -> Noto Sans CJK SC.
    NOTE: XiLiuTi is NOT obtainable from any legitimate free source.
    Two web searches found only: Xylitol (unrelated Latin font), commercial
    Founder LiuTi fonts (not free), and a .mtz mobile-font repack
    (wrong format, dubious source). No XiLiuTi on GitHub. Noto Sans CJK SC
    is open-licensed, simple and clean — exactly the simple look asked for.
  - EN: DejaVu Sans Bold -> Liberation Sans Bold. San Francisco is
    Apple-proprietary and not on this Linux VM; Helvetica/Arial also absent.
    Liberation Sans is Arial-metric-compatible = the closest Apple-common
    (Helvetica/Arial) look available here.

Padding fix (user: top and bottom padding must be symmetric):
  In v1 the blank lines were bare \\N. The TOP blank line rendered in the
  style's default font (DejaVu Sans fs40 NOTE / fs48 CAP) while the BOTTOM
  blank line rendered in the EN override font (fs36 NOTE / fs56 CAP) — so
  NOTE had top 40pt vs bottom 36pt, CAP had top 48pt vs bottom 56pt.
  Asymmetric in opposite directions. Fix: put an explicit identical
  {\\fnLiberation Sans\\fs<SIZE>} override on BOTH blank lines, SIZE = the
  CN size (40 NOTE / 48 CAP / 40 COFFEE), so top and bottom padding are
  exactly equal. Text, timings, positions, colors, box style unchanged.
"""
import re
import sys

SRC = "scan/captions-v11-singlebox.ass"
DST = "scan/captions-v11-singlebox-v2.ass"

CN_NEW = "Noto Sans CJK SC"
EN_NEW = "Liberation Sans"

# style -> blank-line font size (= CN size for that kind)
BLANK_SIZE = {"SINGLE": 40, "SINGLE_CAP": 48, "SINGLE_COFFEE": 40}


def main():
    with open(SRC, encoding="utf-8") as f:
        src_text = f.read()

    # 1. Header: style default font DejaVu Sans -> Liberation Sans.
    out_text, n_hdr = re.subn(r"DejaVu Sans", EN_NEW, src_text.split("[Events]")[0])
    header, events = src_text.split("[Events]", 1)
    header = re.sub(r"DejaVu Sans", EN_NEW, header)

    lines = events.splitlines()
    new_lines = []
    n_ev = 0
    for line in lines:
        if not line.startswith("Dialogue:"):
            new_lines.append(line)
            continue
        parts = line[len("Dialogue:"):].split(",", 9)
        style = parts[3]
        text = parts[9]
        size = BLANK_SIZE[style]
        # 2. CN font: Ma Shan Zheng -> Noto Sans CJK SC (sizes unchanged).
        text = text.replace("\\fnMa Shan Zheng", f"\\fn{CN_NEW}")
        # 3. EN font: DejaVu Sans -> Liberation Sans (sizes unchanged).
        text = text.replace("\\fnDejaVu Sans", f"\\fn{EN_NEW}")
        # 4. Symmetric padding: explicit identical override on both blank lines.
        #    Leading blank line: text starts with \N
        assert text.startswith("\\N"), f"unexpected text start at {parts[1]}: {text[:40]}"
        text = f"{{\\fn{EN_NEW}\\fs{size}}}" + text
        #    Trailing blank line: text ends with \N
        assert text.endswith("\\N"), f"unexpected text end at {parts[1]}: {text[-40:]}"
        text = text[:-2] + f"{{\\fn{EN_NEW}\\fs{size}}}\\N"
        parts[9] = text
        new_lines.append("Dialogue:" + ",".join(parts))
        n_ev += 1

    with open(DST, "w", encoding="utf-8") as f:
        f.write(header + "[Events]" + "\n".join(new_lines) + "\n")
    print(f"Transformed {n_ev} events -> {DST}")

    # 5. Mechanical fidelity check: strip overrides + \h, compare CN/EN text
    #    and timings between v1 and v2.
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
            print("  V1:", x)
            print("  V2:", y)
        sys.exit(1)
    # 6. Confirm no Ma Shan Zheng / DejaVu Sans remains, and blank lines carry overrides.
    with open(DST, encoding="utf-8") as f:
        dst = f.read()
    assert "Ma Shan Zheng" not in dst, "Ma Shan Zheng still present!"
    assert "DejaVu Sans" not in dst, "DejaVu Sans still present!"
    assert dst.count("\\fnLiberation Sans\\fs40}\\N") + dst.count("\\fnLiberation Sans\\fs48}\\N") == 2 * len(a), \
        "blank-line overrides missing somewhere"
    print("OK: no old fonts remain; every event has identical top+bottom blank-line overrides")


if __name__ == "__main__":
    main()
