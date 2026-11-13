# Is Inkling 2 Small Suitable for Video Frame Work?

**Date:** 2026-11-13
**Question:** Can Inkling 2 Small do video frame extraction and frame/shot classification?
**Short answer:** It cannot extract frames at all — that is ffmpeg's job, and the model
cannot ingest video. It is well suited to the two judgment tasks that sit on top of
extraction: keyframe selection (which frames matter) and shot classification (what
kind of shot is this, what is happening). That is exactly the split this demo uses.

---

## 1. Get the distinction right

Three different jobs get blurred under "video frame work". They are not the same job,
and they do not belong to the same tool.

| Job | What it is | Who does it |
|---|---|---|
| **Frame extraction** | Pulling still images out of a video file at a fixed rate (e.g. 1 fps). Purely mechanical: decode, sample, write files. The answer is fully determined by the rate you choose. | **ffmpeg.** No model involved. |
| **Keyframe selection** | Choosing *which* of those frames matter — the laugh, the demo on screen, the guitar moment — and which can be dropped. A judgment call about relevance, redundancy, and story. | **A vision-language model (VLM).** This is Inkling 2 Small's job here. |
| **Shot classification** | Labelling each frame or segment: shot scale (wide / medium / close-up), what is in frame (person, screen, audience), what is happening (talking, laughing, demoing). Also a judgment call, with a fixed label set. | **A VLM** (or a specialised classifier). Inkling 2 Small can do this; a small dedicated model can also do it, cheaper and faster. |

The common mistake is to ask the model to do extraction. Inkling 2 Small takes
**text and images only** — it cannot take a video file as input at all (see §2).
Feeding it a video is not a matter of prompt engineering; the input modality does
not exist. Extraction must happen before the model is ever involved, and it is the
cheapest, most reliable part of the pipeline: ffmpeg does it deterministically in
seconds.

---

## 2. What Inkling 2 Small actually is

Facts from the model card and Tinker documentation, read 2026-11-13.

**Model:** Inkling 2 Small, Thinking Machines Lab, released 2026-11-05.
Apache 2.0 licence; weights available on Hugging Face (NVFP4 and MXFP8
checkpoints). 48-layer decoder-only transformer, sparse MoE: 594B total
parameters, 17B active per token. Images are encoded by a vision transformer;
image and text inputs are projected into a shared hidden space and processed
jointly by the decoder.

**Input modalities:** text (UTF-8) and images (any pixel-based image, 40–4096 px
per side for best performance). **No audio input. No video input.** Output is
text only. The model card states a context window of up to 1M tokens; on Tinker
it is served at 64K by default and 256K on a separate SKU
(`thinkingmachines/Inkling-2-Small:peft:262144`).

**Tinker type:** "Hybrid + Vision". Note the contrast with the full Inkling
(975B), which is "Hybrid + **Audio** + Vision" — the first-generation Inkling
accepted audio; Inkling 2 Small does not. The audio gap is a real capability
difference between generations, not a configuration issue.

**Relevant vision benchmarks (model card):**

| Benchmark | Inkling 2 Small | What it measures |
|---|---|---|
| PerceptionBench | 64.7% (2nd best in row) | General visual perception |
| MMMU Pro (Standard) | 81.6% | Multimodal reasoning over images |
| ScreenSpot Pro | 83.8% / 92.0% (with Python) | Visual grounding — locating a described element in an image |
| MuirBench | 79.2% | Multi-image reasoning (comparing across images) |
| MathVision | 92.2% | Visual math reasoning |
| AA Intelligence Index | 30.6 | Overall model quality index |

**What is missing from the model card:** there is **no video-understanding
benchmark** (no Video-MME, MVBench, LongVideoBench, or similar). Training data
is stated to include video, but the model is evaluated and served as an
image+text model. So its video ability is *inferred* from still-image
performance, not demonstrated on video. Treat that as an open question, not a
proven strength.

**Cost on Tinker (serverless inference, 256K):** $0.30 input / $0.03 cached /
$1.00 output per 1M tokens. Our demo call (66 keyframes + transcript +
prompt) used 53,527 input tokens and cost about $0.03. Classification at this
scale is effectively free.

**Serving limits that shape the pipeline:** the Tinker API rejects any single
attached asset over 2,097,152 bytes (2 MB) — measured in our own testing
(2026-11-12). Raw video clips can never be attached; only resized stills.
Each image also costs tokens, so the number of frames per call is bounded by
context and cost, not just by the 2 MB cap.

Sources:
- Model card: https://thinkingmachines.ai/model-card/inkling-2-small/
- Tinker models & pricing: https://tinker-docs.thinkingmachines.ai/tinker/models/models_and_pricing/

---

## 3. Papers: what the research says

The research consensus is that a VLM should *not* watch raw video. The
standard architecture is: extract frames mechanically, select a small set of
keyframes, and hand only those to the VLM. Every paper below works that way.
The open research question is *which* frames to select, not whether to select.

1. **CLIP — Radford et al., 2021.** *Learning Transferable Visual Models From
   Natural Language Supervision.* https://arxiv.org/abs/2103.00020
   The foundation: train an image encoder and a text encoder together so that
   natural language can name any visual concept, enabling zero-shot image
   classification with no task-specific labels. This is why a VLM can classify
   a frame into categories it was never explicitly trained on ("wide shot",
   "audience laughing") just from a text description of the category.

2. **SGNet / MovieShots — Rao et al., ECCV 2020.** *A Unified Framework for
   Shot Type Classification Based on Subject Centric Lens.*
   https://arxiv.org/abs/2008.03548
   The reference work on shot-type classification: separates subject from
   background in two streams to classify shot scale (long / full / medium /
   close-up / extreme close-up) and movement (static / motion / push / pull).
   Built the MovieShots dataset (46K shots from 7K movie trailers). Shows that
   shot scale and movement are learnable, structured attributes — not vague
   taste. Our 7-category taxonomy is a coarser, event-specific version of this
   scheme.

3. **ReaSon — Zhou et al., 2025.** *Reinforced Causal Search with Information
   Bottleneck for Video Understanding.*
   https://arxiv.org/abs/2511.12530 — code: https://github.com/robin-hlt/AAAI26-ReaSon
   Keyframe selection framed as an optimisation problem: a keyframe must be
   both predictively sufficient (the VLM can answer from it) and causally
   necessary (removing it changes the answer). A policy network selects frames
   and is trained by reinforcement learning. Best accuracy on NExT-QA (81.4%)
   and EgoSchema (72.2%) with only 8 frames. Matters here because it gives a
   principled definition of "which frames matter" — and shows that 8 well
   chosen frames beat many poorly chosen ones.

4. **KTV — Song et al., 2026.** *Keyframes and Key Tokens Selection for
   Efficient Training-Free Video LLMs.*
   https://arxiv.org/abs/2602.03615 — code: https://github.com/songbaiyang07-star/KTV
   Two-stage, training-free: first cluster frame-level visual features to pick
   a diverse, representative keyframe set (question-agnostic); then prune
   redundant visual tokens inside each selected frame. A 60-minute video
   (10,800 frames) is reduced to 504 visual tokens with 44.8% accuracy on
   MLVU-Test. Matters here because it shows the cheapest effective method is
   clustering for diversity first, then letting the VLM judge — not handing
   the VLM every frame.

5. **EFS — Chen et al., 2026.** *Event-Anchored Frame Selection for Effective
   Long-Video Understanding.* https://arxiv.org/abs/2603.00983
   A hierarchical, event-aware pipeline: split the video into visually
   homogeneous segments (events) using DINO embeddings, pick the most
   query-relevant frame per event as an anchor, then refine globally with
   Maximal Marginal Relevance for coverage, relevance, and diversity.
   Applied to LLaVA-Video-7B it improves accuracy by 4.7–8.8% on VideoMME,
   LongVideoBench, and MLVU. Matters here because our footage is event
   structured (talks, demos, social moments) — selecting one anchor per event
   is a better default than flat uniform sampling.

6. **FORTE — Huang et al., 2026.** *Adaptive Scoring and Exact Keyframe
   Selection for Long-Video Question Answering.*
   https://arxiv.org/abs/2610.00573
   Training-free: score a sparse set of frames for relevance, predict
   relevance for unscored frames with a Gaussian process, then select the
   final set by exactly optimising relevance plus temporal coverage. Highest
   mean accuracy among compared selectors at every scoring budget. Matters
   here because it shows the value of *coverage*: a good keyframe set must
   span the whole video, not cluster on the most exciting 30 seconds — the
   same failure mode our first rough cut had (all mid-shots, no wide opening).

**What the papers agree on:** (a) extract mechanically, select intelligently;
(b) diversity and coverage matter as much as relevance; (c) a handful of good
frames beats many redundant ones; (d) the VLM's job is judgment over a small,
well-chosen set — not watching everything.

---

## 4. GitHub repos: who actually does this

Real, verified repos that use a vision-language model to classify frames, pick
keyframes, or cut video. None of them uses Inkling 2 Small — the model is
8 days old, and no public repo using it for video work was found in search
(2026-11-13). The only Inkling-specific code that exists is the vendor's own
Tinker Cookbook. That absence is expected, not a red flag: the architecture
below is model-agnostic, and Inkling 2 Small slots into the "vision model"
role these repos already define.

| Repo | What it does | Vision model used |
|---|---|---|
| **HotClip** — https://github.com/xixihhhh/hotclip | Free, local, open-source (AGPL-3.0) AI clipper: long videos / livestream VODs → vertical shorts. AI highlight detection **with a stated reason**, 9 evidence channels (transcript, loudness, shot density, motion, facial emotion, vision, live-chat heat, vocal tone, laughter/applause), auto captions, 9:16 reframe. Every cut ships with a virality score + four-dimension review; timestamps are reverse-aligned from the transcript, never guessed. | Local model via Ollama (default qwen3.5:4b); model is swappable. The "vision" evidence channel is one of nine — the design lesson is that vision alone is not trusted; several channels must agree. |
| **learn-video** — https://github.com/9Tech-Solutions/learn-video | Lets an AI coding agent "watch" a video tutorial. An LLM reads the transcript and picks the moments where the screen matters; ffmpeg pulls just those frames; a vision model reads each frame and fuses it with the surrounding narration. Output is a timeline of notes, one per teaching moment. | Gemini Flash-Lite (vision). Closest architectural twin to our pipeline: transcript-first targeting, ffmpeg frame pull, vision-model read, fusion with narration. |
| **Video_editing_for_clippers (CLIPPER)** — https://github.com/Amario1306619051/Video_editing_for_clippers | Makes 9:16 vertical videos from YouTube. Whisper transcription, then a vision-LM auto-box: it samples frames across a time range, asks the vision model for the subject's bounding box on each, and returns a keyframe track. The model returns `[]` (no box) when the subject is absent — no hallucinated detection. | A separate OpenAI-compatible Qwen-VL endpoint. Demonstrates the VLM-as-frame-judge pattern at per-frame granularity, including the honest "absent" case. |
| **KTV** — https://github.com/songbaiyang07-star/KTV | Reference code for the KTV paper (§3.4): clustering-based keyframe selection + key visual token pruning for training-free video understanding with a VLM. | Any pre-trained VLM (evaluated with LLaVA-v1.6). Model-agnostic by design. |
| **ReaSon** — https://github.com/robin-hlt/AAAI26-ReaSon | Reference code for the ReaSon paper (§3.3): reinforced causal search for keyframe selection. | Policy network + any downstream VLM. |
| **Tinker Cookbook** (vendor) — https://github.com/thinkingmachines/tinker-cookbook | Thinking Machines' official repo for Tinker: fine-tuning and sampling with Inkling models, including the `tml-renderers` package. The only public code that touches Inkling 2 Small. It is a fine-tuning cookbook, not a video tool. | Inkling 2 Small / Inkling (via Tinker). |

**Pattern across all of them:** ffmpeg extracts, a transcript (Whisper) targets,
a vision model judges frames, and the cut is assembled mechanically. No repo
asks the vision model to ingest video. No repo trusts a single signal — every
serious one cross-checks vision against transcript timing, audio energy, or a
second channel.

---

## 5. Verdict for our pipeline

### Where Inkling 2 Small is a good fit

- **Keyframe selection / picks with reasons.** Its strengths line up exactly:
  image understanding (PerceptionBench 64.7%, MMMU Pro 81.6%), multi-image
  reasoning (MuirBench 79.2% — it can compare frames against each other),
  visual grounding (ScreenSpot Pro 83.8% — it can locate a described thing in
  a frame), and a 256K context that holds a whole event's keyframes plus
  transcript plus prompt in one call. It returns structured picks with a
  reason per pick, which makes the decision auditable. Our demo call cost
  ~$0.03. This is the right job for it.
- **Shot classification into a fixed taxonomy.** Given a still frame and a
  label set ("storefront ultra-wide", "audience close-up", …), it can assign
  labels, and it can say "uncertain" instead of guessing. This is the same
  zero-shot classification CLIP made possible, at much higher capability.
  The caveat is that its accuracy on *our* taxonomy is unmeasured until we
  spot-check it — the model card has no shot-classification benchmark.
- **Reading screens.** It reads text in images (slides, posters, phone
  screens) and uses that to identify what a talk is about. Our version-B
  picks showed this directly: it picked up product names off screens that a
  transcript-only method would have missed.

### Where it is not a fit

- **Raw frame extraction.** It cannot take video input. Period. ffmpeg does
  this, deterministically, for free.
- **Audio cues.** It has no audio input (unlike first-generation Inkling).
  Laughter, applause, tone of voice, and the "room went quiet" moment are
  invisible to it. In our footage the Whisper transcript was mostly
  hallucinated crowd noise, so the audio channel is weak anyway — but the
  model cannot compensate for that; it can only work with what it is given.
  If audio energy matters, feed it as numbers (e.g. per-segment loudness
  from ffmpeg silencedetect) in the text prompt, not as audio.
- **Fine-grained temporal precision.** It sees still frames, not motion. It
  cannot tell you the exact frame a laugh starts, whether a cut lands on a
  beat, or how a camera move feels. Its time resolution is the frame
  sampling rate (1 fps in our pipeline), and its pick boundaries are
  approximate — in version B, 12 of 16 picks started at 0:00, i.e. it
  defaulted to clip starts rather than finding precise in-points. Treat its
  timestamps as "this clip, roughly here", and let a human or a rule (e.g.
  trim to the first speech island) refine the exact in/out points.
- **Unverified accuracy on our taxonomy.** Nothing in the model card measures
  shot-type classification accuracy. Our accuracy number must come from our
  own spot-check, not from the vendor's benchmarks. Until that check is done,
  every classification should carry a confidence flag.

### What to use instead, for the parts it cannot do

| Gap | Use instead |
|---|---|
| Frame extraction | ffmpeg (`fps=1` or `fps=1/10`, resize to 1280px, `-q:v 4` to stay under the 2 MB asset limit) |
| Transcript | Whisper (faster-whisper `base`); treat its output as noisy — verify against frames, do not trust it alone |
| Audio energy / laughter signal | ffmpeg `silencedetect` loudness per segment, passed as numbers in the prompt |
| Shot-boundary detection | PySceneDetect (deterministic, free) — finds where one shot ends and the next begins, which a still-frame VLM cannot see |
| Exact cut points | Human review, or trim to speech islands from the transcript; do not take the model's timestamps as exact |
| Accuracy measurement | Human spot-check of a random sample of classifications (our LOG.md quality table) — the only honest accuracy number for our taxonomy |

### Bottom line

Inkling 2 Small is suitable for the judgment half of video frame work and
unsuitable for the mechanical half. That is not a limitation to work around;
it is the correct division of labour, and it is the same division the research
literature and every real repo converge on: **ffmpeg extracts, Whisper
transcribes, the VLM judges, ffmpeg cuts.** The model earns its place by doing
in one call what would take a human hours — reading 66 frames, matching them
to a transcript and a story brief, and returning a reasoned, auditable pick
list for ~$0.03. What it cannot do (video input, audio, exact timing) is
covered by cheap deterministic tools, not by a bigger model. The honest next
step is not a better model but a measured accuracy number for its
classifications on our footage, and a fine-tune on approved picks if that
number is not good enough.

---

## Sources

- Inkling 2 Small model card: https://thinkingmachines.ai/model-card/inkling-2-small/
- Tinker models & pricing: https://tinker-docs.thinkingmachines.ai/tinker/models/models_and_pricing/
- CLIP (Radford et al., 2021): https://arxiv.org/abs/2103.00020
- SGNet / MovieShots (Rao et al., ECCV 2020): https://arxiv.org/abs/2008.03548
- ReaSon (Zhou et al., 2025): https://arxiv.org/abs/2511.12530
- KTV (Song et al., 2026): https://arxiv.org/abs/2602.03615
- EFS (Chen et al., 2026): https://arxiv.org/abs/2603.00983
- FORTE (Huang et al., 2026): https://arxiv.org/abs/2610.00573
- HotClip: https://github.com/xixihhhh/hotclip
- learn-video: https://github.com/9Tech-Solutions/learn-video
- CLIPPER: https://github.com/Amario1306619051/Video_editing_for_clippers
- KTV code: https://github.com/songbaiyang07-star/KTV
- ReaSon code: https://github.com/robin-hlt/AAAI26-ReaSon
- Tinker Cookbook: https://github.com/thinkingmachines/tinker-cookbook
