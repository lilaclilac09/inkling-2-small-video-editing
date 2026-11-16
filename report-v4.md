# v4 re-cut — cover rebuilt, subtitles rewritten, music gentler, room denoised

Built 2026-11-13 in response to Aileen's feedback on v3 (15:31) and on the
v3 V1 video (15:36). v3 files are kept untouched; v4 is a new set.

## What changed

### Cover (cover-v4.jpg, 1920x1080) — rebuilt from scratch
- Lead photo is **HM5A1822**: the girl in a black cap, black top and black
  pants, arms crossed, front-facing, smiling, by the Cursor Café banner.
  (First build cropped her out by mistake — centre was on the banner, not
  on her. Fixed: crop centre moved to ~11% across the frame, where she
  actually stands.)
- Middle: **HM5A1478** (group of eight men by the black Cursor banner,
  logo fully readable). Right: **DJI_20260719092002_0005_D** (woman in a
  white tee presenting at the screen, audience at small tables).
- **No black bar.** Seams are a pure photo-over-photo crossfade: each
  panel is rendered wider than its slot and composited with a horizontal
  gradient alpha mask (0 → 255 across a 120 px seam band). No black
  underlay, no gradient-to-black. Verified by reading the image back and
  by column-brightness analysis (no near-black column in either seam band).
- **Text is not Caveat.** Title "Cursor Cafe Shanghai" is Playfair Display
  Bold (76 pt), date "2026.07.19" is Montserrat SemiBold (44 pt), white
  with a soft shadow, bottom-centre over a subtle bottom gradient only.
  No face or logo is covered.
- HM5A1557 (hand stretched across the frame) is NOT used.

### Subtitles (scan/captions-v4.ass) — rewritten, not just restyled
- **Talk captions are numbered, not described** (per Aileen 15:36): every
  talk segment is just "Talk N" / "分享 N". In v3 order: Talk A → Talk 1,
  Talk E → Talk 2, Talk F → Talk 3, Talk G → Talk 4, Talk M → Talk 5,
  Talk L → Talk 6, Talk N → Talk 7.
- **Non-talk captions are observant and specific**, grounded in the
  shot-list descriptions of what is actually visible — not generic lines.
  Examples (old → new):
  - Hook: "The whole room bursts into laughter — the warmest moment" →
    "The Pairoa demo gets a laugh — the whole room in on the joke"
  - Full room: "A full room on a Saturday morning, everyone leaning in" →
    "The room from the back — code on the screen, every seat taken"
  - Q&A (0050): "Questions from the room, hands going up" →
    "Q&A — he gestures at the Pairoa screen, and someone in the room
    gestures right back"
  - Q&A (0062): "A question about ARIAVA, and the room leans in" →
    "Q&A — a finger pointed at the ARIAVA QR codes, the presenter
    holding the floor"
- Fonts unchanged (Caveat EN / Ma Shan Zheng CN), semi-transparent box.
  Only the words changed.

### Flashback — cups shot removed, timing slowed
- **Pick #4 "Flashback: cups on the bar" (clip 0002) REMOVED.** The frame
  is a cluttered back-of-bar mess: squeeze bottles, jars, a shaker,
  stacked cups, a cardboard box — not a pretty shot. Replaced with the
  **timelapse 延时.MP4 (0:10–0:12.5)**: the room filling up under the
  paper lanterns, sped up. It fits the arc (outside → setup → room
  filling → screen → audience).
- Flashback slowed from 2.0 s to **2.5 s per shot** (she said it was a
  bit too fast but acceptable — a small slowdown, not an over-fix).

### Music — V1 main track changed
- Stay Useless (Cloud Nothings) stays for the first 24 s — she says it
  is very good. After that the main track must be gentler.
- **V1: "Just Used Music Again" (funk) → KOYO "Timing" (gentler,
  emotional, 99 BPM).** Output renamed `recap-v4-timing.mp4`.
- V2 keeps "Another season with you" (already gentle).
- Music beds rebuilt at 111 s (`music/v1-music-bed-v4.mp3`,
  `music/v2-music-bed-v4.mp3`): Stay Useless 0–24 s + 2 s crossfade into
  the main track.

### Room audio — coffee-machine noise
- The room audio had distracting coffee-machine noise mid-video. Applied
  **light FFT denoise (`afftdn nr=8, nf=-30`)** to the room-audio bus
  before the 1.4x volume boost. Voices stay clear; the room is not
  muted. (afftdn targets steady-state hum; intermittent machine bursts
  are reduced, not eliminated.)

### Unchanged from v3
- Same 21 picks (except the cups → timelapse swap and the 2.5 s
  flashbacks), same two grades (V1 Korean variety, V2 Silicon Valley),
  same audio levels (music 0.30, room 1.4).
- Pink/blonde woman still removed everywhere (0026/0052 never picked;
  0042 → 0032 correction stands). Cursor logo clearly visible in the
  same 3 picks (#2 flashback storefront 0037, #7 hosts at the banner
  0032, #21 sign-off 0079).
- No guitar/piano/music showcases — still no afternoon footage.

## Outputs (to be verified after render)
- `recap-v4-timing.mp4` — Version 1, Korean variety, Timing.
- `recap-v4-another-season.mp4` — Version 2, Silicon Valley, Another season.
- `cover-v4.jpg` — rebuilt cover.
- `scan/inkling-video-picks-v4.jsonl`, `scan/captions-v4.ass`,
  `inkling-video-recut-v4.py`, `make_cover_v4.py`,
  `music/v1-music-bed-v4.mp3`, `music/v2-music-bed-v4.mp3`.

## Verification
(ffprobe + frame checks to be filled in after the renders finish.)
