# Ripple

Cut videos with Inkling 2 Small on Tinker. Built for the Cafe Cursor Shanghai recap, July 2026.

## The loop

Video goes in, a finished recap comes out. Inkling does the thinking, ffmpeg does the cutting.

1. **Transcribe.** Whisper turns each clip into a transcript. The clips here carry little clean speech, so the transcript is thin and the pictures do most of the work.
2. **Keyframes.** One frame every ten seconds, downscaled to 1280px wide so each file stays well under the limit below.
3. **Pick.** Inkling 2 Small reads the master prompt, the combined transcript and the keyframes, then picks the moments worth keeping. It outputs timestamps and a plan, never a video file.
4. **Cut.** ffmpeg cuts the picked segments from their source clips, joins them in order and applies a light vintage grade.

The picks become training data. Approved picks are saved as examples and used to fine-tune Inkling 2 Small on Tinker, so the loop gets closer to the editor taste over time.

## The 2 MB limit

Inkling rejects any single attached asset over 2,097,152 bytes (2 MB). A raw 4K clip is 20 to 140 MB, so it can never be attached directly.

The workaround is to split the problem, not the model input:

- **Never send video.** Send text (the transcript) and still images (the keyframes) only.
- **Shrink the frames.** Downscale keyframes to 1280px wide at JPEG quality 4. A 4K frame is several megabytes; the same frame at 1280px is around 30 KB.
- **Scan per clip, decide once.** Each short clip is transcribed and framed on its own, then all the transcripts and keyframes are combined into one pack so Inkling picks across the whole day in a single session.
- **Cut locally.** Inkling returns timestamps. The actual cutting happens on local disk with ffmpeg, where file size is not a constraint.

## Storage

Footage and working files live on the builder machine or in the shared Google Drive folder, whichever is convenient. The finished recap is a single mp4. Nothing here needs a special store.

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

## Music

KOYO, "Timing" (3:16, 99 BPM). It is a commercial OST, so it is fine for the demo and needs clearance before publishing on social platforms.
