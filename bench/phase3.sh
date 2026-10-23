#!/bin/sh
# Phase 3 (2026-10-23): coding set v2 on every model that scored >= 0.86 on v1, plus the 1.5B as a floor.
# GPU rows first (the GPU coder service takes card 0 afterwards), then the CPU ladder at 24 threads.
# Run detached: setsid sh bench/phase3.sh > results/og128x01/phase3.log 2>&1 < /dev/null &
cd "$(dirname "$0")/.." || exit 1
PY=.venv/bin/python
NOTE="llama.cpp $(git -C "${LLAMA_SRC:-$HOME/src/llama.cpp}" rev-parse --short HEAD)"
echo "### coding-v2 GPU single card $(date -u +%FT%TZ)"
for m in granite4.1-3b-q4_0 qwen2.5-coder-7b-q4_0; do
  GGML_VK_VISIBLE_DEVICES=0 HOSTTAG=og128x01-d700x1 $PY bench/bench_server.py --task coding-v2 --model-id $m --threads 4 --ngl 99 --server-args "-ub 256 -fa off" --notes "single D700; $NOTE" || echo "$m FAILED"
done
echo "### coding-v2 GPU both cards $(date -u +%FT%TZ)"
for m in qwen2.5-coder-14b-q4_0 gpt-oss-20b-mxfp4; do
  HOSTTAG=og128x01-d700x2 $PY bench/bench_server.py --task coding-v2 --model-id $m --threads 4 --ngl 99 --server-args "-ub 256 -fa off -sm layer" --notes "dual D700; $NOTE" || echo "$m FAILED"
done
echo "### coding-v2 CPU 24 threads $(date -u +%FT%TZ)"
for m in qwen2.5-coder-1.5b-q4 qwen2.5-coder-3b-q4 granite4.1-3b-q4 qwen3.5-4b-q4 qwen2.5-coder-7b-q4 qwen3.5-9b-q4 qwen3-coder-30b-a3b-q4 qwen3.6-35b-a3b-q4; do
  HOSTTAG=og128x01 $PY bench/bench_server.py --task coding-v2 --model-id $m --threads 24 --notes "$NOTE" || echo "$m FAILED"
done
echo "### done $(date -u +%FT%TZ)"
$PY bench/report.py
