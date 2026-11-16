"""Transcribe the v5 talk clips that lack transcripts (faster-whisper base)."""
import os, sys
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

CLIPS = [
    "DJI_20260719101632_0047_D",  # Talk S Carl Yang
    "DJI_20260719103001_0048_D",  # Talk S Carl Yang
    "DJI_20260719072352_0033_D",  # Talk A
    "DJI_20260719084244_0041_D",  # Talk R
    "DJI_20260719091529_0043_D",  # Talk F
    "DJI_20260719092424_0044_D",  # Talk G
    "DJI_20260719103442_0049_D",  # Talk T
]

from faster_whisper import WhisperModel
print("Loading faster-whisper base (cpu, int8)...", flush=True)
model = WhisperModel("base", device="cpu", compute_type="int8")
print("Model ready.", flush=True)
for clip in CLIPS:
    video = os.path.join("media/DJI_001", clip + ".MP4")
    out_dir = os.path.join("scan", clip)
    os.makedirs(out_dir, exist_ok=True)
    out_srt = os.path.join(out_dir, "transcript.srt")
    if os.path.exists(out_srt) and os.path.getsize(out_srt) > 0:
        print(f"  {clip}: already done, skip", flush=True)
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
        print(f"  {clip}: {info.duration:.1f}s lang={info.language} segs={len(lines)//4}", flush=True)
    except Exception as e:
        print(f"  {clip}: FAILED {e}", flush=True)
print("transcribe_talks_v5 done")
