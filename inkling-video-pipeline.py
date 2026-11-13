"""One-command automation for the Cafe Cursor video-cutting demo.

Chains the whole pipeline so the video goes in one end and clips come out
the other. The only human steps are the ones that must be human: sending
the video, and approving the picks.

  python3 inkling-video-pipeline.py --video cafe-cursor.mp4

What it does, in order:
  1. Probe the video (ffprobe) and report the total duration.
  2. Extract audio and transcribe it with Whisper (timestamps on).
     Needs the `whisper` CLI; if it is missing the script says how to
     install it and stops. Pass --transcript existing.srt to skip this.
  3. Pull one keyframe every 10 seconds with ffmpeg (fps=1/10),
     downscaled to 1280px so each JPG stays under Tinker's 2 MB asset limit.
  4. Build the Playground pack: the Playground prompt + the full
     transcript + the keyframe list, in inkling-video-playground-pack.txt.
  5. Stop and wait for the picks: paste the pack into the Tinker
     Playground (Inkling-2-Small), save its 3 picks to
     inkling-video-picks.jsonl, then run the script again with --cut.
  6. Cut the clips with inkling-video-cut.py (vintage faded filter).

  python3 inkling-video-pipeline.py --video cafe-cursor.mp4 --cut

--dry-run prints every step without running anything heavy.
--skip-transcript skips step 2 (use with --transcript).
"""

import argparse
import json
import os
import shutil
import subprocess
import sys

PLAYGROUND_PROMPT_PATH = "inkling-demo-master-prompt.txt"
SCAN_PROMPT_PATH = "inkling-video-scan-prompt.txt"
PACK_PATH = "inkling-video-playground-pack.txt"
PICKS_PATH = "inkling-video-picks.jsonl"
CUT_SCRIPT = "inkling-video-cut.py"


def run(cmd, dry_run, capture=False):
    print("  $ " + " ".join(cmd))
    if dry_run:
        return None
    return subprocess.run(cmd, capture_output=capture, text=True, check=False)


def need(tool):
    if shutil.which(tool) is None:
        print(f"Missing tool: {tool}")
        return False
    return True


def probe_duration(video, dry_run):
    if dry_run:
        print("  (dry run: duration probe skipped)")
        return None
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", video],
        capture_output=True, text=True)
    if r.returncode != 0:
        print("ffprobe failed — is this a video file?")
        return None
    seconds = float(r.stdout.strip())
    print(f"Total duration: {seconds:.1f}s ({seconds / 60:.1f} min)")
    return seconds


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--transcript", default=None,
                    help="existing transcript file (srt/txt) — skips Whisper")
    ap.add_argument("--cut", action="store_true",
                    help="cut the clips from the picks file (step 6 only)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not os.path.exists(args.video):
        print(f"Video not found: {args.video}")
        print("Send the Cafe Cursor recording first — the pipeline starts from it.")
        return 1

    if args.cut:
        if not os.path.exists(PICKS_PATH):
            print(f"Picks not found: {PICKS_PATH}")
            print("Paste the Playground pack into Inkling first, save its")
            print("3 picks to this file, then run again with --cut.")
            return 1
        cmd = [sys.executable, CUT_SCRIPT, "--video", args.video,
               "--picks", PICKS_PATH, "--out", "clips"]
        if args.dry_run:
            cmd.append("--dry-run")
        r = run(cmd, dry_run=False)
        return r.returncode if r else 0

    print("Step 1: probe the video")
    if not args.dry_run and not need("ffprobe"):
        return 1
    probe_duration(args.video, args.dry_run)

    print("Step 2: transcript (Whisper)")
    transcript = args.transcript
    if transcript is None and args.dry_run:
        print("  (dry run: would run whisper --model base on the video)")
        transcript = "transcript.srt"
    elif transcript is None:
        if not need("whisper"):
            print("Install it with: pip install openai-whisper")
            print("Or pass --transcript <your .srt/.txt> to skip this step.")
            return 1
        transcript = "transcript.srt"
        run(["whisper", args.video, "--model", "base",
             "--output_format", "srt", "--output_dir", "."], args.dry_run)
        if not args.dry_run:
            # Whisper names its output after the input file (<clip>.srt);
            # rename it to the fixed name the rest of the pipeline expects.
            # (--output_filename is not a real Whisper flag, so the old
            # call failed on every clip.)
            produced = os.path.splitext(os.path.basename(args.video))[0] + ".srt"
            if os.path.exists(produced) and produced != transcript:
                os.replace(produced, transcript)
    else:
        print(f"  using existing transcript: {transcript}")
    if not args.dry_run and not os.path.exists(transcript):
        print(f"Transcript not produced: {transcript}")
        return 1

    print("Step 3: keyframes (one every 10 seconds, 1280px wide)")
    if not args.dry_run and not need("ffmpeg"):
        return 1
    # Downscaled to 1280px + JPEG quality 4: each frame lands around
    # 100-300 KB, safely under Tinker's 2 MB per-asset limit. Full-res
    # 4K frames are over 2 MB each and get rejected on upload.
    if not args.dry_run:
        os.makedirs("frames", exist_ok=True)
    run(["ffmpeg", "-y", "-i", args.video, "-vf", "fps=1/10,scale=1280:-1",
         "-q:v", "4", "frames/frame-%04d.jpg"], args.dry_run)

    print("Step 4: build the Playground pack")
    pack_lines = []
    prompt_path = None
    for candidate in (PLAYGROUND_PROMPT_PATH,
                      "inkling-demo-master-prompt-2.txt"):
        if os.path.exists(candidate):
            prompt_path = candidate
            break
    if prompt_path:
        pack_lines.append(open(prompt_path, encoding="utf-8").read())
    else:
        print(f"  (missing {PLAYGROUND_PROMPT_PATH} — pack will lack the prompt)")
    if not args.dry_run and os.path.exists(transcript):
        pack_lines.append("\n\nTranscript:\n")
        pack_lines.append(open(transcript, encoding="utf-8", errors="replace").read())
    pack_lines.append("\n\nKeyframes: one frame every 10 seconds, in frames/.\n")
    if not args.dry_run:
        with open(PACK_PATH, "w", encoding="utf-8") as f:
            f.write("".join(pack_lines))
        print(f"  wrote {PACK_PATH}")
    else:
        print(f"  (dry run: would write {PACK_PATH})")

    print()
    print("Step 5: waiting on the picks (the human step).")
    print(f"  1. Open the Tinker Playground, model Inkling-2-Small.")
    print(f"  2. Paste {PACK_PATH} and attach the frames.")
    print(f"  3. Save its 3 picks to {PICKS_PATH} (one JSON object per line).")
    print(f"  4. Run again: python3 inkling-video-pipeline.py --video {args.video} --cut")
    return 0


if __name__ == "__main__":
    sys.exit(main())
