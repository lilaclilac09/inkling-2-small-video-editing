"""Build the end rolling credits preview (with a pause at each entry).

User (2026-11-16 11:42): "最后滚动那个字幕你做好也截图发给我呀，
然后把它做成那个滚动的每个停留啊，就是我要说的话都在里面了呀，
对吧？要感谢的人都在里面了呀"
Translation: build the end rolling credits, screenshot it; the scroll
must PAUSE at each entry (each line/section holds still briefly so it
is readable), not scroll continuously fast. Everything she asked to
say and everyone to thank must be in it.

User (2026-11-16 12:20, replying to the credits preview video):
"cursor 联系人是什么 删掉 华东 间距小一点 丝滑一点"
("华东" = "滑动" garble = scrolling.) Two changes: DELETE the
"Cursor 联系人 / Cursor team contact" entry (she asked what it is
and wants it gone; it was a placeholder for a contact person whose
name she could not recall -- do NOT re-add it, do NOT invent a name),
and make the scroll smoother: smaller spacing between entries and a
silky, fluid scroll (finer increments, eased motion, tighter gaps).

Revision (2026-11-16 12:20): Cursor contact block REMOVED (20 -> 19
blocks). GAP 90 -> 50px. FPS 10 -> 24. Scroll interpolation is now
smoothstep ease-in-out (zero velocity at both ends, peak mid-scroll)
instead of linear -- no abrupt starts/stops. Hold 1.6s per block
unchanged (readability kept).

Credits text (SETTLED, from requirements-log.md 2026-11-16 08:51-09:13
+ 09:45 + 09:56):
  * Event line + title "特别感谢 / Special Thanks"
  * Thanks: Cursor; Ben Lang; 所有分享的讲者 / All speakers;
    所有参与者 / All participants; 组织者 / Coordinators; 志愿者 /
    Volunteers; Cursor 社区 / The Cursor Community; 咖啡店团队 /
    Cafe Crew (was "咖啡店店主 / The café owner", changed 2026-11-16
    13:36 per user -- "不要店主"); Sunset Cafe 的朋友 / Friends from
    Sunset Cafe; 徐汇区和静安区城管大爷 / The chengguan officers of
    Xuhui and Jing’an; 帮助过我们的人 / Everyone who helped us.
    ("Cursor 联系人 / Cursor team contact" REMOVED 2026-11-16 12:20
    per user; do NOT re-add.)
  * Links (verified): Luma luma.com/nthhqbbg; host site aileena.xyz;
    host X @aileengf1.
  * Host contact: Aileen — X @aileengf1 · aileena.xyz.
  * Editing support / assistance text entries REMOVED: "Assistance:
    Muse" removed 2026-11-16 13:34 per user; "Editing support: Muse"
    removed 2026-11-16 13:35 per user. Instead, the FRONT of the
    credits showed the Muse wordmark + the Thinking Machines Lab logo
    together (a logo block before the header), per user 13:35:
    "直接剪辑支持就是 muse logo 还有 thinking machines lab" +
    "放到前面". The Muse mark was a clean "Muse" wordmark rendered in
    Liberation Sans Bold (white) -- no official Muse logo file was
    available to source, so it was rendered, not downloaded.
  * 2026-11-16 13:41 per user: the Muse wordmark is UGLY ("muse
    算了吧 好丑") -- DROP it entirely. The front of the credits is
    now just the official THINKING MACHINES wordmark alone, centred,
    first ("放 第一"). No Muse text or logo anywhere in the credits.
  * Thinking Machines Lab: logo (sourced from the SGLang repo's docs
    cards, thinkingmachines.png -- the official "THINKING MACHINES"
    wordmark, inverted to white-on-transparent for the black
    background) + joint credit with the Thinking Machines Lab team.
    The joint-credit block is TEXT ONLY now (no logo duplicated there)
    because the TML logo already appears in the front logo block.
  * Consent line (Muse-written, 09:50/09:56): "片中影像皆已征得参与者
    同意公开分享，也请大家不要上传他人的私人肖像。" / EN.
  * Group-contact line (09:45): if anyone wasn't filmed, or wants to
    appear on camera, contact us in the group.

How the pause works:
  The credits are one tall strip (all blocks stacked). The visible
  1920x1080 window scrolls up through it, but the scroll is STEPPED:
  each block HOLDS centred on screen for HOLD_S seconds, then scrolls
  to the next block over SCROLL_S seconds, then holds again. So every
  entry is still and readable in turn -- no continuous fast roll.
  (HOLD_S=1.6, SCROLL_S=0.6, FPS=24 for the preview.)
  2026-11-16 12:20 revision ("丝滑一点"): the scroll between holds
  uses smoothstep ease-in-out (zero velocity at both ends, peak
  mid-scroll) at 24fps, so the motion glides instead of jumping;
  the gap between blocks is tighter (GAP=50).

Style: movie credits -- white text on black, centred. CN: Noto Sans
CJK SC; EN: Liberation Sans. Title bigger; entries regular; closing
lines (consent/group) slightly smaller.

Outputs:
  * credits-strip.png -- the whole credits strip (all blocks), for
    text verification.
  * credits-preview.mp4 -- the rolling preview clip (hold + scroll).
  * v7-preview-credits-1/2/3.png -- three screenshots at hold moments
    (front TML logo alone, a thanks entry, the joint-credit text).
  * tml-logo-white.png -- the inverted TML wordmark (white, transparent).
  * (muse-wordmark-white.png REMOVED 2026-11-16 13:41 -- user said the
    rendered Muse wordmark was ugly; no Muse mark in the credits.)
"""
import os
import subprocess
from PIL import Image, ImageDraw, ImageFont

W, H = 1920, 1080
FPS = 24
HOLD_S = 1.6
SCROLL_S = 0.6

FONT_CN = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
FONT_CN_B = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_EN = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
FONT_EN_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"

TML_SRC = ("../goals/open-kernel-challenge/files/sglang-297e54fd/"
           "docs/cards/logos/thinkingmachines.png")
TML_WHITE = "tml-logo-white.png"
FRONT_LOGO_H = 200   # height of the front TML logo


def font(path, size, bold=False):
    if bold and "NotoSansCJK" in path:
        path = FONT_CN_B
    elif bold and "LiberationSans" in path:
        path = FONT_EN_B
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Word-wrap EN text (or char-wrap CN) to max_w pixels."""
    if not text:
        return []
    words = text.split(" ")
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            # A single over-long word (e.g. a URL) goes on its own line.
            cur = w
    if cur:
        lines.append(cur)
    return lines


# Each block: list of (text, font_path, size, bold, is_logo)
# A block is one pause unit. (CN, EN) pairs render CN line then EN line.
BLOCKS = [
    # Front: TML logo alone (2026-11-16 13:41 per user: Muse wordmark
    # dropped -- "好丑"; Thinking Machines logo goes FIRST, alone).
    [("LOGOS_FRONT", None, 0, False)],
    # Header: event line + title.
    [("上海 Cursor AI 社区 · 2026 年 7 月 19 日", FONT_CN, 40, False),
     ("Shanghai Cursor AI Community · July 19, 2026", FONT_EN, 32, False),
     ("特别感谢", FONT_CN, 72, True),
     ("Special Thanks To", FONT_EN, 54, False)],
    # Thanks (11). 2026-11-16 12:20: "Cursor 联系人" entry DELETED
    # per user -- it was a placeholder, do NOT re-add, do NOT invent a name.
    [("Cursor", FONT_EN, 48, True)],
    [("Ben Lang", FONT_EN, 48, True)],
    [("所有分享的讲者", FONT_CN, 48, False),
     ("All speakers", FONT_EN, 40, False)],
    [("所有参与者", FONT_CN, 48, False),
     ("All participants", FONT_EN, 40, False)],
    [("组织者", FONT_CN, 48, False),
     ("Coordinators", FONT_EN, 40, False)],
    [("志愿者", FONT_CN, 48, False),
     ("Volunteers", FONT_EN, 40, False)],
    [("Cursor 社区", FONT_CN, 48, False),
     ("The Cursor Community", FONT_EN, 40, False)],
    [("咖啡店团队", FONT_CN, 48, False),
     ("Cafe Crew", FONT_EN, 40, False)],
    [("Sunset Cafe 的朋友", FONT_CN, 48, False),
     ("Friends from Sunset Cafe", FONT_EN, 40, False)],
    [("徐汇区和静安区城管大爷", FONT_CN, 48, False),
     ("The chengguan officers of Xuhui and Jing’an", FONT_EN, 40, False)],
    [("帮助过我们的人", FONT_CN, 48, False),
     ("Everyone who helped us", FONT_EN, 40, False)],
    # Links.
    [("相关链接", FONT_CN, 44, False),
     ("Links", FONT_EN, 36, False),
     ("活动报名 · Luma: luma.com/nthhqbbg", FONT_CN, 36, False),
     ("aileena.xyz", FONT_EN, 36, False),
     ("X @aileengf1", FONT_EN, 36, False)],
    # Host contact.
    [("主办方", FONT_CN, 44, False),
     ("Host: Aileen — X @aileengf1 · aileena.xyz", FONT_EN, 36, False)],
    # Thinking Machines Lab joint credit -- TEXT ONLY (the TML logo
    # already appears in the front logo block; do NOT duplicate it).
    [("联合鸣谢", FONT_CN, 44, False),
     ("In collaboration with the Thinking Machines Lab team",
      FONT_EN, 36, False)],
    # Consent line.
    [("片中影像皆已征得参与者同意公开分享，也请大家不要上传他人的私人肖像。",
      FONT_CN, 40, False),
     ("All footage in this film was shared with the participants' "
      "consent — please don't upload anyone else's private portraits.",
      FONT_EN, 32, False)],
    # Group-contact line.
    [("如果没被拍到，或想出镜，请在群里联系我们", FONT_CN, 40, False),
     ("If you weren't filmed, or would like to appear on camera, "
      "contact us in the group.", FONT_EN, 32, False)],
]

GAP = 50          # px between blocks in the strip (was 90; tighter)
MAX_W = 1650      # max text width
LOGO_W = 520      # TML logo display width


def invert_logo():
    """Black-on-white wordmark -> white text, transparent background."""
    src = Image.open(TML_SRC).convert("L")
    # alpha = 255 - luminance (black text opaque, white bg transparent)
    alpha = src.point(lambda v: 255 - v)
    out = Image.new("RGBA", src.size, (255, 255, 255, 0))
    white = Image.new("RGBA", src.size, (255, 255, 255, 255))
    out = Image.composite(white, out, alpha)
    out.save(TML_WHITE)
    print(f"inverted TML logo -> {TML_WHITE} ({src.size})")
    return out


def front_logo(tml_logo):
    """TML logo alone, centred, at FRONT_LOGO_H height.

    (2026-11-16 13:41: the Muse wordmark was dropped -- user said it
    was ugly. The front block is now just the official THINKING
    MACHINES wordmark, alone, first.)
    """
    tw = int(tml_logo.size[0] * FRONT_LOGO_H / tml_logo.size[1])
    return tml_logo.resize((tw, FRONT_LOGO_H), Image.LANCZOS)


def render_block(draw, block, y, logo, front_row):
    """Draw one block centred at x=W/2, starting at y. Returns height."""
    cur = y
    for text, fpath, size, bold in block:
        if text == "LOGO_TML":
            lw = LOGO_W
            lh = int(logo.size[1] * lw / logo.size[0])
            # logo is pasted later (needs RGBA); reserve the space here
            cur += lh + 30
            continue
        if text == "LOGOS_FRONT":
            # front TML logo alone (Muse dropped 2026-11-16 13:41);
            # pasted later
            cur += front_row.size[1] + 30
            continue
        fnt = font(fpath, size, bold)
        lines = wrap(draw, text, fnt, MAX_W)
        for ln in lines:
            bbox = draw.textbbox((0, 0), ln, font=fnt)
            lh = bbox[3] - bbox[1]
            draw.text((W // 2, cur), ln, font=fnt, fill=(255, 255, 255),
                      anchor="ma")
            cur += lh + 8
        cur += 6
    return cur - y


def build_strip(logo, front_row):
    """Render the whole credits strip; return (image, block_centres)."""
    # First pass: measure each block's height on a scratch canvas.
    scratch = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(scratch)
    heights = []
    for block in BLOCKS:
        heights.append(render_block(d, block, 0, logo, front_row))
    total = sum(heights) + GAP * (len(BLOCKS) - 1) + H  # +H top/bottom pad
    strip = Image.new("RGB", (W, total), (0, 0, 0))
    d = ImageDraw.Draw(strip)
    centres = []
    y = H // 2  # first block starts half a screen down (scrolls in)
    for i, block in enumerate(BLOCKS):
        h = heights[i]
        # Draw the block; paste the logo where the placeholder is.
        top = y
        cur = y
        for text, fpath, size, bold in block:
            if text == "LOGO_TML":
                lw = LOGO_W
                lh = int(logo.size[1] * lw / logo.size[0])
                logo_r = logo.resize((lw, lh), Image.LANCZOS)
                strip.paste(logo_r, ((W - lw) // 2, cur), logo_r)
                cur += lh + 30
                continue
            if text == "LOGOS_FRONT":
                fw, fh = front_row.size
                strip.paste(front_row, ((W - fw) // 2, cur), front_row)
                cur += fh + 30
                continue
            fnt = font(fpath, size, bold)
            lines = wrap(d, text, fnt, MAX_W)
            for ln in lines:
                bbox = d.textbbox((0, 0), ln, font=fnt)
                lh = bbox[3] - bbox[1]
                d.text((W // 2, cur), ln, font=fnt, fill=(255, 255, 255),
                       anchor="ma")
                cur += lh + 8
            cur += 6
        centres.append(top + h // 2)
        y += h + GAP
    return strip, centres


def smoothstep(t):
    """Ease-in-out: 0 velocity at both ends, peak mid-way (silky)."""
    return t * t * (3 - 2 * t)


def offsets(centres):
    """Per-frame y-offsets: hold each block centred, eased scroll between."""
    hold_f = int(round(HOLD_S * FPS))
    scroll_f = int(round(SCROLL_S * FPS))
    seq = []  # (offset, is_hold) per frame
    for i, c in enumerate(centres):
        off = c - H // 2
        seq += [(off, True)] * hold_f
        if i + 1 < len(centres):
            nxt = centres[i + 1] - H // 2
            for k in range(1, scroll_f + 1):
                t = smoothstep(k / scroll_f)
                seq.append((off + (nxt - off) * t, False))
    # Final hold on the last block, then scroll it out.
    seq += [(centres[-1] - H // 2, True)] * hold_f
    return seq


def main():
    logo = invert_logo()
    front_row = front_logo(logo)
    print(f"front logo: TML alone {front_row.size} "
          f"({FRONT_LOGO_H}px tall, centred, first)")
    strip, centres = build_strip(logo, front_row)
    strip.save("credits-strip.png")
    print(f"strip: {strip.size}, {len(BLOCKS)} blocks, "
          f"{len(centres)} hold positions")

    seq = offsets(centres)
    total_s = len(seq) / FPS
    print(f"credits duration: {total_s:.1f}s "
          f"({len(seq)} frames @ {FPS}fps; "
          f"hold {HOLD_S}s + scroll {SCROLL_S}s per block)")

    # Encode the preview clip from raw frames.
    cmd = ["ffmpeg", "-y", "-v", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
           "credits-preview.mp4"]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    shots = {}  # frame index -> path (hold moments to screenshot)
    hold_f = int(round(HOLD_S * FPS))
    scroll_f = int(round(SCROLL_S * FPS))
    # Screenshot at the middle of the hold for block 0 (front TML logo
    # alone), block 4 (All speakers), block 15 (joint credit, text only).
    # (18 blocks: front logo at 0; editing + assistance text blocks
    # removed 2026-11-16 13:34/13:35; Muse wordmark dropped 13:41.)
    targets = {0: "v7-preview-credits-1.png",
               4: "v7-preview-credits-2.png",
               15: "v7-preview-credits-3.png"}
    # Frame index of the middle of block i's hold:
    # block i hold starts at i*(hold_f+scroll_f) (except last has no scroll)
    for fi, (off, _is_hold) in enumerate(seq):
        off = int(round(off))
        frame = strip.crop((0, off, W, off + H))
        proc.stdin.write(frame.tobytes())
        # Which block's hold is this frame in?
        idx = fi // (hold_f + scroll_f)
        pos_in = fi % (hold_f + scroll_f)
        if idx in targets and pos_in == hold_f // 2 and idx not in shots:
            frame.save(targets[idx])
            shots[idx] = targets[idx]
    proc.stdin.close()
    proc.wait()
    assert proc.returncode == 0, "ffmpeg failed"
    print("wrote credits-preview.mp4")
    for idx, path in sorted(shots.items()):
        print(f"  screenshot block {idx}: {path}")
    print()
    print("Blocks (18): front TML logo alone + header + 11 thanks +")
    print("links + host + joint credit (text only) + consent + group-contact.")
    print("(Cursor team contact REMOVED 2026-11-16 12:20; 'Assistance: Muse'")
    print("REMOVED 13:34; 'Editing support: Muse' REMOVED 13:35 per user;")
    print("Muse wordmark DROPPED 13:41 per user -- '好丑'; TML logo first, alone.)")


if __name__ == "__main__":
    main()
