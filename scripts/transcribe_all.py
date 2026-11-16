#!/usr/bin/env python3
"""Batch-transcribe all clips in a media dir with faster-whisper.

Loads the model ONCE, then transcribes every MP4 that does not already
have a transcript.srt in its scan folder. Writes SRT files the pipeline
can consume with --transcript.

Usage:
    transcribe_all.py <media_dir> <scan_dir> [--model base]
"""
import argparse
import os
import sys

# PyAV 19 removed the metadata_errors kwarg that faster-whisper 1.2.1
# still passes to av.open(); strip it so decode works.
import av
_av_open = av.open


def _patched_open(*args, **kwargs):
    kwargs.pop("metadata_errors", None)
    return _av_open(*args, **kwargs)


av.open = _patched_open


def srt_time(seconds):
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("media_dir")
    ap.add_argument("scan_dir")
    ap.add_argument("--model", default="base")
    args = ap.parse_args()

    from faster_whisper import WhisperModel
    print(f"Loading faster-whisper model {args.model} (cpu, int8)...", flush=True)
    model = WhisperModel(args.model, device="cpu", compute_type="int8")
    print("Model ready.", flush=True)

    videos = []
    for root, _dirs, files in os.walk(args.media_dir):
        for f in sorted(files):
            if f.lower().endswith(".mp4"):
                videos.append(os.path.join(root, f))
    print(f"{len(videos)} clips found.", flush=True)
    done, skipped, failed = 0, 0, 0
    for video in videos:
        fname = os.path.basename(video)
        clip = os.path.splitext(fname)[0]
        out_dir = os.path.join(args.scan_dir, clip)
        os.makedirs(out_dir, exist_ok=True)
        out_srt = os.path.join(out_dir, "transcript.srt")
        if os.path.exists(out_srt) and os.path.getsize(out_srt) > 0:
            skipped += 1
            continue
        try:
            segments, info = model.transcribe(video, beam_size=5)
            lines = []
            for i, seg in enumerate(segments, 1):
                lines.append(str(i))
                lines.append(f"{srt_time(seg.start)} --> {srt_time(seg.end)}")
                lines.append(seg.text.strip())
                lines.append("")
            with open(out_srt, "w", encoding="utf-8") as fh:
                fh.write("\n".join(lines))
            lang = info.language or "?"
            print(f"  {fname}: {info.duration:.1f}s lang={lang} segs={len(lines) // 4}", flush=True)
            done += 1
        except Exception as e:
            print(f"  {fname}: FAILED {e}", flush=True)
            failed += 1
    print(f"transcribe done: {done} new, {skipped} skipped, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
