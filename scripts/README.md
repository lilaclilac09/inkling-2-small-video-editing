# scripts/

Build scripts for the Cafe Cursor Shanghai recap video (and the reusable
vlog template workflow). All scripts are Python 3, standard library +
Pillow / ffmpeg where noted. Run from the repo root after cloning.

## Layout

- `build_captions_*.py` — build the bilingual `.ass` subtitle files in `scan/`.
- `make_cover_*.py` — build cover images (mood boards, cutouts, sticker borders).
- `inkling-video-recut*.py`, `inkling-video-join.py` — cut and join the video.
- `cutout_one.py`, `test_cutouts.py` — rembg cutout helpers.
- `build_*`, `inkling_picks*.py`, `transcribe_*.py`, `extract_dense*.py`,
  `download_missing_jpgs.py`, `rotate_photos.py`, `update_photo_index.py`,
  `resume_v5_join.py`, `migrate_ripple_to_new_repo.py`, `push_file*.py`,
  `push_to_ripple.py` — pipeline helpers (picks, sheets, transcription,
  photo index, repo push helpers).

## Notes

- Older scripts (v3/v5 era) also exist at the repo top level for
  historical reference; the current builders live here.
- `requirements-log.md` (repo root) is the append-only requirements log.
  Every new requirement gets added with a timestamp before acting on it.
  New entries are written in English directly (the log is English-only).
- Caption text is bilingual (English + Chinese) — that is the subtitle
  data itself. Everything else in this repo is English.
