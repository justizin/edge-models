# Tier: Xeon E5-2697 v2 (Ivy Bridge, AVX only)

og128x01: 12 cores / 24 threads at 2.7 GHz, 125 GB RAM, Debian 13. SIMD: SSE4.2, AVX, F16C. No AVX2, no FMA, no AVX-512.
llama.cpp built with `-march=native`, so every available instruction is used; the gap to modern CPUs is architectural.

## What this tier represents
Any pre-2013 Xeon or Core i7 (Sandy/Ivy Bridge), and by extension the many x86 switch control planes built on older Atom/Xeon-D parts with similar SIMD.

## Phase 1 results (2026-09-21, llama.cpp 6a1a922d2, CPU only)

### Throughput (best of 12/24 threads, pp512 / tg128)
| model | quant | prompt tok/s | gen tok/s |
|---|---|---|---|
| SmolLM2-135M | Q8_0 | 630 | 99 |
| Gemma 3 270M | Q8_0 | 578 | 58 |
| Qwen2.5-Coder-0.5B | Q8_0 | 331 | 47 |
| Qwen3.5-0.8B | Q4_0 | 186 | 30 |
| Qwen3.5-0.8B | Q8_0 | 151 | 23 |
| Llama 3.2 1B | Q4_K_M | 140 | 33 |
| Qwen2.5-Coder-1.5B | Q4_K_M | 100 | 27 |
| Qwen3.5-2B | Q4_K_M | 79 | 18 |
| Gemma 4 E2B | Q4_K_M | 65 | 16 |
| Qwen2.5-Coder-3B | Q4_K_M | 48 | 14 |
| Granite 4.1-3B | Q4_K_M | 42 | 13 |
| Qwen3.5-4B | Q4_K_M | 31 | 8 |
| Gemma 4 E4B | Q4_K_M | 32 | 8 |
| Qwen2.5-Coder-7B | Q4_K_M | 21 | 6 |
| Qwen3.5-9B | Q4_K_M | 17 | 5 |
| Qwen2.5-Coder-14B | Q4_K_M | 10.5 | 3 |
| Qwen3-Coder-30B-A3B | UD-Q4_K_XL | 41 | 11.5 |

Observations:
- Generation is memory-bandwidth bound: for models under ~1 GB, 12 threads (one per core) wins on generation; above that 24 threads wins on both. Prompt processing always wants 24.
- Quant format barely matters for speed here (measured 2026-09-22 on the 7B coder, 24 threads): Q4_K_M 21 / 6.1 tok/s, Q4_0 17.5 / 6.1, Q8_0 20 / 3.9. Generation tracks bytes moved (Q8 is half the speed of Q4), prompt processing is compute-bound and flat across quants. The earlier guess that K-quants are penalized on AVX-only silicon was wrong; keep Q4_K_M. The real ceiling is compute: a 2k-token editor context on a dense 7B takes ~100 s before the first token.
- The MoE coder (30B total, 3.3B active) runs at 3B-class speed with 125 GB RAM holding it resident. It is the only way to get 7B+ quality at usable latency on this CPU.

### Coding task (22 problems, pass@1, median seconds per problem)
| model | pass | s |
|---|---|---|
| Granite 4.1-3B | 0.95 | 6.5 |
| Qwen3-Coder-30B-A3B | 0.95 | 8.8 |
| Qwen3.5-4B | 0.95 | 16.6 |
| Qwen2.5-Coder-3B | 0.91 | 6.6 |
| Qwen2.5-Coder-7B | 0.91 | 12.7 |
| Qwen3.5-9B | 0.91 | 22.2 |
| Qwen3.5-2B | 0.86 | 7.8 |
| Qwen2.5-Coder-1.5B | 0.73 | 3.1 |
| Qwen2.5-Coder-0.5B | 0.55 | 1.9 |
| Qwen3.5-0.8B | 0.41 | 5.0 |

The set saturates at 3B: five models tie within one problem of each other. A harder v2 set (multi-function, stateful, real bug reports) is needed to separate them. What the set does show: sub-1B models are not assistants; 1.5B is the floor for boilerplate; and 3B dense models are the sweet spot on this CPU, matching 7B at half the latency.

### IDS log triage (163 lines, F1 on malicious, median seconds per line)
| model | F1 | P | R | s/line |
|---|---|---|---|---|
| regex rules (stdlib) | 1.00 | 1.00 | 1.00 | 0.00004 |
| naive Bayes (stdlib, 5-fold CV) | 0.89 | 0.86 | 0.94 | 0.00005 |
| Qwen3.5-9B | 0.95 | 0.95 | 0.95 | 16.3 |
| Qwen3.5-4B | 0.92 | 0.88 | 0.95 | 3.6 |
| Gemma 4 E4B | 0.88 | 0.88 | 0.89 | 3.3 |
| Qwen3-Coder-30B-A3B | 0.88 | 0.79 | 1.00 | 2.4 |
| Qwen3.5-2B | 0.78 | 1.00 | 0.64 | 1.9 |
| Qwen3.5-0.8B | 0.64 | 0.52 | 0.84 | 0.6 |
| Gemma 4 E2B | 0.58 | 1.00 | 0.41 | 1.5 |
| LFM2.5-350M | 0.56 | 0.39 | 1.00 | 0.5 |
| Gemma 3 270M | 0.56 | 0.39 | 1.00 | 0.3 |
| Llama 3.2 1B | 0.54 | 0.38 | 0.92 | 0.5 |

- Every model under 1B (and Llama 3.2 1B) answers MALICIOUS to essentially every line: recall 1.0, precision 0.39. They add nothing over a grep.
- Only 4B and up match the naive-Bayes baseline, at 60,000x the per-line cost. On this synthetic set the regex rules are perfect, which is the point: the set is easy, and an LLM that cannot match it does not belong in a pipeline.
- Where an LLM could still earn its place: explaining an alert, summarizing a burst, or handling log formats no rule anticipated. That is a different task and needs a different dataset (real loghub samples), which is the next IDS step.
- Gemma 4 E2B originally logged ~10 s per line; a re-run on 2026-09-22 with identical settings gave the same F1 at 1.5 s/line, and a single request through llama-server takes 2.9 s cold. The first run's latency was a transient artifact (cause not identified; the anomalous result file was dropped). Its real problem is recall 0.41: it calls almost everything benign.

## Recommendation for this tier
- Coding assistant: **Qwen3-Coder-30B-A3B** if the box has the RAM (needs ~20 GB), else **Granite 4.1-3B** or **Qwen2.5-Coder-3B** (2 GB). Serve with `deploy/xeon/llama-coder.service`.
- Log triage: run the stdlib rules + naive Bayes; reserve an LLM (Qwen3.5-4B) for explaining what the classifier flagged.
