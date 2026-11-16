# v7 captions + subtitle-style mockup — report (2026-11-15)

Status: DRAFT for Aileen's review. No video rendered yet. Awaiting her approval of the
captions-v9 text draft + the single-box mockup before any v7 render.

## 1. Captions v9 — what changed (v8 -> v9)

File: `scan/captions-v9.ass` (built by `build_captions_v9.py`).
Same timing, same styles, same layout as v8 (CAP_EN DejaVu Sans Bold, CAP_CN Ma Shan
Zheng, NOTE styles, cream box, bottom placement, max 2 lines, same padding).
Only the TEXT changed. 23 segments, 49 cards, 100 Dialogue lines.

Rule applied (2026-11-15 16:49): for each segment, pull out WHAT THE PERSON IS ACTUALLY
SAYING (the key point), then a SHORT description — every Chinese line ≤ 15 characters.
No brand/product names unless the point requires it (Pairoa, CREWCLAW, Information Radar,
Saraeal all removed). Talk headers kept ("Talk 1..9 / 分享 1..9"). Coffee label unchanged
(0:01:20-0:01:24, "🔊 This is the coffee machine sound / 这是咖啡机的声音").

Story arc (2026-11-15 16:56): the wording now carries the narrative — opening sets up the
day beginning ("一天从这里开始"), hosts are introduced as the people holding it together
("来得最早的朋友" / "一直维持秩序的朋友"), the black-hat portrait is the "before it
starts" beat ("黑帽子，开场前站住了"), talks carry the "what they are saying" thread,
and the closing lands the day ending ("横幅前，散场了" / "人齐了，拍张大合照").

Grounding: Whisper transcripts in the exact pick windows are mostly garbled room chatter,
so no verbatim quotes were invented. Each talk's key point is distilled from the pick
title + reason, the on-screen slide text, or the already-verified v8 content (Talk 5
personal care). Where audio was unclear, the caption focuses on the visible action/idea.

## 2. Final group photo — verdict: v6 is NOT stretched

HM5A1478 original is 6000x4000 (3:2, ratio 1.500). Frame extracted from
`recap-v6-another-season.mp4` at 0:02:05 (125 s) and measured: the photo spans
x 120..1802 (1683 px, 87.7% of the 1920 frame) with ~120 px cream bars on BOTH sides.
A 16:9 stretch would fill all 1920 px with no cream bars. The v6 `add_photo` path
(`scale=3840:2160:force_original_aspect_ratio=decrease` + cream `#F7F1E5` pad) is already
correct — original ratio on cream, people undistorted. (The Ken Burns zoom crops the
top/bottom slightly as it zooms, so the visible photo looks a touch wider, but nothing
is stretched.) Aileen most likely watched v5 by mistake — v5 DID stretch 3:2 photos to
16:9 (its frame at 125 s fills the full width, no cream bars). v7 keeps the same correct
v6 handling; no photo fix needed. No new photos added.

## 3. Subtitle style mockup — single cream box

File: `subtitle-style-mockup.png` (frame from v6 at 0:33, Talk 1 Pairoa moment).
The mockup burns ONE Dialogue event holding both lines (CN, then EN, separated by \N)
under a single style with BorderStyle=4 (opaque box) and cream BackColour, so libass
draws ONE cream rectangle around both lines. The box is slightly taller than v8's
(leading/trailing blank lines add vertical padding; \h padding gives side breathing room).
Per-line fonts are kept via inline overrides so the look stays familiar: CN in
Ma Shan Zheng (fs40), EN in DejaVu Sans Bold (fs36).

Verified visually: one cream rectangle, both CN ("现场演示，全场盯着屏幕") and EN
("Demoed live — the room leans in") inside it, no tofu boxes, both lines legible, box
comfortably taller than the text. Mockup ASS: `/tmp/subtitle-style-mockup.ass`.

Note: `captions-v9.ass` currently holds the v9 TEXT in the existing two-box layout
(separate CN/EN events, as in v8). Converting it to the single-box format (one event per
caption with the \fn overrides shown in the mockup) is a mechanical step once Aileen
approves the mockup look. The v7 render will use whichever format she picks.

## 4. Before / after caption pairs (v8 -> v9)

1. Talk 1 (Pairoa demo):
   v8: "Pairoa，现场演示" / "Pairoa, demoed live"
   v9: "现场演示，全场盯着屏幕" / "Demoed live — the room leans in"
   (brand name dropped; the punch is the room leaning in.)

2. Talk 6 (agents):
   v8: "为品牌工作的智能体" / "Agents that work for your brand"
   v9: "AI 替你扮演你的用户" / "AI plays your customers for you"
   (the actual idea from the talk: AI simulates your customers' personas to test the product.)

3. Talk 5 (personal care):
   v8: "输入你的地址——实时天气来调整日常护理" (18 chars) / "Type in your address — live weather shapes your routine"
   v9: "按实时天气，调你的护理" (11 chars) / "Live weather shapes your routine"
   (same verified point, cut to a punch.)

4. Closing (group photo):
   v8: "门口的大合照" / "The group, at the door"
   v9: "人齐了，拍张大合照" / "Everyone's here — group photo"
   (lands the story beat: everyone's here, one photo, day over.)

## 5. What is NOT done (awaiting approval)

- No v7 video render (per redirect). When she approves the v9 text + mockup style, render
  both music versions with `inkling-video-recut-v7.py` (copy of v6, unchanged photo handling)
  and `scan/captions-v9.ass` (converted to single-box if she picks that style).
- No new photos added. No music/grading/order/timing changes.
