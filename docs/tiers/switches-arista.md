# Tier: Arista EOS

Facts from `docs/research-2026-09-20.md` §5.

- EOS 4.32+ is AlmaLinux 9-based (RHEL 9 userland), all platforms x86. `bash` from the CLI. Extensions ship as RPM/SWIX; persistence via `/mnt/flash/rc.eos` or `boot-extensions`.
- Docker is not bundled; EOS ~4.30+ has a native `container-manager` CLI: load an image from flash, set `memory hard-limit` and `cpu shares`, `on-boot`, privileged. Configuration survives upgrades. This is the intended path.
- RAM by platform: 720XP/722XPM 4 GB (dual-core), 7010T 4 GB, 7050X3 8 GB, 7280R3 16 GB (K/A SKUs 64 GB + 120 GB SSD).

## Plan
1. Virtual first: cEOS-lab (free with arista.com registration), containerlab kind `arista_ceos`. Verify `container-manager` semantics and the `x86-64-v2` static build (`deploy/static/build.sh`) inside it.
2. Package: minimal container (scratch or AlmaLinux-minimal) with `llama-completion`/`llama-server` + model on flash. Budget by platform: 4 GB boxes get 270M–800M Q8; 8 GB boxes 2B Q4; 16 GB boxes 4B Q4.
3. Real hardware: probe over the console (`show version`, `bash -c 'nproc; free -m; df -h /mnt/flash; grep -m1 flags /proc/cpuinfo'`), then deploy with a hard memory limit and low CPU shares. Measure: tok/s, and control-plane impact (`show processes top`, `ProcMgr`/`Sysdb` CPU, CLI latency, BGP/STP timers).
4. IDS angle: on-box syslog triage with the stdlib baseline first (Python 3 is present), LLM only if it beats it.

## Static payload measured (2026-10-23)

The `x86-64-v2` static build (`deploy/static/`, llama.cpp b11796) runs unchanged inside `almalinux:9-minimal`, the EOS 4.32+ userland, with no libraries present. One thread, `--cpus 1 --memory 2g` (a 720XP/7010T-class budget), pp256 / tg64:

| model | prompt tok/s | gen tok/s |
|---|---|---|
| SmolLM2-135M Q8_0 | 30.9 | 19.3 |
| LFM2.5-350M Q8_0 | 12.9 | 9.0 |
| Qwen3.5-0.8B Q4_0 | 8.2 | 4.6 |

Measured on the Ivy Bridge Xeon, so a real switch CPU (Atom C2000/C3000 at 1.7-2.2 GHz, no AVX) will land lower, likely by 2-3x. Two lessons from the build: llama.cpp now defaults `GGML_BMI2=ON`, which SIGILLs on every pre-Haswell core including these Atoms, so the v2 build turns it off; and `LLAMA_OPENSSL` must be off for a static link. Reading: a 4 GB EOS box can run the 135M-350M models for short answers at ~10-20 tok/s on one core; anything 1B+ is a batch job. The cEOS-lab verification of `container-manager` itself still needs the arista.com download.
