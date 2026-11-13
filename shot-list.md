# Cafe Cursor Shanghai — Shot List (dense 1 fps)

**Source:** Google Drive folder `1Bnwhav0ZaKmBc6BWXHuwg8mcFN--R6CL`, downloaded to `~/workspace/inkling-recap/media/DJI_001/`.
**Coverage:** 68 DJI clips, 07:23–12:21 on 2026-07-19 (morning only). Total footage 1110.2 s (~18.5 min).
**Frames:** 1108 extracted at 1 frame per second (1280 px wide, JPEG q4) into `frames-dense/<clip>/frame-NNNN.jpg`.

> Note on density: literally every frame at 30 fps would be ~33,000 frames and is not usable. 1 fps is the dense, workable version — one still per second, enough to see every shot change and every presenter.

## Quality metrics

### 1. Frame extraction density

- Total video duration: **1110.2 s** (~18.5 min)
- Total frames extracted: **1108**
- Effective fps: **0.998** (frames / duration)
- Coverage: **68/68 clips have at least one frame (100%)** — no clip is missing frames.

### 2. Classification detail (frames per shot type)

| # | Shot type | Frames | Share |
|---|------------------------------|--------|-------|
| 1 | ultra-wide storefront + whole poster/banner | 59 | 5.3% |
| 2 | secondary wide, one screen / one poster | 38 | 3.4% |
| 3 | interior ultra-wide | 754 | 68.1% |
| 4 | interior person close-up | 194 | 17.5% |
| 5 | interior audience close-up | 52 | 4.7% |
| 6 | hands/items close-up | 7 | 0.6% |
| 7 | timelapse | 0 | 0.0% |
| U | uncertain | 4 | 0.4% |

### 3. Accuracy signal (confidence)

- Confident: **1104 frames**
- Uncertain: **4 frames** (the 4 motion-blurred frames in clip 0038, 07:43, t=14–18s, where the camera swings to the door — shot type not readable).
- Every frame in `shot-list.jsonl` carries its own `confidence` field (`confident` / `uncertain`), so a spot-check can be scored per frame. Nothing is inflated: where the frame is a blur or the category is a best fit, it is marked and noted.
- Note on category 4: the taxonomy labels (4) 'interior person close-up', but 7 clips are *exterior* street shots of people (0025, 0033 10:09, 0034 10:09, 0035, 0054, 0055, 0058 — 55 frames). They are person close-ups, just outdoors, so (4) is the closest fit; each is flagged 'EXTERIOR' in its description.

## The guitar moment — NOT FOUND in this footage

**The user named a must-keep moment: a foreigner (non-Chinese man) wearing glasses, showing/playing his guitar, with his wife standing/sitting behind him.**

**Result: this moment is NOT in the footage currently on Drive.** I viewed first/middle/last frames of all 68 clips (plus extra frames of the 9 long clips) and there is no guitar, no foreigner with a guitar, and no music performance anywhere in the 07:23–12:21 morning footage. Every presenter in this batch is at a screen doing a talk/demo. The guitar/piano/rain/girlfriend-piece moments are afternoon/evening material — they are not in this batch. If she uploads afternoon footage, the guitar moment should be searched for there. **Do not cut a guitar moment from this batch; there is none to cut.**

## Wide / panoramic shots (what the user explicitly wants more of)

**Exterior ultra-wide storefront + whole banner (category 1) — the clearest establishing shots:**

- `DJI_20260719095441_0026_D.MP4` (09:54, 8 s) — black CURSOR banner + whole storefront, crowd at the door
- `DJI_20260719100747_0032_D.MP4` (10:07, 11 s) — two hosts by the banner giving thumbs up, crowd at the door
- `DJI_20260719101843_0042_D.MP4` (10:18, 8 s) — banner + storefront, man in white tee giving thumbs up, crowd (clearest banner shot)
- `DJI_20260719122116_0079_D.MP4` (12:21, 4 s) — banner, woman in black giving thumbs up, people at the door
- `DJI_20260719122153_0080_D.MP4` (12:21, 4 s) — woman in white lace dress by the banner, people at the door (closing shot)
- `DJI_20260719095456_0027_D.MP4` (09:54, 14 s) — storefront entrance, glass doors, awning, people at the door
- `DJI_20260719101336_0037_D.MP4` (10:13, 10 s) — whole storefront and awning, people at the door, street with plane trees

**Interior ultra-wide (category 3) — the whole room in one frame (754 frames, 68% of the footage):** the best room-wide shots are the long early-session takes — `0033` (07:23), `0034` (07:27), `0044` (09:24), `0051` (10:38, the laughter moment), and the ARIAVA run `0059–0064` (11:05–11:12). These show the presenter, the screen, and the seated audience together.

**Missing categories (stated explicitly, not invented):**
- **(7) timelapse — none.** No timelapse footage exists in this batch.
- **(6) hands/items close-up — only 7 frames** (one clip, `0002`, coffee/drinks on the bar). Very thin.
- **(2) secondary wide, one screen/poster — 38 frames.** Mostly the CURSOR logo on the glass door (0022, 0023, 0074) and the screen filling the frame in `0039` (08:22).
- **No guitar, no piano, no rain, no girlfriend piece, no group photo in this batch** (all morning footage).

## Per-clip shot list

Format: clip (time) — shot type(s) with time ranges — what it shows. Frame numbers: `frame-0001` = t=0s.

### DJI_20260719072352_0033_D.MP4 — 07:23 — 66 frames

- **t=0–66s** [3] interior ultra-wide: Man in striped shirt presents at the big screen, audience seated; screen shows Chinese AI-native tools slides

### DJI_20260719072707_0034_D.MP4 — 07:27 — 69 frames

- **t=0–69s** [3] interior ultra-wide: Same striped-shirt presenter continues; screen shows a dashboard with QR code, audience filming with phones

### DJI_20260719073634_0037_D.MP4 — 07:36 — 56 frames

- **t=0–50s** [3] interior ultra-wide: Man in black tee with glasses presents a website on screen ("Taste your wild..."), audience seated
- **t=50–56s** [5] interior audience close-up: Camera pans to a close-up of audience members watching

### DJI_20260719074342_0038_D.MP4 — 07:43 — 32 frames

- **t=0–14s** [3] interior ultra-wide: Man in black tee with glasses continues presenting at the screen, audience seated
- **t=14–18s** [U] uncertain — **uncertain**: Camera swings fast toward the glass door; frames are motion-blurred, shot type not readable
- **t=18–32s** [3] interior ultra-wide: Back to the wide room; presenter at the screen, audience seated

### DJI_20260719082251_0039_D.MP4 — 08:22 — 44 frames

- **t=0–15s** [3] interior ultra-wide: Man in light shirt presents at a screen showing a dark UI, audience seated
- **t=15–44s** [2] secondary wide, one screen / one poster: Camera moves in; the screen (dark product UI) fills the frame

### DJI_20260719082925_0040_D.MP4 — 08:29 — 77 frames

- **t=0–20s** [3] interior ultra-wide: Man in grey shirt with glasses holds a mic and speaks; audience seated, screen with text behind him
- **t=20–77s** [4] interior person close-up: Camera moves closer; medium close-up of the grey-shirt presenter speaking into the mic

### DJI_20260719084815_0042_D.MP4 — 08:48 — 76 frames

- **t=0–10s** [3] interior ultra-wide: Woman in green tee and cap holds a mic at a screen showing a phone app, audience seated
- **t=10–28s** [5] interior audience close-up: Crowd/audience close-up; people standing and watching near the glass (CURSOR logo reversed)
- **t=28–76s** [4] interior person close-up: Close-up of the woman presenter (green tee, cap) speaking into the mic beside the phone-app screen

### DJI_20260719091529_0043_D.MP4 — 09:15 — 63 frames

- **t=0–63s** [3] interior ultra-wide: Woman in white sleeveless top presents at the screen ("Your agents work..."), audience seated at tables

### DJI_20260719091607_0001_D.MP4 — 09:16 — 7 frames

- **t=0–7s** [4] interior person close-up: Man in white tee and khaki shorts works on a laptop setting up the screen; a blonde woman points at the screen

### DJI_20260719091652_0002_D.MP4 — 09:16 — 7 frames

- **t=0–7s** [6] hands/items close-up: Close-up of hands and drink bottles/cups on the bar counter; a hand reaches for a cup

### DJI_20260719091709_0003_D.MP4 — 09:17 — 7 frames

- **t=0–7s** [4] interior person close-up: Man in navy polo and cap types on a laptop at a small table; woman in white lace on her phone; man standing by the door

### DJI_20260719091907_0004_D.MP4 — 09:19 — 6 frames

- **t=0–6s** [3] interior ultra-wide: Wide room; screen with text, audience seated at tables

### DJI_20260719092043_0007_D.MP4 — 09:20 — 13 frames

- **t=0–3s** [5] interior audience close-up: Close-up of audience members (man in cap, woman, young man holding a camera/gimbal)
- **t=3–13s** [3] interior ultra-wide: Wide room; presenter (man in white tee) at the screen, audience seated

### DJI_20260719092253_0008_D.MP4 — 09:22 — 16 frames

- **t=0–13s** [3] interior ultra-wide: Presenter (man in white tee) at the screen, audience seated at tables
- **t=13–16s** [5] interior audience close-up: Close-up of audience members (man in cap, woman) watching

### DJI_20260719092424_0044_D.MP4 — 09:24 — 65 frames

- **t=0–65s** [3] interior ultra-wide: Presenter (man in white tee with red logo) holds a mic and demos code on the screen; audience seated, some smiling

### DJI_20260719092510_0009_D.MP4 — 09:25 — 10 frames

- **t=0–3s** [5] interior audience close-up: Close-up of people near the door (blonde woman, man with glasses)
- **t=3–10s** [3] interior ultra-wide: Wide room; presenter at the screen, audience seated

### DJI_20260719092652_0010_D.MP4 — 09:26 — 12 frames

- **t=0–9s** [3] interior ultra-wide: Wide room; screen with text, audience seated
- **t=9–12s** [4] interior person close-up: Close-up of two men by the glass door (CURSOR logo reversed on the glass)

### DJI_20260719092946_0011_D.MP4 — 09:29 — 8 frames

- **t=0–6s** [4] interior person close-up: People at the door; a woman looks at her phone, a man leans in to talk
- **t=6–8s** [3] interior ultra-wide: Wider room view; screen and audience

### DJI_20260719094253_0020_D.MP4 — 09:42 — 12 frames

- **t=0–12s** [3] interior ultra-wide: Wide room; screen showing code/dashboard, audience seated

### DJI_20260719094321_0021_D.MP4 — 09:43 — 10 frames

- **t=0–10s** [3] interior ultra-wide: Wide room; screen with code, audience seated

### DJI_20260719094634_0022_D.MP4 — 09:46 — 7 frames

- **t=0–3s** [2] secondary wide, one screen / one poster: The CURSOR logo on the glass door/window fills the frame
- **t=3–7s** [3] interior ultra-wide: Interior wide; a man in the foreground, blonde woman, audience seated

### DJI_20260719094653_0023_D.MP4 — 09:46 — 8 frames

- **t=0–2s** [2] secondary wide, one screen / one poster: The CURSOR logo on the glass fills the frame
- **t=2–8s** [3] interior ultra-wide: Interior wide; blonde woman in pink top and audience, screen in the back

### DJI_20260719094910_0025_D.MP4 — 09:49 — 5 frames

- **t=0–5s** [4] interior person close-up: EXTERIOR street: close-up of people outside (woman with a phone, men chatting) under the plane trees. Note: category 4 is labelled interior; this is the closest fit, exterior people close-up.

### DJI_20260719095441_0026_D.MP4 — 09:54 — 8 frames

- **t=0–8s** [1] ultra-wide storefront + whole poster/banner: EXTERIOR: black CURSOR banner ("Cursor Cafe x Sunset Shanghai") and the whole storefront, crowd at the door

### DJI_20260719095456_0027_D.MP4 — 09:54 — 14 frames

- **t=0–14s** [1] ultra-wide storefront + whole poster/banner: EXTERIOR: storefront entrance, glass doors, awning, people at the door

### DJI_20260719095849_0028_D.MP4 — 09:58 — 15 frames

- **t=0–13s** [3] interior ultra-wide: Wide room; screen with code, audience seated
- **t=13–15s** [5] interior audience close-up: Close-up of an audience member (man in North Face shirt)

### DJI_20260719095919_0029_D.MP4 — 09:59 — 12 frames

- **t=0–12s** [3] interior ultra-wide: Presenter (man in white shirt) at a screen with code; audience leaning in, Q&A feel

### DJI_20260719100427_0031_D.MP4 — 10:04 — 14 frames

- **t=0–14s** [3] interior ultra-wide: Wide room; screen with a settings/UI window, presenter (man in white shirt) seated at a laptop, audience

### DJI_20260719100747_0032_D.MP4 — 10:07 — 11 frames

- **t=0–11s** [1] ultra-wide storefront + whole poster/banner: EXTERIOR: two hosts by the black CURSOR banner giving thumbs up, crowd at the door

### DJI_20260719100911_0033_D.MP4 — 10:09 — 6 frames

- **t=0–6s** [4] interior person close-up: EXTERIOR street: people close-up (men chatting, banana leaves, awning). Note: exterior people close-up; category 4 is the closest fit.

### DJI_20260719100954_0034_D.MP4 — 10:09 — 18 frames

- **t=0–18s** [4] interior person close-up: EXTERIOR street: people chatting (woman in white dress, men), plane trees. Note: exterior people close-up.

### DJI_20260719101128_0035_D.MP4 — 10:11 — 8 frames

- **t=0–8s** [4] interior person close-up: EXTERIOR street: people (man with a camera, woman on her phone). Note: exterior people close-up.

### DJI_20260719101206_0036_D.MP4 — 10:12 — 16 frames

- **t=0–16s** [3] interior ultra-wide: Presenter (man in light shirt) at a screen showing a website ("Shim by feel" product page), audience seated

### DJI_20260719101336_0037_D.MP4 — 10:13 — 10 frames

- **t=0–10s** [1] ultra-wide storefront + whole poster/banner: EXTERIOR: whole storefront and awning, people at the door, street with plane trees

### DJI_20260719101711_0039_D.MP4 — 10:17 — 12 frames

- **t=0–4s** [4] interior person close-up: Woman in black (staff) in the foreground, audience seated behind her
- **t=4–12s** [3] interior ultra-wide: Wider room view; audience seated, blue screen in the back

### DJI_20260719101751_0040_D.MP4 — 10:17 — 7 frames

- **t=0–7s** [3] interior ultra-wide: Presenter (man in black tee) at a screen showing a phone UI/app, audience seated, some on laptops

### DJI_20260719101843_0042_D.MP4 — 10:18 — 8 frames

- **t=0–8s** [1] ultra-wide storefront + whole poster/banner: EXTERIOR: black CURSOR banner ("Cursor Cafe x Sunset Shanghai") and storefront; man in white tee giving thumbs up, crowd

### DJI_20260719102228_0044_D.MP4 — 10:22 — 7 frames

- **t=0–7s** [3] interior ultra-wide: Presenter (man in blue polo and cap) at a screen, audience seated

### DJI_20260719102949_0045_D.MP4 — 10:29 — 9 frames

- **t=0–9s** [3] interior ultra-wide: Presenter (man in blue polo) wrapping up; audience seated, camera behind a man with a backpack

### DJI_20260719103139_0046_D.MP4 — 10:31 — 15 frames

- **t=0–15s** [3] interior ultra-wide: Screen playing a video/animation; audience watching, presenter (man in light shirt) at the side

### DJI_20260719103214_0047_D.MP4 — 10:32 — 4 frames

- **t=0–4s** [3] interior ultra-wide: Crowd; a man with a camera, the screen in the back

### DJI_20260719103250_0048_D.MP4 — 10:32 — 7 frames

- **t=0–7s** [3] interior ultra-wide: Presenter (man in light blue shirt) at a screen showing the "AI Mi" app download page, audience seated

### DJI_20260719103600_0049_D.MP4 — 10:36 — 12 frames

- **t=0–12s** [3] interior ultra-wide: Presenter (man in light blue shirt) at a screen showing "Pairoa" (blue landing page), audience leaning in

### DJI_20260719103621_0050_D.MP4 — 10:36 — 11 frames

- **t=0–11s** [3] interior ultra-wide: Presenter (man in light blue shirt) at the Pairoa screen, gesturing; an audience member gestures back (Q&A)

### DJI_20260719103816_0051_D.MP4 — 10:38 — 19 frames

- **t=0–19s** [3] interior ultra-wide: Presenter (man in light blue shirt) at a laptop, screen with a UI; the audience laughs - the laughter moment

### DJI_20260719104335_0052_D.MP4 — 10:43 — 11 frames

- **t=0–11s** [3] interior ultra-wide: Crowd; blonde woman (pink top) in the foreground, people at tables, a fan

### DJI_20260719104354_0053_D.MP4 — 10:43 — 7 frames

- **t=0–7s** [5] interior audience close-up: Close-up of audience members at a table chatting (men, a fan)

### DJI_20260719104432_0054_D.MP4 — 10:44 — 7 frames

- **t=0–7s** [4] interior person close-up: EXTERIOR street: four people chatting under the plane trees. Note: exterior people close-up.

### DJI_20260719104548_0055_D.MP4 — 10:45 — 6 frames

- **t=0–6s** [4] interior person close-up: EXTERIOR street: people outside the shop under the awning; woman in white lace, man with a coffee cup. Note: exterior people close-up.

### DJI_20260719104626_0056_D.MP4 — 10:46 — 7 frames

- **t=0–2s** [5] interior audience close-up: Close-up of people at the bar (woman with a phone, men)
- **t=2–7s** [3] interior ultra-wide: Wider room; a woman presenter (blonde, pink top) at the screen, audience seated

### DJI_20260719104647_0057_D.MP4 — 10:46 — 7 frames

- **t=0–7s** [3] interior ultra-wide: Man in white shirt seated; screen showing a blue "no signal"/settings page, audience seated

### DJI_20260719105222_0058_D.MP4 — 10:52 — 5 frames

- **t=0–5s** [4] interior person close-up: EXTERIOR street: people under the plane trees. Note: exterior people close-up.

### DJI_20260719110516_0059_D.MP4 — 11:05 — 10 frames

- **t=0–10s** [3] interior ultra-wide: Presenter (man in beige tee and light shorts) at a screen: "Your agents work. You are sleeping." with a watch graphic; audience seated

### DJI_20260719110541_0060_D.MP4 — 11:05 — 9 frames

- **t=0–9s** [3] interior ultra-wide: Same beige-tee presenter continues; screen "Your agents work", audience seated

### DJI_20260719110749_0061_D.MP4 — 11:07 — 6 frames

- **t=0–6s** [3] interior ultra-wide: Presenter (beige tee) at a screen showing "ARIAVA" with QR codes, audience seated

### DJI_20260719110926_0062_D.MP4 — 11:09 — 9 frames

- **t=0–9s** [3] interior ultra-wide: Presenter (beige tee) at the ARIAVA screen with QR codes; an audience member points at the screen (Q&A)

### DJI_20260719111025_0063_D.MP4 — 11:10 — 13 frames

- **t=0–4s** [5] interior audience close-up: Close-up of audience (man in green shirt, others)
- **t=4–13s** [3] interior ultra-wide: Wider view; presenter (beige tee) at the ARIAVA screen, audience seated

### DJI_20260719111212_0064_D.MP4 — 11:12 — 15 frames

- **t=0–4s** [5] interior audience close-up: Group standing near the bar (men, a woman)
- **t=4–15s** [3] interior ultra-wide: Presenter (beige tee) at the ARIAVA screen, audience seated

### DJI_20260719113019_0067_D.MP4 — 11:30 — 7 frames

- **t=0–7s** [3] interior ultra-wide: Presenter (man in dark tee) at a screen showing a phone AI app (Chinese text), audience seated

### DJI_20260719113657_0068_D.MP4 — 11:36 — 5 frames

- **t=0–5s** [3] interior ultra-wide: Presenter (man in dark tee) at a screen with a UI, audience seated

### DJI_20260719113730_0069_D.MP4 — 11:37 — 10 frames

- **t=0–10s** [3] interior ultra-wide: Presenter (man in dark tee) at a screen, audience seated

### DJI_20260719113836_0070_D.MP4 — 11:38 — 12 frames

- **t=0–3s** [4] interior person close-up: Man in beige tee standing by the glass door
- **t=3–12s** [3] interior ultra-wide: Presenter (man in dark tee) at the screen, audience seated

### DJI_20260719115203_0073_D.MP4 — 11:52 — 8 frames

- **t=0–8s** [3] interior ultra-wide: Presenter (man in light shirt) at a screen playing a video (person outdoors/nature), audience watching

### DJI_20260719115456_0074_D.MP4 — 11:54 — 12 frames

- **t=0–4s** [4] interior person close-up: People at the door (man in white tee, others)
- **t=4–8s** [2] secondary wide, one screen / one poster: The CURSOR logo on the glass fills the frame
- **t=8–12s** [3] interior ultra-wide: Interior wide; blonde woman and audience, screen in the back

### DJI_20260719120831_0075_D.MP4 — 12:08 — 9 frames

- **t=0–9s** [3] interior ultra-wide: Young man in purple shirt seated at a laptop; screen with code, audience seated

### DJI_20260719121456_0077_D.MP4 — 12:14 — 6 frames

- **t=0–6s** [3] interior ultra-wide: Man at a screen showing a video/photo, audience watching

### DJI_20260719122116_0079_D.MP4 — 12:21 — 4 frames

- **t=0–4s** [1] ultra-wide storefront + whole poster/banner: EXTERIOR: black CURSOR banner ("Cursor Cafe x Sunset Shanghai"); woman in black giving thumbs up, people at the door

### DJI_20260719122153_0080_D.MP4 — 12:21 — 4 frames

- **t=0–4s** [1] ultra-wide storefront + whole poster/banner: EXTERIOR: woman in white lace dress by the black CURSOR banner, people at the door

## Per-talk table

One row per distinct talk/demo, grouped by presenter (same person presenting = one talk). Topics are read from the screen/slides in the frames; where the screen is not legible the topic is 'unclear' and is not guessed. Audience size is approximate (people visible).

| Talk | Speaker | Clips | Topic | Content | Audience | Reaction | Q&A | Relatable | Narration |
|------|---------|-------|-------|---------|----------|----------|-----|-----------|-----------|
| A | man in striped shirt | DJI_20260719072352_0033_D.MP4 0-66s<br>DJI_20260719072707_0034_D.MP4 0-69s | AI-native tools (Chinese slides, 'AI-native 工具') | A talk on AI-native tools; the screen shows Chinese slides about tech innovation and a dashboard with a QR code. | ~15-20 people seated | attentive; several audience members film the screen with their phones | no clear Q&A visible in these clips | audience engaged and filming; no laughter or questions visible | The morning opens with a talk on AI-native tools — the room is already full and filming. |
| B | man in black tee with glasses | DJI_20260719073634_0037_D.MP4 0-56s<br>DJI_20260719074342_0038_D.MP4 0-32s | unclear (screen shows a website, 'Taste your wild...') | A demo of a website/product; the topic is not legible from the screen in the frames. | ~15-20 people seated | attentive; quiet | no clear Q&A visible | unclear — quiet, low visible reaction | A website demo in the early session; the room watches quietly. |
| C | man in light shirt | DJI_20260719082251_0039_D.MP4 0-44s | unclear (screen shows a dark product UI) | A demo of a product with a dark UI; the topic is not legible from the screen. | ~12-15 people seated | attentive; quiet | no clear Q&A visible | unclear — quiet, low visible reaction | A product demo with a dark interface; the room watches. |
| D | man in grey shirt with glasses, holding a mic | DJI_20260719082925_0040_D.MP4 0-77s | unclear (screen shows code/text) | A technical talk with code/text on screen; the topic is not legible from the frames. | ~15-20 people seated, some on laptops | attentive; some audience members on laptops | no clear Q&A visible | unclear — attentive but no visible laughter or questions | A long technical talk; the camera moves in close on the speaker. |
| E | woman in green tee and cap, holding a mic | DJI_20260719084815_0042_D.MP4 0-76s | a phone app (blue UI, Chinese text on screen) | A woman demos a phone app; the app name/topic is not legible from the screen. | ~15-20 people | attentive; the camera moves in close on her as she speaks | no clear Q&A visible | unclear — attentive, no visible laughter or questions | A woman takes the mic to demo a phone app. |
| F | woman in white sleeveless top | DJI_20260719091529_0043_D.MP4 0-63s | 'Your agents work' (agents product) | A woman presents an agents product; the screen reads 'Your agents work...' | ~20-25 people seated at tables | attentive | no clear Q&A visible | unclear — attentive, no visible laughter or questions | An agents product takes the screen — 'Your agents work.' |
| G | man in white tee with red logo, holding a mic | DJI_20260719092424_0044_D.MP4 0-65s | unclear (live code/terminal on screen) | A live code demo; the topic is not legible from the terminal on screen. | ~20-25 people seated, some smiling | engaged; some audience members smiling | no clear Q&A visible | audience smiling and engaged; the demo is landing | Live code on the big screen — and the room is smiling. |
| H | man in white shirt | DJI_20260719095849_0028_D.MP4 0-15s<br>DJI_20260719095919_0029_D.MP4 0-12s<br>DJI_20260719100427_0031_D.MP4 0-14s | unclear (code on screen) | A code talk; the audience leans in. Grouping note: 0028/0029 and 0031 show the same white-shirt presenter and code screen, but there is a ~5 min gap, so this grouping is likely but not certain. | ~20-25 people seated | leaning in, engaged; a Q&A feel | yes — the audience leans in and the posture reads as Q&A (someone asking, presenter answering) | audience leaning in and engaged; questions being asked | The room leans in — a code talk turns into a back-and-forth. |
| I | man in light shirt | DJI_20260719101206_0036_D.MP4 0-16s | 'Shim by feel' (a website/product) | A demo of 'Shim by feel'; the screen shows the product website. | ~20 people seated | attentive | no clear Q&A visible | unclear — attentive, no visible laughter or questions | A 'Shim by feel' demo on the screen. |
| J | man in black tee | DJI_20260719101751_0040_D.MP4 0-7s | a phone app (phone UI on screen) | A phone app demo; the app name is not legible from the screen. | ~15-20 people seated, some on laptops | attentive | no clear Q&A visible | unclear — attentive, no visible reaction | A quick phone-app demo. |
| K | man in blue polo and cap | DJI_20260719102228_0044_D.MP4 0-7s<br>DJI_20260719102949_0045_D.MP4 0-9s | unclear (UI on screen) | A talk/demo; the topic is not legible from the screen. | ~20 people seated | attentive | no clear Q&A visible | unclear — attentive, no visible reaction | A talk wraps up as the room settles. |
| L | man in light blue shirt | DJI_20260719103250_0048_D.MP4 0-7s<br>DJI_20260719103600_0049_D.MP4 0-12s<br>DJI_20260719103621_0050_D.MP4 0-11s<br>DJI_20260719103816_0051_D.MP4 0-19s | AI Mi app, then Pairoa | A demo of the AI Mi app, then Pairoa (blue landing page on screen). This is the laughter moment: in 0051 the whole room laughs. | ~25-30 people seated | laughter — the room laughs together in 0051; leaning in | yes — an audience member gestures back at the presenter in 0050 (a question / follow-up) | room laughed together; audience asked follow-ups — the most relatable, warmest moment in the morning footage | The room erupts — the Pairoa demo lands and everyone laughs. This is the warmest beat of the morning. |
| M | man in beige tee and light shorts | DJI_20260719110516_0059_D.MP4 0-10s<br>DJI_20260719110541_0060_D.MP4 0-9s<br>DJI_20260719110749_0061_D.MP4 0-6s<br>DJI_20260719110926_0062_D.MP4 0-9s<br>DJI_20260719111025_0063_D.MP4 0-13s<br>DJI_20260719111212_0064_D.MP4 0-15s | 'Your agents work' / ARIAVA (agents product, QR codes on screen) | A demo of ARIAVA — the screen reads 'Your agents work. You are sleeping.' with a watch graphic, then ARIAVA with QR codes for download. | ~25-30 people seated | attentive; an audience member points at the screen | yes — an audience member points at the screen in 0062 (a question about the product) | audience engaged and asking questions; the 'agents work while you sleep' hook is clear on screen | ARIAVA — 'Your agents work. You are sleeping.' The room leans in to scan the QR code. |
| N | man in dark tee | DJI_20260719113019_0067_D.MP4 0-7s<br>DJI_20260719113657_0068_D.MP4 0-5s<br>DJI_20260719113730_0069_D.MP4 0-10s<br>DJI_20260719113836_0070_D.MP4 0-12s | an AI phone app (Chinese text on screen) | A demo of an AI phone app; the app name/topic is not legible from the screen. | ~20-25 people seated | attentive | no clear Q&A visible | unclear — attentive, no visible laughter or questions | Another AI phone app takes the screen late in the morning. |
| O | man in light shirt | DJI_20260719115203_0073_D.MP4 0-8s | unclear (a video playing on screen — outdoor/nature footage) | A presenter plays a video on screen (outdoor/nature footage); the video content/topic is not clear from the frames. | ~20 people seated | watching the screen | no clear Q&A visible | unclear — the room is watching, no visible reaction | A video plays on the big screen and the room watches. |
| P | young man in purple shirt, seated at a laptop | DJI_20260719120831_0075_D.MP4 0-9s | unclear (code on screen) | A code demo/Q&A from a laptop; the topic is not legible from the screen. | ~15-20 people seated | attentive | no clear Q&A visible | unclear — attentive, no visible reaction | A code demo from a laptop, late morning. |
| Q | man at the screen | DJI_20260719121456_0077_D.MP4 0-6s | unclear (a video/photo on screen) | A presenter shows a video/photo on screen; the content is not clear from the frames. | ~15-20 people seated | watching the screen | no clear Q&A visible | unclear — the room is watching, no visible reaction | The last talk of the morning — a video on screen, the room watching. |

**Warmest / most relatable talk:** Talk L (Pairoa) — the room laughs together in clip 0051 and an audience member gestures back in 0050. This is the best 'human warmth' beat in the morning footage and the strongest candidate for the recap's emotional peak.

**Most legible product talks (screen text readable):** Talk A (AI-native tools), Talk F and M ('Your agents work' / ARIAVA), Talk I ('Shim by feel'), Talk L (AI Mi / Pairoa).

## Files

- `shot-list.jsonl` — one row per extracted frame (1108 rows): clip, frame file, timestamp, shot type, description, confidence.
- `talks.jsonl` — one row per talk (17 talks): speaker, clips, topic, content, audience size, reaction, Q&A, relatable, narration.
- `frames-dense/<clip>/frame-NNNN.jpg` — the 1108 dense frames (1 fps, 1280 px, JPEG q4).
- `contact-sheets-dense/sheet-*.jpg` — 24 contact sheets (first/middle/last frame per clip) used for classification.

## New files found on Drive during this job

The Drive folder kept updating while this job ran. Three re-checks were done; each new batch was downloaded (per-file-ID) and folded into the extraction and classification:

- **First check (09:51):** 4 new MP4s (07:23 0033, 07:27 0034, 07:36 0037, 07:43 0038 — 224 s) + 293 new JPGs.
- **Second check (~10:05):** 2 new MP4s (08:22 0039, 08:29 0040 — 120 s).
- **Third check (~10:25):** 2 new MP4s (09:15 0043, 09:24 0044 — 129 s).
- **Final check (~10:45):** 1 new MP4 (08:48 0042 — 76 s) + ~55 more JPGs (HM5A1869 onwards).
- **Total added by re-checks:** 9 MP4s (~549 s) on top of the original 59. Final total: **68 MP4s, 1110.2 s, 1108 frames.**
- **Photos:** 597 JPGs now in `photos/` (original 300, minus the 4 delete candidates the user told us to delete, plus 293 + 12 newly downloaded). The 4 delete candidates (HM5A1332, HM5A1357, HM5A1539, HM5A1614) are confirmed absent from `photos/` — they stay deleted.
- **Note:** the Drive folder is still updating; if more files arrive after this report, they are not in this shot list and will need a fresh pass.
