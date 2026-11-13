# v5 — the story cut (Cursor Café Shanghai, 2026-07-19)

Two versions, same story cut and captions, different music + grade.
Both 127.5 s, 1920×1080, 30 fps, H.264 + AAC.

| file | music | grade |
|---|---|---|
| `recap-v5-another-season.mp4` | Yerin Baek "Another season with you" (Stay Useless first 24 s) | silicon — clean, warm |
| `recap-v5-just-used-music-again.mp4` | "Just Used Music Again" funk (Stay Useless first 24 s) | korean — warm, glowy |

Videos are local only (too big for GitHub). This report covers the
cut, the subtitle system, the cover, and the fixes.

## The story (Inkling 2 Small re-picked it)

Inkling 2 Small (via the Tinker API, max_tokens 32000, ~$0.05) re-ordered
the day into a 5-beat arc instead of a chronological montage.
20 video picks, 128.5 s of source, 9 talks numbered in STORY order
(important first), not by their original letter.

1. **Arrival** — storefront (0037), the timelapse of the room filling up
   (延時.MP4), walking in (0027).
2. **The hosts** — the two hosts at the Cursor banner (0032), kept early
   and captioned as Aileen described them: "the friend who came
   earliest" / "the friend who kept order".
3. **The talks, important first** — Talk 1 Pairoa (the warmest, laughter
   at 0051), Talk 2 Carl Yang Agent/Harness (the most legible title
   slide), then Talk 3 (AI-native tools), Talk 4 (phone chat app),
   Talk 5 (personal-care app), Talk 6 (agents for a brand), Talk 7
   (CREWCLAW), Talk 8 (Information Radar), Talk 9 (agents while you sleep).
4. **Human moments** — Q&A, reactions, people chatting by the drinks
   fridge, the audience gimbal shot.
5. **Closing** — sign-off at the banner (0079) + the group photo
   (HM5A1478) as the final frame.

## Photos mixed into the video (Ken Burns slow zoom)

Three stills, interleaved with the video clips:

- **Photo A** (3 s, after walking in) — the girl in a white shirt under
  the green plane trees (0054 frame-0003), drink and tablet in hand.
- **Photo B** (3 s, after the hosts) — the girl in the black cap and
  black clothes by the Cursor banner (HM5A1822).
- **Photo C** (4 s, final frame) — the group of eight men by the banner
  (HM5A1478), Cursor logo clearly readable.

## Subtitle system v6 (the 17:09 + 17:14 feedback)

The v5 subtitle system was rebuilt after Aileen's 17:09 feedback
("the copy is uncultured, the style is uncomfortable") and her 17:14
correction (subtitles should switch, not linger).

- **Style**: cream/beige background (opaque warm cream box), BLACK text.
  Caveat EN / Ma Shan Zheng CN for captions; DejaVu Sans Bold /
  Noto Sans CJK SC Bold for annotations. Warm, clear, cute.
- **Layout**: MAX 2 LINES at once (1 EN + 1 CN). Never 4 lines.
  All cards sit at the same bottom position, so the subtitle never
  jumps around the frame.
- **Timing**: each card stays a comfortable reading duration (~2–3 s,
  never lingering). Within one scene, the subtitle CYCLES through
  2–3 cards in a row while the speech continues. 49 cards across
  23 segments.
- **Captions**: restrained, cultured, understated. No atmosphere-hyping
  ("warmest moment", "the whole room laughs" are out). Talk captions
  are "Talk N" / "Share N" in story order.
- **Annotations**: where the audio is intelligible, they explain HOW
  the person used the tool (the process), not just what it is.
  Talk E is the detailed one (verified transcript): "Personal care —
  it remembers your skin" then "Type in your address — live weather
  shapes your routine".
- **Emoji note**: colour emoji (🧴 etc.) do NOT render in this libass
  build — they show as empty boxes, tested twice. The monochrome
  coffee glyph U+2615 DOES render cleanly in DejaVu Sans, so the
  coffee-machine label uses it. Annotation emoji were left out rather
  than shipped as tofu boxes.

### Per-talk annotations (added / skipped)

Added (6): Talk 2 Carl Yang (Agent era — history + enterprise Harness);
Talk 4 chat app (demoed live from his phone); Talk 5 personal care
(verified, see above); Talk 6 agents for a brand; Talk 8 Information
Radar (AI-news dashboard); Talk 9 agents work while you sleep.
Skipped (3): Talk 1 Pairoa (screen is a landing page, purpose unclear);
Talk 3 (screen only says "AI-native tools", too vague); Talk 7 CREWCLAW
(audio hallucinated, screen is terminal code, purpose unclear).
Nothing was invented for the skipped talks.

### Coffee-machine label

The room audio is loud in the middle. Audio analysis (sustained
loudness + 2–4 kHz / 4–8 kHz spectral energy) puts the loudest
sustained mechanical noise at final-video t=80–84 s (inside the
Talk E segment, 79–86 s). A small label shows there, above the
subtitle: "☕ coffee machine". The room audio is also
denoised (afftdn) where it is loud.

### Audio mix (17:09)

Music must not cover the voices. Music lowered 0.30 → **0.22**;
room/voices boosted 1.4 → **1.6** and compressed (acompressor,
threshold −18 dB, ratio 3, makeup 4) so voices are louder and more
solid/full. Measured: mean volume −14.4 dB (was −21.2 dB in the
v5-subtitle version), max 0.0 dB.

### Grade (17:09)

Both grades pushed warmer + more vivid than v5 (the old grade was
too flat/cold; the silicon grade was actually cool/blue).
korean: saturation 1.32, contrast 1.12, brightness 0.07,
colour balance rs +0.12 / bs −0.10.
silicon: saturation 1.22, contrast 1.12, brightness 0.05,
colour balance rs +0.08 / bs −0.06 (flipped from cool to warm).
korean stays the warm/glowy one, silicon the clean one.

## Cover — cover-v5.jpg (cutout approach)

Aileen rejected the blended 3-photo collage ("ugly"). The cover is
rebuilt as CUTOUTS on a clean warm cream background (#F7F1E5),
1920×1080:

- **Hero, top-right, BIGGEST** — the girl under the green trees
  (0054 frame-0003), cut out with rembg (u2netp), full figure, head
  intact, smiling at the camera.
- **Bottom-left** — the girl in the black cap and black clothes
  (HM5A1822), waist-up, arms crossed, smiling.
- **Bottom-centre** — the group by the banner (HM5A1478), cut out
  with u2net_human_seg, all 7–8 men solid.
- Text "Cursor Cafe Shanghai" / "2026.07.19" top-left, Playfair
  Display Bold + Montserrat SemiBold, dark warm brown. No face and
  no Cursor logo covered. Verified by reading it back: no black bar,
  no cut-off heads, no overlapping cutouts.

(Cutout note: the large rembg model bria-rmbg OOM-killed the VM
twice — do not use it. u2netp works for the girls; u2net_human_seg
for the group.)

## Earlier fixes (still in)

- Pink/blonde woman removed (clips 0026 and 0052 excluded; the one
  0042 pick that showed her was replaced with 0032).
- Cursor logo clearly visible in 3 picks (0037 storefront, 0032 hosts
  at the banner, 0079 sign-off).
- Ugly cup shot (clip 0002, the cluttered back-of-bar) removed;
  replaced by the timelapse.
- Flashback slowed 2 s → 2.5 s per shot.

## Files

- `scan/inkling-video-picks-v5.jsonl` — 20 Inkling story picks.
- `scan/captions-v5.ass` — the v5 subtitle file (superseded).
- `scan/captions-v6.ass` — the v6 subtitle file actually burned in
  (49 cards, cream/black, max 2 lines, coffee label at 80–84 s).
- `build_captions_v6.py` — the v6 caption builder.
- `inkling-video-recut-v5.py` — the render script (warmer grades,
  music 0.22, room 1.6 + acompressor, afftdn, silent-audio fix for
  the timelapse).
- `cover-v5.jpg` — the cutout cover.
- `recap-v5-another-season-v5sub.mp4` — backup of the v5-subtitle
  render (before the v6 re-render).

## Verification

Both videos: ffprobe 127.5 s, 1920×1080, 30 fps, H.264 + AAC.
Frames read back at t=2 (arrival, cream subtitle legible), t=30
(Talk 1 Pairoa, "Talk 1" + Pairoa screen), t=53 (Carl Yang title
slide + annotation), t=82 (Talk E: presenter in green cap, bottle
screen "Welcome to your bottle", coffee label "☕ coffee machine" above the "Personal care" annotation, no tofu), t=125
(closing group photo, Cursor logo clear).
Audio: mean −14.4 dB, max 0.0 dB; the two versions have different
audio (different music beds) confirmed by hash.
