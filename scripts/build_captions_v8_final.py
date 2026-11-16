"""Build scan/captions-v8-final.ass (28 captions) for the v8 recap.

Source of truth: scan/captions-v8-script-draft.txt (28 captions, revised 2
— text approved by the user, extended into scene descriptions).
Caption 28 uses the Luma wording VERBATIM (user: do not paraphrase):
  CN: 不同的人聚在一起，共建、共创、共鸣，深度交流加生活，Cursor 把边界都模糊了，总有人能接住你的问题。
  EN: Different people together, building, creating, resonating — deep
  exchange and everyday life, Cursor blurring the boundaries, and always
  someone to catch your question.

Timings are RETIMED from the v7 main-body times for the v8 rebuild:
  * pick reorder: 1,2,3,4,7(laughter HOOK, full 10s),13,14,5,6,8,9,10,
    11,12,15,16,17,18,19,20 — the laughter clip moved to the FRONT as a
    hook (right after the opening arrival picks); D09 (interaction) moves
    with it. Talk 1 is now just pick 5 (trimmed 6s->5s) + pick 6.
  * Talk 1 trim: pick 5 6s->5s (0:02-0:07). Pick 7 NOT trimmed (full 10s).
  * photos moved to the END of the main body (3 photos, 3s/3s/8s).
    Photo3 (group, 8s) carries D27 (3s) + D28 summary (5s).
  * D04/D05/D06 (the three friends) compressed to 2.0s each to fit pick 4
    (photoB, which D06 overlapped in v7, moved to the end).
  * D07 shortened to end at pick 6 start (50.0) to avoid overlap with D08.
Style: v10 single-box cream (SINGLE: CN fs40, EN fs36, BorderStyle=4).
Long EN/CN wrapped with PIL measurement so nothing overflows the frame.
Latin words (e.g. "Cursor") are never split across lines.
"""
import re
from PIL import ImageFont

SRC_ASS = "scan/captions-v11-singlebox-v10.ass"
DST = "scan/captions-v8-final.ass"

FONT_CN = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
FONT_EN_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
MAX_W = 1600  # max text width px (inside the box, excl. \\h padding)

PAD = "\\h" * 9
TOP_BLANK = "{\\fnLiberation Sans\\fs18}\\h"
BOTTOM_BLANK = "{\\fnLiberation Sans\\fs25}\\h"

# (start, end, CN, EN) — v8 main-body times, retimed per the docstring.
# Text = draft revised 2, verbatim (caption 28 = Luma wording verbatim).
CAPS = [
    ("0:00:00.00", "0:00:02.75", "准备了很久，这一天终于来了，我们等着大家来签到",
     "After a long time preparing, the day finally came — we were here, waiting for everyone to check in"),
    ("0:00:05.50", "0:00:08.00", "门口一直有人在排队，一个接一个进来",
     "There was always a queue at the door, people coming in one after another"),
    ("0:00:13.00", "0:00:15.75", "推开门进来，里面是特别轻松、特别积极的氛围",
     "Step inside, and the atmosphere is relaxed, positive, alive"),
    ("0:00:18.50", "0:00:20.50", "开门之前就已经来的朋友",
     "The friend who arrived before the doors even opened"),
    ("0:00:20.50", "0:00:22.50", "一直维持秩序的朋友",
     "The friend keeping everything in order"),
    ("0:00:22.50", "0:00:24.50", "筹备千人女性黑客松的朋友",
     "The friend preparing the thousand-women hackathon"),
    ("0:00:26.19", "0:00:29.85", "台上和台下互动得特别好，大家在一个特别好的气氛里，你问我答",
     "The stage and the crowd were completely in sync — questions and answers flowing in a wonderful atmosphere"),
    ("0:00:35.00", "0:00:36.25", "这是女生做的护肤产品，会根据天气来调整你的护理",
     "This skincare product, made by a woman, adjusts your routine to the weather"),
    ("0:00:36.25", "0:00:37.50", "背景里是咖啡机在磨豆子",
     "In the background, the coffee machine is grinding beans"),
    ("0:00:41.27", "0:00:43.38", "来自硅谷的 CPO，介绍他们的 AI 如何扮成用户帮你测产品",
     "A CPO from Silicon Valley, showing how their AI plays your user to test the product"),
    ("0:00:43.38", "0:00:45.50", "它比你更懂你的品牌",
     "It knows your brand better than you"),
    ("0:00:47.56", "0:00:50.00", "不用注册，一分钟就能让你的产品接进 AI",
     "No sign-up — your products connect to AI in a minute"),
    ("0:00:50.00", "0:00:53.25", "有观众想交流，台上马上给出了特别精彩的回答",
     "Someone in the audience wanted to talk, and the speaker answered beautifully right away"),
    ("0:00:58.56", "0:01:02.00", "Agent 时代发展史",
     "The Agent era, a short history"),
    ("0:01:04.44", "0:01:08.50", "AI 在跑的时候，沙盒、观测、校准一个都不能少",
     "When AI is running, sandbox, observability, calibration — you need all three"),
    ("0:01:10.56", "0:01:14.00", "他分享了科研绘图为什么需要 AI 原生工具",
     "He shared why research plots need AI-native tools"),
    ("0:01:14.00", "0:01:17.50", "后排的观众都在举着手机记录",
     "The audience in the back row held up their phones, recording everything"),
    ("0:01:19.23", "0:01:25.00", "这是他自己做的手机 AI 聊天 App",
     "This is the mobile AI chat app he built himself"),
    ("0:01:26.50", "0:01:29.00", "终端里，Agent 在审代码",
     "In the terminal, agents review the code"),
    ("0:01:29.00", "0:01:31.50", "任务排队，一个一个跑",
     "Tasks queue up and run, one by one"),
    ("0:01:33.00", "0:01:35.50", "信息雷达，创业情报全在这",
     "Information Radar — founders' intel, all here"),
    ("0:01:35.50", "0:01:38.00", "外面在下暴雨，所以光线比较暗",
     "Pouring rain outside, so the light is dim"),
    ("0:01:44.50", "0:01:47.25", "指着二维码提问",
     "Pointing at the QR code, asking"),
    ("0:01:47.25", "0:01:50.00", "大家对展示的东西特别好奇，特别积极地交流",
     "Everyone was curious about what was shown, exchanging ideas eagerly"),
    ("0:01:52.25", "0:01:54.50", "两场分享之间，我们稍微休息一下",
     "Between the two talks, we took a short break"),
    ("0:01:54.50", "0:01:57.50", "经过一整天的分享，活动收尾了，给大家拍张照片",
     "After a full day of sharing, we wrapped up — and took a photo for everyone"),
    ("0:02:02.50", "0:02:05.50", "人齐了，拍张合照",
     "Everyone's here — group photo"),
    ("0:02:05.50", "0:02:10.50", "不同的人聚在一起，共建、共创、共鸣，深度交流加生活，Cursor 把边界都模糊了，总有人能接住你的问题。",
     "Different people together, building, creating, resonating — deep exchange and everyday life, Cursor blurring the boundaries, and always someone to catch your question."),
]


def text_w(text, font_path, size):
    f = ImageFont.truetype(font_path, size)
    return f.getlength(text)


def _cn_tokens(text):
    """Split CN text into tokens: CJK chars singly, ASCII word runs whole
    (so 'Cursor' is never split across lines)."""
    tokens, cur_ascii = [], ""
    for ch in text:
        if ch.isascii() and (ch.isalnum() or ch in "'-"):
            cur_ascii += ch
        else:
            if cur_ascii:
                tokens.append(cur_ascii)
                cur_ascii = ""
            tokens.append(ch)
    if cur_ascii:
        tokens.append(cur_ascii)
    return tokens


def wrap_cn(text, size=40):
    """Wrap CN to lines <= MAX_W (CJK chars singly; ASCII words kept whole)."""
    f = ImageFont.truetype(FONT_CN, size)
    lines, cur = [], ""
    for tok in _cn_tokens(text):
        if f.getlength(cur + tok) <= MAX_W:
            cur += tok
        else:
            if cur:
                lines.append(cur)
            cur = tok
    if cur:
        lines.append(cur)
    return lines


def wrap_en(text, size=36):
    """Wrap EN to lines <= MAX_W at word boundaries."""
    f = ImageFont.truetype(FONT_EN_B, size)
    words = text.split(" ")
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if f.getlength(trial) <= MAX_W:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def to_cs(t):
    h, m, s = t.split(":")
    return int(h) * 360000 + int(m) * 6000 + int(round(float(s) * 100))


def event(start, end, cn, en):
    cn_lines = wrap_cn(cn)
    en_lines = wrap_en(en)
    parts = [TOP_BLANK]
    for ln in cn_lines:
        parts.append("{\\fnNoto Sans CJK SC\\fs40\\b0}" + PAD + ln + PAD)
    for ln in en_lines:
        parts.append("{\\fnLiberation Sans\\fs36\\b1}" + PAD + ln + PAD)
    parts.append(BOTTOM_BLANK)
    text = "\\N".join(parts)
    return f"Dialogue: 0,{start},{end},SINGLE,,0,0,0,,{text}"


def main():
    with open(SRC_ASS, encoding="utf-8") as f:
        src = f.read()
    head, sep, tail = src.partition("[Events]\n")
    assert sep, "no [Events] section"
    fmt_line, _, _ = tail.partition("\n")

    # Sort by start time (the list above is in pick order, not time order,
    # because picks 13/14 and the laughter hook moved earlier).
    caps = sorted(CAPS, key=lambda c: to_cs(c[0]))
    events = []
    for start, end, cn, en in caps:
        events.append(event(start, end, cn, en))
        cn_l = wrap_cn(cn)
        en_l = wrap_en(en)
        if len(cn_l) > 1 or len(en_l) > 1:
            print(f"  wrapped {start}: CN {len(cn_l)} lines, EN {len(en_l)} lines")

    out = head + sep + fmt_line + "\n" + "\n".join(events) + "\n"
    with open(DST, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"wrote {DST}: {len(events)} events")

    # --- Checks ---
    assert len(events) == 28, f"expected 28, got {len(events)}"
    spans = sorted((to_cs(c[0]), to_cs(c[1])) for c in caps)
    for (s1, e1), (s2, e2) in zip(spans, spans[1:]):
        assert e1 <= s2, f"overlap: {s1}-{e1} vs {s2}-{e2}"
    for start, end, cn, en in caps:
        for ln in wrap_cn(cn):
            assert text_w(ln, FONT_CN, 40) <= MAX_W, f"CN overflow {start}: {ln}"
        for ln in wrap_en(en):
            assert text_w(ln, FONT_EN_B, 36) <= MAX_W, f"EN overflow {start}: {ln}"
    blob = "\n".join(events)
    for bad in ["分享 1", "Talk 1", "分享 2", "Talk 2", "分享 3", "Talk 3",
                "分享 4", "Talk 4", "分享 5", "Talk 5", "分享 6", "Talk 6",
                "分享 7", "Talk 7", "分享 8", "Talk 8", "分享 9", "Talk 9",
                "人还没来齐", "房间活过来了", "四十分钟", "外面是街",
                "梧桐树下", "树下，她在等开场", "一个手势，就是回答",
                "讲的人笑了", "端着饮料", "你的 agent 在工作", "而你继续生活",
                "大合照", "按实时天气，调你的护理", "全场都笑了",
                "你的护肤柜，记住你的皮肤，还按实时天气调你的护理",
                "这是咖啡机的声音", "讲完了，问题一个接一个来了",
                "两场分享之间，喘口气", "横幅前，散场了",
                "再看一眼今天的讲者", "One more look at today's speakers"]:
        assert bad not in blob, f"forbidden text present: {bad}"
    # Caption 28 verbatim (Luma wording) — check on PLAIN text (formatting
    # and line-wrap breaks the raw substring, so strip overrides first).
    plain = re.sub(r"\{[^}]*\}", "", blob).replace("\\h", "").replace("\\N", "")
    assert "共建、共创、共鸣，深度交流加生活，Cursor 把边界都模糊了，总有人能接住你的问题。" in plain
    assert "Cursor blurring the boundaries, and always someone to catch your question." in plain
    print("OK: 28 events, no overlaps, all lines fit, no forbidden text,")
    print("    caption 28 = Luma wording verbatim.")


if __name__ == "__main__":
    main()
