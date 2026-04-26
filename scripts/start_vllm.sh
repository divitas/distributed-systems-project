#!/usr/bin/env bash
set -e

source scripts/setup_env.sh

COMMON_ARGS=(
  "$MODEL_NAME"
  --host "$VLLM_HOST"
  --port "$VLLM_PORT"
  --max-model-len "$MAX_MODEL_LEN"
  --gpu-memory-utilization "$GPU_MEMORY_UTILIZATION"
)

if [ "$CACHE_BACKEND" = "none" ]; then
  echo "Starting vLLM without LMCache..."
  vllm serve "${COMMON_ARGS[@]}"

elif [ "$CACHE_BACKEND" = "lmcache_inprocess" ]; then
  echo "Starting vLLM with LMCache in-process connector..."
  vllm serve "${COMMON_ARGS[@]}" \
    --kv-transfer-config \
    '{"kv_connector":"LMCacheConnectorV1", "kv_role":"kv_both"}'

elif [ "$CACHE_BACKEND" = "lmcache_mp" ]; then
  echo "Starting vLLM with LMCache MP connector..."
  echo "Make sure scripts/start_lmcache_server.sh is already running."
  vllm serve "${COMMON_ARGS[@]}" \
    --kv-transfer-config \
    '{"kv_connector":"LMCacheMPConnector", "kv_role":"kv_both"}'

else
  echo "Unknown CACHE_BACKEND: $CACHE_BACKEND"
  echo "Valid options: none, lmcache_inprocess, lmcache_mp"
  exit 1
fi