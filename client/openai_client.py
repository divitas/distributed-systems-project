from __future__ import annotations

import os
import time
from typing import Any

from openai import OpenAI


class VLLMClient:
    def __init__(self) -> None:
        host = os.getenv("VLLM_HOST", "127.0.0.1")
        port = os.getenv("VLLM_PORT", "8000")

        self.model = os.getenv("MODEL_NAME", "meta-llama/Llama-3.1-8B-Instruct")
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

        response = self.client.completions.create(
            model=self.model,
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        end = time.perf_counter()

        text = response.choices[0].text

        return {
            "prompt_chars": len(prompt),
            "output_chars": len(text),
            "latency_sec": end - start,
            "text": text,
        }