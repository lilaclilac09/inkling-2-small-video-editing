# Training data for the Inkling 2 Small video-cutting LoRA

File: `inkling-video-picks-full.jsonl` — **32 examples** (17 real + 15 synthetic).

This is the dataset for the LoRA fine-tune (`inkling-video-cutting-v1`) that teaches
Inkling 2 Small Aileen's video-cutting taste. It bakes in **every rule** in
`requirements-log.md`, not just the 17 approved v2 picks.

## What is in the file

One JSON object per line. Each row is one training example with the same schema
the SFT script expects:

| field | meaning |
|---|---|
| `node` | `morning` / `afternoon` — which part of the day the moment is from |
| `tags` | which priority moments / rules this pick covers (e.g. `["guitar", "laughter"]`) |
| `transcript_excerpt` | Whisper-style transcript of the moment, with timestamps |
| `keyframes` | frame paths (`<file>/frames/frame-NNNN.jpg`) or a descriptive line |
| `clip` | the pick: `{file, start, end, title, reason}` — this is what the model learns to output |
| `synthetic` | `true` for the 15 teaching examples, absent for the 17 real v2 picks |
| `synthetic_note` | why this row exists and what rule it teaches |
| `covers` | short label of the requirement(s) this row covers |

### The 17 real picks (rows 1–17)

The approved v2 picks from `scan/inkling-video-picks-v2.jsonl`, unchanged.
Real files, real timestamps, real titles/reasons. These are the ground truth.

### The 15 synthetic picks (rows 18–32)

Each one teaches a specific requirement from the log. All titles/reasons are
written in proper, fluent, detailed English — the cultured writing standard
Aileen demanded (never garbled English like "that everybody love").

| # | Title | Requirement it teaches |
|---|---|---|
| S1 | The room erupts — open on the laugh | Hook first: Talk L laughter opens the video, not a wide |
| S2 | The banner, the street, the morning crowd | Wide panoramic opening; front-facing people; Cursor logo readable; never open on a close-up head or backs-only shot |
| S3 | Talk F: your agents work while you sleep | Feature women presenters; showcase monologue |
| S4 | Talk E: she demos the app live | Feature women presenters across the cut (more than one beat) |
| S5 | Talk I: Shim by feel | Showcase monologue (guest presenting their own work) |
| S6 | Talk H: the room asks back | Prefer follow-up questions / audience response |
| S7 | The volunteers, before anyone arrives | Volunteers as a thread (setup + rain scramble) |
| S8 | The guitar: a song for the room | Guitar is must-keep |
| S9 | Piano: the room goes quiet | Piano is must-keep |
| S10 | A song written for his girlfriend | Girlfriend piece is must-keep |
| S11 | The rain arrives all at once | Rain is must-keep; volunteers; exterior |
| S12 | The big group photo | Group photo is must-keep; ending + flashback |
| S13 | The whole day, in six seconds | Timelapse |
| S14 | Sponsored cups on the stainless bar | Cultured, detailed writing; texture beats between talks |
| S15 | Talk M: your agents work while you sleep | Cut on sentence boundaries; clear takeaway line |

Priority-moment coverage (the SFT script's own checklist): **all 9 covered** —
guitar, girlfriend, piano, showcase monologue, follow-up, laughter, rain,
volunteers, group photo. None missing. (The 17 real picks alone covered only
follow-up, laughter, showcase monologue — the synthetic rows fill the other six.)

## Grounding: what is real and what is a placeholder

- **Every `clip.file` is a real filename.** No invented file names. Morning files
  exist in `media/DJI_001/`; `延时.MP4` is verified in the Drive listing.
- **Every start/end is inside the file's verified duration** (checked with ffprobe).
- **Every keyframe path is a real extracted frame**, except S13 (timelapse), whose
  frames are not extracted yet — its keyframes are descriptive, and the note says so.
- **PLACEHOLDER ROWS (re-anchor before training): S8–S12.** The guitar, piano,
  girlfriend piece, rain, and group photo are AFTERNOON moments. At the time this
  file was built, no afternoon file names were verified in Drive (the re-scan was
  still running), so those five rows anchor to real morning files ONLY as format
  placeholders. Their TASTE signal (tags, title, reason) is real and is the point
  of the row — but their `file`/`start`/`end` must be replaced with the real
  afternoon file + timestamps from the re-scan before training. Each row's
  `synthetic_note` says this. If you train with the placeholders as-is, the model
  will learn a false file→content association for those five rows.
- **S1 vs v2 pick #12:** both use clip 0051 (the laughter). v2 #12 frames it as the
  climax; S1 frames it as the OPENER. That is intentional — Aileen's v3 rule is
  "Talk L laughter first." The two rows together teach the model that this moment
  is strong enough to open the video.

## How to run the fine-tune

On Aileen's Mac (where `tinker auth login` is done):

```bash
cd ~/tinker-first-session
INKLING_PICKS_PATH=inkling-video-picks-full.jsonl uv run inkling-video-sft.py
```

The script reads the file from `INKLING_PICKS_PATH` (default is
`inkling-video-picks.jsonl` in the current directory). Make sure this file is in
`~/tinker-first-session/` first — copy it from here.

What the script does: LoRA rank 16, 10 steps, lr 2e-4, base model
`thinkingmachines/Inkling-2-Small`, saves a checkpoint named
`inkling-video-cutting-v1`, then prints a Playground URL and a before/after
comparison on two test prompts. Loss should fall from ~0.9 toward ~0 over the
10 steps (the first smoke run went 0.9471 → 0.0006).

**Before training, do the re-anchoring step:** replace the `file`/`start`/`end`
of rows S8–S12 with the real afternoon files from the re-scan (see "PLACEHOLDER
ROWS" above). If the afternoon files are not verified yet, you can train on the
27 non-placeholder rows first and add the five afternoon rows in a later run.

## Regenerating

The dataset is generated by `build_full_picks.py` in this directory (it loads the
17 real picks, appends the 15 synthetic rows, and validates: valid JSON, every
clip has file/start/end/title/reason, timestamps in range, files exist, keyframe
paths exist). Re-run it after editing the synthetic rows:

```bash
cd ~/workspace/inkling-recap && python3 build_full_picks.py
```
