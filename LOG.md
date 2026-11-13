# Build Log — Inkling 2 Small Video Editing

A running log of every step in this demo. Each entry says what was done, when,
and what the result was. Quality numbers (extraction density, classification
accuracy, cut precision) are recorded here as they are measured.

All times are Asia/Shanghai (CST, UTC+8).

---

## 2026-11-12 — Setup

- **Tinker API access verified.** Credential `custom.tinker`, normal User-Agent.
  Inkling 2 Small 256K variant (`thinkingmachines/Inkling-2-Small:peft:262144`)
  returns HTTP 200 on the Anthropic-compatible endpoint.
- **Master prompt written** (`inkling-demo-master-prompt.txt`, 12 sections):
  story, atmosphere, 10 priorities, 3-node structure, style rules, music
  (KOYO "Timing" + 3 alternates + beat grid), pick rules, output format.
- **Pipeline scripts written** (`inkling-video-pipeline.py`,
  `inkling-video-combine.py`, `inkling-video-cut.py`,
  `inkling-video-recap.py`, `inkling-video-editor-mcp.py`,
  `inkling-video-sft.py`).
- **Per-asset size limit found:** the Tinker API rejects any single attached
  asset over 2,097,152 bytes (2 MB). Raw MP4 clips can never be attached;
  only text + sub-2MB images. Workaround: keyframes resized to 1280px wide.

## 2026-11-13 01:35 — First rough cuts (versions A and B)

- **Source material:** 59 MP4 clips + 300 JPG photos (6.0 GB) from the event,
  downloaded from Google Drive to the build VM. All footage is morning-only
  (09:16–12:21, 2026-07-19). No guitar, piano, rain, or group photo in this
  batch. Whisper transcripts are mostly hallucinated crowd noise; picks were
  made from visual keyframes, not transcripts.
- **Version A (Muse picks):** `recap-rough.mp4`, 123.35 s, 17 segments,
  146 MB. Picks from visual keyframes.
- **Version B (Inkling 2 Small picks):** one API call, 66 keyframes as
  base64 (9.8 MB request), 53,527 input tokens, 10,000 output tokens,
  cost ~$0.03. 16 complete picks, 109.0 s. One filename slip corrected
  (pick #1 timestamp). Cut to `recap-inkling.mp4`, 109.13 s, 119 MB.
- **A/B overlap:** 6 clips shared. A leans atmospheric/structural; B leans
  product-specific (it read the screens).
- **Reports pushed:** A/B comparison to `aileen_machina_01`, Inkling method
  report to this repo (`how-inkling-2-small-cut-this-video.md`).

## 2026-11-13 08:58 — Photo classification (300 photos)

- All 300 photos classified by scene: talk 101, social 73, audience 45,
  demo 40, portrait 21, group 7, signage 7, detail 2, bad 4.
- 54 burst groups (255 photos) + 45 singletons; 99 best-of-burst selected.
- Headshots split: men 19, women 2 (thumbnail reads, approximate).
- Group photo to keep: HM5A1478. Delete candidates: 4.
- 69 photos (23%) need 90-degree rotation.

## 2026-11-13 09:53 — Research: Kling AI, Seedance, directors

- `research-shot-picking-transitions.md` (26 sources, all URLs verified).
- Kling 3.0 = storyboard first (wide → close-up, per-shot framing/duration/
  camera, transitions), then generate. Seedance = single-pass coherence,
  one action + one camera move + one duration per shot, transitions
  beat-matched to audio. Neither has an official GitHub repo (closed/
  commercial). Closest real repo: Kuaishou Mise-en-Video.
- Directors' rules adopted: coverage wide → tight, re-establish with a wide
  after close-ups, hide cuts inside motion (match on action), bridge with
  sound (J/L-cuts), cut to the listener's reaction, save the tightest
  close-up for the emotional peak, cut on music phrase boundaries
  (Timing 19.4 s), photos as 1–2 s flashbacks, never long holds.

## 2026-11-13 10:02 — Music: all 4 tracks downloaded and verified

- KOYO "Timing" — 196.44 s (3:16). YouTube fan video.
- 88rising & RHYME SO "Just Used Music Again" — 211.02 s (3:31). Official.
- Yerin Baek "Another season with you" — 210.07 s (3:30). Official.
- Cloud Nothings "Stay Useless" — 173.38 s (2:53; ~9.6 s trailing silence,
  music ends ~163.8 s). Official Carpark Records video.
- All MP3, 44.1 kHz stereo, in `music/`. Downloaded with yt-dlp (Android
  player client; default web client was bot-blocked). Spotify has no
  download API and was not used.
- All 4 uploaded to the Google Drive source folder for later reuse.
- Copyright: commercial tracks, demo use only. Publishing on social needs
  clearance or a licensed swap.

## 2026-11-13 10:08 — Repo renamed

- Old name `ripple` was unclear. New name: `inkling-2-small-video-editing`.
- Direct rename was blocked (GitHub 403: the API key lacks admin permission),
  so a new repo was created under the new name and all 9 files were migrated
  from `ripple`. The old `ripple` repo still exists; it can be deleted in
  the GitHub web UI.
- Framing going forward: Muse only prepares the raw material (transcripts,
  keyframes, packaging, ffmpeg cutting). Inkling 2 Small makes all the
  picking decisions. The repo shows what Inkling did, not Muse.

## 2026-11-13 10:13 — Photos rotated and cleaned (original 300)

- 70 files rotated 90° counter-clockwise to upright (67 from the rotation
  set + 3 the first pass missed). 2 in the set were already upright
  (HM5A1497, HM5A1498) and were not rotated.
- 4 bad shots deleted (HM5A1332, HM5A1357, HM5A1539, HM5A1614), moved to
  recoverable trash (expiry 2026-12-13). Still present in Google Drive.
- Index: 300 → 296 rows. Best-of-burst: 99 → 95. 0 broken symlinks.
- Method: jpegtran was not installable in this VM, so PIL at quality 100 /
  4:4:4 was used (visually lossless; files roughly doubled in size).
- Note: a second batch of photos is still downloading to the same Drive
  folder (405 JPGs on disk and growing, ~593 total). The new files are NOT
  in the index and will need their own classification + rotation pass.
  The 37 files still at Orientation 8 are all from this new batch.

## 2026-11-13 10:29 — Report: is Inkling 2 Small suitable for frame work?

- `inkling-frame-classification-suitability.md` (283 lines, English).
- Verdict: suitable for the judgment half (keyframe selection, shot
  classification), unsuitable for the mechanical half (raw frame extraction —
  it cannot ingest video at all; ffmpeg does that, deterministically, free).
- Evidence: model card benchmarks (PerceptionBench 64.7%, MMMU Pro 81.6%,
  ScreenSpot Pro 83.8%, MuirBench 79.2%); 6 arXiv papers (CLIP, SGNet/
  MovieShots, ReaSon, KTV, EFS, FORTE); 5 GitHub repos (HotClip, learn-video,
  CLIPPER, KTV, ReaSon) + Tinker Cookbook.
- Explicit finding: no public GitHub repo using Inkling 2 Small for video
  work exists yet (model is 8 days old).
- Limits noted: no audio input, no fine-grained temporal precision (12 of 16
  version-B picks defaulted to clip starts), no video benchmark on the model
  card — accuracy on our shot taxonomy is unmeasured until spot-checked.

## 2026-11-13 10:47 — Shot list done (dense 1 fps, 68 clips, 1108 frames)

- `shot-list.md` (407 lines) + `shot-list.jsonl` (1108 rows) + `talks.jsonl`
  (17 talks). Frames in `frames-dense/` (1 fps, 1280 px, JPEG q4).
- Coverage: 68 clips, 1110.2 s total, 07:23–12:21 (morning only). Effective
  fps 0.998. 68/68 clips have frames (100%).
- Shot-type counts: (1) storefront ultra-wide 59; (2) secondary wide 38;
  (3) interior ultra-wide 754 (68%); (4) person close-up 194; (5) audience
  close-up 52; (6) hands/items 7; (7) timelapse 0; uncertain 4.
- Confidence: 1104 confident, 4 uncertain (motion-blurred frames in clip
  0038, t=14–18s).
- **Guitar moment: NOT FOUND in this footage.** Actively searched all 68
  clips (first/middle/last frames + extra frames of long clips). No guitar,
  no foreigner with a guitar, no music performance. Guitar/piano/rain/
  girlfriend-piece are afternoon/evening material, not in this morning batch.
  If afternoon footage is uploaded, search there.
- Warmest talk: Talk L (Pairoa) — room laughs together in clip 0051,
  audience member gestures back in 0050. Best human-warmth beat.
- New files folded in during the job: 9 MP4s (final 68 clips) + photos now
  597 JPGs. Final Drive re-check before delivery: no new files.
- Spot-check (parent, 5 random frames, one per category 1/3/4/5/6):
  **5/5 correct.** Small sample — a larger check would firm up the number,
  but the classification looks sound.

## 2026-11-13 10:52 — README and master prompt updated (new repo)

- README rewritten: title now "Inkling 2 Small Video Editing"; framing
  is explicit (Inkling decides, Muse only prepares raw material); Music
  section expanded (Timing + 3 alternates + beat grid); story and
  transitions section added; file index added.
- Master prompt updated: §5 flashback rule tightened (photos are 1–2 s
  flashbacks, never long holds); §12 input is now 1 fps dense; new §13
  shot taxonomy (7 types); new §14 transitions and story (wide → tight,
  match on action, J/L-cuts, cut to the listener, peak close-up saved,
  cut on phrase boundaries).

## 2026-11-13 11:52 — Re-cut v2 done (Inkling picks + crossfades + music + subtitles)

- **v2 picks (Inkling 2 Small, 256K variant):** one API call over the dense
  shot list, ~60-80 representative frames + master prompt (§13 taxonomy,
  §14 transitions). 17 picks, 120.0 s total. Arc: wide open (storefront +
  banner 0026, hosts 0032) → setup → talks (A/B/E/G/H) → Pairoa build-up
  (0049, 0050) → **peak: 0051 room laughs, pick #12, 12 s (longest)** →
  listener cut (0063) → ARIAVA (0059, 0062) → wide close (0052, 0079).
  All timestamps within clip durations, all filenames match real files,
  all nodes "morning". No guitar moment — correctly not included.
- **First attempt truncated:** `stop_reason: max_tokens` at 16,000 output
  tokens (only 5 complete picks) — the model's 35,711-char thinking block
  ate the budget. Re-ran with `max_tokens: 32000`; finished
  `stop_reason: end_turn`, 17 picks, 15,933 output tokens. Total cost for
  both calls ≈ **$0.05** (input $0.30/1M, cached $0.03/1M, output $1.00/1M).
- **Cut:** `recap-v2.mp4`, **112.0 s**, 1920×1080, 30 fps, H.264 + AAC,
  64 MB, 3360 frames. 17 segments joined with **0.5 s crossfades**
  (xfade video + acrossfade audio) between every pair. **Music:** KOYO
  "Timing" mixed at 0.15 under the room audio. **Subtitles:** one caption
  per segment (the pick title) burned in, white with black outline.
- **Two build problems found and fixed:**
  - Source clips have mixed resolution/fps (2688×1512 @ 59.94, 2688×1512
    @ 29.97, 1920×1080 @ 29.97). xfade requires identical inputs, so
    segments are now normalized to 1920×1080 @ 30 fps during the cut
    (`inkling-video-recut.py`).
  - The single 18-input xfade join **OOM-killed** the VM (6 GB). Rebuilt
    the join in two groups (seg 0–8 → groupA, seg 9–16 → groupB, then
    A+B) with `inkling-video-join.py`; peak memory stayed under 4 GB.
- **Verification:** final duration 112.0 s = 120.0 s picks − 16×0.5 s
  crossfades (exact). Frame check: opening subtitle "Storefront and
  Cursor Cafe banner" visible at t=3 s; peak subtitle "Talk L: the room
  laughs" visible at t=80 s with the laughing room in frame. Audio: stereo
  AAC, room + music mixed.
- **Two model-read details to confirm on viewing:** pick 8 names a
  "CREWCLAW code demo" / "white Coca-Cola tee" (shot list: "white tee with
  red logo"); pick 6 reads the screen as "Tame your wild, vibe-coded apps"
  (shot list: "Taste your wild…"). Both are plausible reads from the
  frames; flag for a visual check, not a re-pick.
- **Delivered to Aileen in chat** (recap-v2.mp4 attached) with a note on
  the "Tame/Taste" wording to confirm.

## 2026-11-13 13:20 — Vlog template system (reusable: opening + subtitles + closing)

- **`vlog-template/`** turns the one-off Cafe Cursor pipeline into a reusable
  vlog modulator. Every piece takes plain inputs (title, date, location,
  captions list, credits list) — nothing is hardcoded to this event.
- **Subtitles** (`subtitles/make_subtitles.py` + `styles.json`): 3 styles,
  captions JSON -> ASS, burned with ffmpeg libass.
  `cute` = Caveat EN / Ma Shan Zheng CN, warm white, handwritten;
  `clean` = DejaVu Sans / Noto Sans CJK SC, no box, tech talks;
  `bilingual` = EN over CN on a semi-transparent box.
  All three verified legible on real footage frames.
- **Opening** (`opening/make_opening.py`): 1920x1080 title card from any wide
  shot (darkened + bottom gradient, text in the lower half so a banner/logo
  in the top quarter is never covered), slow Ken Burns zoom, fades in from
  black. Title font auto-picks Caveat (Latin) or Ma Shan Zheng (Chinese).
- **Closing** (`closing/make_closing.py`): movie-style, credits JSON driven.
  `scroll` = rolling credits over black (gold headings, "Shot with Inkling
  2 Small" footer, music attribution); `card` = static "Thanks for watching"
  end card. Both take `--music` (mixed at 0.3, faded out).
- **Assembler** (`assemble_vlog.py`): opening + body + closing with 0.5 s
  dissolves (xfade + acrossfade). Sample: 3 + 12 + 8 − 2×0.5 = **22.04 s
  exact**; dissolve frames verified (title card melting into footage).
- **Two bugs found and fixed during testing:** (1) `styles.json` lacked
  `back_color` for cute/clean — generator now defaults it; (2) the scroll
  credits filter referenced audio input `[1:a]` but music is input `[2:a]`
  (background + roll image come first) — fixed by threading the audio index
  through; (3) long footer lines overflowed the 1920 px roll — fonts now
  shrink-to-fit (max width 1760 px).
- Sample videos are local only (`vlog-template/samples/`); scripts, docs,
  and verification frames are in the repo.

## In progress

- **Frame extraction + shot list.** Dense 1 fps extraction across all clips,
  classified into 7 shot types (storefront ultra-wide, secondary wide,
  interior ultra-wide, interior person close-up, interior audience close-up,
  hands/items close-up, timelapse), plus a per-talk table (speaker, topic,
  content, audience size, reaction, Q&A, relatability) and a flagged
  must-keep guitar moment (foreigner with glasses + guitar + wife behind).
  Quality metrics (extraction density, classification counts, confidence)
  will be recorded here when it reports.
- **Re-cut (vlog style).** New picks, transitions, story arc, wide shots,
  flashback photos (1–2 s), subtitles, music mix (Timing main, 3 alternates
  available). Report will map each Kling/Seedance/director principle to
  where it was used in the cut.

---

## Quality metrics

Recorded as measured. "Accuracy" is estimated by spot-checking a random
sample of classifications against the frames themselves.

| Metric | Value | How measured | When |
|---|---|---|---|
| Frame extraction density | 1108 frames / 1110.2 s = 0.998 fps, 68/68 clips covered (100%) | frames / total video seconds | 2026-11-13 10:47 |
| Shot-type classification counts | (1) 59, (2) 38, (3) 754, (4) 194, (5) 52, (6) 7, (7) 0, uncertain 4 | per-category frame counts | 2026-11-13 10:47 |
| Classification accuracy (est.) | 5/5 correct in a random 5-frame spot check (one per category) — small sample, looks sound | random-sample spot check | 2026-11-13 10:47 |
| Cut precision | exact: final 112.0 s = 120.0 s picks − 16×0.5 s crossfades; all 17 segments present; subtitles verified on frames (opening t=3 s, peak t=80 s) | final duration vs picks sum; visual frame check | 2026-11-13 11:52 |
| v2 picks (Inkling) | 17 picks, 120.0 s; all timestamps in range, all files exist, all nodes "morning"; peak 0051 laughter in at #12 | picks file validation + clip existence check | 2026-11-13 11:52 |
| v2 picks cost | ≈ $0.05 for 2 calls (attempt 1 truncated at 16k tokens, attempt 2 at 32k succeeded) | Tinker billing rates, token counts from API | 2026-11-13 11:52 |
| Music duration verification | 4/4 exact | ffprobe vs expected length | 2026-11-13 10:02 |
| Photo rotation | 70/70 upright, 0 failures | EXIF Orientation check | 2026-11-13 10:13 |
| Photo index integrity | 296 rows, all files present | row count + file existence | 2026-11-13 10:13 |
| Vlog template verification | 3/3 subtitle styles legible on frames; opening card + scroll + card render at 1920x1080; assembled sample 22.04 s = 3+12+8−2×0.5 s (exact); dissolves verified on frames | visual frame reads + ffprobe durations | 2026-11-13 13:20 |
