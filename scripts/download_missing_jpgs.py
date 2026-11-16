#!/usr/bin/env python3
"""Download the missing JPGs from the Drive folder by file ID.
Skips files that already exist with non-zero size. Retries failures.
Usage: python3 download_missing_jpgs.py
"""
import json, os, subprocess, sys, time

ROOT = os.path.dirname(os.path.abspath(__file__))
MEDIA = os.path.join(ROOT, "media", "DJI_001")
GDOWN = os.path.join(ROOT, "venv", "bin", "gdown")
LOG = os.path.join(ROOT, "download-jpgs.log")

with open(os.path.join(ROOT, "missing-jpgs.json")) as f:
    missing = json.load(f)

def log(msg):
    line = f"{time.strftime('%H:%M:%S')} {msg}"
    print(line, flush=True)
    with open(LOG, "a") as lf:
        lf.write(line + "\n")

done = 0
failed = []
for i, (name, fid) in enumerate(missing, 1):
    dest = os.path.join(MEDIA, name)
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        done += 1
        continue
    ok = False
    for attempt in range(3):
        r = subprocess.run(
            [GDOWN, fid, "-O", dest],
            capture_output=True, text=True, timeout=180)
        if os.path.exists(dest) and os.path.getsize(dest) > 10000:
            ok = True
            break
        time.sleep(3)
    if ok:
        done += 1
    else:
        failed.append(name)
    if i % 25 == 0:
        log(f"progress: {i}/{len(missing)} attempted, {done} have file, {len(failed)} failed")

log(f"FINISHED: {done}/{len(missing)} have file, failed={failed}")
