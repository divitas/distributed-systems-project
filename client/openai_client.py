from __future__ import annotations

import os
import time
from statistics import mean
from typing import Any

from openai import OpenAI
from dotenv import load_dotenv


DEFAULT_MODEL = "Qwen/Qwen3-8B"


class VLLMClient:
    def __init__(self) -> None:
        load_dotenv()

        host = os.getenv("VLLM_HOST", "127.0.0.1")
        port = os.getenv("VLLM_PORT", "8000")

        self.model = os.getenv("MODEL_NAME", DEFAULT_MODEL)
        self.client = OpenAI(
            base_url=f"http://{host}:{port}/v1",
            api_key="EMPTY",
        )

    def complete(
        self,
        prompt: str,
        max_tokens: int = 64,
        temperature: float = 0.0,
    ) -> dict[str, Any]:
        start = time.perf_counter()

        response_stream = self.client.completions.create(
            model=self.model,
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=True,
        )

        chunks: list[str] = []
        inter_token_latencies: list[float] = []
        first_token_at: float | None = None
        last_token_at: float | None = None

        for chunk in response_stream:
            if not chunk.choices:
                continue

            text_delta = chunk.choices[0].text or ""
            if not text_delta:
                continue

            now = time.perf_counter()
            if first_token_at is None:
                first_token_at = now
            elif last_token_at is not None:
                inter_token_latencies.append(now - last_token_at)

            last_token_at = now
            chunks.append(text_delta)

        end = time.perf_counter()

        text = "".join(chunks)
        ttft_sec = first_token_at - start if first_token_at is not None else None
        avg_itl_sec = mean(inter_token_latencies) if inter_token_latencies else None

        return {
            "prompt_chars": len(prompt),
            "output_chars": len(text),
            "output_chunks": len(chunks),
            "latency_sec": end - start,
            "ttft_sec": ttft_sec,
            "avg_itl_sec": avg_itl_sec,
            "text": text,
        }
