#!/usr/bin/env bash
set -e

source scripts/setup_env.sh

vllm serve "$MODEL_NAME" \
  --host "$VLLM_HOST" \
  --port "$VLLM_PORT" \
  --max-model-len 16384 \
  --gpu-memory-utilization 0.80 \
  --kv-transfer-config \
  '{"kv_connector":"LMCacheMPConnector", "kv_role":"kv_both"}'