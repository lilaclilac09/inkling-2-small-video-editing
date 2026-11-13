# Video Cutting Requirements Log — Cafe Cursor Shanghai (and future vlogs)

APPEND-ONLY. Every new requirement from Aileen gets added at the end with a timestamp. Never delete or rewrite an old entry. If a requirement is superseded, add a new entry that says so and references the old one. All cutting, picking, subtitling, grading, cover, and template work must follow this log.

---

## 2026-11-11 — Original brief (first ask)

- Cut ONE ~2-minute recap video of the Cafe Cursor Shanghai event (Sun July 19, 2026, 10:00–17:00, cafe on Yanqing Road, French Concession).
- 3 highlight clips are a LATER optional step, not part of this cut.
- **Inkling 2 Small makes ALL picking decisions** (which moments, what order, why — with a reason per pick). Muse ONLY prepares raw material (download, Whisper, keyframes, shrink under 2MB, pack, ffmpeg cutting, photo rotation/classification). Repo/demos must NOT show Muse cutting.
- The video must have story, warmth, and smooth transitions — not just spliced clips.
- What matters in the event (her words): 自发展示 (self-organized showcases) + 气氛/交流 (atmosphere/exchange) + 追问 (follow-up questions). Most moving = music creation + solving everyday problems with AI.
- MUST-KEEP moments: foreign man playing guitar; someone wrote/performed something for his girlfriend (FORM UNVERIFIED — could be a song, code, or something else; do NOT call it a "song" or "女友曲" until verified); piano.
- Ending = big group photo + flashback.
- Afternoon plum-rain downpour started SUDDENLY; volunteers 焦头烂额 (overwhelmed).
- Cursor cup drinks tasty; cafe decor beautiful.
- Music: KOYO "Timing" is the main track.
- All footage available at the time was MORNING ONLY (07:23–12:21). Afternoon/evening material (guitar, piano, rain, group photo) was NOT in the footage and must come from her later uploads.

## 2026-11-12 — Reusable loop + fine-tuning (long-term)

- This is a REUSABLE LOOP, not a one-off: video → Whisper transcript + keyframes → Inkling picks by her taste → ffmpeg cuts → finished video. Reuse for vlogs after this event.
- FINE-TUNING IS IN SCOPE: approved picks become training data; LoRA fine-tune Inkling 2 Small so it learns her taste. Sequence: run event end-to-end → save approved picks → fine-tune → reuse tuned model for vlogs.
- Division of labor (re-stated): Muse only prepares raw material; Inkling 2 Small makes ALL picking decisions.

## 2026-11-13 11:58 — v2 feedback (she liked v2: "写得很不错，剪得很好")

- HOOK AT FRONT: Talk L laughter (clip 0051) OR Talk M (ARIAVA) first, before the wide opening. Use Talk L.
- REMOVE the pink/blonde woman: every segment showing the woman with pink-dyed blonde hair must be REMOVED entirely. Visually inspect frames; err on removing when unsure; report clip+timestamp of removals.
- 0052 (full room before noon) also near the front, after the hook.
- FAST FLASHBACK montage at the start (1–2s per shot).
- MORE WOMEN featured (presenters + audience).
- MORE EXTERIOR/STREET shots showing the whole streetscape.
- ORGANIZE BY SPACE (exterior → interior flow).
- LOUDER AUDIO: music was too quiet at 0.15 → music 0.30; voices clearer/stronger and forward ("人声要稍微深一点、强一点，要能听得清大家在说什么"). Room audio 1.4. Caveat: source room audio is noisy crowd chatter; louder ≠ crystal-clear.
- TWO OTHER MUSIC TRACKS TO COMPARE: produce TWO versions — one with "Just Used Music Again" (music/just-used-music-again.mp3), one with "Another season with you" (music/another-season-with-you.mp3).
- SUBTITLES NICER + BILINGUAL OUTLINES: every TALK gets a simple outline of what they're presenting, in small bottom caption text, clearly legible, BILINGUAL EN line + CN line, REFINED look, HANDWRITTEN FONT PREFERRED (cuter). Non-talk segments get short bilingual captions too. Semi-transparent background box, larger than v2's plain FontSize 20. If no handwritten font, download Caveat (EN) + Ma Shan Zheng (CN) from Google Fonts; fall back to cleanest sans-serif and say so if handwritten fails.
- COLOR GRADING IS IMPORTANT — two directions mapped to the two versions:
  - Version 1 (Just Used Music Again) = Korean variety (韩综) / dating-show (恋综) style: soft diffused glowy light (柔光), vivid color contrast, warm/flattering skin tones, CLOSE-UPS of everyone (prioritize shot types 4+5). Grade hint: saturation ~1.10, contrast ~1.05, brightness ~0.05.
  - Version 2 (Another season) = Silicon Valley style: clean, crisp, tech, strong contrast, cooler tint. Hint: saturation ~1.05, contrast ~1.15, brightness ~-0.02.
- REFERENCE VLOG: https://www.bilibili.com/video/BV1HTp96mEQP/ (Berlin travel vlog by 亦涵, 2026-10-12). Casual, warm, relaxed, daily-life. Use as the feel reference for v3 (esp. Version 1).
- COVER IMAGE (new deliverable): cover-v3.jpg, 1920×1080, best wide shot as base (0026/0042/0052), overlay date "2026.07.19" + "Cursor Cafe Shanghai" (time "10:00–17:00" if it fits), handwritten/refined style, Cursor logo NOT covered by text. Read it back to verify legibility. Commit to repo.
- INKLING MUST DO THE V3 PICKING (re-stated 12:07): call Inkling 2 Small via Tinker API with the new constraints in the prompt (max_tokens 32000), NOT pick by hand. Own frame inspection is only for (a) identifying the pink/blonde woman and (b) finding women/exterior shots for the input pack. If Inkling's picks still include her or a too-close head opening, remove/fix that one pick and report it as a correction.
- OPENING MUST BE WIDE/PANORAMIC (12:07): the v2 opening check-in shot has heads too big/too close, uncomfortable. NO close-up heads at the very start.
- CURSOR LOGO MUST BE PROMINENT (12:35): prefer shots where the Cursor logo/black banner is clearly readable (0026, 0032, 0042, 0079, 0080); opening wide + 1–2 more moments must show it clearly; cover image must keep the logo uncovered. Report how many v3 picks clearly show the logo.
- COMMIT EVERYTHING to GitHub in ENGLISH: new picks file, scripts if modified, LOG.md v3 entry + metrics, v3 report, cover image. Repo: lilaclilac09/inkling-2-small-video-editing.

## 2026-11-13 13:07 — Music feedback

- "Stay Useless" (Cloud Nothings) FIRST 24 SECONDS is very good: exciting, strong beat, great for an opening or when people do something well. Use it for the opening hook / fast flashback, then crossfade to the version's main track.
- The four tracks are DIFFERENT STYLES: one soft/gentle, one funk, one techno, one rock. Map: Another season = soft/gentle; Just Used Music Again = funk; Timing = emotional/K-drama; Stay Useless = rock, high-energy.
- (Note: "Stay Useless" music ends ~163.8s, ~9.6s trailing silence. For the hook, use only the first 24s.)

## 2026-11-13 13:53 — Video feedback (she is unhappy with the template sample)

- The 22-second sample is TOO SHORT. A sample/demo must be long enough to judge (full-length, ~2 min).
- The OPENING PHOTO IS WRONG. Do NOT use the 0026 storefront frame — or ANY shot that is only heads/backs with no front-facing people — as the opening or title-card base. She said this before; it was used anyway. Opening must be a wide shot where you can SEE what is happening: front-facing people, a clear scene, the room, the stage, or the banner with people facing camera.
- v1 (the first cut) was GOOD. Changes made it worse. Go back to what worked in v1; v3 is a refinement, not a reinvention.
- RE-EXTRACT FRAMES from new videos, and SAVE THE DATA (frame extraction results must be persisted to files, not lost).
- GIVE HER THE SHOT LIST (shot-list.md).
- She has NOT HEARD THE MUSIC yet. Music must be audible in samples (not too quiet, not missing).
- CAPTIONS MUST BE WELL-WRITTEN. Garbled English like "that everybody love" and "that follow up questions all the love why" is unacceptable. She wants CULTURED, DETAILED scene descriptions: proper, fluent English (and Chinese where bilingual), describing who is doing what, the mood, what is happening. No awkward phrasing. If a caption reads like broken English, rewrite it.
- "Tame" vs "Taste" (pick 6 subtitle) and "CREWCLAW / white Coca-Cola tee" (pick 8) details are UNRESOLVED — she has not confirmed them yet. Do not present them as settled.

## 2026-11-13 14:29 — GoPro footage

- GoPro-shot footage looks TOO GRAY / washed out. She wants to delete it.
- DO NOT DELETE YET. GoPro flat/log profile looks gray by design; it is fixable with color grading (saturation/contrast boost). Flag GoPro clips in the re-scan report; show her a graded sample first; she decides after seeing it.

## 2026-11-13 13:54 / 14:26 — Drive re-scan

- She is uploading ALL videos to the Drive folder (ID 1Bnwhav0ZaKmBc6BWXHuwg8mcFN--R6CL). When she says "重新扫", re-scan the Drive.
- ONLY process NEW videos. Do NOT re-download or re-process the 68 already scanned (morning only). There are internal records of what was scanned (shot-list.jsonl, media/DJI_001/).
- For new videos: download, extract dense 1fps frames, SAVE the data, update shot-list.md / shot-list.jsonl / talks.jsonl.
- PRIORITY: find the missing afternoon moments — foreign man guitar, other music showcases (piano), girlfriend piece, afternoon plum-rain downpour, big group photo. Report explicitly whether each is found, with clip + timestamp.
- FLAG GOOD OPENING CANDIDATES in the new footage: wide shots with front-facing people, a clear scene, the room/stage, or the banner with people facing camera. Top 3–5 with clip + timestamp + reason.

## 2026-11-13 14:31 — Cover image (new direction, supersedes the single-wide-shot cover)

- Make the cover like Somi's vlog thumbnail (reference: YouTube "somi" search, Somi vlog thumbnail style).
- A 3-PHOTO COLLAGE, 1920×1080, with FEATHERED/SOFT EDGES — the three photos blend into each other, NOT hard-cut rectangles.
- The three photos:
  1. A GIRL with the BAND (a woman posing/taking a photo with the band/musicians).
  2. People OUTSIDE with the LOGO (or with "Ella") — people posing outdoors by the Cursor banner/logo.
  3. An INDOOR SCENE (a good interior shot of the room/event).
- Overlay date "2026.07.19" + "Cursor Cafe Shanghai" in handwritten/refined style; do NOT cover faces or the Cursor logo.
- If a photo type cannot be found, use the closest match and say so — do not invent a photo.

## 2026-11-13 — Reusable vlog template system

- Build a REUSABLE vlog template ("vlog modulator") for future vlogs, not just this event:
  - SUBTITLE FORMAT TEMPLATES: 2–3 reusable styles (cute/handwritten, clean/tech, bilingual EN+CN). Ready-to-use ffmpeg configs.
  - OPENING TITLE CARD + TRANSITION: reusable card (title, date, location) that transitions smoothly into footage (fade/dissolve), film-opening feel, not a hard cut.
  - MOVIE-STYLE CLOSING CREDITS / THANKS: rolling credits or elegant static end card, with music attribution and a "Shot with Inkling 2 Small" credit line.
- Driven by simple inputs (title, date, location, credits list, subtitle style name), not hardcoded to this event.
- Documented (README) so a new vlog can be assembled from the template.

## Standing rules (apply to everything)

- Inkling 2 Small makes ALL picking decisions. Muse only prepares raw material. Repo/demos must NOT show Muse cutting.
- Commit EVERYTHING to GitHub in ENGLISH. Repo: lilaclilac09/inkling-2-small-video-editing.
- Music is COMMERCIAL — demo use only; publishing on social needs clearance/licensed swap.
- Subtitles: bilingual EN + CN, handwritten font preferred (Caveat EN / Ma Shan Zheng CN), refined look, semi-transparent background box, clearly legible. Captions must be proper, fluent, detailed, cultured writing — never garbled English.
- The fine-tuned model checkpoint lives on Tinker, NOT in a GitHub repo. Do NOT access her private repos. Training data (picks) goes in the PUBLIC repo.
- When she pastes someone else's message and asks what it wants, lead with one plain sentence of what the other party asks. When she trails off mid-sentence, ask her to finish rather than guessing.
- Copy-paste text (DMs, messages, application answers) goes in a PLAIN CODE BLOCK, never a blockquote.
- "记得 update readme" — when work ships, update the README to reflect the current state.

---

## How to use this log

- Before starting any cut, pick, subtitle, grade, cover, or template work, READ this log.
- When Aileen gives a new requirement or correction, APPEND it here (with date/time) BEFORE acting on it, and confirm it back to her.
- When a requirement changes, do NOT edit the old entry — append a new entry that supersedes it and references the old one.
- If a requirement in this log conflicts with what a subagent is doing, the log wins — stop the subagent and redirect it.

## 2026-11-13 15:31 — v3 feedback (she dislikes the cover + subtitles)

- COVER IS UGLY (her words: "这篇的太丑了"). Problems:
  - BLACK BAR in the middle of the collage — the feathered edge between photos reads as a black vertical bar, looks like a film-strip simulation. REMOVE it: photos must be properly cut out and blended into each other, NO dark seam/bar.
  - LEFT photo has a HAND stretched across the frame — remove/replace that photo.
  - NO girl front-facing in the cover. She wants a girl's front face.
  - SPECIFIC PHOTO SHE NAMES: a girl in a BLACK HAT and BLACK CLOTHES, front-facing — "把她拿出来" (use her). Find this photo in the photo index (photos/ + photo-index.jsonl) and put her in the cover.
  - TEXT IS UGLY — do not use that font/style for the cover text. Use a better-looking, more refined font.
- SUBTITLES FEEL BRAINLESS ("没有脑袋的感觉") — the captions read as generic/thoughtless. Rewrite them to be genuinely observant and specific to what is actually happening in each segment (real details, real talk content, real human moments), not formulaic scene descriptions. Do not invent talk content.
- FLASHBACK slightly too fast, but acceptable ("还可以") — keep, or slow slightly; do not over-fix.

## 2026-11-13 15:36 — v3 V1 feedback (she likes it overall)

- Overall: the video is shot well ("拍得蛮不错的"). Music opening is good.
- TEXT IS UNCULTURED ("字母写得好没有文化") — the caption wording is poor.
- TALKS: number them "Talk 1, Talk 2, Talk 3, Talk 4" (one two three four) instead of descriptive talk titles. Applies to every talk segment caption. (This supersedes the "observant/specific talk captions" instruction from 15:31 for TALK segments only; non-talk segments still get observant, specific captions.)
- COFFEE MACHINE SOUND in the middle of the video is distracting (room audio). Reduce/denoise the room audio where the coffee machine is loud.
- A COFFEE CUP SHOT looks ugly ("咖啡杯有点太丑了") — identify and remove/replace the ugly cup shot.
- MUSIC: keep Stay Useless first 24s (very good, energetic opening). After that, switch the main track to something GENTLER. (V1's funk "Just Used Music Again" is too much after the opening — use KOYO "Timing" as the gentler main track for V1; V2 keeps "Another season with you".)
- Rest is good ("其他的还蛮好的").

## 2026-11-13 15:39-15:40 — v3 story + cover redesign (major redirect)

- THE CUT HAS NO STORY ("没有什么剧情"). The video must have a narrative arc, not just a montage of talks. Restructure into a story: arrival → room fills → hosts → talks (important ones FIRST) → human moments → closing. Inkling must re-pick/re-order with a story prompt, or the existing picks must be re-ordered into a story.
- USE PHOTOS IN THE VIDEO, not only video clips ("咖啡杯和照片不要只用视频"). Mix still photos (from the 597-photo library) into the cut — Ken Burns / slow zoom on stills, interleaved with video. Find the PRETTIEST shots.
- MUSIC (supersedes 15:36 "gentler" note in part): Stay Useless first 24s opening stays. Main track after that = "Another season with you" (Yerin Baek — she said "Eiling Back", i.e. Yerin Baek). The FUNK track ("Just Used Music Again") is ALSO good — keep it as an alternate version. (V1 main track = Yerin Baek gentle; keep a funk version available.)
- CAPTIONS ARE UNCULTURED ("文案写得太没有文化了"). Write with more culture and restraint. DO NOT deliberately emphasize how good the atmosphere/vibe is ("不要刻意强调氛围有多好"). Do NOT write lines like "bring everyone to laugh together" / "the whole room laughs". Describe what is happening plainly, elegantly, specifically. Talk captions = "Talk 1, Talk 2, Talk 3, Talk 4..." numbering (from 15:36).
- THE TWO HOSTS MUST NOT BE DELETED. They are important. Describe them as: "the friend who came earliest" (来的最早的朋友) and "the friend who has been helping keep order" (一直在帮我们保持秩序的朋友). The hosts shot (0032, hosts at the banner) stays.
- "CALL THE PAT" (15:39:48, unclear — possibly Carl Yang / Talk S, or a specific person/segment): give it more story; put the IMPORTANT talks first. CLARIFY with Aileen who/what "Call the Pat" is.
- COVER REDESIGN (supersedes the 3-photo blended collage):
  - Three blended photos side-by-side looks UGLY. Do NOT do that again.
  - CUT OUT the people (抠图 — mask/extract subjects from background) and ARRANGE them on the cover. The BIGGEST cutout goes in the TOP-RIGHT corner.
  - NO ONE may have their head cut off / beheaded by the crop ("不要有任何人是断头切头").
  - Photos to use: (a) the BEAUTIFUL GIRL UNDER THE GREEN TREES (a video frame or photo — find it, crop her out); (b) a girl ALONE with the banner (solo photo with banner); (c) the BIG GROUP PHOTO AT THE DOOR (门口大合照).
  - Verify by reading the finished cover back: no cut-off heads, no black bar, arrangement clean.

## 2026-11-13 15:59 — app intro annotations

- There is a scene where a HAT-WEARING GIRL introduces her app (Talk E, clip 0042, woman demos her phone app). For the talks, IF the audio is clear enough to hear and transcribe, make a SMALL SUMMARY of what the person is introducing and WHAT IT IS FOR, and add it as a small annotation on the video: an emoji + simple text in a simple font. (Conditional on audio intelligibility — the room audio is noisy; if a talk cannot be heard clearly, do not invent a summary.)
- Ideally do this simple intro for ALL talks, not just the hat girl — a one-line note per talk saying what it is and what it is for.

## 2026-11-13 16:08 — Talk E annotation style

- Do NOT label Talk E narrowly as a "skincare app" (护肤App). Categorize it more broadly as PERSONAL CARE (个人护理) or everyday items/lifestyle (物品/生活类). The annotation should feel like LIFESTYLE content, not a product spec.
- The annotation text should be BIGGER and NICER-LOOKING (larger font, better styling).
- Example direction: "🧴 个人护理——记住你的皮肤，按所在城市的实时天气定制日常护理" / "🧴 Personal care — a routine that remembers your skin and adapts to your city's live weather".

## 2026-11-13 17:09 — v5 subtitle / audio / grade feedback

- NOISE: the noise is loud. When the coffee machine sound is AUDIBLE, ADD A LABEL for it on screen (e.g. "☕ 咖啡机" / "coffee machine") — annotate the sound instead of only denoising it.
- SUBTITLES — layout:
  - Each subtitle stays on screen LONGER.
  - MAX 2 LINES at once — never 4 lines. Mixing EN + CN in 4 lines looks ugly.
  - Format: 1 line EN + 1 line CN max, short and concise. If there is more to say, split it into MULTIPLE sequential subtitles (cycle through them) instead of one long block.
  - When a scene holds/pauses, CYCLE through several subtitle lines for that scene — do not leave one static subtitle sitting there.
  - Placement: keep subtitles at the BOTTOM, consistent. Do NOT scatter them into empty areas of the frame (that looks messy).
- SUBTITLES — style:
  - Background: CREAM / BEIGE (米黄色).
  - Text: BLACK or high-contrast colors. Use APPLE emojis.
  - Current style is uncomfortable to look at; the new style should be warm, clear, cute.
- ANNOTATIONS — content:
  - When you can hear what someone is introducing, explain HOW they used the software/tool to make it (the process), not just what it is.
  - Text MAY BE MORE DETAILED (not just one short line) — but split it into multiple sequential subtitles (max 2 lines each) if long.
- GRADE: warmer, prettier colors, stronger/more vivid contrast, CUTER. Current grade is too flat/cold.
- AUDIO MIX (after the cut): music must NOT cover the voices. Voices should be LOUDER and more SOLID/full. Lower the music relative to the voices; boost/compress the voices if needed.
- ON-SCREEN INFO must be clearer / more legible (captions, annotations, screen text).

## 2026-11-13 17:14 — subtitle timing CORRECTION (supersedes 17:09 "longer duration")

- CORRECTION: do NOT make each subtitle last longer. The OPPOSITE.
- Each subtitle stays for a COMFORTABLE human reading duration (normal, not extended).
- Instead, show MORE segments in sequence: within one scene, cycle through 2-3 subtitle lines consecutively.
- When a scene holds/pauses, keep SWITCHING the subtitle 2-3 times in a row while the person's speech continues in the audio. Do not leave one subtitle static.
- (Max 2 lines at once, cream background, black/high-contrast text, Apple emojis, bottom placement — those stand.)

## 2026-11-13 19:06 — v5 cover: OK overall, cutout edges must be cleaner

- User reviewed cover-v5.jpg: "还可以 这个 还可以 边缘扣的干净点" — the cover is OK overall, but the cutout edges must be cleaned up.
- DO NOT redesign the layout — same composition, same positions, same sizes, same text. Only cleaner edges.
- The previous rembg cutouts have halos / rough fringes / background-colour bleed, and faint grey smudges around the group cutout. Fix by re-extracting with alpha matting and/or refining the alpha mask (erode 1-2px, feather, defringe).

## 2026-11-13 19:07 — v5 cover: group bigger, banner in background, legs back

- User's verdict: the cutouts are good, sizes/placement are good, the beautiful girl (hero, green trees) is very good — "真的很不错，好多了好多了". Just these small changes and it will be perfect.
- MIDDLE GROUP BIGGER: the group in the middle (HM5A1478) should be made larger — they are the group, show them bigger.
- GROUP LEGS WERE CUT OFF: "中间这个，怎么把腿抠没了" — the group's legs got cut off in the cutout. Restore the FULL legs (re-extract so the whole body including legs is in the mask, and place them so the legs are fully visible inside the canvas, not cropped).
- BACKGROUND: show a bit of the BANNER in the background (the Cursor / collaboration banner) — the cover background should not be only plain cream; a bit of banner should show through.
- LEFT GIRL (black-hat girl, HM5A1822): REVEAL HER BACKGROUND — do not cut her out clean onto plain cream; show the background behind her (the banner she was photographed in front of).
- SHOW ALL THE TEXT: the words/text on the banner must be visible and legible ("把所有的字亮出来").
- Cleaner cutout edges (from 19:06) still apply.

## 2026-11-13 19:08 — v5 cover: legs + background behind the men + interior speaking shots + typography

- User is quite satisfied with the cover overall ("这个封面图还蛮满意的", "剪得很好"), only the typography/layout is a bit ugly ("只有排版有点难看").
- THE MAN/MEN IN THE MIDDLE HAVE NO LEGS (repeated, emphatic): "中间那个男的怎么没有腿啊" — restore full legs on the group cutout. This repeats the 19:07 legs point; make sure the legs are actually visible this time.
- BACKGROUND BEHIND THE MAN/MEN MUST SHOW TOO: "那个男的背后的那个背景也要露出来" — like the left girl, the group should keep their background visible behind them, not be a clean cutout on plain cream.
- INTERIOR SPEAKING SHOTS: pick shots that show someone SPEAKING/presenting — interior scenes of a talk in progress ("选一些能够看到就是他正在演讲的那种内部的景象"), inside + banner ("内内外 banner"). Use an interior presenting shot as a background element if it fits the layout.
- TYPOGRAPHY: improve the cover text styling — current layout/typography looks a bit ugly. Keep the same text ("Cursor Cafe Shanghai" / "2026.07.19") but make it look better.

## 2026-11-13 19:16 — v5 video: subtitles need more adjustment + opening voices too loud

- SUBTITLES STILL NEED ADJUSTMENT (she did not specify exactly how yet — clarification pending; she trailed off mid-sentence).
- OPENING VOICES TOO LOUD: at the very start, where the video shows/says the outside is bustling/noisy ("外面闹"), the human voices (room/crowd audio) are WAY too loud. The v5 boost (room 1.6 + compressor) overshot at the opening. Pull the room audio down at the opening and/or rebalance vs music.
- The opening does not SHOW the bustling outside the way the subtitle describes it ("你没有展现出来这个样子") — the visuals/audio do not convey the noisy/bustling street as claimed. Needs clarification on what she wants the opening to show.
- She trailed off ("然后我觉得这个不是很,那个什么我们就对先") — asked to finish the sentence before re-rendering.

## 2026-11-13 19:17 — v5 subtitles: unify fonts, wider cream box, no outline; speed is good

- SUBTITLES ARE INCONSISTENT: the live subtitles are not uniform — fonts differ between earlier and later parts ("字体前后不一致"). UNIFY the fonts: same font set for all captions and annotations throughout the whole video.
- CREAM BACKGROUND BOX WIDER: the light-yellow/cream subtitle box should be LONGER (wider) so that ALL text has a bit of blank space on the LEFT and RIGHT sides — visible padding/margin on both sides of the text inside the box.
- FONT OUTLINE: remove the outline/border around the glyphs ("字体本身就不要去包线了") — black text on the cream box, no stroke/border around the letters.
- SPEED IS GOOD: the current subtitle timing/cycling speed is fine ("现在这个速度就蛮好") — do NOT change the timing.
- (Bundled re-render fix from 19:16: pull the room audio DOWN during the opening ~24s only — the voices are too loud at the start. The rest of the mix stays as v5.)

## 2026-11-13 19:19 — coffee label: bigger speaker icon + "this is the coffee machine sound"

- COFFEE LABEL CHANGE (video): where the coffee machine sound is heard mid-video, replace the small "☕ 咖啡机 · coffee machine" label with a BIGGER SPEAKER icon (small horn/loudspeaker, e.g. 🔊) plus text saying THIS IS THE COFFEE MACHINE SOUND ("这是咖啡机的声音"). Make the label bigger/more prominent than the current small one.
- Note: colour emoji do NOT render in this libass build (tofu) — only the monochrome ☕ glyph rendered. If a speaker emoji does not render, use an image overlay or a text glyph that does render; do not ship tofu boxes.

## 2026-11-13 19:19 — COVER: NO MORE CUTOUTS — mood board style (supersedes the cutout direction)

- User verdict: the cover is very good ("这个封面很好啊"), BUT the cutouts look weird ("你抠得起那怪怪的") and the middle group's legs STILL have not come back ("中间这个腿还是没有回来").
- DECISION — STOP CUTTING OUT PEOPLE ENTIRELY ("你干脆不要抠了", "我觉得还是不要抠了"). This SUPERSEDES the 15:40 cutout direction (cut out people and arrange cutouts) and the v5/v5b cutout approach.
- NEW APPROACH — MOOD BOARD: put the photos on a canvas like a mood board ("用一个 canvas 上面放像 mood board 一样把它放上去，中间隔一点就可以了"). Rectangular photo panels placed on the cream canvas with a little SPACE/GAP between them. No masks, no rembg cutouts, no feathered edges — just the photos as they are.
- Same photos/layout as the v5b cover (text top-left, interior speaking shot top-centre, green-trees girl top-right, black-hat girl with banner bottom-left, group bottom-centre, bigger with full legs + background). The hero girl becomes a photo panel too (full photo with her green-trees background), NOT a cutout.
- The legs problem is solved by construction: full photos show full bodies naturally, no mask can truncate them.
- (Her "cut out the top-right girl and another girl in profile" suggestion in the same message is superseded by the "don't cut out" decision that followed it in the same breath.)

## 2026-11-13 19:42 — COVER mood board: use the ORIGINAL full photos, no cropping + add more photos

- User: the mood-board direction is right ("对，是这样"), BUT the photos are still cropped/cut ("你还是call图了") — she can tell they are not the full pictures.
- DO NOT CROP: go find the ORIGINAL full photos of the four images and place them on the canvas AT PROPORTIONAL SCALE ("按比例贴") — keep each photo's original aspect ratio, just scale to fit. No cropping, no cutting out.
  - This means: full HM5A1822 (black-hat girl, not the 0.76 crop) and full HM5A1478 (group, not the 0.84 crop — even if the 8th man is in it). Full frames for the interior shot and the hero too.
- ADD MORE PHOTOS to the mood board: find interior shots of talks/speaking in CLOSE-UP ("室内的演讲的大头的画面") and shots of people INTERACTING/CHATTING ("大家交流的画面"), and paste those on as well.
- Still a mood board, still no cutouts, still cream canvas with gaps between panels. Same text ("Cursor Cafe Shanghai" / "2026.07.19").
