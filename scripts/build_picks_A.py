#!/usr/bin/env python3
"""Build version-A picks (my own judgment) for the rough cut.

Reads the scan/ folders, pulls the transcript excerpt overlapping each
pick's [start, end], lists keyframes, writes the JSONL.
"""
import json
import os
import re

SCAN = "/home/hatch/workspace/inkling-recap/scan"
OUT = "/home/hatch/workspace/inkling-recap/scan/inkling-video-picks-rough.jsonl"

# (clip_number, start, end, title, reason, tags)
PICKS = [
    ("0025", 0.0, 5.4, "Arriving — sunny Yanqing Road",
     "Opening establishing shot: plane trees, brick French Concession street, people chatting outside. Sunny morning, sets the place.",
     ["opening", "street", "french-concession", "sunny"]),
    ("0001", 0.0, 6.8, "Setting up the screen",
     "Morning setup: host and volunteer getting the big screen and laptop going before anyone arrives. The work before the event.",
     ["setup", "screen", "morning", "volunteers"]),
    ("0002", 0.0, 6.6, "Coffee brewing",
     "Close on the coffee bar — pour-over, cups, the cafe at work. The smell of the morning, before the talks.",
     ["coffee", "cafe", "atmosphere"]),
    ("0007", 2.0, 10.0, "First talk — the room fills",
     "First session: presenter at the screen, a full room at round tables, paper lanterns. The event is on.",
     ["talk", "showcase", "audience", "morning"]),
    ("0020", 1.0, 9.0, "Live code on the big screen",
     "A showcase with a terminal/dashboard on screen and the room watching. Real work being shown, not slides.",
     ["showcase", "code", "demo", "audience"]),
    ("0022", 0.0, 7.4, "The host rallies the room",
     "The host (blonde, pink top) stands in the middle of the room gesturing while the screen sits on 'no signal' — the in-between moment, the room laughing.",
     ["host", "laughter", "crowd", "in-between"]),
    ("0026", 0.0, 7.7, "Cursor Cafe — the door",
     "Outside the entrance: the black CURSOR banner, the crowd at the door, green awning. The brand and the queue.",
     ["cursor", "banner", "entrance", "crowd"]),
    ("0029", 2.0, 10.0, "Q&A — leaning in",
     "A presenter at the small table with the laptop, screen showing a doc, the front rows leaning in. Discussion, not lecture.",
     ["qa", "discussion", "showcase", "audience"]),
    ("0031", 2.0, 10.0, "Demo on screen",
     "Presenter pointing at the big screen (a desktop app), the room watching. A working demo, mid-flow.",
     ["demo", "showcase", "screen", "audience"]),
    ("0034", 4.0, 12.0, "Spilling onto the street",
     "Break time outside: the woman in white chatting with a group under the plane trees, everyone laughing. The social half of the event.",
     ["street", "break", "social", "laughter", "sunny"]),
    ("0040", 0.0, 7.5, "A phone demo",
     "Presenter mirroring a phone to the big TV — a mobile demo, the audience watching a small screen made big.",
     ["demo", "phone", "showcase", "mobile"]),
    ("0046", 2.0, 10.0, "Swipe left, swipe right",
     "The most visual slide of the morning: an illustrated dating-app deck ('swipe left, swipe right') on screen, presenter telling the story.",
     ["demo", "dating-app", "slides", "showcase"]),
    ("0051", 4.0, 14.0, "Pairoa — the room laughs",
     "The Pairoa demo at its best: presenter at the laptop, the screen showing the app, and the front row laughing. Longest single moment, the warmest reaction.",
     ["demo", "pairoa", "laughter", "audience", "highlight"]),
    ("0059", 0.0, 9.5, "Your agents work",
     "A clean, readable English slide — 'Your agents work. You keep living.' — a young presenter pitching an AI agent. The most quotable frame of the day.",
     ["demo", "ai-agent", "pitch", "showcase"]),
    ("0079", 0.0, 3.6, "Noon — the banner",
     "End of the morning: a guest standing by the Cursor Cafe banner at the door, people milling. The sign-off image.",
     ["cursor", "banner", "noon", "closing"]),
    ("0080", 0.0, 3.75, "By the banner, still talking",
     "Same doorway a minute later: the woman in white by the banner, still in conversation. The event doesn't end, it just keeps talking.",
     ["cursor", "banner", "social", "closing"]),
]


def srt_segments(path):
    """Return list of (start, end, text) from an .srt file."""
    segs = []
    if not os.path.exists(path):
        return segs
    with open(path, encoding="utf-8", errors="ignore") as f:
        text = f.read()
    blocks = re.split(r"\n\s*\n", text.strip())
    for b in blocks:
        lines = [l for l in b.splitlines() if l.strip()]
        if len(lines) < 3:
            continue
        m = re.match(r"(\d+):(\d+):([\d.,]+)\s*-->\s*(\d+):(\d+):([\d.,]+)", lines[1])
        if not m:
            continue
        def ts(h, mi, s):
            return int(h) * 3600 + int(mi) * 60 + float(s.replace(",", "."))
        s0 = ts(m.group(1), m.group(2), m.group(3))
        s1 = ts(m.group(4), m.group(5), m.group(6))
        segs.append((s0, s1, " ".join(lines[2:])))
    return segs


def find_clip_file(num):
    for name in os.listdir(os.path.join(SCAN)):
        if name.startswith("DJI_") and f"_{num}_D" in name:
            return name
    return None


rows = []
total = 0.0
for num, start, end, title, reason, tags in PICKS:
    clipdir = find_clip_file(num)
    if not clipdir:
        print(f"WARN: clip {num} not found in scan/")
        continue
    srt = os.path.join(SCAN, clipdir, "transcript.srt")
    segs = srt_segments(srt)
    # excerpt: segments overlapping [start, end]
    parts = [t for (s0, s1, t) in segs if s1 > start and s0 < end]
    if parts:
        excerpt = " / ".join(parts)[:300]
    else:
        excerpt = "(no speech detected in this range — Whisper found only crowd noise)"
    frames_dir = os.path.join(SCAN, clipdir, "frames")
    frames = sorted(os.listdir(frames_dir)) if os.path.isdir(frames_dir) else []
    clip_file = f"DJI_001/{clipdir}.MP4"
    row = {
        "node": title,
        "tags": tags,
        "transcript_excerpt": excerpt,
        "keyframes": frames,
        "clip": {
            "file": clip_file,
            "start": start,
            "end": end,
            "title": title,
            "reason": reason,
        },
    }
    rows.append(row)
    total += end - start
    print(f"{num} {start}-{end} ({end-start:.1f}s) {title} | frames={frames} | segs={len(parts)}")

with open(OUT, "w", encoding="utf-8") as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

print(f"\nwrote {OUT}: {len(rows)} picks, total {total:.1f}s ({total/60:.2f} min)")
