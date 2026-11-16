"""Extract 1fps frames (1280px wide, q4) from every DJI clip."""
import glob, os, subprocess, sys
media = os.path.expanduser('~/workspace/inkling-recap/media/DJI_001')
out_root = os.path.expanduser('~/workspace/inkling-recap/frames-dense')
os.makedirs(out_root, exist_ok=True)
clips = sorted(glob.glob(os.path.join(media, '*.MP4')))
total = 0
for clip in clips:
    base = os.path.splitext(os.path.basename(clip))[0]
    out_dir = os.path.join(out_root, base)
    os.makedirs(out_dir, exist_ok=True)
    # skip if already extracted
    existing = glob.glob(os.path.join(out_dir, 'frame-*.jpg'))
    if existing:
        total += len(existing)
        continue
    r = subprocess.run(['ffmpeg','-y','-v','error','-i',clip,
        '-vf','fps=1,scale=1280:-2','-q:v','4',
        os.path.join(out_dir,'frame-%04d.jpg')],
        capture_output=True, text=True)
    if r.returncode != 0:
        print(f"FAIL {base}: {r.stderr[-200:]}", flush=True)
        continue
    n = len(glob.glob(os.path.join(out_dir, 'frame-*.jpg')))
    total += n
    print(f"{base}: {n} frames", flush=True)
print(f"TOTAL frames: {total}")
