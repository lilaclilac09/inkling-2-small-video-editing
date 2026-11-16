"""Build the v8 rolling credits with a SMOOTH CONTINUOUS scroll.

Replaces the stepped scroll (hold 1.6s + eased scroll 0.6s per block,
which looked choppy like a PPT) with one constant-speed vertical drift:
no holds, no easing steps, no pauses. Same 18 blocks / same text /
same fonts (Noto Sans CJK SC for CN, Liberation Sans for EN) / same
white-on-black style / same TML-logo-only front block.

Motion: linear, 30fps, 40.0s (1200 frames). Starts with the front TML
logo centred, ends with the last block just scrolled off the top.
Scroll range is measured from the strip itself (first block centre to
last non-black row), so the speed is constant and the end is clean.

Outputs (overwrite the v7 credits in place — v8 supersedes v7):
  * credits-preview.mp4 -- the smooth rolling clip (30fps, 40.0s)
  * credits-audio.mp4   -- same video + silent AAC (for the v8 render)
  * credits-strip.png   -- regenerated strip (same content)
  * v8-preview-credits-1/2/3.png -- frames at 25%/50%/75% of the scroll
"""
import os
import subprocess
import numpy as np
from PIL import Image

import build_credits_preview as bcp

W, H = bcp.W, bcp.H
FPS = 30
DUR_S = 40.0
NFRAMES = int(round(DUR_S * FPS))


def last_content_row(strip):
    """Y of the last non-black row in the strip (bottom of last block)."""
    a = np.asarray(strip.convert("L"))
    rows = np.where(a.max(axis=1) > 12)[0]
    return int(rows[-1]) if len(rows) else strip.size[1] - 1


def main():
    logo = bcp.invert_logo()
    front_row = bcp.front_logo(logo)
    strip, centres = bcp.build_strip(logo, front_row)
    strip.save("credits-strip.png")
    print(f"strip: {strip.size}, {len(bcp.BLOCKS)} blocks")

    off_start = centres[0] - H // 2          # front logo centred
    off_end = last_content_row(strip)         # last block just exited
    dist = off_end - off_start
    speed = dist / NFRAMES
    print(f"scroll: off {off_start} -> {off_end} ({dist}px over "
          f"{NFRAMES} frames @ {FPS}fps = {speed:.2f} px/frame, "
          f"{speed * FPS:.1f} px/s, {DUR_S:.1f}s)")

    cmd = ["ffmpeg", "-y", "-v", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
           "credits-preview.mp4"]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    shots = {NFRAMES // 4: "v8-preview-credits-1.png",
             NFRAMES // 2: "v8-preview-credits-2.png",
             (3 * NFRAMES) // 4: "v8-preview-credits-3.png"}
    for fi in range(NFRAMES):
        off = int(round(off_start + dist * fi / (NFRAMES - 1)))
        off = max(0, min(off, strip.size[1] - H))
        frame = strip.crop((0, off, W, off + H))
        proc.stdin.write(frame.tobytes())
        if fi in shots:
            frame.save(shots[fi])
            print(f"  screenshot frame {fi} (off {off}): {shots[fi]}")
    proc.stdin.close()
    proc.wait()
    assert proc.returncode == 0, "ffmpeg failed"
    print("wrote credits-preview.mp4 (smooth, 30fps, 40.0s)")

    # credits-audio.mp4: same video + silent AAC (what the render consumes).
    cmd = ["ffmpeg", "-y", "-v", "error", "-i", "credits-preview.mp4",
           "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
           "-map", "0:v", "-map", "1:a", "-t", str(DUR_S),
           "-c:v", "copy", "-c:a", "aac", "credits-audio.mp4"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    assert r.returncode == 0, f"credits-audio failed: {r.stderr[-500:]}"
    print("wrote credits-audio.mp4 (video + silent AAC, 40.0s)")


if __name__ == "__main__":
    main()
