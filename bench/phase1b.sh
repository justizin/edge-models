#!/bin/sh
# Phase 1 leftovers: quant-format comparison and the MoE trio that downloaded after the main queue.
cd "$(dirname "$0")/.." || exit 1
echo "### quantcmp $(date -u +%FT%TZ)"
REPS=2 THREADS=24 sh bench/bench_llamacpp.sh qwen2.5-coder-7b-q4_0 qwen2.5-coder-7b-q8
echo "### moe $(date -u +%FT%TZ)"
REPS=2 THREADS=24 sh bench/bench_llamacpp.sh gpt-oss-20b-mxfp4 qwen3.5-35b-a3b-q4 qwen3.6-35b-a3b-q4
echo "### moe coding $(date -u +%FT%TZ)"
for m in qwen3.6-35b-a3b-q4 gpt-oss-20b-mxfp4; do .venv/bin/python bench/bench_server.py --task coding --model-id $m --threads 24 || echo "coding $m failed"; done
echo "### done $(date -u +%FT%TZ)"
.venv/bin/python bench/report.py
