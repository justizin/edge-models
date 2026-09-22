#!/bin/sh
# Phase 2c: Q4_0 variants on the D700s, and coding runs for the models that only became usable on GPU.
cd "$(dirname "$0")/.." || exit 1
while pgrep -f "bench/fetch_models.sh" >/dev/null; do sleep 30; done
export EXTRA="-ub 256 -fa off"
echo "### Q4_0 single card $(date -u +%FT%TZ)"
GGML_VK_VISIBLE_DEVICES=0 HOSTTAG=og128x01-d700x1 REPS=2 THREADS=4 NGL=99 sh bench/bench_llamacpp.sh qwen2.5-coder-3b-q4_0 granite4.1-3b-q4_0 gemma4-e4b-q4_0
echo "### Q4_0 dual card $(date -u +%FT%TZ)"
HOSTTAG=og128x01-d700x2 REPS=2 THREADS=4 NGL=99 EXTRA="$EXTRA -sm layer" sh bench/bench_llamacpp.sh qwen2.5-coder-14b-q4_0
echo "### coding on GPU: gpt-oss-20b (2 cards), 14B Q4_0 (2 cards), Granite Q4_0 (1 card) $(date -u +%FT%TZ)"
HOSTTAG=og128x01-d700x2 .venv/bin/python bench/bench_server.py --task coding --model-id gpt-oss-20b-mxfp4 --threads 4 --ngl 99 --server-args "-ub 256 -fa off -sm layer" --notes "dual D700" || echo "gpt-oss coding FAILED"
HOSTTAG=og128x01-d700x2 .venv/bin/python bench/bench_server.py --task coding --model-id qwen2.5-coder-14b-q4_0 --threads 4 --ngl 99 --server-args "-ub 256 -fa off -sm layer" --notes "dual D700" || echo "14b q4_0 coding FAILED"
GGML_VK_VISIBLE_DEVICES=0 HOSTTAG=og128x01-d700x1 .venv/bin/python bench/bench_server.py --task coding --model-id granite4.1-3b-q4_0 --threads 4 --ngl 99 --server-args "-ub 256 -fa off" --notes "single D700" || echo "granite q4_0 coding FAILED"
echo "### done $(date -u +%FT%TZ)"
.venv/bin/python bench/report.py
