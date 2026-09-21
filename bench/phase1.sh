#!/bin/sh
# Phase 1 queue for the Xeon: sequential so runs never overlap. Log: results/<host>/phase1.log
cd "$(dirname "$0")/.." || exit 1
PYV=.venv/bin/python
SMALL="smollm2-135m-q8 smollm2-360m-q8 gemma3-270m-q8 lfm2.5-350m-q8 qwen2.5-coder-0.5b-q8 qwen3.5-0.8b-q4_0 llama3.2-1b-q4 qwen2.5-coder-1.5b-q4 qwen3.5-2b-q4 gemma4-e2b-q4 qwen2.5-coder-3b-q4 granite4.1-3b-q4 qwen3.5-4b-q4 gemma4-e4b-q4 qwen3.5-9b-q4"
echo "### small ladder bench $(date -u +%FT%TZ)"
for t in 12 24; do REPS=2 THREADS=$t sh bench/bench_llamacpp.sh $SMALL; done
echo "### clean t=12 rerun of 7B/14B $(date -u +%FT%TZ)"
REPS=2 THREADS=12 sh bench/bench_llamacpp.sh qwen2.5-coder-7b-q4 qwen2.5-coder-14b-q4
echo "### coding task $(date -u +%FT%TZ)"
for m in qwen3.5-0.8b-q8 qwen2.5-coder-0.5b-q8 qwen2.5-coder-1.5b-q4 qwen3.5-2b-q4 qwen2.5-coder-3b-q4 granite4.1-3b-q4 qwen3.5-4b-q4 qwen2.5-coder-7b-q4 qwen3.5-9b-q4 qwen3-coder-30b-a3b-q4; do
  $PYV bench/bench_server.py --task coding --model-id "$m" --threads 24 || echo "coding $m failed"
done
echo "### ids task $(date -u +%FT%TZ)"
for m in gemma3-270m-q8 lfm2.5-350m-q8 qwen3.5-0.8b-q8 llama3.2-1b-q4 qwen3.5-2b-q4 gemma4-e2b-q4 qwen3.5-4b-q4 gemma4-e4b-q4 qwen3.5-9b-q4 qwen3-coder-30b-a3b-q4; do
  $PYV bench/bench_server.py --task ids --model-id "$m" --threads 24 || echo "ids $m failed"
done
echo "### done $(date -u +%FT%TZ)"
$PYV bench/report.py
