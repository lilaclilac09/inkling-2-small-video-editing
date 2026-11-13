"""SFT for Inkling 2 Small on the Cafe Cursor video-cutting picks.

Pipeline: training data -> summary -> fine-tune (LoRA) -> compare before/after.

Where the data comes from (one JSON object per line in inkling-video-picks.jsonl):
  node               morning / afternoon / evening
  tags               which priority moments this pick covers, e.g. ["guitar", "laughter"]
  transcript_excerpt Whisper transcript of the picked moment, with timestamps
  keyframes          one-line descriptions of the ffmpeg frames around the moment
  clip.start/end     Inkling's pick, corrected by Aileen if needed
  clip.title/reason  Inkling's pick, corrected by Aileen if needed
Each approved pick = one training example. A pick she rejected is NOT in v1.

Usage:
  cd ~/tinker-first-session
  uv run inkling-video-sft.py            # uses inkling-video-picks.jsonl
  INKLING_PICKS_PATH=other.jsonl uv run inkling-video-sft.py

Adapted from the official first-training.py, which already ran on this machine
(loss 0.9471 -> 0.0006, 10 steps, checkpoint first-sft). Same shape, new data:
base model thinkingmachines/Inkling-2-Small, LoRA rank 16, train only on the
answer tokens (prompt weight 0, answer weight 1).

One gotcha (Matt Suiche's note): get_tokenizer() does not exist for Thinking
Machines models. If it fails here, decode through the tinker-cookbook renderer
instead of the tokenizer.
"""

import asyncio
import json
import os
import sys

PICKS_PATH = os.environ.get("INKLING_PICKS_PATH", "inkling-video-picks.jsonl")
BASE_MODEL = "thinkingmachines/Inkling-2-Small"
CHECKPOINT_NAME = "inkling-video-cutting-v1"
RANK = 16
STEPS = 10
LEARNING_RATE = 2e-4

PLAYGROUND_PROMPT = """You are cutting a tech meetup talk into short clips for social media.

Below is the full transcript with timestamps, plus keyframes from the video.

Pick the 3 most shareable moments. Each clip 30-90 seconds. For each clip, give:
- start and end timestamp
- a short title
- one line on why it works standalone

Only pick moments that make sense without the rest of the talk. Prefer moments with a clear takeaway, a live demo, or a surprising point. Prefer moments where a guest is presenting their own work in their own words (a showcase monologue). Prefer moments that include audience response (laughter, applause, someone picking up the thread) or follow-up questions. Do not cut mid-sentence; extend to the nearest sentence boundary if needed. Timestamps must match the transcript.

Transcript:
"""

PRIORITY_MOMENTS = [
    "guitar", "girlfriend", "piano", "showcase monologue",
    "follow-up", "laughter", "rain", "volunteers", "group photo",
]

TEST_PROMPTS = [
    "Transcript excerpt: [14:02:11] someone sits at the piano and plays a short tune. [14:02:40] the room goes quiet, then applauds. Pick the clip.",
    "Transcript excerpt: [10:15:00] a guest stands up and explains the tool she built for her neighbours. [10:17:30] someone in the room asks how it handles rainy days. Pick the clip.",
]


def load_picks(path):
    if not os.path.exists(path):
        return []
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def summarize(rows):
    print(f"Training examples: {len(rows)}")
    nodes = {}
    covered = set()
    total_chars = 0
    for r in rows:
        nodes[r.get("node", "?")] = nodes.get(r.get("node", "?"), 0) + 1
        for t in r.get("tags", []):
            covered.add(t)
        total_chars += len(r.get("transcript_excerpt", "")) + len(json.dumps(r.get("clip", {})))
    print(f"By time node: {nodes}")
    print(f"Priority moments covered: {sorted(covered)}")
    missing = [m for m in PRIORITY_MOMENTS if m not in covered]
    print(f"Priority moments missing: {missing if missing else 'none'}")
    print(f"Rough size: ~{total_chars // 4} tokens")
    if missing:
        print("Note: the model cannot learn a moment type it has never seen. "
              "Add an example for each missing moment before the next run.")
    return missing


def build_example(row):
    prompt = (
        PLAYGROUND_PROMPT
        + row.get("transcript_excerpt", "")
        + "\n\nKeyframes:\n"
        + "\n".join(row.get("keyframes", []))
    )
    answer = json.dumps(row.get("clip", {}), ensure_ascii=False)
    return prompt, answer


async def main():
    rows = load_picks(PICKS_PATH)
    summarize(rows)
    if len(rows) < 3:
        print()
        print("Not enough training data yet (need at least 3 approved picks).")
        print("Data comes from the video: transcript + keyframes + Inkling picks")
        print("plus Aileen's corrections. Write them to")
        print(f"  {PICKS_PATH}")
        print("one JSON object per line, then run again.")
        return

    import tinker

    service_client = tinker.ServiceClient(display_name="inkling-video-cutting")

    training_client = await service_client.create_lora_training_client(
        base_model=BASE_MODEL, rank=RANK
    )

    base_client = await service_client.create_sampling_client(base_model=BASE_MODEL)

    tokenizer = training_client.get_tokenizer()

    examples = [build_example(r) for r in rows]

    def make_datum(prompt, answer):
        messages = [{"role": "user", "content": prompt}, {"role": "assistant", "content": answer}]
        prompt_text = tokenizer.apply_chat_template(
            messages[:1], tokenize=False, add_generation_prompt=True, enable_thinking=False
        )
        full_text = tokenizer.apply_chat_template(messages, tokenize=False, enable_thinking=False)
        prompt_tokens = tokenizer.encode(prompt_text, add_special_tokens=False)
        completion_tokens = tokenizer.encode(
            full_text[len(prompt_text):], add_special_tokens=False
        )
        tokens = prompt_tokens + completion_tokens
        weights = [0.0] * len(prompt_tokens) + [1.0] * len(completion_tokens)
        return tinker.Datum(
            model_input=tinker.ModelInput.from_ints(tokens[:-1]),
            loss_fn_inputs={"target_tokens": tokens[1:], "weights": weights[1:]},
        )

    training_data = [make_datum(p, a) for p, a in examples]

    for step in range(STEPS):
        fwdbwd_future = training_client.forward_backward(training_data, "cross_entropy")
        optim_future = training_client.optim_step(tinker.AdamParams(learning_rate=LEARNING_RATE))
        fwdbwd_result = await fwdbwd_future
        await optim_future
        logprobs = [
            lp for output in fwdbwd_result.loss_fn_outputs for lp in output["logprobs"].tolist()
        ]
        weights = [
            w for datum in training_data for w in datum.loss_fn_inputs["weights"].tolist()
        ]
        loss = -sum(lp * w for lp, w in zip(logprobs, weights)) / sum(weights)
        print(f"Step {step:2d}: loss = {loss:.4f}")

    save_future = training_client.save_weights_for_sampler(name=CHECKPOINT_NAME)
    checkpoint = await save_future
    trained_client = await service_client.create_sampling_client(model_path=checkpoint.path)

    print(f"\nTry it in the Playground: {checkpoint.get_playground_url()}&reasoning_effort=none")

    async def sample(client, prompt):
        prompt_text = tokenizer.apply_chat_template(
            [{"role": "user", "content": prompt}],
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False,
        )
        prompt_tokens = tokenizer.encode(prompt_text, add_special_tokens=False)
        result = await client.sample(
            prompt=tinker.ModelInput.from_ints(prompt_tokens),
            num_samples=1,
            sampling_params=tinker.SamplingParams(max_tokens=512, temperature=0.7),
        )
        return result.sequences[0]

    def decode(sequence):
        return tokenizer.decode(sequence.tokens, skip_special_tokens=True).strip()

    for prompt in TEST_PROMPTS:
        before = await sample(base_client, prompt)
        after = await sample(trained_client, prompt)
        print(f"\nQ: {prompt}")
        print(f"Before: {decode(before)}")
        print(f"After:  {decode(after)}")


if __name__ == "__main__":
    asyncio.run(main())
