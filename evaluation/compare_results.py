from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


def load_jsonl(path: str) -> list[dict]:
    rows = []
    with Path(path).open() as f:
        for line in f:
            rows.append(json.loads(line))
    return rows


def summarize_by_round(rows: list[dict]) -> dict[int, float]:
    by_round = defaultdict(list)

    for row in rows:
        by_round[row["round_id"]].append(row["latency_sec"])

    return {
        round_id: sum(values) / len(values)
        for round_id, values in sorted(by_round.items())
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline", required=True)
    parser.add_argument("--lmcache", required=True)

    args = parser.parse_args()

    baseline_rows = load_jsonl(args.baseline)
    lmcache_rows = load_jsonl(args.lmcache)

    baseline_summary = summarize_by_round(baseline_rows)
    lmcache_summary = summarize_by_round(lmcache_rows)

    print("\nAverage latency by round")
    print("------------------------")

    rounds = sorted(set(baseline_summary) | set(lmcache_summary))

    for round_id in rounds:
        base = baseline_summary.get(round_id)
        cache = lmcache_summary.get(round_id)

        if base is None or cache is None:
            continue

        speedup = base / cache if cache > 0 else 0

        print(
            f"round={round_id} "
            f"baseline={base:.4f}s "
            f"lmcache={cache:.4f}s "
            f"speedup={speedup:.2f}x"
        )


if __name__ == "__main__":
    main()