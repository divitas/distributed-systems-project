from __future__ import annotations

import json
from pathlib import Path
from statistics import mean, median


def summarize_metric(rows: list[dict], metric_key: str) -> dict:
    latencies = [
        row[metric_key]
        for row in rows
        if row.get(metric_key) is not None
    ]

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


def summarize_latencies(rows: list[dict]) -> dict:
    return summarize_metric(rows, "latency_sec")


def write_jsonl(path: str, rows: list[dict]) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")
