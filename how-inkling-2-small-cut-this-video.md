# How Inkling 2 Small Cut This Video

**Date:** 13 November 2026
**Event:** Cafe Cursor Shanghai, Sunday 19 July 2026
**Model:** Thinking Machines Inkling 2 Small, via Tinker
**Result:** a 109-second recap, 16 segments, picked entirely by the model

## The loop

The pipeline is deliberately boring. Nothing in it is new; the point is that it is repeatable.

1. **Transcribe.** Whisper turns each clip into a timestamped transcript.
2. **Keyframes.** One frame every 10 seconds, downscaled so each image fits the model's per-asset limit.
3. **Pick.** Inkling reads the prompt, the transcripts and the keyframes, and returns a list of moments as structured data: clip, start, end, title, reason.
4. **Cut.** ffmpeg assembles the chosen segments in order, applies a light vintage filter, and writes the recap.

Inkling never touches a video file. It outputs timestamps and a plan. ffmpeg does the cutting. That separation is the whole design.

## The 2 MB limit, and how to fit under it

The Tinker API rejects any single attached asset over **2,097,152 bytes (2 MB)**. The error is:

> Failed to process input: Asset is too large: max allowed is 2097152 bytes

A raw DJI clip is 20 to 140 MB. It can never be attached. So the video itself is never sent. What is sent is:

- **Text.** The master prompt plus the transcripts. Text is small.
- **Stills.** Keyframes extracted with ffmpeg at 1280 px wide, JPEG quality 4. Each frame lands at roughly 30 to 116 KB, an order of magnitude under the limit.

That is the entire workaround. Shrink the pictures, keep the words, and let the model pick from stills. The 66 keyframes for this batch total 7.7 MB across the whole request; no single one is anywhere near 2 MB.

There is a second limit that matters just as much: **context**. 66 images plus a transcript is about 53,000 tokens. That does not fit in the model's default 64K context once the prompt and the output budget are counted. So this run used the 256K-context variant, `thinkingmachines/Inkling-2-Small:peft:262144`. If you only have the 64K model, split the batch into two calls (for example, morning and afternoon) and merge the pick lists afterwards.

## The call

One POST to the Tinker Anthropic-compatible endpoint:

- **Endpoint:** `https://tinker.thinkingmachines.dev/services/tinker-prod/anthropic/api/v1/messages`
- **Model:** `thinkingmachines/Inkling-2-Small:peft:262144`
- **max_tokens:** 10,000
- **Input:** the master prompt, a note that the footage is morning-only and that the transcripts are unreliable, the per-clip transcripts, and 66 keyframes as base64 images, each labelled with its clip name, frame time and clip duration.
- **Request body:** 9.8 MB
- **Response:** HTTP 200, 16 complete picks, plus a thinking trace.

**Tokens and cost.** 53,527 input tokens, 10,000 output tokens. At the published serverless rates for this variant (input $0.30 per million, output $1.00 per million), the call cost about **$0.03**. The model also produced a long thinking trace (about 20,000 characters) before writing the picks; that thinking is billed as output tokens, which is why the output budget matters (see below).

## What Inkling picked

16 moments, 109 seconds in total, all from the morning (09:16–12:21):

| # | Clip | Time | Title |
|---|------|------|-------|
| 1 | 0026 | 0:00–0:07 | Doors open at the Cursor Cafe |
| 2 | 0032 | 0:00–0:07 | Hosts by the Cursor Cafe banner |
| 3 | 0002 | 0:00–0:05 | Drinks at the bar counter |
| 4 | 0003 | 0:00–0:07 | People settling in with laptops |
| 5 | 0007 | 0:00–0:06 | Host opens to a packed room |
| 6 | 0021 | 0:00–0:07 | Dashboard talk |
| 7 | 0031 | 0:00–0:06 | Live screen-setting demo |
| 8 | 0036 | 0:00–0:05 | Shim by feel, shipping demo |
| 9 | 0048 | 0:00–0:07 | AI Mi app launch page |
| 10 | 0050 | 0:03–0:10 | Pairoa, question from the floor |
| 11 | 0051 | 0:08–0:16 | The room laughing at the demo |
| 12 | 0059 | 0:00–0:09 | Your agents work, you sleep |
| 13 | 0062 | 0:03–0:09 | Pointing at the ARIAVA slide |
| 14 | 0070 | 0:02–0:10 | This is the era of imitation |
| 15 | 0063 | 0:00–0:08 | Volunteers behind the bar |
| 16 | 0074 | 0:00–0:06 | Check-in at the doorway |

Two things stand out. First, Inkling read the screens: it named the products on display (Shim by feel, AI Mi, Pairoa, ARIAVA) and picked the sharpest product moment in each. Second, it picked front-of-house beats a human might skip (hosts by the banner, volunteers behind the bar, check-in at the doorway) — the people who make the room work, not just the people on stage.

## The cut

A small script (`inkling-video-recap.py`) reads the pick list, resolves each clip file under a media directory, and runs ffmpeg: trim each segment, apply the vintage filter (`eq=saturation=0.88:contrast=0.96:brightness=0.02`), concatenate in order, and write the recap. The output is `recap-inkling.mp4`, 109 seconds, 2688×1512 H.264. No music (no audio file yet), no on-screen text, no narration.

## Where the model was wrong

Two things, both worth knowing before trusting this blindly.

### 1. One filename slip

Inkling wrote `DJI_20260719095456_0026_D.mp4` for its first pick. No such file exists. The real file is `DJI_20260719095441_0026_D.MP4`. Same clip number (0026), different timestamp digits — it mixed the timestamp of the neighbouring clip (0027, which starts at 09:54:56) with the number of clip 0026. 15 of 16 filenames were exactly right. The fix was mechanical: match the clip number to the file on disk. The lesson is to validate every filename against the media directory before cutting, and to prefer a stable identifier (the clip number) over a filename the model reconstructs from memory.

### 2. Output cut short

The call hit the 10,000-token output limit (`stop_reason: max_tokens`). The model was mid-way through a 17th pick (clip 0025, the street arrival) when the budget ran out, so the pick list ends at 16. The reason is that the model spends most of its output budget thinking: the thinking trace was about 20,000 characters before it wrote a single pick. For a batch this size, set `max_tokens` to 16,000 or higher, or ask for fewer picks per call. A re-run with a larger budget would recover the 17th pick and bring the total to roughly 115 seconds.

## The transcript problem

The transcripts were mostly hallucinated. Whisper rendered crowd noise as speech (repeated phrases, wrong languages). Inkling was told this upfront and judged mainly from the keyframes. The one transcript quote it kept, it flagged as "wording uncertain". The practical lesson: for noisy event footage, pictures are the signal and the transcript is decoration. A cheap improvement is to feed per-segment audio energy (from ffmpeg's silence detection) alongside the frames, so the model can tell speech from noise without trusting the words.

## What this proves, and what it does not

It proves that a vision-language model can pick a coherent 2-minute recap from stills and a prompt, for about three cents, without ever seeing the video. The picks are sensible, the product moments are sharp, and the structure (arrival, setup, talks, demos, laughter, front-of-house) holds together.

It does not prove the model understands the event. It never heard the talks, never saw a moving shot, and never felt the room. It picked from 66 stills. It missed nothing that was in the pictures, but it could not know what was between them. That is why the loop keeps a human in it: the model proposes, a person approves, and the approved picks become training data for the next round.

## Files

- `inkling-video-picks-inkling.jsonl` — the model's raw picks (16 complete, 1 truncated)
- `inkling-video-picks-inkling-cut.jsonl` — the same picks with filenames resolved to disk
- `inkling-video-playground-pack.txt` — the prompt, transcripts and keyframe inventory sent to the model
- `inkling-video-pipeline.py` — transcribe and extract keyframes per clip
- `inkling-video-combine.py` — combine per-clip scans into one pack
- `inkling-video-recap.py` — cut the recap from a pick list
- `inkling-video-sft.py` — fine-tune Inkling 2 Small on approved picks
- `inkling-video-editor-mcp.py` — the same tools as an MCP server
- `inkling-demo-master-prompt.txt` — the master prompt, 12 sections
