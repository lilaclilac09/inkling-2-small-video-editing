"""Ask Inkling 2 Small (via Tinker Anthropic API) to pick the recap moments.

Sends the master prompt, the transcripts and all 66 keyframes (base64,
each well under the 2 MB per-asset limit), then saves Inkling's picks as
JSONL. Uses the 256K model variant because 66 images plus the transcript
do not fit in 64K.

Usage:
  python3 inkling_picks.py
Output:
  ~/workspace/inkling-recap/scan/inkling-video-picks-inkling.jsonl
  ~/workspace/inkling-recap/scan/inkling-picks-raw.json
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
MODEL_64K = "thinkingmachines/Inkling-2-Small"
SCAN_DIR = os.path.expanduser("~/workspace/inkling-recap/scan")
MEDIA_DIR = os.path.expanduser("~/workspace/inkling-recap/media/DJI_001")
PACK = os.path.join(SCAN_DIR, "inkling-video-playground-pack.txt")
OUT_PICKS = os.path.join(SCAN_DIR, "inkling-video-picks-inkling.jsonl")
OUT_RAW = os.path.join(SCAN_DIR, "inkling-picks-raw.json")


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args):
        raise RuntimeError("redirect refused, verify the endpoint")


def clip_durations():
    """Map clip base name (no extension) to duration in seconds."""
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


def main():
    with open(PACK, encoding="utf-8") as f:
        lines = f.read().splitlines()
    # Lines 1-197 are the master prompt; 198-1386 are per-clip transcripts;
    # 1387+ is the keyframe inventory (we attach the images instead).
    master_prompt = "\n".join(lines[:197])
    transcripts = "\n".join(lines[198:1387])

    # Keyframe paths from the inventory section.
    frames = []
    for line in lines[1387:]:
        m = re.match(r"^- (\S+/frames/frame-\d+\.jpg)$", line.strip())
        if m:
            frames.append(m.group(1))
    print(f"keyframes: {len(frames)}")

    durations = clip_durations()
    print(f"clips with durations: {len(durations)}")

    batch_note = (
        "\n\n## BATCH NOTE — read this before picking\n\n"
        "This batch is morning-only footage, 09:16 to 12:21. There is NO guitar, "
        "NO piano, NO rain, NO piece written for a girlfriend, and NO group photo "
        "in these clips. Do not invent them. Pick the best moments from what is "
        "actually here: people arriving, setting up, talks, live demos on screen, "
        "questions and answers, laughter.\n\n"
        "The transcripts below are unreliable. Whisper hallucinated crowd noise, "
        "so most transcript lines are not real speech. Judge moments mainly from "
        "the keyframes. Do not trust a specific transcript quote unless the words "
        "clearly match a visible speaker. If a clip has no clear speech, set "
        "transcript_excerpt to an empty string.\n\n"
        "Output everything in English. Titles, reasons and any narration must be "
        "in English. Do not write Chinese.\n"
    )

    content = []
    content.append({
        "type": "text",
        "text": master_prompt + batch_note + "\n\n## TRANSCRIPTS (unreliable, see batch note)\n\n" + transcripts,
    })

    # Attach each keyframe with a label so the model can map it to a clip.
    for i, rel in enumerate(frames):
        clip = rel.split("/")[0]
        frame_name = rel.split("/")[-1]
        frame_num = int(re.search(r"frame-(\d+)", frame_name).group(1))
        approx_t = (frame_num - 1) * 10
        dur = durations.get(clip, 0.0)
        path = os.path.join(SCAN_DIR, rel)
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("ascii")
        content.append({
            "type": "text",
            "text": f"Keyframe {i + 1}/{len(frames)}: clip {clip}.mp4, frame {frame_name}, "
                    f"about {approx_t}s into a {dur:.1f}s clip.",
        })
        content.append({
            "type": "image",
            "source": {"type": "base64", "media_type": "image/jpeg", "data": b64},
        })

    content.append({
        "type": "text",
        "text": (
            "Now pick the moments for a roughly 2-minute recap (target 110 to 130 "
            "seconds total). Output ONLY one JSON object per line, no other text, "
            "no code fence, no commentary. Each line uses this schema:\n"
            '{"node": "morning", "tags": ["demo"], "transcript_excerpt": "", '
            '"keyframes": ["DJI_.../frames/frame-0001.jpg"], '
            '"clip": {"file": "DJI_....MP4", "start": "0:02", "end": "0:09", '
            '"title": "Short English title", "reason": "One sentence in English"}}\n'
            "clip.start and clip.end are timestamps WITHIN that clip file. "
            "clip.file is the clip filename exactly as shown in the keyframe labels. "
            "node is always \"morning\" for this batch. Order the picks in the order "
            "they should appear in the recap."
        ),
    })

    body = {
        "model": MODEL_256K,
        "max_tokens": 10000,
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
        with urllib.request.build_opener(NoRedirect()).open(request, timeout=600) as response:
            raw = read_json_response(response)
            print(f"HTTP {response.status}")
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:500]}")
        print("Falling back to the 64K model is not attempted here; inspect the error first.")
        return 1

    with open(OUT_RAW, "w", encoding="utf-8") as f:
        json.dump(raw, f, indent=2, ensure_ascii=False)

    # Extract text blocks and parse JSONL lines.
    text = ""
    for block in raw.get("content", []):
        if block.get("type") == "text":
            text += block.get("text", "") + "\n"
    # Strip code fences if the model wrapped the output.
    text = re.sub(r"```(?:jsonl?|json)?\s*", "", text)
    text = text.replace("```", "")
    picks = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("{") and line.endswith("}"):
            try:
                picks.append(json.loads(line))
            except json.JSONDecodeError:
                print(f"skip unparsable line: {line[:120]}")
    print(f"picks parsed: {len(picks)}")
    total = 0.0
    for p in picks:
        clip = p.get("clip", {})
        def ts(v):
            if isinstance(v, (int, float)):
                return float(v)
            parts = [float(x) for x in str(v).split(":")]
            t = 0.0
            for x in parts:
                t = t * 60 + x
            return t
        total += ts(clip.get("end", 0)) - ts(clip.get("start", 0))
    print(f"total picked duration: {total:.1f}s")
    with open(OUT_PICKS, "w", encoding="utf-8") as f:
        for p in picks:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    print(f"wrote {OUT_PICKS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
