#!/usr/bin/env bash
set -e

source scripts/setup_env.sh

OUTPUT_FILE="results/phase1_${CACHE_BACKEND}.jsonl"

echo "Running Phase 1 benchmark..."
echo "CACHE_BACKEND=$CACHE_BACKEND"
echo "OUTPUT_FILE=$OUTPUT_FILE"

python -m evaluation.run_experiment \
  --rounds 3 \
  --max-tokens 64 \
  --output "$OUTPUT_FILE"