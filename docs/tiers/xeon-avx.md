# Tier: Xeon E5-2697 v2 (Ivy Bridge, AVX only)

og128x01: 12 cores / 24 threads at 2.7 GHz, 125 GB RAM, Debian 13. SIMD: SSE4.2, AVX, F16C. No AVX2, no FMA, no AVX-512.
llama.cpp built with `-march=native`, so every available instruction is used; the gap to modern CPUs is architectural.

## What this tier represents
Any pre-2013 Xeon or Core i7 (Sandy/Ivy Bridge), and by extension the many x86 switch control planes built on older Atom/Xeon-D parts with similar SIMD.

## Early observations (Phase 1, in progress)
- Generation speed peaks at 12 threads (one per physical core); 24 threads helps prompt processing only. Memory bandwidth, not compute, bounds generation.
- Q4_K_M prompt processing is disproportionately slow on AVX-only silicon (7B Q4_K_M: ~9 tok/s prompt, ~5 tok/s gen at t=12). The K-quant dot kernels lean on AVX2/FMA. Q8_0 and Q4_0 have leaner AVX paths. **Action:** bench Q8_0 and Q4_0 variants of the same model; quant choice may matter more than parameter count here.
- 125 GB RAM means MoE models (30B-A3B, 35B-A3B) run fully resident; they should give near-3B speed with far better quality. This is the expected sweet spot for a coding assistant on this box.

## Deployment
`deploy/xeon/llama-coder.service`: user systemd unit running `llama-server` on 127.0.0.1:8080 with the best coder found in Phase 1.

## Results
_see README results tables; per-quant comparison to follow_
