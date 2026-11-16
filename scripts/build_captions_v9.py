"""Build scan/captions-v9.ass for the v7 re-cut (subtitle system v9).

Supersedes captions-v8.ass. Changes per Aileen 2026-11-15 16:49
(appended to requirements-log.md):

- EN FONT: no more handwriting. CAP_EN / NOTE_EN switch from Caveat to
  DejaVu Sans Bold (normal, slightly bold). CN keeps Ma Shan Zheng
  (she said the Chinese looks fine as is).
- WIDER PADDING: hard-space padding grows from 3 to ~2 words per side
  (CAP 18 x \\h, NOTE 15 x \\h), so the cream box has clear blank space
  on the LEFT and RIGHT of the letters.

Supersedes captions-v6.ass. Changes per Aileen 2026-11-13 19:17 + 19:19
(appended to requirements-log.md):

- STYLE: cream/beige background (opaque warm cream box), BLACK text,
  high contrast, warm/clear/cute. ONE font set for ALL cards now:
  Caveat EN / Ma Shan Zheng CN for captions AND annotations (v6 used
  DejaVu Sans / Noto Sans CJK SC for annotations, which read as a
  different font front-to-back — unified in v7). Ma Shan Zheng has no
  bold weight, so NOTE_CN is Bold=0 like CAP_CN; Caveat has a real
  Bold, so EN stays Bold=1.
- NO OUTLINE: Outline=0 on every style — no stroke/border around the
  glyphs, black text directly on the cream box. (v6 had Outline=3,
  which drew a pale fringe around the letters.)
- WIDER BOX: every line is padded with 3 hard spaces (\\h) on each
  side, so the cream box is longer and all text has visible blank
  space on the LEFT and RIGHT. Box height unchanged.
- COFFEE-MACHINE LABEL (19:19): replaces the small "☕ 咖啡机" label.
  Bigger speaker icon + text "这是咖啡机的声音" (This is the coffee
  machine sound), DejaVu Sans Bold / Noto Sans CJK SC Bold, 40 pt,
  two lines (EN over CN), same t=80-84s window. The 🔊 glyph (U+1F50A)
  was TESTED in this libass build and renders cleanly as a monochrome
  speaker (unlike colour emoji like 🧴, which show as tofu).
- TIMING UNCHANGED (19:17: "the speed is good"): same ~2-3s cards,
  same 2-3-card cycling, same positions.
- LAYOUT: MAX 2 LINES at once (1 EN + 1 CN). Never 4 lines.
  All cards sit at the SAME bottom position (EN MarginV 110, CN 50),
  so the subtitle never jumps around.
- TIMING (17:14 correction — supersedes "longer duration"): each card
  stays for a COMFORTABLE human reading duration (~2-3s, never
  lingering). Within one scene, CYCLE through 2-3 cards in sequence
  while the speech continues — do not leave one subtitle static.
  Title cards ("Talk N") get a shorter weight; content cards get more.
- ANNOTATIONS: where the audio is intelligible, explain HOW they used
  the tool (the process), not just what it is. Talk E is the detailed
  one (verified transcript): tell it your skin -> it remembers you;
  type in your address -> live weather shapes your routine.
- COFFEE MACHINE LABEL: audio analysis (sustained-loudness + spectral
  2-4k/4-8k energy) puts the loudest sustained mechanical noise at
  final-video t=80-84s (Talk E segment, 79-86s). A small label
  "☕ 咖啡机 · coffee machine" shows there, above the subtitle.

Timeline = 20 Inkling video picks + 3 interleaved still photos (Ken Burns).
Segments joined with 0.5s crossfades, so segment k starts at
sum(durations[:k]) - k * 0.5.
"""

import json

XFADE = 0.5
PICKS = "scan/inkling-video-picks-v5.jsonl"
OUT = "scan/captions-v9.ass"

# Hard-space padding per side: ~2 words (CAP 18, NOTE 15, coffee 15).
PAD_CAP = "\\h" * 18
PAD_NOTE = "\\h" * 15

# Warm cream background (opaque). ASS colour is &HAABBGGRR:
# cream RGB(245,230,204) -> BB=CC GG=E6 RR=F5 -> &H00CCE6F5.
CREAM = "&H00CCE6F5"
BLACK = "&H00000000"

# Cards per timeline segment, in order. Each card: (en, cn, kind, weight).
# kind "cap" = Caveat/Ma Shan Zheng (title or plain observation);
# kind "note" = DejaVu Sans Bold / Noto Sans CJK SC Bold (explains what/how).
# weight: relative display time within the segment (title cards are short).
CARDS = [
    # 1  0037 arrival
    [("The day starts here", "一天从这里开始", "cap", 1.0),
     ("Not everyone is here yet", "人还没来齐", "cap", 1.0)],
    # 2  timelapse
    [("One by one, they arrive", "一个接一个，人来了", "cap", 1.0),
     ("The room comes alive", "房间活过来了", "cap", 1.0),
     ("Forty minutes, in eight seconds", "四十分钟，八秒看完", "cap", 1.0)],
    # 3  0027 walking in
    [("Push the door, step inside", "推门进来", "cap", 1.0),
     ("Outside the street, inside the room", "外面是街，里面是房间", "cap", 1.0)],
    # 4  Photo A (green-trees girl)
    [("Under the trees, waiting for it to start", "树下，她在等开场", "cap", 1.0)],
    # 5  0032 hosts (unchanged from v8 — already punchy, per log's host wording)
    [("The friend who came earliest", "来得最早的朋友", "cap", 1.0),
     ("The friend who's been keeping order", "一直维持秩序的朋友", "cap", 1.0)],
    # 6  Photo B (black-hat girl)
    [("Black cap, standing by before it starts", "黑帽子，开场前站住了", "cap", 1.0)],
    # 7  0049 Pairoa — Talk 1 (brand name dropped per 2026-11-15 feedback)
    [("Talk 1", "分享 1", "cap", 0.6),
     ("Demoed live — the room leans in", "现场演示，全场盯着屏幕", "note", 1.0)],
    # 8  0050 Q&A
    [("A hand goes up", "台下有人举手了", "cap", 1.0),
     ("One gesture — that's the answer", "一个手势，就是回答", "cap", 1.0)],
    # 9  0051 laughter — Talk 1
    [("Talk 1", "分享 1", "cap", 0.6),
     ("One demo, and the room is laughing", "一个演示，把全场逗笑了", "cap", 1.0),
     ("The speaker laughs, so does the room", "讲的人笑了，听的人也笑了", "cap", 1.0)],
    # 10 0047 Carl Yang — Talk 2
    [("Talk 2", "分享 2", "cap", 0.6),
     ("Where the Agent era came from", "Agent 时代从哪来", "note", 1.0)],
    # 11 0048 Carl Yang — Talk 2
    [("Talk 2", "分享 2", "cap", 0.6),
     ("Enterprise Harness — how to ship it", "企业级 Harness，怎么落地", "note", 1.0)],
    # 12 0033 Talk A — Talk 3
    [("Talk 3", "分享 3", "cap", 0.6),
     ("Tools born for AI", "为 AI 而生的工具", "note", 1.0)],
    # 13 0007 audience
    [("Back row — phones are up", "后排，手机都举起来了", "cap", 1.0)],
    # 14 0041 Talk R — Talk 4
    [("Talk 4", "分享 4", "cap", 0.6),
     ("A chat app he built himself", "自己做的聊天 App", "note", 1.0),
     ("Phone in hand, demoed live", "拿着手机，现场演示", "note", 1.0)],
    # 15 0042 Talk E — Talk 5 (personal care; verified v8 content, shortened to <=15 chars)
    [("Talk 5", "分享 5", "cap", 0.6),
     ("Personal care — it remembers your skin", "个人护理，记住你的皮肤", "note", 1.0),
     ("Live weather shapes your routine", "按实时天气，调你的护理", "note", 1.0)],
    # 16 0043 Talk F — Talk 6 (AI simulates personas to test products; brand name dropped)
    [("Talk 6", "分享 6", "cap", 0.6),
     ("AI plays your customers for you", "AI 替你扮演你的用户", "note", 1.0),
     ("It knows your brand better than you", "它比你更懂你的品牌", "note", 1.0)],
    # 17 0044 Talk G — Talk 7 (product name dropped)
    [("Talk 7", "分享 7", "cap", 0.6),
     ("Code running in the terminal", "终端里，代码在跑", "note", 1.0),
     ("Typed live, run live", "现场敲代码，现场跑", "note", 1.0)],
    # 18 0049-T Talk T — Talk 8 (product name dropped)
    [("Talk 8", "分享 8", "cap", 0.6),
     ("One dashboard, all the AI news", "一个面板，看遍 AI 新闻", "note", 1.0),
     ("Trends, rankings, a map — all here", "趋势、排名、地图，全在这", "note", 1.0)],
    # 19 0059 Talk M — Talk 9 (on-screen hook, kept as the two-beat)
    [("Talk 9", "分享 9", "cap", 0.6),
     ("Your agents work", "你的 agent 在工作", "note", 1.0),
     ("While you sleep", "而你在睡觉", "note", 1.0)],
    # 20 0062 Q&A
    [("Pointing at the QR, asking", "指着二维码提问", "cap", 1.0),
     ("Talk's over — questions begin", "讲完了，问题来了", "cap", 1.0)],
    # 21 0054 street
    [("Drinks in hand, chatting on their feet", "端着饮料，站着聊", "cap", 1.0),
     ("Between talks, a breather", "两场分享之间，喘口气", "cap", 1.0)],
    # 22 0079 sign-off
    [("At the banner — that's a wrap", "横幅前，散场了", "cap", 1.0)],
    # 23 Photo C (group)
    [("Everyone's here — group photo", "人齐了，拍张大合照", "cap", 1.0)],
]

# Coffee-machine label (19:19): bigger speaker icon + "this is the coffee
# machine sound". Final-video time range where the sustained mechanical
# noise peaks (audio analysis, see report-v5.md). Talk E segment is
# 79-86s; the machine is loudest 80-84s.
COFFEE_LABEL = (80.0, 84.0,
                "🔊 This is the coffee machine sound", "这是咖啡机的声音")

PHOTOS = [
    (2, 3.0),   # after pick #3 (0027) — Photo A
    (3, 3.0),   # after pick #4 (0032) — Photo B
    (19, 4.0),  # after pick #20 (0079) — Photo C, final frame
]


def parse_ts(value):
    parts = [float(p) for p in str(value).split(":")]
    total = 0.0
    for p in parts:
        total = total * 60 + p
    return total


def ass_time(t):
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def main():
    picks = [json.loads(l) for l in open(PICKS, encoding="utf-8") if l.strip()]
    durations = []
    for i, p in enumerate(picks):
        c = p["clip"]
        durations.append(parse_ts(c["end"]) - parse_ts(c["start"]))
        for (after_idx, dur) in PHOTOS:
            if after_idx == i:
                durations.append(dur)
    assert len(durations) == len(CARDS) == 23, (len(durations), len(CARDS))

    lines = []
    lines.append("[Script Info]")
    lines.append("ScriptType: v4.00+")
    lines.append("PlayResX: 1920")
    lines.append("PlayResY: 1080")
    lines.append("WrapStyle: 0")
    lines.append("ScaledBorderAndShadow: yes")
    lines.append("")
    lines.append("[V4+ Styles]")
    lines.append("Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding")
    # Cream box, black text. All cards share the same bottom position
    # (EN MarginV 110, CN MarginV 50) so the subtitle never jumps.
    lines.append(f"Style: CAP_EN,DejaVu Sans,56,{BLACK},&H000000FF,&H00FFFFFF,{CREAM},1,0,0,0,100,100,0,0,4,0,0,2,60,60,110,1")
    lines.append(f"Style: CAP_CN,Ma Shan Zheng,48,{BLACK},&H000000FF,&H00FFFFFF,{CREAM},0,0,0,0,100,100,0,0,4,0,0,2,60,60,50,1")
    lines.append(f"Style: NOTE_EN,DejaVu Sans,38,{BLACK},&H000000FF,&H00FFFFFF,{CREAM},1,0,0,0,100,100,0,0,4,0,0,2,60,60,110,1")
    lines.append(f"Style: NOTE_CN,Ma Shan Zheng,36,{BLACK},&H000000FF,&H00FFFFFF,{CREAM},0,0,0,0,100,100,0,0,4,0,0,2,60,60,50,1")
    # Coffee-machine label: bigger + more prominent (19:19). DejaVu Sans
    # Bold / Noto Sans CJK SC Bold, 40 pt, two lines (EN over CN).
    # The 🔊 glyph (U+1F50A) was tested in this libass build and renders
    # cleanly as a monochrome speaker — keep the label in DejaVu Sans,
    # which is the font the glyph was verified in.
    lines.append(f"Style: COFFEE_EN,DejaVu Sans,40,{BLACK},&H000000FF,&H00FFFFFF,{CREAM},1,0,0,0,100,100,0,0,4,0,0,2,60,60,275,1")
    lines.append(f"Style: COFFEE_CN,Noto Sans CJK SC,40,{BLACK},&H000000FF,&H00FFFFFF,{CREAM},1,0,0,0,100,100,0,0,4,0,0,2,60,60,205,1")
    lines.append("")
    lines.append("[Events]")
    lines.append("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text")
    lines.append("")

    t = 0.0
    n_cards = 0
    for k, cards in enumerate(CARDS):
        dur = durations[k]
        start = t
        end = t + dur
        # Display window: trim the last 0.5s (crossfade) except final segment.
        end_show = end - XFADE if k < len(CARDS) - 1 else end
        window = end_show - start
        total_w = sum(c[3] for c in cards)
        cur = start
        for (en, cn, kind, w) in cards:
            ce = cur + window * (w / total_w)
            en_style = "CAP_EN" if kind == "cap" else "NOTE_EN"
            cn_style = "CAP_CN" if kind == "cap" else "NOTE_CN"
            pad = PAD_CAP if kind == "cap" else PAD_NOTE
            # Pad each line with 3 hard spaces (\\h) on both sides so the
            # cream box is wider than the text (19:17).
            lines.append(f"Dialogue: 0,{ass_time(cur)},{ass_time(ce)},{cn_style},,0,0,0,,{pad}{cn}{pad}")
            lines.append(f"Dialogue: 0,{ass_time(cur)},{ass_time(ce)},{en_style},,0,0,0,,{pad}{en}{pad}")
            cur = ce
            n_cards += 1
        t = end - XFADE

    # Coffee-machine label: two lines (EN over CN), both padded.
    c0, c1, cen, ccn = COFFEE_LABEL
    lines.append(f"Dialogue: 0,{ass_time(c0)},{ass_time(c1)},COFFEE_EN,,0,0,0,,{PAD_NOTE}{cen}{PAD_NOTE}")
    lines.append(f"Dialogue: 0,{ass_time(c0)},{ass_time(c1)},COFFEE_CN,,0,0,0,,{PAD_NOTE}{ccn}{PAD_NOTE}")

    total = sum(durations) - (len(durations) - 1) * XFADE
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Wrote {OUT}: {len(CARDS)} segments, {n_cards} cards, "
          f"coffee label {c0}-{c1}s, final video duration {total:.1f}s")


if __name__ == "__main__":
    main()
