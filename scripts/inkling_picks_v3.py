"""Ask Inkling 2 Small (via Tinker Anthropic API) for the v3 recap picks.

Vlog-style re-cut, v3 direction from the user:
- HOOK first: Talk L laughter (0051) opens the video.
- Opening must be a WIDE / PANORAMIC shot — no close-up heads at the start.
- Fast flashback after the hook, then exterior -> interior (organized by space).
- Full-room wide shot near the front (NOT clip 0052 — see exclusion below).
- EXCLUDE the pink/blonde woman: do not pick from clip 0026 (blonde
  ponytail woman in the foreground) or clip 0052 (blonde woman in a pink
  top in the foreground for the whole clip). Also exclude any other segment
  where a blonde woman in a pink top is prominent.
- MORE women (presenters and audience), MORE exterior/street shots showing
  the whole streetscape, and close-ups of individual people (shot types
  4 person close-up and 5 audience close-up) so everyone gets a moment.
- Overall feel: warm, relaxed, daily-life vlog (like a casual travel vlog),
  not overly polished. Korean-variety warmth for the feel.

Uses the 256K model variant. max_tokens 32000 to avoid truncation.

Usage:
  python3 inkling_picks_v3.py
Output:
  ~/workspace/inkling-recap/scan/inkling-video-picks-v3.jsonl
  ~/workspace/inkling-recap/scan/inkling-picks-v3-raw.json
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
OUT_PICKS = os.path.join(SCAN_DIR, "inkling-video-picks-v3.jsonl")
OUT_RAW = os.path.join(SCAN_DIR, "inkling-picks-v3-raw.json")

# (clip base name without extension, timestamp seconds)
# frame file = frame-{t+1:04d}.jpg
# EXCLUDED: 0026 (blonde ponytail woman) and 0052 (blonde woman in pink top).
SELECTED = [
    # Opening wide / establishing (NO close-up heads at the start)
    ("DJI_20260719095456_0027_D", 5),
    ("DJI_20260719101336_0037_D", 3),
    ("DJI_20260719100747_0032_D", 3),
    ("DJI_20260719101843_0042_D", 3),
    ("DJI_20260719094910_0025_D", 2),
    ("DJI_20260719122153_0080_D", 2),
    ("DJI_20260719122116_0079_D", 2),
    # Setup / arrival
    ("DJI_20260719091607_0001_D", 3),
    ("DJI_20260719091652_0002_D", 3),
    ("DJI_20260719091709_0003_D", 3),
    ("DJI_20260719092043_0007_D", 1),
    ("DJI_20260719092253_0008_D", 5),
    ("DJI_20260719092510_0009_D", 1),
    # Talk A — AI-native tools
    ("DJI_20260719072352_0033_D", 10),
    ("DJI_20260719072707_0034_D", 5),
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
    # Talk E — woman green tee phone app (woman presenter + close-up)
    ("DJI_20260719084815_0042_D", 5),
    ("DJI_20260719084815_0042_D", 15),
    ("DJI_20260719084815_0042_D", 30),
    ("DJI_20260719084815_0042_D", 50),
    # Talk F — woman white sleeveless, agents product (woman presenter)
    ("DJI_20260719091529_0043_D", 5),
    ("DJI_20260719091529_0043_D", 20),
    ("DJI_20260719091529_0043_D", 40),
    # Talk G — live code, smiling
    ("DJI_20260719092424_0044_D", 20),
    ("DJI_20260719092424_0044_D", 50),
    # Talk H — code Q&A, leaning in
    ("DJI_20260719095849_0028_D", 5),
    ("DJI_20260719095919_0029_D", 5),
    ("DJI_20260719100427_0031_D", 7),
    # Talk I — Shim by feel
    ("DJI_20260719101206_0036_D", 8),
    # Talk L — AI Mi / Pairoa, laughter peak (HOOK)
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
    ("DJI_20260719104354_0053_D", 3),
    ("DJI_20260719104626_0056_D", 1),
    ("DJI_20260719115456_0074_D", 2),
    ("DJI_20260719115456_0074_D", 6),
    ("DJI_20260719094634_0022_D", 1),
    ("DJI_20260719104548_0055_D", 3),
    ("DJI_20260719105222_0058_D", 2),
    # Fillers — room, code, street
    ("DJI_20260719091907_0004_D", 3),
    ("DJI_20260719092253_0008_D", 14),
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
    return "\n".join(lines[198:1387])


def main():
    with open(MASTER_PROMPT, encoding="utf-8") as f:
        master_prompt = f.read()

    durations = clip_durations()
    print(f"clips with durations: {len(durations)}")

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
        "\n\n## BATCH NOTE — v3, read this before picking\n\n"
        "This batch is morning-only footage, 07:23 to 12:21 on 2026-07-19. "
        "There is NO guitar, NO piano, NO rain, NO piece written for a "
        "girlfriend, and NO group photo in these clips. Do not invent them.\n\n"
        "## EXCLUSION — the pink/blonde woman (hard rule, do not violate)\n\n"
        "Do NOT pick any segment that prominently shows a blonde woman in a "
        "pink top, or a woman with long blonde hair in a ponytail. "
        "Specifically DO NOT pick from these two clips at all:\n"
        "- DJI_20260719095441_0026_D.MP4 (a blonde woman with a long ponytail "
        "stands in the foreground for the whole clip).\n"
        "- DJI_20260719104335_0052_D.MP4 (a blonde woman in a pink top stands "
        "in the foreground for the whole clip).\n"
        "If any other clip prominently shows a blonde woman in a pink top, "
        "do not pick that segment either. When in doubt, leave it out.\n\n"
        "## V3 STRUCTURE — follow this order\n\n"
        "1. HOOK FIRST: open the video with the Talk L laughter moment, clip "
        "DJI_20260719103816_0051_D (the whole room laughs together, around "
        "t=5-17s). It is the warmest, most relatable moment and the best "
        "hook. Put it FIRST, before any establishing shot.\n"
        "2. OPENING MUST BE WIDE: the very first frames must be a WIDE / "
        "PANORAMIC shot — a storefront ultra-wide or a full-room wide. Do NOT "
        "open on a close-up of people's heads or faces. The opening frame "
        "should show the whole scene (the street, the storefront, the room), "
        "not individual heads filling the frame. (The previous cut opened on "
        "a check-in shot where heads were too big and too close to the "
        "camera; that is exactly what to avoid.) The hook in step 1 is itself "
        "a wide shot of the room laughing, so it satisfies this — but any "
        "shot that follows the hook and opens a new section must also be "
        "wide, not a head close-up.\n"
        "3. FAST FLASHBACK right after the hook: a quick montage of 4-6 shots, "
        "1-2 seconds each, flashing through the day (storefront, setting up, "
        "cups, a screen, the audience) before settling into the main flow.\n"
        "4. FULL-ROOM WIDE near the front: after the flashback, put a wide "
        "shot of the full room (for example clip DJI_20260719072707_0034_D, "
        "or another interior ultra-wide that does NOT show the excluded "
        "woman). This re-establishes the space.\n"
        "5. ORGANIZE BY SPACE: structure the video as a walk through the "
        "space — exterior / street first (storefront, people outside, the "
        "street scene), then move inside (the room, the talks, the audience). "
        "The viewer should feel like they are walking in from the street.\n"
        "6. MORE WOMEN: include more shots featuring women — women presenters "
        "(Talk E, the woman in the green tee and cap presenting a phone app, "
        "clip DJI_20260719084815_0042_D; Talk F, the woman in the white "
        "sleeveless top presenting 'Your agents work', clip "
        "DJI_20260719091529_0043_D) and women in the audience. Prefer a "
        "woman-presenter moment over a similar man-presenter moment when "
        "both are available.\n"
        "7. MORE EXTERIOR: include more outside / street shots that show the "
        "whole streetscape (shot type 1 storefront ultra-wide, and exterior "
        "street frames). The viewer should see the street, the trees, the "
        "neighbourhood, not just the inside of the cafe.\n"
        "8. CLOSE-UPS OF EACH PERSON: give individual people their moment — "
        "prefer person close-ups (shot type 4) and audience close-ups "
        "(shot type 5) for the presenters and for audience reactions, so "
        "faces get screen time instead of only wide room shots. In "
        "particular, use a close-up for the Talk E woman presenter (clip "
        "0042 has close-ups at t=28-47s) and for audience reactions.\n"
        "9. Keep the Q&A moments (clip 0050, the room gestures back; clip "
        "0062, the ARIAVA QR Q&A).\n"
        "10. Close with a wide sign-off at the banner (clip 0079 or 0080).\n\n"
        "## FEEL\n\n"
        "Warm, relaxed, daily-life vlog — like a casual travel vlog, "
        "unhurried, not overly polished. The atmosphere matters more than "
        "the product details. People enjoying themselves, the room, the "
        "street, the light.\n\n"
        "The transcripts below are unreliable. Whisper hallucinated crowd "
        "noise, so most transcript lines are not real speech. Judge moments "
        "mainly from the keyframes, the per-talk table, and the per-clip shot "
        "summary. Do not trust a specific transcript quote unless the words "
        "clearly match a visible speaker. If a clip has no clear speech, set "
        "transcript_excerpt to an empty string.\n\n"
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
            "should appear in the recap: FIRST the 0051 laughter hook, then "
            "the fast flashback (1-2s shots), then exterior/street, then a "
            "full-room wide, then the talks and demos (with women presenters "
            "and close-ups), then Q&A, then a closing wide at the banner. "
            "Aim for 18 to 22 picks. Remember: NO picks from clips 0026 or "
            "0052, NO close-up heads at the very start, and the first pick "
            "must be the 0051 laughter moment."
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
        if "0026_D" in fn or "0052_D" in fn:
            issues.append(f"EXCLUDED clip picked (pink/blonde woman): {fn}")
    print(f"total picked duration: {total:.1f}s")
    if issues:
        print("ISSUES:")
        for i in issues:
            print("  " + i)
    else:
        print("all pick filenames match real media files; no excluded clips")

    with open(OUT_PICKS, "w", encoding="utf-8") as f:
        for p in picks:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    print(f"wrote {OUT_PICKS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
