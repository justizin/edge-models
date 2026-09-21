# Tier: Raspberry Pi

Facts from `docs/research-2026-09-20.md` §4; local numbers to follow once a Pi is on the bench.

- Pi 5 (Cortex-A76, dotprod + FP16, no i8mm/SVE; ~5 GB/s measured memory bandwidth). Must build with `-DGGML_NATIVE=ON` (`deploy/pi/build.sh`); generic arm64 builds are ~10x slower. Expected gen tok/s: 270M–600M ≈ 20+, 1B Q4 ≈ 15–18, 2B ≈ 7, 3–4B ≈ 4–5, 8B ≈ 2. 8 GB vs 16 GB changes what fits, not speed.
- Pi 4 (Cortex-A72, no dotprod): 2–3x slower; usable only for ≤400M models.
- Pi Zero 2 W (512 MB): 135M–270M Q8 only, and the stdlib IDS baselines.
- Hailo AI HAT+ 2 (Hailo-10H, Jan 2026, $130): LLM decode is *slower* than the Pi 5 CPU (≈7 vs 9 tok/s on 1.5B) but prefill is ~6x faster and it offloads host RAM/CPU at lower system power (7 W vs 11 W). Max ~1.7B. Worth a row in the matrix only if the user has one; not a purchase recommendation for this project. Hailo-8/8L: vision only.
- VideoCore Vulkan: 0.15 tok/s, not viable.

## Plan
1. `deploy/pi/build.sh` on the Pi, `bench/probe.sh`, `bench/bench_llamacpp.sh <model.gguf>` for the `pi`/`pi5` tagged models (copy GGUFs over from the Xeon's HF cache with rsync).
2. IDS pipeline: rsyslog on the Pi receives from lab hosts, a small daemon (derived from `bench_server.py`'s ids runner) scores lines with the naive-Bayes baseline first and an LLM second, writes alerts. Inject the dataset's brute-force sequence to verify.
3. Coding: `llama-server` with Qwen2.5-Coder-1.5B or Qwen3.5-2B; measure real editor latency for FIM on a Pi 5.
