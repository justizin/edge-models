#!/bin/sh
# Phase 2: FirePro D700 (Tahiti, RADV) ladder. Runs under `sg render`. Waits for phase1b to finish first.
cd "$(dirname "$0")/.." || exit 1
while pgrep -f "bench/phase1b.sh" >/dev/null; do sleep 30; done
export RADV_DEBUG=novm,syncshaders,zerovram
export EXTRA="-ub 256 -fa off"
ONE="smollm2-360m-q8 gemma3-270m-q8 qwen3.5-0.8b-q4_0 qwen3.5-0.8b-q8 llama3.2-1b-q4 qwen2.5-coder-1.5b-q4 qwen3.5-2b-q4 gemma4-e2b-q4 qwen2.5-coder-3b-q4 granite4.1-3b-q4 qwen3.5-4b-q4 gemma4-e4b-q4 qwen2.5-coder-7b-q4 qwen2.5-coder-7b-q4_0 qwen3.5-9b-q4"
echo "### single card (device 0) $(date -u +%FT%TZ)"
GGML_VK_VISIBLE_DEVICES=0 HOSTTAG=og128x01-d700x1 REPS=2 THREADS=4 NGL=99 sh bench/bench_llamacpp.sh $ONE
echo "### dual card, layer split $(date -u +%FT%TZ)"
HOSTTAG=og128x01-d700x2 REPS=2 THREADS=4 NGL=99 EXTRA="$EXTRA -sm layer" sh bench/bench_llamacpp.sh qwen2.5-coder-7b-q4 qwen2.5-coder-7b-q4_0 qwen2.5-coder-7b-q8 qwen3.5-9b-q4 qwen2.5-coder-14b-q4
echo "### long-context probe for the RADV DeviceLost bug $(date -u +%FT%TZ)"
GGML_VK_VISIBLE_DEVICES=0 HOSTTAG=og128x01-d700x1 REPS=1 THREADS=4 NGL=99 NP=2048 NG=64 sh bench/bench_llamacpp.sh qwen2.5-coder-3b-q4
echo "### coding task on GPU $(date -u +%FT%TZ)"
GGML_VK_VISIBLE_DEVICES=0 HOSTTAG=og128x01-d700x1 .venv/bin/python bench/bench_server.py --task coding --model-id qwen2.5-coder-7b-q4_0 --threads 4 --ngl 99 --server-args "-ub 256 -fa off" --notes "single D700" || echo "coding gpu 7b failed"
HOSTTAG=og128x01-d700x2 .venv/bin/python bench/bench_server.py --task coding --model-id qwen2.5-coder-14b-q4 --threads 4 --ngl 99 --server-args "-ub 256 -fa off -sm layer" --notes "dual D700" || echo "coding gpu 14b failed"
echo "### ids task on GPU $(date -u +%FT%TZ)"
GGML_VK_VISIBLE_DEVICES=0 HOSTTAG=og128x01-d700x1 .venv/bin/python bench/bench_server.py --task ids --model-id qwen3.5-4b-q4 --threads 4 --ngl 99 --server-args "-ub 256 -fa off" --notes "single D700" || echo "ids gpu 4b failed"
echo "### done $(date -u +%FT%TZ)"
.venv/bin/python bench/report.py
