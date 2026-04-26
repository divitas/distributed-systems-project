#!/usr/bin/env bash
set -e

export HF_TOKEN="${HF_TOKEN:-your_huggingface_token_here}"

export MODEL_NAME="${MODEL_NAME:-meta-llama/Llama-3.1-8B-Instruct}"
export VLLM_HOST="${VLLM_HOST:-127.0.0.1}"
export VLLM_PORT="${VLLM_PORT:-8000}"

export LMCACHE_USE_EXPERIMENTAL=True
export LMCACHE_CONFIG_FILE="${LMCACHE_CONFIG_FILE:-configs/lmcache_cpu.yaml}"

echo "MODEL_NAME=$MODEL_NAME"
echo "VLLM_HOST=$VLLM_HOST"
echo "VLLM_PORT=$VLLM_PORT"
echo "LMCACHE_CONFIG_FILE=$LMCACHE_CONFIG_FILE"