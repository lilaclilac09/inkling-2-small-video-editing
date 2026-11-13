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
| Frame extraction density | pending | frames / total video seconds | after shot list |
| Shot-type classification counts | pending | frames per category | after shot list |
| Classification accuracy (est.) | pending | random-sample spot check | after shot list |
| Cut precision | pending | final segments vs Inkling picks | after re-cut |
| Music duration verification | 4/4 exact | ffprobe vs expected length | 2026-11-13 10:02 |
| Photo rotation | 70/70 upright, 0 failures | EXIF Orientation check | 2026-11-13 10:13 |
| Photo index integrity | 296 rows, all files present | row count + file existence | 2026-11-13 10:13 |
