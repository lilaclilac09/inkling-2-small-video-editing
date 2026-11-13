"""Build scan/captions-v5.ass for the v5 story cut.

Timeline = 20 Inkling video picks + 3 interleaved still photos (Ken Burns):
  - Photo A (green-trees girl, 0054 frame-0003) after pick #3 (walking in).
  - Photo B (black-hat girl HM5A1822) after pick #4 (hosts).
  - Photo C (group HM5A1478) after pick #20 (sign-off), the final frame.

Caption style (Aileen 2026-11-13 15:39-15:40): restrained, cultured,
understated. Describe what is happening plainly and specifically.
Do NOT hype the atmosphere/vibe ("warmest moment", "whole room laughs",
"everyone leaning in" are all out).
Talk segments are numbered "Talk N" / "Share N" in STORY order
(important first), not by their original letter.
Non-talk segments get one observant, specific line.
Fonts: Caveat EN 52pt / Ma Shan Zheng CN 46pt, semi-transparent box
(same as v3 — the font was fine, only the words were brainless).

Timing: each caption spans its segment in the final video. Segments are
joined with 0.5s crossfades, so segment k starts at
sum(durations[:k]) - k * 0.5 and ends at start + duration (the last
0.5s overlaps the next segment's start, matching the v3 convention of
ending each caption 0.5s before the segment's nominal end where the
next caption begins).
"""

import json

XFADE = 0.5

PICKS = "scan/inkling-video-picks-v5.jsonl"

# (en, cn) per timeline segment, in order.
# Talks are numbered in story order:
#   Talk 1 = Talk L (Pairoa, picks #5 + #7), Talk 2 = Talk S (Carl Yang,
#   picks #8 + #9), Talk 3 = Talk A, Talk 4 = Talk R, Talk 5 = Talk E,
#   Talk 6 = Talk F, Talk 7 = Talk G, Talk 8 = Talk T, Talk 9 = Talk M.
CAPTIONS = [
    ("Yanqing Road in the morning", "早上的延庆路"),                       # 1  0037 arrival
    ("The room fills, one chair at a time", "座位一个一个坐满"),           # 2  timelapse
    ("Through the glass doors", "穿过玻璃门"),                            # 3  0027 walking in
    ("A drink, a tablet, under the plane trees", "一杯饮料，一块平板，梧桐树下"),  # 4  Photo A
    ("The hosts — one came earliest, one kept order", "主持人——一位来得最早，一位维持着秩序"),  # 5  0032 hosts
    ("Black cap, arms crossed, by the banner", "黑帽子，抱着胳膊，横幅旁"),  # 6  Photo B
    ("Talk 1", "分享 1"),                                                # 7  0049 Pairoa
    ("A question, answered with a gesture", "一个问题，一个手势作答"),      # 8  0050 Q&A
    ("Talk 1", "分享 1"),                                                # 9  0051 laughter (Talk L)
    ("Talk 2", "分享 2"),                                                # 10 0047 Carl Yang
    ("Talk 2", "分享 2"),                                                # 11 0048 Carl Yang
    ("Talk 3", "分享 3"),                                                # 12 0033 Talk A
    ("Filming from the seats", "坐在座位上拍"),                           # 13 0007 audience
    ("Talk 4", "分享 4"),                                                # 14 0041 Talk R
    ("Talk 5", "分享 5"),                                                # 15 0042 Talk E
    ("Talk 6", "分享 6"),                                                # 16 0043 Talk F
    ("Talk 7", "分享 7"),                                                # 17 0044 Talk G
    ("Talk 8", "分享 8"),                                                # 18 0049 Talk T
    ("Talk 9", "分享 9"),                                                # 19 0059 Talk M
    ("A finger at the QR codes", "手指着二维码"),                          # 20 0062 Q&A
    ("Four people, drinks in hand", "四个人，手里拿着饮料"),               # 21 0054 street
    ("At the banner, the day ends", "横幅前，一天结束"),                    # 22 0079 sign-off
    ("The group, at the door", "门口的大合照"),                            # 23 Photo C
]

# App-intro annotations, keyed by 0-based timeline segment index.
# Added only where the audio is intelligible enough OR the screen text is
# legible enough to say what the thing is and what it is for.
# Skipped (audio garbled/hallucinated AND screen too vague for a purpose):
#   Talk 1 Pairoa (landing page, purpose unclear), Talk 3 (screen only says
#   "AI-native tools"), Talk 7 CREWCLAW (terminal code, purpose unclear).
# Talk E is VERIFIED from a faster-whisper transcript (skincare app).
ANNOTATIONS = {
    9: ("The Agent era — history, and enterprise Harness solutions",
        "Agent 时代——历史，以及企业级 Harness 方案"),          # Talk 2 (0047)
    10: ("The Agent era — history, and enterprise Harness solutions",
         "Agent 时代——历史，以及企业级 Harness 方案"),         # Talk 2 (0048)
    13: ("A chat app, demoed live from his phone",
         "一个聊天 App，用手机现场演示"),                        # Talk 4 (0041)
    14: ("Personal care — a routine that remembers your skin and adapts to your city's live weather",
         "个人护理——记住你的皮肤，按所在城市的实时天气定制日常护理"),  # Talk 5 (0042)
    15: ("Agents that work for your brand — it knows more than you remember",
         "为品牌工作的智能体——它比你更了解你的品牌"),          # Talk 6 (0043)
    17: ("Information Radar — an AI-news dashboard",
         "信息雷达——AI 资讯仪表盘"),                            # Talk 8 (0049-T)
    18: ("Your agents work while you sleep",
         "智能体替你工作，你睡觉也没停"),                        # Talk 9 (0059)
}

# Photo insertions: (after pick index 0-based, duration seconds).
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
    # Build the timeline durations in order.
    durations = []
    for i, p in enumerate(picks):
        c = p["clip"]
        durations.append(parse_ts(c["end"]) - parse_ts(c["start"]))
        for (after_idx, dur) in PHOTOS:
            if after_idx == i:
                durations.append(dur)
    assert len(durations) == len(CAPTIONS) == 23, (len(durations), len(CAPTIONS))

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
    lines.append("Style: EN,Caveat,52,&H00FFFFFF,&H000000FF,&H80000000,&H99000000,1,0,0,0,100,100,0,0,4,1,0,2,60,60,110,1")
    lines.append("Style: CN,Ma Shan Zheng,46,&H00FFFFFF,&H000000FF,&H80000000,&H99000000,0,0,0,0,100,100,0,0,4,1,0,2,60,60,50,1")
    # App-intro annotations: BIGGER and nicer — larger, bold, simple font,
    # above the Talk caption. NOTE_EN sits above NOTE_CN; both above Talk EN.
    lines.append("Style: NOTE_EN,DejaVu Sans,36,&H00FFFFFF,&H000000FF,&H80000000,&H99000000,1,0,0,0,100,100,0,0,4,1,0,2,60,60,245,1")
    lines.append("Style: NOTE_CN,Noto Sans CJK SC,34,&H00FFFFFF,&H000000FF,&H80000000,&H99000000,1,0,0,0,100,100,0,0,4,1,0,2,60,60,195,1")
    lines.append("")
    lines.append("[Events]")
    lines.append("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text")
    lines.append("")

    t = 0.0
    for k, (en, cn) in enumerate(CAPTIONS):
        dur = durations[k]
        start = t
        end = t + dur
        # The next caption starts 0.5s before this segment's nominal end
        # (crossfade), so trim the last 0.5s except on the final segment.
        end_show = end - XFADE if k < len(CAPTIONS) - 1 else end
        lines.append(f"Dialogue: 0,{ass_time(start)},{ass_time(end_show)},CN,,0,0,0,,{cn}")
        lines.append(f"Dialogue: 0,{ass_time(start)},{ass_time(end_show)},EN,,0,0,0,,{en}")
        # App-intro annotation (small, simple font, above the Talk caption).
        if k in ANNOTATIONS:
            a_en, a_cn = ANNOTATIONS[k]
            lines.append(f"Dialogue: 0,{ass_time(start)},{ass_time(end_show)},NOTE_CN,,0,0,0,,{a_cn}")
            lines.append(f"Dialogue: 0,{ass_time(start)},{ass_time(end_show)},NOTE_EN,,0,0,0,,{a_en}")
        t = end - XFADE

    total = sum(durations) - (len(durations) - 1) * XFADE
    with open("scan/captions-v5.ass", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Wrote scan/captions-v5.ass: {len(CAPTIONS)} captions, "
          f"final video duration {total:.1f}s")


if __name__ == "__main__":
    main()
