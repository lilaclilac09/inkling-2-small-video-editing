#!/usr/bin/env python3
"""A simple video editor, as a tool the agent can call.

Inkling on its own cannot cut video — it is a language model, it has
no hands and outputs no video file. What it can do inside an agent
harness (Amp) is call tools. This file is that tool: a minimal MCP
server over stdio (standard library only, no SDK needed) that wraps
the local ffmpeg scripts.

Tools:
  probe_video       — total duration of a video file
  transcribe_video  — Whisper transcript with timestamps (.srt)
  extract_keyframes — one frame every 10 seconds (ffmpeg fps=1/10)
  cut_clips         — one mp4 per pick (inkling-video-cut.py)
  build_recap       — the ~2-minute recap: segments in order, joined,
                      music mixed low if given (inkling-video-recap.py)

Run it from the folder that holds the scripts:
  python3 inkling-video-editor-mcp.py

Amp loads it as an MCP server; the agent then picks moments with
Inkling and cuts them by calling these tools. Playground cannot use
it — Playground is chat-only, no tools — so this only works inside a
harness with tool calling (Amp).
"""

import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def script(name):
    return os.path.join(HERE, name)


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    out = (r.stdout or "") + (r.stderr or "")
    return r.returncode, out.strip()[-2000:]


TOOLS = [
    {"name": "probe_video",
     "description": "Report the total duration of a video file.",
     "inputSchema": {"type": "object",
                     "properties": {"video": {"type": "string",
                                              "description": "path to the video file"}},
                     "required": ["video"]}},
    {"name": "transcribe_video",
     "description": "Transcribe a video's audio with Whisper (timestamps on) into transcript.srt.",
     "inputSchema": {"type": "object",
                     "properties": {"video": {"type": "string"}},
                     "required": ["video"]}},
    {"name": "extract_keyframes",
     "description": "Pull one keyframe every 10 seconds into frames/frame-NNNN.jpg.",
     "inputSchema": {"type": "object",
                     "properties": {"video": {"type": "string"}},
                     "required": ["video"]}},
    {"name": "cut_clips",
     "description": "Cut one mp4 per pick from the picks file into clips/.",
     "inputSchema": {"type": "object",
                     "properties": {"video": {"type": "string"},
                                    "picks": {"type": "string",
                                              "description": "picks jsonl file, one JSON object per line"}},
                     "required": ["video", "picks"]}},
    {"name": "build_recap",
     "description": "Build the ~2-minute recap: cut the picked segments in order, join them, mix the music file low underneath if given.",
     "inputSchema": {"type": "object",
                     "properties": {"video": {"type": "string"},
                                    "picks": {"type": "string"},
                                    "music": {"type": "string",
                                              "description": "optional music file (mp3)"},
                                    "out": {"type": "string",
                                            "description": "output file, default recap.mp4"}},
                     "required": ["video", "picks"]}},
]


def call_tool(name, args):
    video = args.get("video", "")
    if name == "probe_video":
        if not os.path.exists(video):
            return f"Video not found: {video}"
        rc, out = run(["ffprobe", "-v", "error", "-show_entries",
                       "format=duration", "-of",
                       "default=noprint_wrappers=1:nokey=1", video])
        if rc != 0:
            return f"ffprobe failed: {out}"
        seconds = float(out)
        return f"Total duration: {seconds:.1f}s ({seconds / 60:.1f} min)"
    if name == "transcribe_video":
        if not os.path.exists(video):
            return f"Video not found: {video}"
        rc, out = run(["whisper", video, "--model", "base",
                       "--output_format", "srt", "--output_dir", ".",
                       "--output_filename", "transcript"])
        if rc != 0:
            return ("Whisper failed. If it is not installed: pip install openai-whisper. "
                    f"Details: {out}")
        return "Transcript written to transcript.srt"
    if name == "extract_keyframes":
        if not os.path.exists(video):
            return f"Video not found: {video}"
        rc, out = run(["ffmpeg", "-y", "-i", video, "-vf", "fps=1/10",
                       "frames/frame-%04d.jpg"])
        if rc != 0:
            return f"ffmpeg failed: {out}"
        return "Keyframes written to frames/ (one every 10 seconds)"
    if name == "cut_clips":
        picks = args.get("picks", "")
        rc, out = run([sys.executable, script("inkling-video-cut.py"),
                       "--video", video, "--picks", picks, "--out", "clips"])
        return out or f"exit={rc}"
    if name == "build_recap":
        picks = args.get("picks", "")
        cmd = [sys.executable, script("inkling-video-recap.py"),
               "--video", video, "--picks", picks,
               "--out", args.get("out", "recap.mp4")]
        if args.get("music"):
            cmd += ["--music", args["music"]]
        rc, out = run(cmd)
        return out or f"exit={rc}"
    return f"Unknown tool: {name}"


def send(obj):
    sys.stdout.write(json.dumps(obj) + "\n")
    sys.stdout.flush()


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        method = msg.get("method", "")
        mid = msg.get("id")
        if method == "initialize":
            send({"jsonrpc": "2.0", "id": mid, "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "inkling-video-editor",
                               "version": "0.1.0"}}})
        elif method == "tools/list":
            send({"jsonrpc": "2.0", "id": mid,
                  "result": {"tools": TOOLS}})
        elif method == "tools/call":
            params = msg.get("params", {})
            text = call_tool(params.get("name", ""),
                             params.get("arguments", {}))
            send({"jsonrpc": "2.0", "id": mid, "result": {
                "content": [{"type": "text", "text": text}]}})
        elif method == "ping":
            send({"jsonrpc": "2.0", "id": mid, "result": {}})
        elif method.startswith("notifications/"):
            continue
        else:
            if mid is not None:
                send({"jsonrpc": "2.0", "id": mid, "error": {
                    "code": -32601, "message": f"method not found: {method}"}})


if __name__ == "__main__":
    main()
