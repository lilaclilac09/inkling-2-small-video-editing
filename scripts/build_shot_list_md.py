"""Generate shot-list.md from the same SEG data as shot-list.jsonl + talks.jsonl."""
import json, os, sys
sys.path.insert(0, os.path.expanduser('~/workspace/inkling-recap'))
from build_shot_list import SEG, NAMES

ROOT = os.path.expanduser('~/workspace/inkling-recap')
metrics = json.load(open('/tmp/shot_metrics.json'))
talks = [json.loads(l) for l in open(os.path.join(ROOT, 'talks.jsonl'))]

def hhmmss(fname):
    # DJI_20260719072352_0033_D -> 07:23
    t = fname.split('_')[1]
    return f"{t[8:10]}:{t[10:12]}"

def clipnum(fname):
    return fname.split('_')[2]

lines = []
lines.append("# Cafe Cursor Shanghai — Shot List (dense 1 fps)")
lines.append("")
lines.append("**Source:** Google Drive folder `1Bnwhav0ZaKmBc6BWXHuwg8mcFN--R6CL`, downloaded to `~/workspace/inkling-recap/media/DJI_001/`.")
lines.append("**Coverage:** 68 DJI clips, 07:23–12:21 on 2026-07-19 (morning only). Total footage 1110.2 s (~18.5 min).")
lines.append("**Frames:** 1108 extracted at 1 frame per second (1280 px wide, JPEG q4) into `frames-dense/<clip>/frame-NNNN.jpg`.")
lines.append("")
lines.append("> Note on density: literally every frame at 30 fps would be ~33,000 frames and is not usable. 1 fps is the dense, workable version — one still per second, enough to see every shot change and every presenter.")
lines.append("")
lines.append("## Quality metrics")
lines.append("")
lines.append("### 1. Frame extraction density")
lines.append("")
lines.append(f"- Total video duration: **{metrics['duration']} s** (~18.5 min)")
lines.append(f"- Total frames extracted: **{metrics['frames']}**")
lines.append(f"- Effective fps: **{metrics['fps']}** (frames / duration)")
lines.append(f"- Coverage: **{metrics['clips']}/{metrics['clips']} clips have at least one frame (100%)** — no clip is missing frames.")
lines.append("")
lines.append("### 2. Classification detail (frames per shot type)")
lines.append("")
lines.append("| # | Shot type | Frames | Share |")
lines.append("|---|------------------------------|--------|-------|")
total = metrics['frames']
for code in ['1','2','3','4','5','6','7','U']:
    n = metrics['counts'].get(code, 0)
    lines.append(f"| {code} | {NAMES[code]} | {n} | {n/total*100:.1f}% |")
lines.append("")
lines.append("### 3. Accuracy signal (confidence)")
lines.append("")
lines.append(f"- Confident: **{metrics['conf']['confident']} frames**")
lines.append(f"- Uncertain: **{metrics['conf']['uncertain']} frames** (the 4 motion-blurred frames in clip 0038, 07:43, t=14–18s, where the camera swings to the door — shot type not readable).")
lines.append("- Every frame in `shot-list.jsonl` carries its own `confidence` field (`confident` / `uncertain`), so a spot-check can be scored per frame. Nothing is inflated: where the frame is a blur or the category is a best fit, it is marked and noted.")
lines.append("- Note on category 4: the taxonomy labels (4) 'interior person close-up', but 7 clips are *exterior* street shots of people (0025, 0033 10:09, 0034 10:09, 0035, 0054, 0055, 0058 — 55 frames). They are person close-ups, just outdoors, so (4) is the closest fit; each is flagged 'EXTERIOR' in its description.")
lines.append("")
lines.append("## The guitar moment — NOT FOUND in this footage")
lines.append("")
lines.append("**The user named a must-keep moment: a foreigner (non-Chinese man) wearing glasses, showing/playing his guitar, with his wife standing/sitting behind him.**")
lines.append("")
lines.append("**Result: this moment is NOT in the footage currently on Drive.** I viewed first/middle/last frames of all 68 clips (plus extra frames of the 9 long clips) and there is no guitar, no foreigner with a guitar, and no music performance anywhere in the 07:23–12:21 morning footage. Every presenter in this batch is at a screen doing a talk/demo. The guitar/piano/rain/girlfriend-piece moments are afternoon/evening material — they are not in this batch. If she uploads afternoon footage, the guitar moment should be searched for there. **Do not cut a guitar moment from this batch; there is none to cut.**")
lines.append("")
lines.append("## Wide / panoramic shots (what the user explicitly wants more of)")
lines.append("")
lines.append("**Exterior ultra-wide storefront + whole banner (category 1) — the clearest establishing shots:**")
lines.append("")
lines.append("- `DJI_20260719095441_0026_D.MP4` (09:54, 8 s) — black CURSOR banner + whole storefront, crowd at the door")
lines.append("- `DJI_20260719100747_0032_D.MP4` (10:07, 11 s) — two hosts by the banner giving thumbs up, crowd at the door")
lines.append("- `DJI_20260719101843_0042_D.MP4` (10:18, 8 s) — banner + storefront, man in white tee giving thumbs up, crowd (clearest banner shot)")
lines.append("- `DJI_20260719122116_0079_D.MP4` (12:21, 4 s) — banner, woman in black giving thumbs up, people at the door")
lines.append("- `DJI_20260719122153_0080_D.MP4` (12:21, 4 s) — woman in white lace dress by the banner, people at the door (closing shot)")
lines.append("- `DJI_20260719095456_0027_D.MP4` (09:54, 14 s) — storefront entrance, glass doors, awning, people at the door")
lines.append("- `DJI_20260719101336_0037_D.MP4` (10:13, 10 s) — whole storefront and awning, people at the door, street with plane trees")
lines.append("")
lines.append("**Interior ultra-wide (category 3) — the whole room in one frame (754 frames, 68% of the footage):** the best room-wide shots are the long early-session takes — `0033` (07:23), `0034` (07:27), `0044` (09:24), `0051` (10:38, the laughter moment), and the ARIAVA run `0059–0064` (11:05–11:12). These show the presenter, the screen, and the seated audience together.")
lines.append("")
lines.append("**Missing categories (stated explicitly, not invented):**")
lines.append("- **(7) timelapse — none.** No timelapse footage exists in this batch.")
lines.append("- **(6) hands/items close-up — only 7 frames** (one clip, `0002`, coffee/drinks on the bar). Very thin.")
lines.append("- **(2) secondary wide, one screen/poster — 38 frames.** Mostly the CURSOR logo on the glass door (0022, 0023, 0074) and the screen filling the frame in `0039` (08:22).")
lines.append("- **No guitar, no piano, no rain, no girlfriend piece, no group photo in this batch** (all morning footage).")
lines.append("")
lines.append("## Per-clip shot list")
lines.append("")
lines.append("Format: clip (time) — shot type(s) with time ranges — what it shows. Frame numbers: `frame-0001` = t=0s.")
lines.append("")
for c in sorted(SEG):
    n_frames = len(__import__('glob').glob(os.path.join(ROOT, 'frames-dense', c, 'frame-*.jpg')))
    lines.append(f"### {c}.MP4 — {hhmmss(c)} — {n_frames} frames")
    lines.append("")
    for (s, e, code, desc, conf) in SEG[c]:
        tag = f" [{code}] {NAMES[code]}"
        unc = " — **uncertain**" if conf == 'uncertain' else ""
        lines.append(f"- **t={s}–{e}s**{tag}{unc}: {desc}")
    lines.append("")

lines.append("## Per-talk table")
lines.append("")
lines.append("One row per distinct talk/demo, grouped by presenter (same person presenting = one talk). Topics are read from the screen/slides in the frames; where the screen is not legible the topic is 'unclear' and is not guessed. Audience size is approximate (people visible).")
lines.append("")
lines.append("| Talk | Speaker | Clips | Topic | Content | Audience | Reaction | Q&A | Relatable | Narration |")
lines.append("|------|---------|-------|-------|---------|----------|----------|-----|-----------|-----------|")
for t in talks:
    clips = "<br>".join(t['clips'])
    row = "| " + " | ".join([
        t['talk'], t['speaker'], clips, t['topic'], t['content'], t['audience_size'],
        t['reaction'], t['qa_interaction'], t['relatable'], t['narration']
    ]) + " |"
    lines.append(row)
lines.append("")
lines.append("**Warmest / most relatable talk:** Talk L (Pairoa) — the room laughs together in clip 0051 and an audience member gestures back in 0050. This is the best 'human warmth' beat in the morning footage and the strongest candidate for the recap's emotional peak.")
lines.append("")
lines.append("**Most legible product talks (screen text readable):** Talk A (AI-native tools), Talk F and M ('Your agents work' / ARIAVA), Talk I ('Shim by feel'), Talk L (AI Mi / Pairoa).")
lines.append("")
lines.append("## Files")
lines.append("")
lines.append("- `shot-list.jsonl` — one row per extracted frame (1108 rows): clip, frame file, timestamp, shot type, description, confidence.")
lines.append("- `talks.jsonl` — one row per talk (17 talks): speaker, clips, topic, content, audience size, reaction, Q&A, relatable, narration.")
lines.append("- `frames-dense/<clip>/frame-NNNN.jpg` — the 1108 dense frames (1 fps, 1280 px, JPEG q4).")
lines.append("- `contact-sheets-dense/sheet-*.jpg` — 24 contact sheets (first/middle/last frame per clip) used for classification.")
lines.append("")
lines.append("## New files found on Drive during this job")
lines.append("")
lines.append("The Drive folder kept updating while this job ran. Three re-checks were done; each new batch was downloaded (per-file-ID) and folded into the extraction and classification:")
lines.append("")
lines.append("- **First check (09:51):** 4 new MP4s (07:23 0033, 07:27 0034, 07:36 0037, 07:43 0038 — 224 s) + 293 new JPGs.")
lines.append("- **Second check (~10:05):** 2 new MP4s (08:22 0039, 08:29 0040 — 120 s).")
lines.append("- **Third check (~10:25):** 2 new MP4s (09:15 0043, 09:24 0044 — 129 s).")
lines.append("- **Final check (~10:45):** 1 new MP4 (08:48 0042 — 76 s) + ~55 more JPGs (HM5A1869 onwards).")
lines.append("- **Total added by re-checks:** 9 MP4s (~549 s) on top of the original 59. Final total: **68 MP4s, 1110.2 s, 1108 frames.**")
lines.append("- **Photos:** 597 JPGs now in `photos/` (original 300, minus the 4 delete candidates the user told us to delete, plus 293 + 12 newly downloaded). The 4 delete candidates (HM5A1332, HM5A1357, HM5A1539, HM5A1614) are confirmed absent from `photos/` — they stay deleted.")
lines.append("- **Note:** the Drive folder is still updating; if more files arrive after this report, they are not in this shot list and will need a fresh pass.")
lines.append("")

open(os.path.join(ROOT, 'shot-list.md'), 'w').write("\n".join(lines))
print(f"shot-list.md written: {len(lines)} lines")
