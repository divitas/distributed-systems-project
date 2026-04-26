from __future__ import annotations

import argparse
import time

from tqdm import tqdm

from client.openai_client import VLLMClient
from evaluation.metrics import summarize_latencies, write_jsonl
from workload.generate_workload import generate_reuse_workload


def run(rounds: int, max_tokens: int, output_path: str) -> None:
    client = VLLMClient()
    workload = generate_reuse_workload(rounds=rounds)

    rows: list[dict] = []

    for request in tqdm(workload, desc="Running workload"):
        result = client.complete(
            prompt=request.prompt,
            max_tokens=max_tokens,
            temperature=0.0,
        )

        rows.append(
            {
                "request_id": request.request_id,
                "round_id": request.round_id,
                "document_id": request.document_id,
                "question": request.question,
                "prompt_chars": result["prompt_chars"],
                "output_chars": result["output_chars"],
                "latency_sec": result["latency_sec"],
                "timestamp": time.time(),
            }
        )

    write_jsonl(output_path, rows)

    print("\nSummary:")
    print(summarize_latencies(rows))

    print("\nAverage latency by round:")
    for round_id in sorted(set(row["round_id"] for row in rows)):
        round_rows = [row for row in rows if row["round_id"] == round_id]
        print(f"round={round_id}", summarize_latencies(round_rows))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument("--max-tokens", type=int, default=64)
    parser.add_argument("--output", type=str, default="results/run.jsonl")

    args = parser.parse_args()

    run(
        rounds=args.rounds,
        max_tokens=args.max_tokens,
        output_path=args.output,
    )

"""
python -m evaluation.run_experiment \
  --rounds 3 \
  --max-tokens 64 \
  --output results/inprocess_cpu.jsonl
"""