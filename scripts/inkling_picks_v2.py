"""Ask Inkling 2 Small (via Tinker Anthropic API) for the v2 recap picks.

Vlog-style re-cut. Sends the UPDATED master prompt (with §13 shot taxonomy
and §14 transitions/story), a compact per-talk summary, a compact per-clip
shot summary (from the dense 1 fps shot list), the old transcripts (flagged
unreliable), and ~71 selected dense frames as base64.

Uses the 256K model variant. max_tokens 16000 so the list is not truncated.

Usage:
  python3 inkling_picks_v2.py
Output:
  ~/workspace/inkling-recap/scan/inkling-video-picks-v2.jsonl
  ~/workspace/inkling-recap/scan/inkling-picks-v2-raw.json
"""
import base64
import json
import os
import re
import subprocess
import sys
import urllib.request

sys.path.insert(0, "/opt/muse/skills/custom-connector-setup/bin")
from dynamic_credentials import add_surrogate_to_request, read_json_response

BASE_URL = "https://tinker.thinkingmachines.dev/services/tinker-prod/anthropic/api/v1/messages"
MODEL_256K = "thinkingmachines/Inkling-2-Small:peft:262144"
RECAP_DIR = os.path.expanduser("~/workspace/inkling-recap")
SCAN_DIR = os.path.join(RECAP_DIR, "scan")
MEDIA_DIR = os.path.join(RECAP_DIR, "media/DJI_001")
FRAMES_DIR = os.path.join(RECAP_DIR, "frames-dense")
MASTER_PROMPT = os.path.expanduser("~/workspace/your_files/inkling-demo-master-prompt.txt")
OLD_PACK = os.path.join(SCAN_DIR, "inkling-video-playground-pack.txt")
SHOT_LIST = os.path.join(RECAP_DIR, "shot-list.jsonl")
TALKS = os.path.join(RECAP_DIR, "talks.jsonl")
OUT_PICKS = os.path.join(SCAN_DIR, "inkling-video-picks-v2.jsonl")
OUT_RAW = os.path.join(SCAN_DIR, "inkling-picks-v2-raw.json")

# (clip base name without extension, timestamp seconds)
# frame file = frame-{t+1:04d}.jpg
SELECTED = [
    # Opening wide / establishing
    ("DJI_20260719095441_0026_D", 2),
    ("DJI_20260719095456_0027_D", 5),
    ("DJI_20260719101336_0037_D", 5),
    ("DJI_20260719100747_0032_D", 3),
    ("DJI_20260719101843_0042_D", 3),
    ("DJI_20260719094910_0025_D", 2),
    # Setup / arrival
    ("DJI_20260719091607_0001_D", 3),
    ("DJI_20260719091652_0002_D", 3),
    ("DJI_20260719091709_0003_D", 3),
    ("DJI_20260719092043_0007_D", 1),
    ("DJI_20260719092510_0009_D", 1),
    # Talk A — AI-native tools
    ("DJI_20260719072352_0033_D", 10),
    ("DJI_20260719072707_0034_D", 30),
    ("DJI_20260719072707_0034_D", 60),
    # Talk B — website demo
    ("DJI_20260719073634_0037_D", 20),
    ("DJI_20260719073634_0037_D", 52),
    # Talk C — dark UI
    ("DJI_20260719082251_0039_D", 5),
    ("DJI_20260719082251_0039_D", 25),
    # Talk D — grey shirt mic
    ("DJI_20260719082925_0040_D", 10),
    ("DJI_20260719082925_0040_D", 40),
    # Talk E — woman green tee phone app
    ("DJI_20260719084815_0042_D", 5),
    ("DJI_20260719084815_0042_D", 15),
    ("DJI_20260719084815_0042_D", 50),
    # Talk F — agents product
    ("DJI_20260719091529_0043_D", 20),
    # Talk G — live code, smiling
    ("DJI_20260719092424_0044_D", 20),
    ("DJI_20260719092424_0044_D", 50),
    # Talk H — code Q&A, leaning in
    ("DJI_20260719095849_0028_D", 5),
    ("DJI_20260719095919_0029_D", 5),
    ("DJI_20260719100427_0031_D", 7),
    # Talk I — Shim by feel
    ("DJI_20260719101206_0036_D", 8),
    # Talk L — AI Mi / Pairoa, laughter peak
    ("DJI_20260719103250_0048_D", 3),
    ("DJI_20260719103600_0049_D", 5),
    ("DJI_20260719103621_0050_D", 5),
    ("DJI_20260719103816_0051_D", 5),
    ("DJI_20260719103816_0051_D", 10),
    ("DJI_20260719103816_0051_D", 15),
    # Talk M — ARIAVA
    ("DJI_20260719110516_0059_D", 5),
    ("DJI_20260719110749_0061_D", 3),
    ("DJI_20260719110926_0062_D", 4),
    ("DJI_20260719111025_0063_D", 2),
    ("DJI_20260719111212_0064_D", 10),
    # Talk N — AI phone app
    ("DJI_20260719113019_0067_D", 3),
    ("DJI_20260719113836_0070_D", 8),
    # Late / closing / audience / exterior
    ("DJI_20260719115203_0073_D", 4),
    ("DJI_20260719120831_0075_D", 4),
    ("DJI_20260719121456_0077_D", 3),
    ("DJI_20260719104335_0052_D", 5),
    ("DJI_20260719104354_0053_D", 3),
    ("DJI_20260719104626_0056_D", 1),
    ("DJI_20260719115456_0074_D", 2),
    ("DJI_20260719115456_0074_D", 6),
    ("DJI_20260719094634_0022_D", 1),
    ("DJI_20260719104548_0055_D", 3),
    ("DJI_20260719105222_0058_D", 2),
    ("DJI_20260719122116_0079_D", 2),
    ("DJI_20260719122153_0080_D", 2),
    # Fillers — room, code, street
    ("DJI_20260719091907_0004_D", 3),
    ("DJI_20260719092253_0008_D", 5),
    ("DJI_20260719092652_0010_D", 10),
    ("DJI_20260719094253_0020_D", 6),
    ("DJI_20260719094321_0021_D", 5),
    ("DJI_20260719094653_0023_D", 5),
    ("DJI_20260719101128_0035_D", 4),
    ("DJI_20260719101711_0039_D", 2),
    ("DJI_20260719101751_0040_D", 3),
    ("DJI_20260719102949_0045_D", 5),
    ("DJI_20260719103139_0046_D", 7),
    ("DJI_20260719103214_0047_D", 2),
    ("DJI_20260719104432_0054_D", 3),
    ("DJI_20260719113657_0068_D", 2),
    ("DJI_20260719113730_0069_D", 5),
]


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args):
        raise RuntimeError("redirect refused, verify the endpoint")


def clip_durations():
    out = {}
    for name in os.listdir(MEDIA_DIR):
        if not name.lower().endswith(".mp4"):
            continue
        path = os.path.join(MEDIA_DIR, name)
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "csv=p=0", path],
            capture_output=True, text=True)
        try:
            out[os.path.splitext(name)[0]] = float(r.stdout.strip())
        except ValueError:
            out[os.path.splitext(name)[0]] = 0.0
    return out


def talk_summary():
    """Compact one-line-per-talk summary from talks.jsonl."""
    lines = ["## PER-TALK TABLE (17 talks, read from the frames; topics marked unclear are NOT guessed)"]
    with open(TALKS, encoding="utf-8") as f:
        for line in f:
            t = json.loads(line)
            clips = "; ".join(t.get("clips", []))
            lines.append(
                f"Talk {t.get('talk')}: speaker={t.get('speaker')}; "
                f"topic={t.get('topic')}; content={t.get('content')}; "
                f"audience={t.get('audience_size')}; reaction={t.get('reaction')}; "
                f"qa={t.get('qa_interaction')}; relatable={t.get('relatable')}; "
                f"clips={clips}"
            )
    return "\n".join(lines)


def clip_summary():
    """Compact one-line-per-clip shot summary, compressed from shot-list.jsonl."""
    from collections import OrderedDict
    # group frames by clip, compress consecutive same shot_type+description
    by_clip = OrderedDict()
    with open(SHOT_LIST, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            by_clip.setdefault(r["clip"], []).append(r)
    lines = ["## PER-CLIP SHOT SUMMARY (68 clips, 1 fps dense frames; shot types 1-7 per master prompt §13)"]
    for clip, rows in by_clip.items():
        segs = []
        cur = None
        for r in rows:
            key = (r["shot_type"], r["description"])
            if cur and cur[0] == key:
                cur[1] = r["timestamp_sec"]
            else:
                if cur:
                    segs.append(cur)
                cur = [key, r["timestamp_sec"], r["timestamp_sec"]]
        if cur:
            segs.append(cur)
        parts = []
        for (stype, desc), s, e in segs:
            if s == e:
                parts.append(f"[{stype}] t={s}s: {desc}")
            else:
                parts.append(f"[{stype}] t={s}-{e}s: {desc}")
        lines.append(f"{clip}: " + " | ".join(parts))
    return "\n".join(lines)


def old_transcripts():
    with open(OLD_PACK, encoding="utf-8") as f:
        lines = f.read().splitlines()
    # Lines 198-1386 are per-clip transcripts for the original 59 clips.
    return "\n".join(lines[198:1387])


def main():
    with open(MASTER_PROMPT, encoding="utf-8") as f:
        master_prompt = f.read()

    durations = clip_durations()
    print(f"clips with durations: {len(durations)}")

    # Verify selected frames exist and are within clip duration.
    verified = []
    for clip, t in SELECTED:
        frame_name = f"frame-{t + 1:04d}.jpg"
        path = os.path.join(FRAMES_DIR, clip, frame_name)
        dur = durations.get(clip, 0.0)
        if not os.path.exists(path):
            print(f"MISSING frame file: {path}")
            continue
        if t >= dur:
            print(f"SKIP t={t}s beyond duration {dur:.1f}s: {clip}")
            continue
        size = os.path.getsize(path)
        if size > 2_097_152:
            print(f"SKIP oversize frame ({size} bytes): {path}")
            continue
        verified.append((clip, t, frame_name, path, dur, size))
    print(f"selected frames verified: {len(verified)} (requested {len(SELECTED)})")
    total_frame_bytes = sum(v[5] for v in verified)
    print(f"total frame bytes: {total_frame_bytes / 1024 / 1024:.1f} MB")

    batch_note = (
        "\n\n## BATCH NOTE — read this before picking\n\n"
        "This batch is morning-only footage, 07:23 to 12:21 on 2026-07-19. "
        "There is NO guitar, NO piano, NO rain, NO piece written for a "
        "girlfriend, and NO group photo in these clips. Do not invent them. "
        "Pick the best moments from what is actually here: people arriving, "
        "setting up, talks, live demos on screen, questions and answers, "
        "laughter — and the warmest moment is the room laughing together in "
        "clip DJI_20260719103816_0051_D (Talk L, Pairoa). That laughter moment "
        "is the emotional peak of the recap; save the tightest close-up for it "
        "and do not spend it early.\n\n"
        "The transcripts below are unreliable. Whisper hallucinated crowd "
        "noise, so most transcript lines are not real speech. Judge moments "
        "mainly from the keyframes, the per-talk table, and the per-clip shot "
        "summary. Do not trust a specific transcript quote unless the words "
        "clearly match a visible speaker. If a clip has no clear speech, set "
        "transcript_excerpt to an empty string.\n\n"
        "This is a VLOG-style recap, not a montage of hard cuts. Follow master "
        "prompt §14: open on a wide, go tighter, re-establish with a wide "
        "after close-ups, cut to the listener (the room laughing) at the peak, "
        "and land cuts on the music phrase boundaries (19.4 s for Timing). "
        "Order the picks so the day reads front to back: wide open → talks "
        "and demos unfold, each with a room response → laughter peak → "
        "closing wide.\n\n"
        "Output everything in English. Titles, reasons and any narration must "
        "be in English. Do not write Chinese.\n"
    )

    context = (
        master_prompt
        + batch_note
        + "\n\n" + talk_summary()
        + "\n\n" + clip_summary()
        + "\n\n## TRANSCRIPTS (unreliable, see batch note — original 59 clips only)\n\n"
        + old_transcripts()
    )

    content = [{"type": "text", "text": context}]

    for i, (clip, t, frame_name, path, dur, size) in enumerate(verified):
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("ascii")
        content.append({
            "type": "text",
            "text": f"Keyframe {i + 1}/{len(verified)}: clip {clip}.mp4, frame {frame_name}, "
                    f"about {t}s into a {dur:.1f}s clip.",
        })
        content.append({
            "type": "image",
            "source": {"type": "base64", "media_type": "image/jpeg", "data": b64},
        })

    content.append({
        "type": "text",
        "text": (
            "Now pick the moments for a roughly 2-minute vlog-style recap "
            "(target 110 to 130 seconds total). Output ONLY one JSON object per "
            "line, no other text, no code fence, no commentary. Each line uses "
            "this schema:\n"
            '{"node": "morning", "tags": ["demo"], "transcript_excerpt": "", '
            '"keyframes": ["DJI_.../frames/frame-0001.jpg"], '
            '"clip": {"file": "DJI_....MP4", "start": "0:02", "end": "0:09", '
            '"title": "Short English title", "reason": "One sentence in English"}}\n'
            "clip.start and clip.end are timestamps WITHIN that clip file, in "
            "m:ss format. clip.file is the clip filename exactly as shown in "
            "the keyframe labels (with the .MP4 extension). node is always "
            "\"morning\" for this batch. Order the picks in the order they "
            "should appear in the recap: wide opening first, talks and demos "
            "in the middle, the 0051 laughter moment as the peak near the end, "
            "then a closing wide. Aim for 14 to 18 picks."
        ),
    })

    body = {
        "model": MODEL_256K,
        "max_tokens": 32000,
        "messages": [{"role": "user", "content": content}],
    }
    data = json.dumps(body).encode("utf-8")
    print(f"request body: {len(data) / 1024 / 1024:.1f} MB")

    request = urllib.request.Request(BASE_URL, data=data, method="POST")
    request.add_header("Content-Type", "application/json")
    request.add_header("anthropic-version", "2023-06-01")
    request.add_header("User-Agent", "curl/8.5.0")
    add_surrogate_to_request(
        request, "custom.tinker",
        allowed_hosts=["tinker.thinkingmachines.dev"],
    )
    try:
        with urllib.request.build_opener(NoRedirect()).open(request, timeout=900) as response:
            raw = read_json_response(response)
            print(f"HTTP {response.status}")
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:800]}")
        return 1

    with open(OUT_RAW, "w", encoding="utf-8") as f:
        json.dump(raw, f, indent=2, ensure_ascii=False)
    print(f"stop_reason: {raw.get('stop_reason')}")
    usage = raw.get("usage", {})
    print(f"usage: {usage}")

    text = ""
    for block in raw.get("content", []):
        if block.get("type") == "text":
            text += block.get("text", "") + "\n"
    text = re.sub(r"```(?:jsonl?|json)?\s*", "", text)
    text = text.replace("```", "")
    picks = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("{") and line.endswith("}"):
            try:
                picks.append(json.loads(line))
            except json.JSONDecodeError:
                print(f"skip unparsable line: {line[:150]}")
    print(f"picks parsed: {len(picks)}")

    def ts(v):
        if isinstance(v, (int, float)):
            return float(v)
        parts = [float(x) for x in str(v).split(":")]
        t = 0.0
        for x in parts:
            t = t * 60 + x
        return t

    total = 0.0
    media = {}
    for name in os.listdir(MEDIA_DIR):
        if name.lower().endswith(".mp4"):
            media[name] = True
    issues = []
    for p in picks:
        clip = p.get("clip", {})
        total += ts(clip.get("end", 0)) - ts(clip.get("start", 0))
        fn = clip.get("file", "")
        if fn not in media:
            issues.append(f"filename not in media/: {fn}")
    print(f"total picked duration: {total:.1f}s")
    if issues:
        print("ISSUES:")
        for i in issues:
            print("  " + i)
    else:
        print("all pick filenames match real media files")

    with open(OUT_PICKS, "w", encoding="utf-8") as f:
        for p in picks:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    print(f"wrote {OUT_PICKS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
