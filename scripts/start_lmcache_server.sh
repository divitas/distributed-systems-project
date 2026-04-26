#!/usr/bin/env bash
set -e

source scripts/setup_env.sh

lmcache server \
  --l1-size-gb 20 \
  --eviction-policy LRU \
  --chunk-size 256