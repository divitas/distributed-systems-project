# LMCache + vLLM Prefix KV-Cache Reuse Experiment

This project studies prefix KV-cache reuse using the official **LMCache + vLLM** integration.

The goal is to move away from the earlier custom HuggingFace-based prototype where KV caches were manually extracted, cloned, stored, and promoted across GPU/CPU/disk tiers. That prototype was useful for understanding the design, but it did not use LMCache directly. This version uses **vLLM** as the inference engine and **LMCache** as the KV-cache layer.

## Project Goal

The main goal is to evaluate how prefix KV-cache reuse affects:

- Time to First Token
- overall request latency
- throughput
- cache reuse behavior
- cache pressure behavior in later phases

Phase 1 focuses on verifying that LMCache works with a single vLLM server and that repeated long-prefix prompts show latency improvement across rounds.

## Background

The earlier version of this project implemented a custom LMCache-inspired system using HuggingFace `transformers`. It manually handled KV-cache extraction, local GPU/CPU/disk tiering, eviction policies, a controller, synthetic workloads, and benchmark collection.

That version was useful for understanding KV-cache reuse and eviction behavior, but it was not using the official LMCache implementation. The current version pivots toward a more faithful setup by using LMCache directly with vLLM.

## Phase 1 Scope

Phase 1 includes:

- one vLLM OpenAI-compatible server
- LMCache enabled in-process through the vLLM connector
- a repeated-prefix document QA workload
- request latency measurement
- round-by-round latency comparison

Phase 1 does not include:

- multiple vLLM workers
- custom routing
- Redis or shared cache backend
- concurrent QPS sweeps
- custom eviction policy implementation
- PD disaggregation
- failure recovery

Those will be added in later phases after the basic LMCache integration is verified.

## Project Structure

```text
lmcache-vllm-eviction/
├── README.md
├── requirements.txt
├── .env.example
│
├── configs/
│   └── lmcache_cpu.yaml
│
├── scripts/
│   ├── setup_env.sh
│   └── start_vllm_inprocess.sh
│
├── workload/
│   ├── __init__.py
│   ├── documents.py
│   └── generate_workload.py
│
├── client/
│   ├── __init__.py
│   └── openai_client.py
│
├── evaluation/
│   ├── __init__.py
│   ├── metrics.py
│   └── run_experiment.py
│
└── results/
    └── .gitkeep
````

## Directory Overview

### `configs/`

Contains LMCache configuration files.

For Phase 1, `lmcache_cpu.yaml` enables CPU-backed local KV-cache storage. Disk and distributed cache backends are disabled in this phase.

### `scripts/`

Contains shell scripts for environment setup and launching services.

* `setup_env.sh` loads environment variables.
* `start_vllm_inprocess.sh` starts vLLM with LMCache enabled in-process.

### `workload/`

Contains the synthetic repeated-prefix workload.

The workload is designed around long documents and multiple questions. The document prefix remains the same across rounds, while the question changes. This allows LMCache to reuse prefix KV-cache chunks.

### `client/`

Contains the OpenAI-compatible client used to send requests to the vLLM server.

Since vLLM exposes an OpenAI-compatible API, the benchmark client can use the official OpenAI Python client with a local vLLM endpoint.

### `evaluation/`

Contains scripts for running the benchmark and summarizing latency metrics.

The main experiment script records per-request latency and compares average latency across workload rounds.

### `results/`

Stores benchmark output files such as JSONL logs.

## Requirements

Recommended environment:

* Python 3.10+
* CUDA-enabled GPU
* Linux or SLURM GPU node
* Hugging Face token if using gated models
* vLLM-compatible model

Recommended models:

```bash
meta-llama/Llama-3.1-8B-Instruct
Qwen/Qwen3-8B
mistralai/Mistral-7B-Instruct-v0.3
```

For initial testing, use a smaller open model if GPU memory is limited.

## Installation

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Environment Setup

Copy the example environment file:

```bash
cp .env.example .env
```

Update `.env` with your model and Hugging Face token if needed.

Example:

```bash
HF_TOKEN=your_huggingface_token_here
MODEL_NAME=meta-llama/Llama-3.1-8B-Instruct
VLLM_HOST=127.0.0.1
VLLM_PORT=8000
LMCACHE_CONFIG_FILE=configs/lmcache_cpu.yaml
LMCACHE_USE_EXPERIMENTAL=True
```

## LMCache Configuration

Phase 1 uses:

```text
configs/lmcache_cpu.yaml
```

This configuration enables local CPU-backed KV-cache storage and disables disk offload.

The purpose is to keep the first experiment simple and verify that LMCache is correctly connected to vLLM.

## Running Phase 1

### Step 1: Start vLLM with LMCache

In the first terminal:

```bash
source .venv/bin/activate
bash scripts/start_vllm_inprocess.sh
```

Wait until vLLM finishes loading the model and starts serving on the configured host and port.

Default endpoint:

```text
http://127.0.0.1:8000
```

You can verify the server is running with:

```bash
curl http://127.0.0.1:8000/v1/models
```

### Step 2: Run the Benchmark

In a second terminal:

```bash
source .venv/bin/activate
python -m evaluation.run_experiment \
  --rounds 3 \
  --max-tokens 64 \
  --output results/phase1_inprocess_cpu.jsonl
```

## Expected Result

The benchmark runs repeated long-prefix requests.

Expected behavior:

```text
Round 0: slower because prefixes are cold
Round 1: faster because prefixes can be reused
Round 2: similar to or faster than Round 1
```

The result file is saved to:

```text
results/phase1_inprocess_cpu.jsonl
```

Each row contains request-level information such as:

* request ID
* round ID
* document ID
* question
* prompt length
* output length
* latency
* timestamp

## How to Check Results

The experiment script prints an overall summary and latency grouped by round.

You can also inspect the result file manually:

```bash
head results/phase1_inprocess_cpu.jsonl
```

A successful Phase 1 run should show lower average latency in later rounds compared to round 0.

## Success Criteria

Phase 1 is successful if:

* vLLM starts without connector errors
* LMCache config loads correctly
* the benchmark sends requests successfully
* the JSONL results file is created
* later rounds show lower average latency than round 0
* the GPU does not run out of memory

## Troubleshooting

### vLLM server is not reachable

Check whether the server is running:

```bash
curl http://127.0.0.1:8000/v1/models
```

If running on a remote node, use SSH port forwarding:

```bash
ssh -L 8000:127.0.0.1:8000 username@cluster-node
```

### CUDA out of memory

Try reducing GPU memory utilization or model length in the vLLM launch script.

Useful changes:

```bash
--gpu-memory-utilization 0.70
--max-model-len 8192
```

You can also switch to a smaller model.

### No latency improvement across rounds

Possible causes:

* prompts are too short
* output generation dominates latency
* repeated prefixes are not identical
* cache budget is too small
* LMCache connector did not initialize correctly

Try lowering generated tokens:

```bash
python -m evaluation.run_experiment \
  --rounds 4 \
  --max-tokens 16 \
  --output results/phase1_short_decode.jsonl
```

This makes prefill cost more visible.

### Hugging Face access error

Log in with:

```bash
huggingface-cli login
```

Or set:

```bash
export HF_TOKEN=your_huggingface_token_here
```

## Next Phases

After Phase 1 works, continue with the following phases.

### Phase 2: LMCache MP Mode

Run LMCache as a standalone server and connect vLLM using the MP connector.

This is useful because later experiments will involve multiple vLLM instances sharing cache state.

### Phase 3: Disk Offload

Enable disk-backed KV-cache storage and test cache pressure.

This phase helps evaluate how latency changes when hot KV chunks stay in memory while colder chunks move to disk.

### Phase 4: Concurrency Benchmark

Add an async benchmark client and run QPS sweeps.

This phase should measure:

* average latency
* p95 latency
* p99 latency
* throughput
* requests per second
* tokens per second

### Phase 5: Multi-vLLM Workers

Run multiple vLLM servers on different ports.

Example:

```text
Worker 1: http://127.0.0.1:8000
Worker 2: http://127.0.0.1:8001
Worker 3: http://127.0.0.1:8002
```

This will prepare the system for distributed cache-aware routing.

### Phase 6: Cache-Aware Routing

Add a router that sends requests with the same prefix to the same worker.

The purpose is to preserve locality and improve cache reuse.

Possible routing strategies:

* round-robin routing
* hash-based routing
* prefix-aware routing
* cache-aware routing

### Phase 7: Policy Experiments

Compare policy-inspired behavior through routing, cache pressure, admission patterns, and workload design.

Possible policy comparisons:

* LRU-style baseline
* LFU-style repeated document access
* semantic-aware grouped workloads
* learned/adaptive routing strategy

At this stage, the project can start reconnecting with the original eviction-policy research question.

## Current Status

Phase 1 is the baseline integration step.

The immediate objective is not to reproduce the full LMCache paper yet. The objective is to verify that:

```text
vLLM + LMCache + repeated-prefix workload = observable prefix reuse benefit
```

Once that is confirmed, the project can move toward multi-worker distributed experiments.

```

One note: the “Background” wording is based on your uploaded project context, where the earlier repo used HuggingFace `transformers`, manually stored KV caches, and had tiered cache/eviction components. :contentReference[oaicite:0]{index=0}
```

Non-LM Cache
export MODEL_NAME=MODEL_NAME
export CACHE_BACKEND=none
export VLLM_HOST=127.0.0.1
export VLLM_PORT=8000
export MAX_MODEL_LEN=8192
export GPU_MEMORY_UTILIZATION=0.75

bash scripts/start_vllm.sh

export MODEL_NAME=MODEL_NAME
export CACHE_BACKEND=none
export VLLM_HOST=127.0.0.1
export VLLM_PORT=8000

bash scripts/run_phase1.sh

LM Cache enabled:

export MODEL_NAME=Qwen/Qwen3-8B
export CACHE_BACKEND=lmcache_inprocess
export LMCACHE_CONFIG_FILE=configs/lmcache_cpu.yaml
export LMCACHE_USE_EXPERIMENTAL=True
export VLLM_HOST=127.0.0.1
export VLLM_PORT=8000
export MAX_MODEL_LEN=8192
export GPU_MEMORY_UTILIZATION=0.75

bash scripts/start_vllm.sh

export MODEL_NAME=Qwen/Qwen3-8B
export CACHE_BACKEND=lmcache_inprocess
export VLLM_HOST=127.0.0.1
export VLLM_PORT=8000

bash scripts/run_phase1.sh

Compare results:

python -m evaluation.compare_results \
  --baseline results/phase1_none.jsonl \
  --lmcache results/phase1_lmcache_inprocess.jsonl