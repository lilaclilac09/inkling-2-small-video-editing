"""Build scan/captions-v6.ass for the v5 story cut (subtitle system v6).

Supersedes captions-v5.ass. Changes per Aileen 2026-11-13 17:09 + 17:14
(appended to requirements-log.md):

- STYLE: cream/beige background (opaque warm cream box), BLACK text,
  high contrast, warm/clear/cute. Caveat EN / Ma Shan Zheng CN for
  captions, DejaVu Sans Bold / Noto Sans CJK SC Bold for annotations.
  (Colour emoji do NOT render in this libass build — they show as tofu
  boxes, tested twice. The monochrome coffee glyph U+2615 DOES render
  cleanly in DejaVu Sans, so the coffee-machine label uses it.)
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
  The coffee-machine label shows there, above the subtitle.

Timeline = 20 Inkling video picks + 3 interleaved still photos (Ken Burns).
Segments joined with 0.5s crossfades, so segment k starts at
sum(durations[:k]) - k * 0.5.
"""

import json

XFADE = 0.5
PICKS = "scan/inkling-video-picks-v5.jsonl"
OUT = "scan/captions-v6.ass"

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
    [("Yanqing Road in the morning", "早上的延庆路", "cap", 1.0),
     ("The café, before the talks begin", "演讲开始前的咖啡馆", "cap", 1.0)],
    # 2  timelapse
    [("The room fills, one chair at a time", "座位一个一个坐满", "cap", 1.0),
     ("Paper lanterns, a glowing screen", "纸灯笼，亮着的屏幕", "cap", 1.0),
     ("Forty minutes, in eight seconds", "四十分钟，浓缩成八秒", "cap", 1.0)],
    # 3  0027 walking in
    [("Through the glass doors", "穿过玻璃门", "cap", 1.0),
     ("The street, the trees, the door", "街道、梧桐、门口", "cap", 1.0)],
    # 4  Photo A (green-trees girl)
    [("A drink, a tablet, under the plane trees", "一杯饮料，一块平板，梧桐树下", "cap", 1.0)],
    # 5  0032 hosts
    [("The friend who came earliest", "来得最早的朋友", "cap", 1.0),
     ("The friend who kept order", "维持秩序的朋友", "cap", 1.0)],
    # 6  Photo B (black-hat girl)
    [("Black cap, arms crossed, by the banner", "黑帽子，抱着胳膊，横幅旁", "cap", 1.0)],
    # 7  0049 Pairoa — Talk 1
    [("Talk 1", "分享 1", "cap", 0.6),
     ("Pairoa, demoed live", "Pairoa，现场演示", "note", 1.0)],
    # 8  0050 Q&A
    [("A question from the floor", "台下有人提问", "cap", 1.0),
     ("Answered with a gesture", "一个手势作答", "cap", 1.0)],
    # 9  0051 laughter — Talk 1
    [("Talk 1", "分享 1", "cap", 0.6),
     ("The demo gets a laugh", "演示引来了一阵笑声", "cap", 1.0),
     ("A light-blue shirt, a live demo", "浅蓝衬衫，现场演示", "cap", 1.0)],
    # 10 0047 Carl Yang — Talk 2
    [("Talk 2", "分享 2", "cap", 0.6),
     ("The Agent era — a history", "Agent 时代——一段历史", "note", 1.0)],
    # 11 0048 Carl Yang — Talk 2
    [("Talk 2", "分享 2", "cap", 0.6),
     ("and enterprise Harness solutions", "以及企业级 Harness 方案", "note", 1.0)],
    # 12 0033 Talk A — Talk 3
    [("Talk 3", "分享 3", "cap", 0.6),
     ("AI-native tools, on the screen", "屏幕上是 AI 原生工具", "note", 1.0)],
    # 13 0007 audience
    [("Listening, from the back row", "后排的听众", "cap", 1.0)],
    # 14 0041 Talk R — Talk 4
    [("Talk 4", "分享 4", "cap", 0.6),
     ("A chat app", "一个聊天 App", "note", 1.0),
     ("Demoed live from his phone", "用手机现场演示", "note", 1.0)],
    # 15 0042 Talk E — Talk 5 (HOW, from the verified transcript)
    [("Talk 5", "分享 5", "cap", 0.6),
     ("Personal care — it remembers your skin", "个人护理——它记住你的皮肤", "note", 1.0),
     ("Type in your address — live weather shapes your routine",
      "输入你的地址——实时天气来调整日常护理", "note", 1.0)],
    # 16 0043 Talk F — Talk 6
    [("Talk 6", "分享 6", "cap", 0.6),
     ("Agents that work for your brand", "为品牌工作的智能体", "note", 1.0),
     ("It knows more than you remember", "它比你更了解你的品牌", "note", 1.0)],
    # 17 0044 Talk G — Talk 7
    [("Talk 7", "分享 7", "cap", 0.6),
     ("Terminal code, on the screen", "屏幕上是终端代码", "note", 1.0),
     ("CREWCLAW, in the terminal", "终端里的 CREWCLAW", "note", 1.0)],
    # 18 0049-T Talk T — Talk 8
    [("Talk 8", "分享 8", "cap", 0.6),
     ("Information Radar", "信息雷达", "note", 1.0),
     ("AI news, in one dashboard", "AI 新闻，集中在一个面板", "note", 1.0)],
    # 19 0059 Talk M — Talk 9
    [("Talk 9", "分享 9", "cap", 0.6),
     ("Your agents work", "你的 agent 在工作", "note", 1.0),
     ("You are sleeping", "你在睡觉", "note", 1.0)],
    # 20 0062 Q&A
    [("A finger at the QR codes", "手指着二维码", "cap", 1.0),
     ("Questions, after the talk", "分享结束后的提问", "cap", 1.0)],
    # 21 0054 street
    [("Four people, drinks in hand", "四个人，手里拿着饮料", "cap", 1.0),
     ("Chatting between talks", "两场分享之间的闲聊", "cap", 1.0)],
    # 22 0079 sign-off
    [("At the banner, the day ends", "横幅前，一天结束", "cap", 1.0)],
    # 23 Photo C (group)
    [("The group, at the door", "门口的大合照", "cap", 1.0)],
]

# Coffee-machine label: final-video time range where the sustained
# mechanical noise peaks (audio analysis, see report-v5.md).
# Talk E segment is 79-86s; the machine is loudest 80-84s.
COFFEE_LABEL = (80.0, 84.0, "☕ 咖啡机 · coffee machine")

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
    lines.append(f"Style: CAP_EN,Caveat,56,{BLACK},&H000000FF,&H00FFFFFF,{CREAM},1,0,0,0,100,100,0,0,4,3,0,2,60,60,110,1")
    lines.append(f"Style: CAP_CN,Ma Shan Zheng,48,{BLACK},&H000000FF,&H00FFFFFF,{CREAM},0,0,0,0,100,100,0,0,4,3,0,2,60,60,50,1")
    lines.append(f"Style: NOTE_EN,DejaVu Sans,38,{BLACK},&H000000FF,&H00FFFFFF,{CREAM},1,0,0,0,100,100,0,0,4,3,0,2,60,60,110,1")
    lines.append(f"Style: NOTE_CN,Noto Sans CJK SC,36,{BLACK},&H000000FF,&H00FFFFFF,{CREAM},1,0,0,0,100,100,0,0,4,3,0,2,60,60,50,1")
    # Coffee-machine label: small, above the subtitle (MarginV 200).
    lines.append(f"Style: COFFEE,DejaVu Sans,28,{BLACK},&H000000FF,&H00FFFFFF,{CREAM},1,0,0,0,100,100,0,0,4,2,0,2,60,60,200,1")
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
            lines.append(f"Dialogue: 0,{ass_time(cur)},{ass_time(ce)},{cn_style},,0,0,0,,{cn}")
            lines.append(f"Dialogue: 0,{ass_time(cur)},{ass_time(ce)},{en_style},,0,0,0,,{en}")
            cur = ce
            n_cards += 1
        t = end - XFADE

    # Coffee-machine label.
    c0, c1, ctext = COFFEE_LABEL
    lines.append(f"Dialogue: 0,{ass_time(c0)},{ass_time(c1)},COFFEE,,0,0,0,,{ctext}")

    total = sum(durations) - (len(durations) - 1) * XFADE
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Wrote {OUT}: {len(CARDS)} segments, {n_cards} cards, "
          f"coffee label {c0}-{c1}s, final video duration {total:.1f}s")


if __name__ == "__main__":
    main()
