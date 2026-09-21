# edge-models

What can small-to-medium open models usefully do on hardware nobody would call an AI box?
Old x86 CPUs, pre-ROCm AMD GPUs, Raspberry Pis, iPhones, and the Linux/BSD control planes inside network switches.

Two tasks are measured on every tier: a **simple coding assistant** and **intrusion-detection / log triage** (with classical baselines, because LLMs are usually the wrong tool for that job).

Plan: `~/.claude/plans/scalable-juggling-dijkstra.md`. Hardware on hand: `docs/inventory.md`.

## Layout

| Path | What |
|---|---|
| `models/manifest.yaml` | the model ladder (HF repo, file, quant, tags) |
| `bench/probe.sh` | fingerprint a host -> `results/<host>/probe.json` |
| `bench/fetch_models.sh [id\|tag]` | download models into the HF cache |
| `bench/bench_llamacpp.sh [-t N] [-ngl N] [id\|tag\|file.gguf]` | llama-bench -> `results/<host>/bench-*.json` |
| `bench/bench_server.py` | latency + task quality against a running llama-server |
| `bench/tasks/` | coding and IDS task sets and scorers |
| `bench/report.py` | regenerate the tables below from `results/` |
| `docs/tiers/` | one note per hardware tier |
| `deploy/` | per-platform deployment: systemd units, container/SWIX/IOx packaging |
| `labs/` | virtual switch topologies (cEOS, N9Kv, vJunos) |

Setup on the dev host: `~/.local/bin/uv venv .venv && uv pip install --python .venv/bin/python pyyaml "huggingface_hub[cli]" requests`.
Scripts find `llama-bench` at `$LLAMA_BIN` (default `~/src/llama.cpp/build/bin`) and models under `$HF_HOME`.

## Results

<!-- results:start -->
### Hosts probed

| host | cpu | cores | simd | ram | gpu (driver) | llama.cpp |
|---|---|---|---|---|---|---|
| og128x01 | Intel(R) Xeon(R) CPU E5-2697 v2 @ 2.70GHz | 24 | sse4_2 avx f16c | 125 GB | Advanced Micro Devices, Inc. [AMD/ATI] Tahiti XT [Radeon HD  (radeon) | 6a1a922d2 |

### llama-bench throughput (best over thread counts)

| host | model | quant/size | ngl | prompt tok/s (threads) | gen tok/s (threads) |
|---|---|---|---|---|---|
| og128x01 | qwen2.5-coder-14b-q4 | Medium 8.98 GB | 0 | 10.5 (t=24) | 3.2 (t=24) |
| og128x01 | qwen2.5-coder-7b-q4 | Medium 4.68 GB | 0 | 20.9 (t=24) | 6.1 (t=24) |
| og128x01 | qwen3-coder-30b-a3b-q4 | Medium 17.66 GB | 0 | 41.2 (t=24) | 11.5 (t=24) |
| og128x01 | qwen3.5-0.8b-q8 | Q8_0 0.82 GB | 0 | 150.8 (t=24) | 23.1 (t=24) |

### Task scores

| host | task | model | score | n | median latency s | notes |
|---|---|---|---|---|---|---|
| og128x01 | coding | qwen3.5-0.8b-q8 | 0.0 | 2 | 19.95 | smoke |
| og128x01 | ids | qwen3.5-0.8b-q8 | 0.5 | 6 | 3.994 | smoke |
<!-- results:end -->

## Findings and recommendations

_filled in per tier as phases complete; see `docs/tiers/`._
