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

The recap is cut as a vlog, not a montage. The structure is: wide establishing shot → the day unfolding talk by talk → the warmest moment (the room laughing together) as the emotional peak → a closing wide + photo flashbacks.

Transitions follow the directors' rules, not hard cuts: coverage goes wide → tight and re-establishes with a wide after close-ups; cuts hide inside motion (match on action); sound bridges the cut (J/L-cuts) instead of silence; the cut lands on the listener's reaction, not the speaker; the tightest close-up is saved for the emotional peak; cuts land on music phrase boundaries (see the beat grid below); photos are 1–2 s flashbacks, never long holds. The full research behind these rules is in `research-shot-picking-transitions.md` (in the build workspace) and the per-cut mapping is in the re-cut report.

## Music

Main track and alternates. All four are downloaded and verified (see `LOG.md`). All are commercial tracks — fine for the demo, needs clearance or a licensed swap before publishing on social platforms.

**Main: KOYO — "Timing" (타이밍)**, 3:16, 99 BPM. Korean OST ballad (EXchange2 Pt. 4 OST, Sep 24 2022). Beat 0.61 s, bar 2.42 s. 8-bar phrase boundaries (19.4 s): 0:00, 0:19, 0:39, 0:58, 1:18, 1:37, 1:56, 2:16, 2:35, 2:55, 3:14. Cut on phrase boundaries. Music stays low (volume 0.15) under voices.

**Alternates:**
- 88rising & RHYME SO — "Just Used Music Again", 3:31, 123 BPM.
- Yerin Baek — "Another season with you", 3:30, 120 BPM.
- Cloud Nothings — "Stay Useless", 2:47 (file 2:53, ~9.6 s trailing silence), 169 BPM — highlight bursts only.

## Storage

Footage and working files live on the builder machine or in the shared Google Drive folder, whichever is convenient. The finished recap is a single mp4. Nothing here needs a special store. The four music tracks are also uploaded to the shared Drive folder for later reuse.

## Scripts

| Script | What it does |
| --- | --- |
| `inkling-video-pipeline.py` | One clip in: probe, transcribe, extract keyframes, build a pack |
| `inkling-video-combine.py` | Merge per-clip outputs into one pack for a whole-day pick |
| `inkling-video-cut.py` | Cut one clip per pick with the vintage grade |
| `inkling-video-recap.py` | Cut picked segments from many source clips and join them into the recap |
| `inkling-video-sft.py` | Summarise approved picks and fine-tune Inkling 2 Small on Tinker |
| `inkling-video-editor-mcp.py` | Minimal MCP server: probe, transcribe, keyframes, cut, recap |
| `inkling-demo-master-prompt.txt` | The 12-section prompt Inkling picks from |

## Files in this repo

- `README.md` — this file.
- `LOG.md` — a running build log: every step, with dates and quality numbers (extraction density, classification counts, spot-check accuracy, cut precision).
- `shot-list.md` — the dense 1 fps shot list: 68 clips, 1108 frames, 7 shot types, per-talk table.
- `how-inkling-2-small-cut-this-video.md` — how Inkling 2 Small cut the first recap (method, the 2 MB limit, cost ~$0.03).
- `inkling-frame-classification-suitability.md` — is Inkling 2 Small suitable for frame extraction and classification? (Answer: no for extraction, yes for selection and classification — with evidence, papers, and GitHub repos.)
- `inkling-demo-master-prompt.txt` — the master prompt.
- `inkling-video-*.py` — the pipeline scripts.
