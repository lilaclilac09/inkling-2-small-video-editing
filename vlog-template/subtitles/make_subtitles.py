#!/usr/bin/env python3
"""Build an ASS subtitle file from a captions list, in one of the named styles.

Input captions JSON: a list of objects, each:
  {"start": 3.0, "end": 8.5, "en": "The room laughs", "cn": "全场都笑了"}
  start/end are seconds (float). "en" and/or "cn" — at least one required.
  Optional "title": true marks a segment title (rendered larger).

Styles live in styles.json next to this script:
  cute       — handwritten vlog (Caveat EN / Ma Shan Zheng CN, warm white)
  clean      — tech talk (DejaVu Sans / Noto Sans CJK SC, no box)
  bilingual  — EN line over CN line on a semi-transparent box

Usage:
  python3 make_subtitles.py --captions captions.json --style cute --out out.ass
  python3 make_subtitles.py --captions captions.json --style bilingual --out out.ass

Burn onto video with ffmpeg (libass):
  ffmpeg -i body.mp4 -vf "subtitles=out.ass" -c:a copy body-sub.mp4
"""

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def ass_time(t):
    """Seconds (float) -> ASS timestamp H:MM:SS.cc."""
    t = max(0.0, float(t))
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def esc(text):
    """Escape ASS override braces; keep the text otherwise verbatim."""
    return text.replace("{", "\\{").replace("}", "\\}")


def style_block(name, s, play_res):
    """One ASS V4+ style line from a style dict."""
    def line(lang, suffix=""):
        d = s[lang]
        return (
            f"Style: {name}{suffix},{d['font']},{d['size']},"
            f"{d['color']},{d['color']},{d['outline_color']},"
            f"{d.get('back_color', '&H80000000')},"
            f"{-1 if d.get('bold') else 0},0,0,0,100,100,0,0,"
            f"{d['border_style']},{d['outline']},{d['shadow']},"
            f"{s['alignment']},10,10,{s['margin_v']},1"
        )
    # EN and CN get their own styles; the bilingual event uses inline {\fn} tags.
    return line("en", ""), line("cn", "CN")


def build_ass(captions, style_name, styles):
    if style_name not in styles:
        raise ValueError(f"unknown style {style_name!r}; choices: {sorted(styles)}")
    s = styles[style_name]
    w, h = s["play_res"]
    en_style, cn_style = style_block("Vlog", s, (w, h))

    out = []
    out.append("[Script Info]")
    out.append("ScriptType: v4.00+")
    out.append(f"PlayResX: {w}")
    out.append(f"PlayResY: {h}")
    out.append("ScaledBorderAndShadow: yes")
    out.append("")
    out.append("[V4+ Styles]")
    out.append(
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
        "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, "
        "ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
        "Alignment, MarginL, MarginR, MarginV, Encoding"
    )
    out.append(en_style)
    out.append(cn_style)
    out.append("")
    out.append("[Events]")
    out.append("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text")

    for cap in captions:
        start = ass_time(cap["start"])
        end = ass_time(cap["end"])
        en = esc(cap.get("en", "").strip())
        cn = esc(cap.get("cn", "").strip())
        if not en and not cn:
            continue
        title = cap.get("title", False)
        if style_name == "bilingual" and en and cn:
            # One event, two lines, each in its own font via inline tags.
            en_fs = s["en"]["size"] + (6 if title else 0)
            cn_fs = s["cn"]["size"] + (4 if title else 0)
            text = (
                f"{{\\fn{s['en']['font']}\\fs{en_fs}}}{en}"
                f"\\N{{\\fn{s['cn']['font']}\\fs{cn_fs}}}{cn}"
            )
            out.append(f"Dialogue: 0,{start},{end},Vlog,,0,0,0,,{text}")
        elif en and cn:
            # Non-bilingual styles: EN and CN as two stacked events.
            out.append(f"Dialogue: 0,{start},{end},Vlog,,0,0,0,,{en}")
            out.append(f"Dialogue: 0,{start},{end},VlogCN,,0,0,0,,{cn}")
        elif en:
            out.append(f"Dialogue: 0,{start},{end},Vlog,,0,0,0,,{en}")
        else:
            out.append(f"Dialogue: 0,{start},{end},VlogCN,,0,0,0,,{cn}")
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser(description="Build an ASS subtitle file in a named style.")
    ap.add_argument("--captions", required=True, help="captions JSON list")
    ap.add_argument("--style", default="cute", choices=["cute", "clean", "bilingual"],
                    help="subtitle style (default: cute)")
    ap.add_argument("--out", required=True, help="output .ass path")
    args = ap.parse_args()

    with open(os.path.join(HERE, "styles.json"), encoding="utf-8") as f:
        styles = json.load(f)
    with open(args.captions, encoding="utf-8") as f:
        captions = json.load(f)

    ass = build_ass(captions, args.style, styles)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(ass)
    n = len([c for c in captions if c.get("en") or c.get("cn")])
    print(f"wrote {args.out}: style={args.style}, {n} caption events")
    return 0


if __name__ == "__main__":
    sys.exit(main())
