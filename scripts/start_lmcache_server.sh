#!/usr/bin/env bash
set -e

source scripts/setup_env.sh

echo "Starting standalone LMCache server for MP mode..."

lmcache server \
  --l1-size-gb 20 \
  --eviction-policy LRU \
  --chunk-size 256