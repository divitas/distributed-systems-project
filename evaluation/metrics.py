from __future__ import annotations

import json
from pathlib import Path
from statistics import mean, median


def summarize_latencies(rows: list[dict]) -> dict:
    latencies = [row["latency_sec"] for row in rows]

    if not latencies:
        return {}

    sorted_latencies = sorted(latencies)

    def percentile(p: float) -> float:
        index = int((len(sorted_latencies) - 1) * p)
        return sorted_latencies[index]

    return {
        "count": len(latencies),
        "avg_latency_sec": mean(latencies),
        "median_latency_sec": median(latencies),
        "p95_latency_sec": percentile(0.95),
        "p99_latency_sec": percentile(0.99),
        "min_latency_sec": min(latencies),
        "max_latency_sec": max(latencies),
    }


def write_jsonl(path: str, rows: list[dict]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")