# edge-models

What can small-to-medium open models usefully do on hardware nobody would call an AI box?
Old x86 CPUs, pre-ROCm AMD GPUs, Raspberry Pis, iPhones, and the Linux/BSD control planes inside network switches.

Two tasks are measured on every tier: a **coding assistant** (v1: boilerplate functions; v2: component-sized problems that separate the 3B / 7B / MoE models) and **intrusion-detection / log triage** (with classical baselines, because LLMs are usually the wrong tool for that job).

Roadmap and open work: `docs/roadmap.md` (tracked as [issues](https://github.com/justizin/edge-models/issues)). Hardware on hand: `docs/inventory.md`.

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
| `learn/` | neural-network lessons, numpy and PyTorch side by side, leading to the IDS / adversarial exercises (`learn/README.md`) |

Setup on the dev host: `~/.local/bin/uv venv .venv && uv pip install --python .venv/bin/python pyyaml "huggingface_hub[cli]" requests`.
For the `learn/` lessons add: `uv pip install --python .venv/bin/python numpy scikit-learn matplotlib && uv pip install --python .venv/bin/python torch --index-url https://download.pytorch.org/whl/cpu`.
Scripts find `llama-bench` at `$LLAMA_BIN` (default `~/src/llama.cpp/build/bin`) and models under `$HF_HOME`.

## Results

<!-- results:start -->
### Hosts probed

| host | cpu | cores | simd | ram | gpu (driver) | llama.cpp |
|---|---|---|---|---|---|---|
| og128x01 | Intel(R) Xeon(R) CPU E5-2697 v2 @ 2.70GHz | 24 | sse4_2 avx f16c | 125 GB | Advanced Micro Devices, Inc. [AMD/ATI] Tahiti XT [Radeon HD  (amdgpu) | 6a1a922d2 |

### llama-bench throughput (best over thread counts)

| host | model | quant/size | ngl | prompt tok/s (threads) | gen tok/s (threads) |
|---|---|---|---|---|---|
| og128x01 | gemma3-270m-q8 | Q8_0 0.29 GB | 0 | 577.8 (t=24) | 58.4 (t=12) |
| og128x01 | gemma4-e2b-q4 | Q4_K_M 3.09 GB | 0 | 65.0 (t=24) | 15.5 (t=24) |
| og128x01 | gemma4-e4b-q4 | Q4_K_M 4.96 GB | 0 | 31.5 (t=24) | 8.1 (t=24) |
| og128x01 | gpt-oss-20b-mxfp4 | MXFP4 MoE 12.10 GB | 0 | 36.8 (t=24) | 10.4 (t=24) |
| og128x01 | granite4.1-3b-q4 | Q4_K_M 2.10 GB | 0 | 42.4 (t=24) | 12.8 (t=24) |
| og128x01 | lfm2.5-350m-q8 | Q8_0 0.38 GB | 0 | 379.1 (t=24) | 56.4 (t=12) |
| og128x01 | llama3.2-1b-q4 | Q4_K_M 0.80 GB | 0 | 140.3 (t=24) | 33.2 (t=24) |
| og128x01 | qwen2.5-coder-0.5b-q8 | Q8_0 0.67 GB | 0 | 331.1 (t=24) | 47.4 (t=24) |
| og128x01 | qwen2.5-coder-1.5b-q4 | Q4_K_M 1.11 GB | 0 | 99.5 (t=24) | 26.7 (t=24) |
| og128x01 | qwen2.5-coder-14b-q4 | Q4_K_M 8.98 GB | 0 | 10.5 (t=24) | 3.2 (t=24) |
| og128x01 | qwen2.5-coder-3b-q4 | Q4_K_M 2.10 GB | 0 | 48.3 (t=24) | 14.1 (t=24) |
| og128x01 | qwen2.5-coder-7b-q4 | Q4_K_M 4.68 GB | 0 | 20.9 (t=24) | 6.1 (t=24) |
| og128x01 | qwen2.5-coder-7b-q4_0 | Q4_0 4.43 GB | 0 | 18.0 (t=24) | 6.5 (t=24) |
| og128x01 | qwen2.5-coder-7b-q8 | Q8_0 8.09 GB | 0 | 20.2 (t=24) | 3.9 (t=24) |
| og128x01 | qwen3-coder-30b-a3b-q4 | Q4_K_M 17.66 GB | 0 | 41.2 (t=24) | 11.5 (t=24) |
| og128x01 | qwen3.5-0.8b-q4_0 | Q4_0 0.55 GB | 0 | 186.1 (t=24) | 31.3 (t=24) |
| og128x01 | qwen3.5-0.8b-q8 | Q8_0 0.82 GB | 0 | 150.8 (t=24) | 23.1 (t=24) |
| og128x01 | qwen3.5-2b-q4 | Q4_K_M 1.27 GB | 0 | 79.1 (t=24) | 17.6 (t=24) |
| og128x01 | qwen3.5-35b-a3b-q4 | Q4_K_M 22.01 GB | 0 | 39.7 (t=24) | 7.5 (t=24) |
| og128x01 | qwen3.5-4b-q4 | Q4_K_M 2.73 GB | 0 | 31.2 (t=24) | 7.9 (t=24) |
| og128x01 | qwen3.5-9b-q4 | Q4_K_M 5.67 GB | 0 | 17.3 (t=24) | 4.8 (t=24) |
| og128x01 | qwen3.6-35b-a3b-q4 | Q4_K_M 22.12 GB | 0 | 37.2 (t=24) | 7.6 (t=24) |
| og128x01 | smollm2-135m-q8 | Q8_0 0.14 GB | 0 | 629.5 (t=24) | 98.5 (t=12) |
| og128x01 | smollm2-360m-q8 | Q8_0 0.38 GB | 0 | 278.7 (t=24) | 45.6 (t=12) |
| og128x01-d700x1 | gemma3-270m-q8 | Q8_0 0.29 GB | 99 | 4268.3 (t=4) | 105.3 (t=4) |
| og128x01-d700x1 | gemma4-e2b-q4 | Q4_K_M 3.09 GB | 99 | 444.7 (t=4) | 29.7 (t=4) |
| og128x01-d700x1 | gemma4-e4b-q4 | Q4_K_M 4.96 GB | 99 | 229.0 (t=4) | 21.5 (t=4) |
| og128x01-d700x1 | gemma4-e4b-q4_0 | Q4_0 4.82 GB | 99 | 251.3 (t=4) | 24.7 (t=4) |
| og128x01-d700x1 | granite4.1-3b-q4 | Q4_K_M 2.10 GB | 99 | 296.6 (t=4) | 30.9 (t=4) |
| og128x01-d700x1 | granite4.1-3b-q4_0 | Q4_0 1.98 GB | 99 | 326.7 (t=4) | 36.9 (t=4) |
| og128x01-d700x1 | llama3.2-1b-q4 | Q4_K_M 0.80 GB | 99 | 957.3 (t=4) | 84.4 (t=4) |
| og128x01-d700x1 | qwen2.5-coder-1.5b-q4 | Q4_K_M 1.11 GB | 99 | 188.8 (t=4) | 54.0 (t=4) |
| og128x01-d700x1 | qwen2.5-coder-3b-q4 | Q4_K_M 2.10 GB | 99 | 344.9 (t=4) | 37.3 (t=4) |
| og128x01-d700x1 | qwen2.5-coder-3b-q4_0 | Q4_0 1.99 GB | 99 | 373.4 (t=4) | 43.2 (t=4) |
| og128x01-d700x1 | qwen2.5-coder-7b-q4 | Q4_K_M 4.68 GB | 99 | 38.3 (t=4) | 20.6 (t=4) |
| og128x01-d700x1 | qwen2.5-coder-7b-q4_0 | Q4_0 4.43 GB | 99 | 174.0 (t=4) | 24.8 (t=4) |
| og128x01-d700x1 | qwen3.5-0.8b-q4_0 | Q4_0 0.55 GB | 99 | 332.9 (t=4) | 66.5 (t=4) |
| og128x01-d700x1 | qwen3.5-0.8b-q8 | Q8_0 0.82 GB | 99 | 317.8 (t=4) | 70.0 (t=4) |
| og128x01-d700x1 | qwen3.5-2b-q4 | Q4_K_M 1.27 GB | 99 | 146.7 (t=4) | 15.4 (t=4) |
| og128x01-d700x1 | qwen3.5-4b-q4 | Q4_K_M 2.73 GB | 99 | 61.2 (t=4) | 24.7 (t=4) |
| og128x01-d700x1 | qwen3.5-9b-q4 | Q4_K_M 5.67 GB | 99 | 32.6 (t=4) | 17.5 (t=4) |
| og128x01-d700x1 | smollm2-360m-q8 | Q8_0 0.38 GB | 99 | 2027.4 (t=4) | 97.9 (t=4) |
| og128x01-d700x1-noworkaround | qwen2.5-coder-3b-q4 | Q4_K_M 2.10 GB | 99 | 328.5 (t=4) | 39.8 (t=4) |
| og128x01-d700x2 | gpt-oss-20b-mxfp4 | MXFP4 MoE 12.10 GB | 99 | 108.6 (t=4) | 23.0 (t=4) |
| og128x01-d700x2 | qwen2.5-coder-14b-q4 | Q4_K_M 8.98 GB | 99 | 35.1 (t=4) | 9.4 (t=4) |
| og128x01-d700x2 | qwen2.5-coder-14b-q4_0 | Q4_0 8.51 GB | 99 | 109.1 (t=4) | 13.8 (t=4) |
| og128x01-d700x2 | qwen2.5-coder-7b-q4 | Q4_K_M 4.68 GB | 99 | 72.8 (t=4) | 14.4 (t=4) |
| og128x01-d700x2 | qwen2.5-coder-7b-q4_0 | Q4_0 4.43 GB | 99 | 221.4 (t=4) | 24.3 (t=4) |
| og128x01-d700x2 | qwen2.5-coder-7b-q8 | Q8_0 8.09 GB | 99 | 81.2 (t=4) | 16.4 (t=4) |
| og128x01-d700x2 | qwen3.5-9b-q4 | Q4_K_M 5.67 GB | 99 | 52.4 (t=4) | 17.2 (t=4) |
| og128x01-d700x2-ncmoe24 | gpt-oss-20b-mxfp4 | MXFP4 MoE 12.10 GB | 99 | 50.8 (t=24) | 8.9 (t=24) |
| og128x01-d700x2-ncmoe36 | qwen3-coder-30b-a3b-q4 | Q4_K_M 17.66 GB | 99 | 13.7 (t=24) | 8.1 (t=24) |
| og128x01-d700x2-ncmoe48 | qwen3-coder-30b-a3b-q4 | Q4_K_M 17.66 GB | 99 | 11.1 (t=24) | 6.9 (t=24) |
| og128x01-static-v2-almalinux | lfm2.5-350m-q8 | Q8_0 0.38 GB | 0 | 12.9 (t=1) | 9.0 (t=1) |
| og128x01-static-v2-almalinux | qwen3.5-0.8b-q4_0 | Q4_0 0.55 GB | 0 | 8.2 (t=1) | 4.6 (t=1) |
| og128x01-static-v2-almalinux | smollm2-135m-q8 | Q8_0 0.14 GB | 0 | 30.9 (t=1) | 19.3 (t=1) |
| og128x01-static-v2-busybox | lfm2.5-350m-q8 | Q8_0 0.38 GB | 0 | 12.9 (t=1) | 9.0 (t=1) |
| og128x01-static-v2-busybox | qwen3.5-0.8b-q4_0 | Q4_0 0.55 GB | 0 | 8.2 (t=1) | 4.8 (t=1) |
| og128x01-static-v2-busybox | smollm2-135m-q8 | Q8_0 0.14 GB | 0 | 30.7 (t=1) | 20.2 (t=1) |

### Task scores

| host | task | model | score | n | median latency s | notes |
|---|---|---|---|---|---|---|
| og128x01 | coding | qwen3.5-0.8b-q8 | 0.409 | 22 | 5.0 |  |
| og128x01 | coding | qwen2.5-coder-0.5b-q8 | 0.545 | 22 | 1.9 |  |
| og128x01 | coding | qwen2.5-coder-1.5b-q4 | 0.727 | 22 | 3.11 |  |
| og128x01 | coding | qwen3.5-2b-q4 | 0.864 | 22 | 7.84 |  |
| og128x01 | coding | qwen2.5-coder-3b-q4 | 0.909 | 22 | 6.56 |  |
| og128x01 | coding | granite4.1-3b-q4 | 0.955 | 22 | 6.46 |  |
| og128x01 | coding | qwen3.5-4b-q4 | 0.955 | 22 | 16.57 |  |
| og128x01 | coding | qwen2.5-coder-7b-q4 | 0.909 | 22 | 12.68 |  |
| og128x01 | coding | qwen3.5-9b-q4 | 0.909 | 22 | 22.19 |  |
| og128x01 | coding | qwen3-coder-30b-a3b-q4 | 0.955 | 22 | 8.79 |  |
| og128x01 | ids | gemma3-270m-q8 | 0.558 | 163 | 0.281 |  |
| og128x01 | ids | lfm2.5-350m-q8 | 0.558 | 163 | 0.464 |  |
| og128x01 | ids | qwen3.5-0.8b-q8 | 0.639 | 163 | 0.633 |  |
| og128x01 | ids | llama3.2-1b-q4 | 0.542 | 163 | 0.523 |  |
| og128x01 | ids | qwen3.5-2b-q4 | 0.777 | 163 | 1.925 |  |
| og128x01 | ids | qwen3.5-4b-q4 | 0.916 | 163 | 3.641 |  |
| og128x01 | ids | gemma4-e4b-q4 | 0.882 | 163 | 3.338 |  |
| og128x01 | ids | qwen3.5-9b-q4 | 0.952 | 163 | 16.314 |  |
| og128x01 | ids | qwen3-coder-30b-a3b-q4 | 0.881 | 163 | 2.354 |  |
| og128x01 | coding | qwen3.6-35b-a3b-q4 | 1.0 | 22 | 16.42 |  |
| og128x01 | coding | gpt-oss-20b-mxfp4 | 0.909 | 22 | 28.65 |  |
| og128x01 | ids | gemma4-e2b-q4 | 0.584 | 163 | 1.51 | rerun 2026-09-22 to check 9.7 s/line anomaly |
| og128x01 | coding-v2 | qwen2.5-coder-1.5b-q4 | 0.0 | 23 | 11.59 | llama.cpp 0a1ef309c |
| og128x01 | coding-v2 | qwen2.5-coder-3b-q4 | 0.087 | 23 | 18.37 | llama.cpp 0a1ef309c |
| og128x01 | coding-v2 | granite4.1-3b-q4 | 0.087 | 23 | 21.52 | llama.cpp 0a1ef309c |
| og128x01 | coding-v2 | qwen3.5-4b-q4 | 0.217 | 23 | 140.4 | llama.cpp 0a1ef309c |
| og128x01 | coding-v2 | qwen2.5-coder-7b-q4 | 0.174 | 23 | 37.44 | llama.cpp 0a1ef309c |
| og128x01 | coding-v2 | qwen3.5-9b-q4 | 0.391 | 23 | 137.77 | llama.cpp 0a1ef309c |
| og128x01 | coding-v2 | qwen3-coder-30b-a3b-q4 | 0.304 | 23 | 50.28 | llama.cpp 0a1ef309c |
| og128x01 | coding-v2 | qwen3.6-35b-a3b-q4 | 0.652 | 23 | 144.61 | llama.cpp 0a1ef309c |
| og128x01-d700x1 | coding | qwen2.5-coder-7b-q4_0 | 0.909 | 22 | 4.54 | single D700 |
| og128x01-d700x1 | ids | qwen3.5-4b-q4 | 0.908 | 163 | 1.677 | single D700 |
| og128x01-d700x1 | coding | granite4.1-3b-q4_0 | 0.909 | 22 | 3.8 | single D700 |
| og128x01-d700x1 | coding-v2 | granite4.1-3b-q4_0 | 0.13 | 23 | 9.05 | single D700; llama.cpp 0a1ef309c |
| og128x01-d700x1 | coding-v2 | qwen2.5-coder-7b-q4_0 | 0.13 | 23 | 11.61 | single D700; llama.cpp 0a1ef309c |
| og128x01-d700x2 | coding | qwen2.5-coder-14b-q4 | 0.955 | 22 | 13.77 | dual D700 |
| og128x01-d700x2 | coding | gpt-oss-20b-mxfp4 | 0.864 | 22 | 15.58 | dual D700 |
| og128x01-d700x2 | coding | qwen2.5-coder-14b-q4_0 | 0.909 | 22 | 10.24 | dual D700 |
| og128x01-d700x2 | coding-v2 | qwen2.5-coder-14b-q4_0 | 0.478 | 23 | 25.37 | dual D700; llama.cpp 0a1ef309c |
| og128x01-d700x2 | coding-v2 | gpt-oss-20b-mxfp4 | 0.261 | 23 | 50.09 | dual D700; llama.cpp 0a1ef309c |
<!-- results:end -->

## Findings and recommendations

Per-tier detail lives in `docs/tiers/`. Short version, updated as phases complete:

| tier | status | coding assistant | log triage |
|---|---|---|---|
| Xeon E5-2697 v2, AVX only, 125 GB (`xeon-avx.md`) | done | Qwen3-Coder-30B-A3B (11.5 tok/s, v1 0.95 / v2 0.30) for interactive use; Qwen3.6-35B-A3B (7.6 tok/s, v2 **0.65**, 2 min/answer) when quality matters; the 3B models only do boilerplate (v2 0.09). | Not an LLM job: stdlib regex + naive Bayes at ~50 µs/line beat every model under 9B. Use Qwen3.5-4B only to explain flagged lines. |
| 2x FirePro D700 6 GB, RADV Vulkan (`radeon-gcn1-vulkan.md`) | done, serving | Granite 4.1-3B **Q4_0** on one card: 37 tok/s, v1 0.91 / v2 0.13, 3.8 s/problem (live on :8081). Qwen2.5-Coder-14B **Q4_0** across both cards: 13.8 tok/s, v2 0.48, the best interactive coder on this box. Use Q4_0 above ~4 GB; avoid the Qwen3.5 family on this GPU; MoE hybrid offload loses to pure CPU. | Qwen3.5-4B at 1.7 s/line, F1 0.91; still loses to the stdlib baselines. |
| Raspberry Pi | awaiting hardware | expected: Qwen2.5-Coder-1.5B / Qwen3.5-2B on a Pi 5 | stdlib baselines; 270M–800M LLM adds nothing |
| iOS | awaiting devices | route 1 apps; Foundation Models for classification only | Foundation Models `@Generable` enum |
| Switches | static payload verified in containers; awaiting inventory | Arista: container-manager + static v2 build (`deploy/static/`, 135M-800M models at 5-19 tok/s on one core); NX-OS: guest shell / Docker; IOS-XE: IOx (license); Junos: Python only, Evolved via Docker once its 20%-core cap is raised | stdlib naive Bayes runs anywhere Python 3 does, including classic Junos |
