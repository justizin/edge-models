#!/bin/sh
# Phase 2b: GPU follow-ups. (1) is the RADV_DEBUG workaround needed on kernel 6.12? (2) MoE with experts on CPU,
# attention on both GPUs (-ncmoe). (3) same for gpt-oss-20b. Runs under `sg render`.
cd "$(dirname "$0")/.." || exit 1
export EXTRA="-ub 256 -fa off"
echo "### 1. long-context WITHOUT RADV_DEBUG $(date -u +%FT%TZ)"
GGML_VK_VISIBLE_DEVICES=0 HOSTTAG=og128x01-d700x1-noworkaround REPS=1 THREADS=4 NGL=99 NP=2048 NG=64 sh bench/bench_llamacpp.sh qwen2.5-coder-3b-q4 || echo "noworkaround FAILED"
export RADV_DEBUG=novm,syncshaders,zerovram
echo "### 2. MoE hybrid: experts on CPU, rest on 2 GPUs $(date -u +%FT%TZ)"
for n in 48 36; do
  HOSTTAG=og128x01-d700x2-ncmoe$n REPS=2 THREADS=24 NGL=99 EXTRA="$EXTRA -sm layer -ncmoe $n" sh bench/bench_llamacpp.sh qwen3-coder-30b-a3b-q4 || echo "ncmoe $n FAILED"
done
echo "### 3. gpt-oss-20b hybrid $(date -u +%FT%TZ)"
HOSTTAG=og128x01-d700x2-ncmoe24 REPS=2 THREADS=24 NGL=99 EXTRA="$EXTRA -sm layer -ncmoe 24" sh bench/bench_llamacpp.sh gpt-oss-20b-mxfp4 || echo "gpt-oss ncmoe FAILED"
echo "### 4. gpt-oss-20b fully on 2 GPUs (12.1 GB into 12 GB, expect spill) $(date -u +%FT%TZ)"
HOSTTAG=og128x01-d700x2 REPS=1 THREADS=4 NGL=99 EXTRA="$EXTRA -sm layer" sh bench/bench_llamacpp.sh gpt-oss-20b-mxfp4 || echo "gpt-oss full FAILED"
echo "### done $(date -u +%FT%TZ)"
.venv/bin/python bench/report.py
