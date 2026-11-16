"""Extract 1fps frames in parallel (4 workers). Skips already-extracted clips."""
import glob, os, subprocess
from concurrent.futures import ThreadPoolExecutor
media = os.path.expanduser('~/workspace/inkling-recap/media/DJI_001')
out_root = os.path.expanduser('~/workspace/inkling-recap/frames-dense')
os.makedirs(out_root, exist_ok=True)
clips = sorted(glob.glob(os.path.join(media, '*.MP4')))
def extract(clip):
    base = os.path.splitext(os.path.basename(clip))[0]
    out_dir = os.path.join(out_root, base)
    os.makedirs(out_dir, exist_ok=True)
    if glob.glob(os.path.join(out_dir, 'frame-*.jpg')):
        return base, len(glob.glob(os.path.join(out_dir, 'frame-*.jpg'))), 'skip'
    r = subprocess.run(['ffmpeg','-y','-v','error','-i',clip,
        '-vf','fps=1,scale=1280:-2','-q:v','4',
        os.path.join(out_dir,'frame-%04d.jpg')],
        capture_output=True, text=True)
    if r.returncode != 0:
        return base, 0, f"FAIL: {r.stderr[-150:]}"
    n = len(glob.glob(os.path.join(out_dir, 'frame-*.jpg')))
    return base, n, 'ok'
total = 0
with ThreadPoolExecutor(max_workers=4) as ex:
    for base, n, status in ex.map(extract, clips):
        total += n
        print(f"{base}: {n} frames [{status}]", flush=True)
print(f"TOTAL frames: {total}")
