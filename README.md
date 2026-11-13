# Inkling 2 Small Video Editing

Cut videos with Inkling 2 Small on Tinker. Built for the Cafe Cursor Shanghai recap, July 2026.

## Who does what

**Inkling 2 Small makes every creative decision.** It reads the keyframes and the transcript, picks the moments worth keeping, orders them into a story, and explains each pick. The model is the editor.

**Muse only prepares the raw material.** It downloads the footage, runs Whisper for transcripts, extracts keyframes, shrinks them under the 2 MB API limit, packs everything into one structured input, and runs ffmpeg to cut exactly what Inkling specified. Muse does the deterministic plumbing — fetching, converting, packaging, cutting. It does not pick.

That split is the point of this repo: the demo shows what the model can do, not what the assistant can do.

## The loop

Video goes in, a finished recap comes out. Inkling does the thinking, ffmpeg does the cutting.

1. **Transcribe.** Whisper turns each clip into a transcript. The clips here carry little clean speech, so the transcript is thin and the pictures do most of the work.
2. **Keyframes.** One frame per second (dense), downscaled to 1280px wide so each file stays well under the limit below. 1 fps is the dense, workable version — 30 fps would be ~33,000 frames and is not usable.
3. **Classify.** Every frame is labelled into one of 7 shot types: (1) storefront ultra-wide, (2) secondary wide (one screen / one poster), (3) interior ultra-wide, (4) interior person close-up, (5) interior audience close-up, (6) hands/items close-up, (7) timelapse. The classification is recorded per frame in `shot-list.jsonl` with a confidence flag.
4. **Pick.** Inkling 2 Small reads the master prompt, the combined transcript and the keyframes, then picks the moments worth keeping. It outputs timestamps and a plan, never a video file.
5. **Cut.** ffmpeg cuts the picked segments from their source clips, joins them in order, adds transitions, mixes music low under the voices, and applies a light vintage grade. Photos appear as 1–2 s flashbacks, never long holds.

The picks become training data. Approved picks are saved as examples and used to fine-tune Inkling 2 Small on Tinker, so the loop gets closer to the editor taste over time.

## The 2 MB limit

Inkling rejects any single attached asset over 2,097,152 bytes (2 MB). A raw 4K clip is 20 to 140 MB, so it can never be attached directly.

The workaround is to split the problem, not the model input:

- **Never send video.** Send text (the transcript) and still images (the keyframes) only.
- **Shrink the frames.** Downscale keyframes to 1280px wide at JPEG quality 4. A 4K frame is several megabytes; the same frame at 1280px is around 30 KB.
- **Scan per clip, decide once.** Each short clip is transcribed and framed on its own, then all the transcripts and keyframes are combined into one pack so Inkling picks across the whole day in a single session.
- **Cut locally.** Inkling returns timestamps. The actual cutting happens on local disk with ffmpeg, where file size is not a constraint.

## Story and transitions

The recap is cut as a vlog, not a montage. The structure is: a hook (the warmest moment first) → a fast flashback → exterior/street, then the full room, then the day unfolding talk by talk → the warmest moment (the room laughing together) as the emotional peak → Q&A → a closing wide + photo flashbacks.

Transitions follow the directors' rules, not hard cuts: coverage goes wide → tight and re-establishes with a wide after close-ups; cuts hide inside motion (match on action); sound bridges the cut (J/L-cuts) instead of silence; the cut lands on the listener's reaction, not the speaker; the tightest close-up is saved for the emotional peak; cuts land on music phrase boundaries (see the beat grid below); photos are 1–2 s flashbacks, never long holds. The full research behind these rules is in `research-shot-picking-transitions.md` (in the build workspace) and the per-cut mapping is in the re-cut report.

## Re-cut v3 (current)

The current cut. 21 picks from Inkling 2 Small (256K variant), 118.0 s of picks, 107.6 s finished. Same picks, subtitles and audio in both versions; they differ in grade and music only.

| | Version 1 — Korean variety | Version 2 — Silicon Valley |
|---|---|---|
| File | `recap-v3-just-used-music-again.mp4` | `recap-v3-another-season.mp4` |
| Music | "Just Used Music Again" (funk) | "Another season with you" (soft/gentle) |
| Grade | Korean variety / dating-show: soft, glowy, warm. `eq=saturation=1.10:contrast=1.05:brightness=0.05`, warm tint | Silicon Valley: crisp, cool, strong contrast. `eq=saturation=1.05:contrast=1.15:brightness=-0.02`, cool tint |
| Duration | 107.6 s, 1920×1080, 30 fps, 66 MB | 107.6 s (expected) |

Both versions open with the same hook: Cloud Nothings "Stay Useless" (rock, high-energy) for the first 24 s — the hook and fast flashback — then crossfade into the version's main track. Room audio 1.4 (voices forward), music 0.30.

**Subtitles:** bilingual outline captions, one per segment. English in Caveat (handwritten, 52 pt bold), Chinese in Ma Shan Zheng (handwritten-style, 46 pt), on a semi-transparent dark box. Each caption is a fluent, detailed one-line description of the scene (who is doing what, the mood), not just a title.

**What v3 changed vs v2:** hook first (Talk L, the room laughing), fast 5×2 s flashback, organised by space (exterior → interior), more women and more exterior/street shots, the pink/blonde woman removed (clips 0026/0052 excluded; one Inkling pick corrected 0042→0032), the Cursor logo prominent in 3 picks, louder audio, two grades and two music tracks to compare. The v2 structure is the backbone; v3 is a refinement, not a reinvention. Full detail in `report-v3.md`.

**What is NOT in the cut:** the guitar/piano/music showcases and the afternoon rain are not in the morning footage (all 17 talks are AI tools/agents/apps/code). They are afternoon material, to be added when that footage arrives. Nothing was invented.

## Cover image

`cover-v3.jpg` (1920×1080). A Somi-style 3-photo collage with feathered/soft edges — the three photos blend into each other, no hard-cut rectangles:

1. A girl with a group (HM5A1557 — woman in a white shirt with a group by the banner). There is no band/musicians photo in the morning material, so this is the closest match.
2. People outside with the logo (HM5A1478 — the group photo, eight men posed by the Cursor banner, logo fully readable).
3. An indoor scene (a woman presenting at the screen, audience at tables).

Date "2026.07.19" and "Cursor Cafe Shanghai" in Caveat (handwritten) at the bottom, over a subtle dark gradient. The text does not cover any face or the Cursor logo; the banner logo stays visible and uncovered.

## Music

Main track and alternates. All four are downloaded and verified (see `LOG.md`). All are commercial tracks — fine for the demo, needs clearance or a licensed swap before publishing on social platforms.

The four tracks are different styles: Another season = soft/gentle; Just Used Music Again = funk; Timing = emotional/K-drama; Stay Useless = rock, high-energy.

**Main: KOYO — "Timing" (타이밍)**, 3:16, 99 BPM. Korean OST ballad (EXchange2 Pt. 4 OST, Sep 24 2022). Beat 0.61 s, bar 2.42 s. 8-bar phrase boundaries (19.4 s): 0:00, 0:19, 0:39, 0:58, 1:18, 1:37, 1:56, 2:16, 2:35, 2:55, 3:14. Cut on phrase boundaries. Music stays low (volume 0.15) under voices in v2; 0.30 in v3.

**Alternates:**
- 88rising & RHYME SO — "Just Used Music Again", 3:31, 123 BPM (funk).
- Yerin Baek — "Another season with you", 3:30, 120 BPM (soft/gentle).
- Cloud Nothings — "Stay Useless", 2:47 (file 2:53, ~9.6 s trailing silence), 169 BPM (rock). The first 24 s are the high-energy hook in v3; the main track crossfades in after.

## Vlog template system

`vlog-template/` turns the one-off Cafe Cursor pipeline into a reusable vlog kit. Nothing is hardcoded to this event — every piece takes plain inputs (title, date, location, a captions list, a credits list) and produces a 1920×1080, 30 fps segment that slots into the existing ffmpeg pipeline. Full docs in `vlog-template/README.md`.

- **Subtitle styles** (`subtitles/`): 3 styles — `cute` (Caveat EN / Ma Shan Zheng CN, handwritten, warm), `clean` (DejaVu Sans / Noto Sans CJK SC, no box, for talks), `bilingual` (EN over CN on a semi-transparent box). `make_subtitles.py` turns a captions JSON file into a `.ass` file; burn it with ffmpeg libass.
- **Opening title card** (`opening/`): `make_opening.py` builds a 1920×1080 card from any wide shot (darkened + bottom gradient, text in the lower half so a banner/logo in the top quarter is never covered), with a slow Ken Burns zoom and a fade in from black. Title font auto-picks Caveat (Latin) or Ma Shan Zheng (Chinese).
- **Closing credits** (`closing/`): `make_closing.py` makes movie-style credits from a credits JSON file — `scroll` (rolling credits over black) or `card` (static "Thanks for watching" end card). Both end with a "Shot with Inkling 2 Small" footer and a music attribution.
- **Assembler** (`assemble_vlog.py`): joins opening + body + closing with 0.5 s dissolves.

```bash
# 1. Cut the body (picks -> segments -> join), e.g. inkling-video-recut-v3.py
# 2. Build the template pieces:
python3 vlog-template/subtitles/make_subtitles.py --captions my-captions.json --style bilingual --out my.ass
python3 vlog-template/opening/make_opening.py --title "My Vlog" --date "2026.10.12" --location "Berlin" --image base.jpg --out opening.mp4
python3 vlog-template/closing/make_closing.py --credits my-credits.json --mode scroll --out closing.mp4
# 3. Assemble:
python3 vlog-template/assemble_vlog.py --opening opening.mp4 --body recap.mp4 --closing closing.mp4 --out my-vlog.mp4
```

## Storage

Footage and working files live on the builder machine or in the shared Google Drive folder, whichever is convenient. The finished recap is a single mp4. Nothing here needs a special store. The four music tracks are also uploaded to the shared Drive folder for later reuse.

## Scripts

| Script | What it does |
| --- | --- |
| `inkling-video-pipeline.py` | One clip in: probe, transcribe, extract keyframes, build a pack |
| `inkling-video-combine.py` | Merge per-clip outputs into one pack for a whole-day pick |
| `inkling-video-cut.py` | Cut one clip per pick with the vintage grade |
| `inkling-video-recap.py` | Cut picked segments from many source clips and join them into the recap |
| `inkling-video-recut-v3.py` | v3 re-cut: cut + grouped join + bilingual ASS subtitles + music bed (room 1.4, music 0.30), `--grade korean\|silicon` |
| `inkling_picks_v3.py` | v3 picks: call Inkling 2 Small via Tinker with the v3 constraints |
| `inkling-video-sft.py` | Summarise approved picks and fine-tune Inkling 2 Small on Tinker |
| `inkling-video-editor-mcp.py` | Minimal MCP server: probe, transcribe, keyframes, cut, recap |
| `inkling-demo-master-prompt.txt` | The master prompt Inkling picks from (14 sections) |

## Files in this repo

- `README.md` — this file.
- `LOG.md` — a running build log: every step, with dates and quality numbers (extraction density, classification counts, spot-check accuracy, cut precision).
- `requirements-log.md` — the append-only requirements log: every requirement from Aileen, in order, from the original brief through v3. All cutting/picking/subtitling/grading/cover work follows this log.
- `report-v3.md` — the v3 re-cut report (picks, exclusions, counts, grades, audio, cover, verification).
- `shot-list.md` — the dense 1 fps shot list: 68 clips, 1108 frames, 7 shot types, per-talk table.
- `scan/inkling-video-picks-v3.jsonl` — the v3 picks (21 picks, Inkling 2 Small).
- `scan/captions-v3.ass` — the v3 bilingual outline subtitles (Caveat + Ma Shan Zheng).
- `cover-v3.jpg` — the v3 cover (Somi-style 3-photo collage, feathered edges).
- `how-inkling-2-small-cut-this-video.md` — how Inkling 2 Small cut the first recap (method, the 2 MB limit, cost ~$0.03).
- `inkling-frame-classification-suitability.md` — is Inkling 2 Small suitable for frame extraction and classification? (Answer: no for extraction, yes for selection and classification — with evidence, papers, and GitHub repos.)
- `inkling-demo-master-prompt.txt` — the master prompt.
- `vlog-template/` — the reusable vlog kit (subtitle styles, opening card, closing credits, assembler).
- `inkling-video-*.py` — the pipeline scripts.
