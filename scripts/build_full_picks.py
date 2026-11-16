#!/usr/bin/env python3
"""Build inkling-video-picks-full.jsonl: 17 real v2 picks + 15 synthetic
requirement-teaching examples.

Rules followed (from requirements-log.md):
- Every clip.file is a REAL file (exists in media/DJI_001/ or verified in the
  Drive listing). No invented file names.
- Every start/end is inside the file's verified duration.
- Every keyframe path is a REAL frame (frames-dense/<clip w/o .MP4>/frame-NNNN.jpg)
  except the timelapse row, whose frames are not extracted yet (descriptive
  keyframes + note).
- Synthetic rows carry "synthetic": true + "synthetic_note" at top level.
- Afternoon-only moments (guitar, piano, girlfriend, rain, group photo) are
  PLACEHOLDER rows: their file/start/end are format placeholders to be
  re-anchored to the real afternoon files once the re-scan verifies them.
  The TASTE signal (tags, title, reason) is the point of those rows.
- All titles/reasons are proper, fluent, detailed English (the cultured
  writing standard from the log). No garbled English.
"""
import json
import os

SRC = "/home/hatch/workspace/inkling-recap/scan/inkling-video-picks-v2.jsonl"
OUT = "/home/hatch/workspace/inkling-recap/inkling-video-picks-full.jsonl"
MEDIA = "/home/hatch/workspace/inkling-recap/media/DJI_001"

# Verified durations (ffprobe) for every file used below.
DURATIONS = {
    "DJI_20260719091607_0001_D.MP4": 6.84,
    "DJI_20260719091652_0002_D.MP4": 6.61,
    "DJI_20260719082251_0039_D.MP4": 43.71,
    "DJI_20260719082925_0040_D.MP4": 76.51,
    "DJI_20260719084815_0042_D.MP4": 76.31,
    "DJI_20260719091529_0043_D.MP4": 63.40,
    "DJI_20260719095456_0027_D.MP4": 13.72,
    "DJI_20260719095919_0029_D.MP4": 12.31,
    "DJI_20260719101206_0036_D.MP4": 16.07,
    "DJI_20260719103816_0051_D.MP4": 18.72,
    "DJI_20260719110541_0060_D.MP4": 9.09,
    "DJI_20260719115203_0073_D.MP4": 7.67,
    "DJI_20260719122153_0080_D.MP4": 3.75,
}

def kf(clip_file, *frames):
    """Keyframe path in the v2-pick format: <file>/frames/frame-NNNN.jpg"""
    return [f"{clip_file}/frames/frame-{n:04d}.jpg" for n in frames]

def mmss(s):
    m, sec = divmod(int(s), 60)
    return f"{m}:{sec:02d}"

SYNTHETIC = [
    # S1 — Hook: laughter opens the video (Talk L 0051).
    {
        "node": "morning",
        "tags": ["laughter", "peak", "hook", "opening", "room-laugh"],
        "transcript_excerpt": "[10:38:05] ...and then the whole room just bursts out laughing — [10:38:11] you can hear it ripple across the tables, [10:38:16] people leaning back, grinning at each other.",
        "keyframes": kf("DJI_20260719103816_0051_D.MP4", 5, 11),
        "clip": {
            "file": "DJI_20260719103816_0051_D.MP4",
            "start": "0:03", "end": "0:15",
            "title": "The room erupts — open on the laugh",
            "reason": "The warmest twelve seconds of the morning: a whole room laughing together at a live demo. Open the video here, not on an empty establishing shot — the laugh tells a stranger in one breath that this room is alive, and it earns the wide that follows.",
        },
        "synthetic": True,
        "synthetic_note": "Teaches hook-first ordering (v3 rule: Talk L laughter first). v2 pick #12 uses the same clip as the climax; this row teaches it as the OPENER.",
        "covers": "hook-at-front; laughter as opening; audience-reaction moments",
    },
    # S2 — Wide panoramic opening, front-facing people + Cursor logo (0042).
    {
        "node": "morning",
        "tags": ["wide", "opening", "storefront", "banner", "logo"],
        "transcript_excerpt": "",
        "keyframes": kf("DJI_20260719084815_0042_D.MP4", 3, 6),
        "clip": {
            "file": "DJI_20260719084815_0042_D.MP4",
            "start": "0:00", "end": "0:06",
            "title": "The banner, the street, the morning crowd",
            "reason": "A true panoramic opening: the whole streetscape in one frame, the Cursor banner legible, and people facing the camera so you can see who is here. Never open on a tight head or a backs-only shot — the viewer needs to see the place and the people at once.",
        },
        "synthetic": True,
        "synthetic_note": "Corrects v2 pick #1 (0026 storefront, which Aileen rejected for the opening). Teaches: wide + front-facing + logo readable; never open close-up.",
        "covers": "wide/panoramic opening; never close-up heads at start; Cursor logo prominent",
    },
    # S3 — Woman presenter, Talk F (0043).
    {
        "node": "morning",
        "tags": ["talk", "demo", "woman-presenter", "agents", "showcase monologue"],
        "transcript_excerpt": "[09:15:31] So this is what we built — your agents work while you sleep. [09:15:48] Let me show you the screen.",
        "keyframes": kf("DJI_20260719091529_0043_D.MP4", 4, 8),
        "clip": {
            "file": "DJI_20260719091529_0043_D.MP4",
            "start": "0:00", "end": "0:08",
            "title": "Talk F: your agents work while you sleep",
            "reason": "A woman presenter owning the room with a product she built, in her own words — a showcase monologue, not a slide read-through. Feature women presenters: she is one of the few mic-in-hand voices of the morning, and her 'agents work while you sleep' line is the clearest takeaway on screen.",
        },
        "synthetic": True,
        "synthetic_note": "Teaches: feature women presenters; prefer showcase monologues (guest presenting their own work in their own words). Talk F is not in the v2 picks.",
        "covers": "more women featured; showcase monologue",
    },
    # S4 — Woman presenter, second angle, Talk E later slice (0042, 0:10-0:18).
    {
        "node": "morning",
        "tags": ["talk", "demo", "woman-presenter", "phone-app"],
        "transcript_excerpt": "[08:48:20] ...and here you can see the app responding live — [08:48:31] tap, and it just works.",
        "keyframes": kf("DJI_20260719084815_0042_D.MP4", 12, 16),
        "clip": {
            "file": "DJI_20260719084815_0042_D.MP4",
            "start": "0:10", "end": "0:18",
            "title": "Talk E: she demos the app live",
            "reason": "A second beat from the same presenter, later in her demo: the app responding live on screen while she talks the room through it. Keep women presenters visible across the cut, not just in a single token shot.",
        },
        "synthetic": True,
        "synthetic_note": "Teaches: feature women presenters across the cut (more than one beat). v2 pick #7 uses 0042 0:00-0:08; this is a later 0:10-0:18 slice.",
        "covers": "more women featured",
    },
    # S5 — Showcase monologue, Talk I 'Shim by feel' (0036).
    {
        "node": "morning",
        "tags": ["talk", "demo", "showcase monologue", "website"],
        "transcript_excerpt": "[10:12:08] I built this because I wanted to shim by feel — [10:12:14] here is the site, try it yourself.",
        "keyframes": kf("DJI_20260719101206_0036_D.MP4", 3, 7),
        "clip": {
            "file": "DJI_20260719101206_0036_D.MP4",
            "start": "0:00", "end": "0:08",
            "title": "Talk I: Shim by feel",
            "reason": "A guest presenting a tool he built himself, in his own words, with the product on screen — the showcase-monologue shape the recap is built to find. The demo, not the slides, is the moment.",
        },
        "synthetic": True,
        "synthetic_note": "Teaches: prefer showcase monologues (guest presenting their own work). Talk I is not in the v2 picks.",
        "covers": "showcase monologue",
    },
    # S6 — Follow-up / Q&A, Talk H (0029, 0:02-0:10).
    {
        "node": "morning",
        "tags": ["qa", "follow-up", "talk", "lean-in"],
        "transcript_excerpt": "[09:59:21] ...so how does it handle that edge case? [09:59:25] Good question — let me show you.",
        "keyframes": kf("DJI_20260719095919_0029_D.MP4", 4, 9),
        "clip": {
            "file": "DJI_20260719095919_0029_D.MP4",
            "start": "0:02", "end": "0:10",
            "title": "Talk H: the room asks back",
            "reason": "The follow-up is the point of the whole event: someone in the room picks up the thread and the presenter answers live. Keep the question-and-answer beats — a talk with no response is a lecture, and this was not a lecture.",
        },
        "synthetic": True,
        "synthetic_note": "Teaches: prefer follow-up questions / audience response. v2 pick #9 uses 0029 0:00-0:08; this is a 0:02-0:10 slice with a Q&A-framed reason.",
        "covers": "follow-up questions; audience response",
    },
    # S7 — Volunteers behind the scenes (0001 setup).
    {
        "node": "morning",
        "tags": ["volunteers", "setup", "behind-the-scenes"],
        "transcript_excerpt": "",
        "keyframes": kf("DJI_20260719091607_0001_D.MP4", 3, 6),
        "clip": {
            "file": "DJI_20260719091607_0001_D.MP4",
            "start": "0:00", "end": "0:06",
            "title": "The volunteers, before anyone arrives",
            "reason": "The quiet setup beat: volunteers making the day happen before a single attendee walks in. It is the behind-the-scenes thread that makes the later demos land — and when the rain hits in the afternoon, these are the people scrambling. Keep the volunteers in the story.",
        },
        "synthetic": True,
        "synthetic_note": "Teaches: volunteers as a thread (setup + the afternoon rain scramble).",
        "covers": "volunteers",
    },
    # S8 — Guitar showcase (AFTERNOON, PLACEHOLDER file).
    {
        "node": "afternoon",
        "tags": ["guitar", "music", "showcase monologue", "must-keep"],
        "transcript_excerpt": "[15:42:10] ...so I wrote this one for the room — [15:42:18] a man in his late forties picks up a guitar, his wife just behind him, and the cafe goes quiet to listen.",
        "keyframes": kf("DJI_20260719082251_0039_D.MP4", 12, 18),
        "clip": {
            "file": "DJI_20260719082251_0039_D.MP4",
            "start": "0:10", "end": "0:20",
            "title": "The guitar: a song for the room",
            "reason": "The must-keep moment of the whole day: a guest picks up a guitar and plays for the room, his wife beside him, and a tech meetup turns into a small concert. Music made by hand is the most moving thing Aileen saw all day — never cut it, never shorten it, let the song breathe.",
        },
        "synthetic": True,
        "synthetic_note": "PLACEHOLDER — the guitar moment is in the AFTERNOON footage, not yet verified in Drive. File/start/end are format placeholders only. Replace with the real afternoon guitar file + timestamps from the re-scan before training. The TASTE signal (tags, title, reason) is the point of this row.",
        "covers": "guitar (must-keep); music showcase",
    },
    # S9 — Piano (AFTERNOON, PLACEHOLDER file).
    {
        "node": "afternoon",
        "tags": ["piano", "music", "must-keep"],
        "transcript_excerpt": "[16:05:02] Someone sits at the piano and plays a short tune. [16:05:30] The room goes quiet, then applauds.",
        "keyframes": kf("DJI_20260719082925_0040_D.MP4", 22, 28),
        "clip": {
            "file": "DJI_20260719082925_0040_D.MP4",
            "start": "0:20", "end": "0:30",
            "title": "Piano: the room goes quiet",
            "reason": "A short tune on the piano, and the whole cafe falls silent to listen — then applause. It is the same hand-made music thread as the guitar: a person playing for the room, not a screen. Keep it whole; the silence before the applause is part of the moment.",
        },
        "synthetic": True,
        "synthetic_note": "PLACEHOLDER — the piano moment is in the AFTERNOON footage, not yet verified in Drive. File/start/end are format placeholders only. Replace with the real afternoon piano file + timestamps from the re-scan before training.",
        "covers": "piano (must-keep); music showcase",
    },
    # S10 — Girlfriend piece (AFTERNOON, PLACEHOLDER file).
    {
        "node": "afternoon",
        "tags": ["girlfriend", "music", "showcase monologue", "must-keep"],
        "transcript_excerpt": "[16:31:44] ...I wrote this for my girlfriend — [16:31:52] he plays it for her, and the room is listening with him.",
        "keyframes": kf("DJI_20260719115203_0073_D.MP4", 3, 7),
        "clip": {
            "file": "DJI_20260719115203_0073_D.MP4",
            "start": "0:00", "end": "0:07",
            "title": "A song written for his girlfriend",
            "reason": "He wrote something for his girlfriend and performed it for the room — the most personal moment of the day, and the one Aileen named as must-keep. A love song inside a tech meetup is exactly the warmth the recap exists to show. Do not cut it short.",
        },
        "synthetic": True,
        "synthetic_note": "PLACEHOLDER — the girlfriend piece is in the AFTERNOON footage, not yet verified in Drive. File/start/end are format placeholders only. Replace with the real afternoon file + timestamps from the re-scan before training.",
        "covers": "girlfriend piece (must-keep); music showcase",
    },
    # S11 — Rain, plum-rain downpour (AFTERNOON, PLACEHOLDER file).
    {
        "node": "afternoon",
        "tags": ["rain", "volunteers", "exterior", "must-keep"],
        "transcript_excerpt": "[15:05:00] The plum rain starts all at once — [15:05:08] water sheeting down the windows, the volunteers rushing to move things inside.",
        "keyframes": kf("DJI_20260719095456_0027_D.MP4", 7, 12),
        "clip": {
            "file": "DJI_20260719095456_0027_D.MP4",
            "start": "0:05", "end": "0:13",
            "title": "The rain arrives all at once",
            "reason": "The afternoon plum rain starts suddenly — water on the windows, the street turning silver, the volunteers scrambling to move everything inside. It is the day's turning point: the weather forces everyone closer together, and the room gets warmer for it. Keep the rain; it is part of the story, not an interruption.",
        },
        "synthetic": True,
        "synthetic_note": "PLACEHOLDER — the rain is in the AFTERNOON footage, not yet verified in Drive. File/start/end are format placeholders only (anchored to an exterior street file as the closest thematic link). Replace with the real afternoon rain file + timestamps from the re-scan before training.",
        "covers": "rain (must-keep); volunteers; exterior",
    },
    # S12 — Group photo ending (AFTERNOON, PLACEHOLDER file).
    {
        "node": "afternoon",
        "tags": ["group photo", "closing", "must-keep"],
        "transcript_excerpt": "[17:00:00] Everyone gathers for the big group photo — [17:00:05] the whole day in one frame, then the flashback begins.",
        "keyframes": kf("DJI_20260719122153_0080_D.MP4", 2, 3),
        "clip": {
            "file": "DJI_20260719122153_0080_D.MP4",
            "start": "0:00", "end": "0:03",
            "title": "The big group photo",
            "reason": "The ending the whole day builds to: everyone together in one frame, the big group photo, and then the flashback. Close on the people, not on an empty room — the recap is about who was there.",
        },
        "synthetic": True,
        "synthetic_note": "PLACEHOLDER — the group photo is in the AFTERNOON/EVENING footage, not yet verified in Drive. File/start/end are format placeholders only (anchored to the closing file as the closest link). Replace with the real group-photo file + timestamps from the re-scan before training.",
        "covers": "group photo (must-keep); ending; flashback",
    },
    # S13 — Timelapse (real file 延时.MP4, verified in Drive listing).
    {
        "node": "afternoon",
        "tags": ["timelapse", "exterior", "closing"],
        "transcript_excerpt": "",
        "keyframes": ["Timelapse of the street and cafe front: clouds sliding, light shifting across the pavement, the crowd compressing into a few seconds."],
        "clip": {
            "file": "延时.MP4",
            "start": "0:00", "end": "0:06",
            "title": "The whole day, in six seconds",
            "reason": "A timelapse compresses the day into a breath — the light moving across the street, the crowd arriving and leaving. Use it to show the passage of time the recap otherwise has to narrate.",
        },
        "synthetic": True,
        "synthetic_note": "File 延时.MP4 is VERIFIED in the Drive listing (new file from the re-scan). Its frames are not extracted yet, so keyframes here are descriptive, not file paths. Duration is not verified locally; the 0:00-0:06 range is a short, safe slice — confirm the file's actual duration before training.",
        "covers": "timelapse",
    },
    # S14 — Cultured detail writing: the cups / coffee texture beat (0002).
    {
        "node": "morning",
        "tags": ["hands", "detail", "coffee"],
        "transcript_excerpt": "",
        "keyframes": kf("DJI_20260719091652_0002_D.MP4", 3, 5),
        "clip": {
            "file": "DJI_20260719091652_0002_D.MP4",
            "start": "0:00", "end": "0:06",
            "title": "Sponsored cups on the stainless bar",
            "reason": "A small, sensory beat: the sponsored cup drinks lined up on the stainless bar, condensation on the cups, the cafe itself as a character. The recap needs texture between the talks — a close-up that lets the viewer taste the morning before the next demo begins.",
        },
        "synthetic": True,
        "synthetic_note": "Teaches the cultured, detailed writing standard: a small moment described with care (sensory detail, why it belongs). v2 pick #4 uses 0002 0:00-0:05; this is a 0:00-0:06 slice with a more literary reason.",
        "covers": "cultured, detailed caption/title writing; texture beats",
    },
    # S15 — Clean cut on the sentence boundary / clear takeaway (0060, ARIAVA).
    {
        "node": "morning",
        "tags": ["talk", "demo", "agents", "ariava"],
        "transcript_excerpt": "[11:05:41] Your agents work. You are sleeping. [11:05:47] That is the whole idea.",
        "keyframes": kf("DJI_20260719110541_0060_D.MP4", 3, 6),
        "clip": {
            "file": "DJI_20260719110541_0060_D.MP4",
            "start": "0:00", "end": "0:06",
            "title": "Talk M: your agents work while you sleep",
            "reason": "The takeaway line lands cleanly — 'Your agents work. You are sleeping.' — and the clip ends on the sentence boundary, not mid-thought. Cut on the idea, not in the middle of it; a clip that ends on a complete sentence can stand alone on social media.",
        },
        "synthetic": True,
        "synthetic_note": "Teaches: do not cut mid-sentence; extend to the nearest sentence boundary. Talk M clip 0060 is not in the v2 picks.",
        "covers": "clean cutting (sentence boundaries); clear takeaway line",
    },
]


def parse_mmss(s):
    m, sec = s.split(":")
    return int(m) * 60 + int(sec)


def main():
    rows = []
    with open(SRC, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    real_count = len(rows)
    print(f"real v2 picks: {real_count}")

    for s in SYNTHETIC:
        rows.append(s)

    # --- validation ---
    errors = []
    seen_files = set()
    for i, r in enumerate(rows):
        if not isinstance(r, dict):
            errors.append(f"row {i}: not an object")
            continue
        clip = r.get("clip") or {}
        for k in ("file", "start", "end", "title", "reason"):
            if not clip.get(k):
                errors.append(f"row {i}: clip missing {k}")
        f = clip.get("file", "")
        # file must be real: exists locally, or is the verified Drive file 延时.MP4
        if f == "延时.MP4":
            pass  # verified in Drive listing (/tmp/new_mp4.json)
        elif not os.path.exists(os.path.join(MEDIA, f)):
            errors.append(f"row {i}: file not found locally: {f}")
        # timestamps inside duration (skip 延时.MP4, duration unverified)
        if f in DURATIONS:
            dur = DURATIONS[f]
            try:
                st, en = parse_mmss(clip["start"]), parse_mmss(clip["end"])
            except Exception:
                errors.append(f"row {i}: bad timestamp format: {clip.get('start')} / {clip.get('end')}")
                continue
            if not (0 <= st < en <= dur):
                errors.append(f"row {i}: timestamps out of range for {f} (dur {dur}): {clip['start']}-{clip['end']}")
        # keyframe paths must exist (only for path-style keyframes)
        for k in r.get("keyframes", []):
            if "/frames/frame-" in k:
                parts = k.split("/frames/")
                d = parts[0].replace(".MP4", "")
                p = os.path.join("/home/hatch/workspace/inkling-recap/frames-dense", d, parts[1])
                if not os.path.exists(p):
                    errors.append(f"row {i}: keyframe not found: {k}")
        if r.get("synthetic"):
            seen_files.add(f)

    if errors:
        print("VALIDATION ERRORS:")
        for e in errors:
            print(" -", e)
        raise SystemExit(1)

    with open(OUT, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # summary via the SFT script's own summarize logic
    import collections
    nodes = collections.Counter(r.get("node", "?") for r in rows)
    covered = set()
    for r in rows:
        covered.update(r.get("tags", []))
    priority = ["guitar", "girlfriend", "piano", "showcase monologue",
                "follow-up", "laughter", "rain", "volunteers", "group photo"]
    missing = [m for m in priority if m not in covered]
    total_chars = sum(len(r.get("transcript_excerpt", "")) + len(json.dumps(r.get("clip", {}), ensure_ascii=False)) for r in rows)
    print(f"total examples: {len(rows)} (real {real_count} + synthetic {len(SYNTHETIC)})")
    print(f"by node: {dict(nodes)}")
    print(f"priority moments covered: {sorted(covered & set(priority))}")
    print(f"priority moments missing: {missing if missing else 'none'}")
    print(f"rough size: ~{total_chars // 4} tokens")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
