# Tier: other devices

Any device follows the same loop: `bench/probe.sh` → build or install llama.cpp → `bench/bench_llamacpp.sh <model.gguf>` → task runs → commit `results/<host>/`.

| Class | How to get llama.cpp on it | Expectation |
|---|---|---|
| Old x86 laptops / desktops (Sandy Bridge–Skylake) | `deploy/static/build.sh` (v2 for pre-Haswell, v3 for Haswell+) or native build | Like the Xeon tier; AVX2 parts (Haswell+) should be 2–4x faster on K-quants. v2 single-core reference numbers: `docs/tiers/switches-arista.md` |
| Android phones | Termux + native build, or PocketPal (Android) | Similar to iOS per chip generation |
| OpenWrt routers (MIPS / ARMv7 / ARM64, 128 MB–1 GB) | only ARM64 boxes with ≥512 MB: static arm64 build; MIPS out of scope | 135M–270M Q8 at best; stdlib IDS baseline is the real fit |
| NAS boxes (x86 Celeron / ARM) | Docker if available, else static build | 0.8–2B |
| Jetson-class boards | CUDA build of llama.cpp | 4–9B comfortably |
| Macs | native Metal build or MLX | far above every other tier here |
