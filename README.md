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
| og128x01 | gemma3-270m-q8 | Q8_0 0.29 GB | 0 | 577.8 (t=24) | 58.4 (t=12) |
| og128x01 | gemma4-e2b-q4 | Q4_K_M 3.09 GB | 0 | 65.0 (t=24) | 15.5 (t=24) |
| og128x01 | gemma4-e4b-q4 | Q4_K_M 4.96 GB | 0 | 31.5 (t=24) | 8.1 (t=24) |
| og128x01 | granite4.1-3b-q4 | Q4_K_M 2.10 GB | 0 | 42.4 (t=24) | 12.8 (t=24) |
| og128x01 | lfm2.5-350m-q8 | Q8_0 0.38 GB | 0 | 379.1 (t=24) | 56.4 (t=12) |
| og128x01 | llama3.2-1b-q4 | Q4_K_M 0.80 GB | 0 | 140.3 (t=24) | 33.2 (t=24) |
| og128x01 | qwen2.5-coder-0.5b-q8 | Q8_0 0.67 GB | 0 | 331.1 (t=24) | 47.4 (t=24) |
| og128x01 | qwen2.5-coder-1.5b-q4 | Q4_K_M 1.11 GB | 0 | 99.5 (t=24) | 26.7 (t=24) |
| og128x01 | qwen2.5-coder-14b-q4 | Q4_K_M 8.98 GB | 0 | 10.5 (t=24) | 3.2 (t=24) |
| og128x01 | qwen2.5-coder-3b-q4 | Q4_K_M 2.10 GB | 0 | 48.3 (t=24) | 14.1 (t=24) |
| og128x01 | qwen2.5-coder-7b-q4 | Q4_K_M 4.68 GB | 0 | 20.9 (t=24) | 6.1 (t=24) |
| og128x01 | qwen3-coder-30b-a3b-q4 | Q4_K_M 17.66 GB | 0 | 41.2 (t=24) | 11.5 (t=24) |
| og128x01 | qwen3.5-0.8b-q4_0 | Q4_0 0.55 GB | 0 | 186.1 (t=24) | 29.7 (t=24) |
| og128x01 | qwen3.5-0.8b-q8 | Q8_0 0.82 GB | 0 | 150.8 (t=24) | 23.1 (t=24) |
| og128x01 | qwen3.5-2b-q4 | Q4_K_M 1.27 GB | 0 | 79.1 (t=24) | 17.6 (t=24) |
| og128x01 | qwen3.5-4b-q4 | Q4_K_M 2.73 GB | 0 | 31.2 (t=24) | 7.9 (t=24) |
| og128x01 | qwen3.5-9b-q4 | Q4_K_M 5.67 GB | 0 | 17.3 (t=24) | 4.8 (t=24) |
| og128x01 | smollm2-135m-q8 | Q8_0 0.14 GB | 0 | 629.5 (t=24) | 98.5 (t=12) |
| og128x01 | smollm2-360m-q8 | Q8_0 0.38 GB | 0 | 278.7 (t=24) | 45.6 (t=12) |

### Task scores

_no task runs yet_
<!-- results:end -->

## Findings and recommendations

_filled in per tier as phases complete; see `docs/tiers/`._
