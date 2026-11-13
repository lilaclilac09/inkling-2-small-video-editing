# Vlog Template System

A reusable kit that turns the Cafe Cursor cutting pipeline into a **vlog
modulator**: the same opening, subtitles, and closing you can drop onto any
future vlog. Nothing here is hardcoded to one event — every piece takes plain
inputs (title, date, location, a captions list, a credits list) and produces
a 1920×1080, 30fps segment that slots into the existing ffmpeg pipeline.

```
vlog-template/
├── subtitles/
│   ├── styles.json            3 subtitle styles (cute / clean / bilingual)
│   ├── make_subtitles.py      captions JSON -> .ass file
│   └── captions.example.json  example captions (EN + CN, timed)
├── opening/
│   └── make_opening.py        title + date + location + base photo -> opening.mp4
├── closing/
│   ├── make_closing.py        credits JSON -> scrolling credits or end card
│   └── credits.example.json   example credits (thanks, music, made-with)
├── assemble_vlog.py           opening + body + closing -> finished vlog
├── samples/                   test renders + verification frames
└── README.md                  this file
```

## The three pieces

### 1. Subtitle styles

| Style | Look | Use when |
|---|---|---|
| `cute` | Handwritten: Caveat (EN) / Ma Shan Zheng (CN), warm white, soft outline | Casual vlogs, travel diaries, warm community events |
| `clean` | DejaVu Sans / Noto Sans CJK SC, white, thin outline, no box | Talks, demos, code walkthroughs — captions stay out of the way |
| `bilingual` | EN line over CN line on a semi-transparent box | Talk outlines for a mixed audience; legible over busy footage |

```bash
# captions.json: [{"start": 3.0, "end": 8.5, "en": "...", "cn": "..."}, ...]
# "title": true on a caption renders it larger.
python3 subtitles/make_subtitles.py --captions my-captions.json --style cute --out my.ass
python3 subtitles/make_subtitles.py --captions my-captions.json --style bilingual --out my.ass

# Burn onto the body (libass):
ffmpeg -i body.mp4 -vf "subtitles=my.ass" -c:a copy body-sub.mp4
```

Fonts are resolved by family name through fontconfig, so the same .ass works
on any machine with the fonts installed: Caveat, Ma Shan Zheng,
DejaVu Sans, Noto Sans CJK SC. (On this VM they live in `~/.fonts/` and
`/usr/share/fonts/`.)

### 2. Opening title card

A 1920×1080 card built from your best wide shot, darkened with a bottom
gradient. Text sits in the **lower half** on purpose — the top quarter stays
clear so a banner or logo in the photo is never covered. The card slowly
zooms in (Ken Burns) and fades in from black, so the dissolve into the first
footage clip feels like a film opening.

```bash
python3 opening/make_opening.py --title "Cursor Cafe Shanghai" \
    --date "2026.07.19" --location "Shanghai · Yanqing Road" \
    --image best-wide-shot.jpg --out opening.mp4 --keep-png card.png

# With a music bed under the card:
python3 opening/make_opening.py --title "My Berlin Vlog" --date "2026.10.12" \
    --location "Berlin" --image base.jpg --music music/koyo-timing.mp3 \
    --out opening.mp4 --duration 3.0
```

Title font is picked automatically: Caveat for Latin titles, Ma Shan Zheng
for Chinese ones. Long titles wrap to two lines.

### 3. Closing credits (movie-style)

Two modes, both driven by a credits JSON file
(`closing/credits.example.json` shows the shape):

```bash
# Rolling credits (default 12s, scrolls up over black, fades in/out):
python3 closing/make_closing.py --credits my-credits.json --mode scroll \
    --duration 12 --music music/koyo-timing.mp3 --out closing-scroll.mp4

# Static end card (default 5s): "Thanks for watching" + top credit lines:
python3 closing/make_closing.py --credits my-credits.json --mode card \
    --duration 5 --music music/koyo-timing.mp3 --out closing-card.mp4
```

Every closing ends with the footer line from your credits file — keep the
`Shot with Inkling 2 Small` line and the music attribution in there. The
tracks in this project are commercial songs used for demo only; clear the
licence (or swap in a licensed track) before publishing anywhere public.

## Putting a vlog together

```bash
# 1. Cut the body with the existing pipeline (picks -> segments -> join),
#    e.g. inkling-video-recut-v3.py, which already burns ASS subtitles
#    and mixes music. Or build a body any other way — it just needs to be
#    1920x1080, 30fps, H.264 + AAC.

# 2. Build the three template pieces (commands above).

# 3. Assemble with 0.5s dissolves between segments:
python3 assemble_vlog.py --opening opening.mp4 --body recap-v3.mp4 \
    --closing closing-scroll.mp4 --out my-vlog.mp4

# Opening and closing are optional:
python3 assemble_vlog.py --body recap-v3.mp4 --closing closing-card.mp4 \
    --out my-vlog.mp4
```

One continuous music bed across the whole video: mix it over the finished
file afterwards, e.g.

```bash
ffmpeg -i my-vlog.mp4 -i music/koyo-timing.mp3 -filter_complex \
  "[1:a]volume=0.15,afade=t=out:st=110:d=2[bed];[0:a][bed]amix=inputs=2:duration=first[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac my-vlog-bed.mp4
```

## Reusing the fine-tuned model

Approved picks from a finished vlog are training data: each approved pick is
one example in `inkling-video-picks.jsonl`. After a vlog ships, append its
picks and re-run `inkling-video-sft.py` (LoRA rank 16, 10 steps) so the next
vlog's picks get closer to your taste. See the repo README and LOG.md.

## Verified on this machine

- All three subtitle styles render legibly on real footage (see
  `samples/verify-*.jpg` — frames pulled from the test renders).
- Opening card + closing scroll + closing card all render at 1920×1080;
  frames in `samples/`.
- Assembled sample (`samples/sample-vlog.mp4`): opening → body → closing
  with 0.5s dissolves; durations add up exactly
  (opening + body + closing − 2 × 0.5s).
