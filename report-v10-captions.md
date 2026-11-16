# v10 captions — report (2026-11-15)

Status: DRAFT for Aileen's review. No video rendered. Built from v9 by text
replacement only: same timing, same styles, same layout, 100 Dialogue lines,
23 segments, 49 cards, final duration 127.5s. Only 14 NOTE cards changed
(28 Dialogue lines); every other line is byte-identical to v9. All Chinese
lines ≤ 15 chars (longest are 14).

Files: `scan/captions-v10.ass` (built by `build_captions_v10.py`).

## Rule applied (2026-11-15 17:06)

v9 described the SCENE ("现场演示，全场盯着屏幕") but not WHAT the speaker
is showing. v10: every talk caption is a ≤15-char summary of WHAT the thing
IS, grounded in the full Whisper transcript for that clip and/or the
on-screen slide text (slides read from frames extracted from
media/DJI_001 at the pick timestamps). Talk headers, coffee label, story arc,
and all non-talk cards are unchanged.

## Before / after per talk

### Talk 1 — Pairoa (clip 0049, 0:02–0:08)
- v9: "现场演示，全场盯着屏幕" / "Demoed live — the room leans in"
- v10: "不用注册，一分钟接进 AI" / "No key, no sign-up — live in a minute"
- Evidence: slide (frame 0049 @0:06) reads "Pairoa — Connect Pairoa to your
  AI in under a minute. Anonymous to start — no key, no sign-up. pairoa.com".
  Transcript is garbled room chatter; the slide is the source.

### Talk 2 — Carl Yang, Agent era + Harness (clips 0047 + 0048)
- v9a: "Agent 时代从哪来" / "Where the Agent era came from"
- v10a: "Agent 时代发展史" / "The Agent era — a short history"
- Evidence: title slide (frame 0047 @0:09) "Agent 时代的到来：发展史与企业级
  Harness 解决方案" (Carl 徐鹏, 2026.7.11).
- v9b: "企业级 Harness，怎么落地" / "Enterprise Harness — how to ship it"
- v10b: "沙盒、观测、校准，三大件" / "Sandbox, observability, calibration"
- Evidence: slide (frame 0048 @0:11) "企业级 Harness 实战：构建 Agent 沙盒与
  可观测性治理体系" + "Harness 三大核心能力：1 Agent 沙盒 (Sandbox) 2 可观测性
  (Observability) 3 校准 (Calibration)".

### Talk 3 — OriVue, AI-native tools (clip 0033, 0:06–0:12)
- v9: "为 AI 而生的工具" / "Tools born for AI"
- v10: "科研绘图，要 AI 原生工具" / "Research plots need AI-native tools"
- Evidence: slide (frame 0033 @0:11) "科研绘图，需要真正的 AI-native 工具 /
  OriVue × Paper Skills / Tools + Domain Knowledge"; transcript (garbled)
  contains "這個科研化體樂影的工具" ("科研绘图工具") and "今天帶來的一個分享
  主要是…".

### Talk 4 — his own chat app (clip 0041, 0:24–0:32) ⚠ PARTIALLY UNDETERMINED
- v9a: "自己做的聊天 App" / "A chat app he built himself"
- v10a: "自己做的 AI 聊天 App" / "An AI chat app he built himself"
- v9b: "拿着手机，现场演示" / "Phone in hand, demoed live"
- v10b: "屏幕上，AI 在帮你分析" / "On screen, the AI is analyzing for you"
- Evidence: phone UI on the big screen shows a chat conversation with header
  "AI 分析", a "Claude" mention, and a long AI reply citing time figures
  ("7小时35分钟", "23:59") — an AI analysis chat, zoom-verified from the
  frame at 0:25.
- FLAG: the transcript for this clip is Whisper garbage ("有沙拉魚" repeated)
  and the chat text is too blurry to read in full, so the app's exact purpose
  (what the analysis is for) could NOT be determined. The v10 captions say
  only what is visible on screen; they do not claim a specific product
  purpose. If Aileen knows what his app does, one line from her would sharpen
  this further.

### Talk 5 — her personal-care app (clip 0042, 0:29–0:36) — VERIFIED
- v9a: "个人护理，记住你的皮肤" / "Personal care — it remembers your skin"
- v10a: "你的护肤柜，记住你的皮肤" / "Your skincare cabinet remembers your skin"
- v9b: "按实时天气，调你的护理" / "Live weather shapes your routine" — UNCHANGED
- Evidence: app welcome screen (frame 0042 @0:30) "欢迎来到你的柜柜 /
  挑选属于你的护肤品吧！" and the city screen (frame 0042 @0:52)
  "你在哪个城市？ / 根据当地天气/温度/湿度/季节…为你推荐 / 上海 33°".
  Note: no transcript.srt exists in scan/ for the 08:48 0042 clip, but the
  content is verified from the two frames plus the v6-verified transcript
  (tell it your skin → it remembers you; city → live weather shapes routine).

### Talk 6 — Saraeal, agents that test products (clip 0043, 0:18–0:24)
- v9a: "AI 替你扮演你的用户" / "AI plays your customers for you"
- v10a: "AI 扮成用户，帮你测产品" / "AI plays your users to test your product"
- v9b: "它比你更懂你的品牌" / "It knows your brand better than you" — UNCHANGED
- Evidence: transcript "我們的公司叫做 Saraeal … 但是现在AI出现了 / AI可以去
  模擬 / 每一二角色的場景 / 不同的場景變化 / 在某一個市場的產品中 …
  我們想要去測試" (AI simulates personas/scenarios in a market to test the
  product); v10a names the purpose (testing), v9b is the on-screen slide
  slogan "Your brand knows more than it remembers".

### Talk 7 — CREWCLAW, live code (clip 0044, 0:18–0:25) ⚠ TRANSCRIPT UNUSABLE
- v9a: "终端里，代码在跑" / "Code running in the terminal"
- v10a: "终端里 Agent 在审代码" / "Agents review code, live in the terminal"
- v9b: "现场敲代码，现场跑" / "Typed live, run live"
- v10b: "任务排队，一个一个跑" / "Tasks queue up and run, one by one"
- Evidence: terminal screen (frame 0044 @0:21, zoom-verified) shows "CREWCLAW"
  + left panel "Code Review Shrimp / 代码评审" + "TEAM QUEUE" + JSON
  {"type": "claude..."} + right panel "ARTIFACTS". The demo visibly hit a
  "model provider network request failed" error live (not captioned).
- FLAG: the transcript for this clip is Whisper garbage about cooking oil
  temperature ("油温百度", "煎食正面子") — completely unusable. The v10
  captions rest on the legible terminal screen only; what the speaker SAID
  about CREWCLAW is unknown.

### Talk 8 — Information Radar (clip 0049, 0:25–0:32)
- v9a: "一个面板，看遍 AI 新闻" / "One dashboard, all the AI news"
- v10a: "信息雷达：AI 创业情报站" / "Information Radar: the AI founders' intel hub"
- v9b: "趋势、排名、地图，全在这" / "Trends, rankings, a map — all here"
- v10b: "政策补贴、排名地图，全在这" / "Policies, subsidies, rankings, maps — all here"
- Evidence: slide (frame 0049 @0:31) "信息雷达 / 政策补贴看板：全国各地 AI
  创业政策、补贴申报 / 园区社区地图：全国 AI 创业园区 / 孵化器的人脉条件 /
  活动黑客松日历：赛事信息、报名入口、组队招募 / 技术排行榜：Github、大模型、
  AI 工具排行榜 / Newsletter（周报）". v9 undersold it as "AI news"; it is a
  founders' intel board (policies, subsidies, parks, hackathons, rankings).

### Talk 9 — agents work while you live (clip 0059, 0:00–0:07) — CORRECTION
- v9a: "你的 agent 在工作" / "Your agents work" — UNCHANGED
- v9b: "而你在睡觉" / "While you sleep"
- v10b: "而你继续生活" / "While you keep living"
- Evidence: slide (frame 0059 @0:06, zoom-verified) reads "Your agents work. /
  You keep living." with a watch graphic. The v5 pick reason's "You are
  sleeping" was wrong; the slide says "keep living". v9's "睡觉" is corrected.

## What is NOT done (awaiting approval)

- No v7 video render. When she approves the v10 text, render both music
  versions with `inkling-video-recut-v7.py` + `scan/captions-v10.ass`
  (converted to single-box format if she picks that style — the v9 mockup
  proved the format works).
- No new photos added. No music/grading/order/timing changes.
- Open: Talk 4's exact app purpose (see flag above) — one line from Aileen
  would sharpen it; otherwise v10 as written is the honest visible-screen
  summary.
