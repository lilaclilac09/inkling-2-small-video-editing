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
