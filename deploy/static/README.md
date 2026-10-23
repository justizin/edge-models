# Static x86-64 llama.cpp for switch control planes

`build.sh` produces fully static `llama-bench`, `llama-completion` and `llama-server` binaries that run on any x86-64 Linux with no shared libraries at all: Arista EOS `container-manager` images, NX-OS guest shell or Docker, IOS-XE IOx, Junos Evolved's Docker, old NAS boxes, anything with a shell and a few hundred MB of flash.

| ARCH | instruction floor | for | tarball |
|---|---|---|---|
| `x86-64-v2` (default) | SSE4.2, POPCNT; no AVX, no BMI2 | Atom C2000/C3000, Xeon-D 1500 in safe mode, Ivy Bridge and older, anything you have not looked up | `out/llama-x86-64-v2-<commit>.tar.gz`, 21 MB |
| `x86-64-v3` | AVX2, FMA, F16C, BMI2 | Xeon-D 1500+, Atom P-series, Haswell and newer | `out/llama-x86-64-v3-<commit>.tar.gz`, 21 MB |

Build on og128x01 (needs `libc6-dev`, `libstdc++-14-dev`, cmake; `~/src/llama.cpp` checked out):

```
ARCH=x86-64-v2 sh deploy/static/build.sh
ARCH=x86-64-v3 sh deploy/static/build.sh
```

Notes from the first build (2026-10-23, llama.cpp 0a1ef309c / b11796):
- **`-DGGML_BMI2=OFF` is required for v2.** llama.cpp now defaults `GGML_BMI2=ON`, which adds `-mbmi2` regardless of `-march`; the first v2 build died with `Illegal instruction` on the Ivy Bridge build host itself (and would on every Atom C2000/C3000). The v3 binary SIGILLs here too, as it should: this host has no AVX2.
- `-DLLAMA_OPENSSL=OFF` is required; llama.cpp now defaults to linking OpenSSL for HTTPS and the shared `libssl.so` breaks `-static`. The server still speaks plain HTTP, which is all a switch needs.
- The glibc static-link warnings (`getpwuid`, `getaddrinfo`, `dlopen`) are expected: those functions want NSS plugins at runtime. Name resolution and user lookup are not used on the paths we care about (`--host <ip>` and model files on flash).
- `objdump` shows AVX/AVX-512 instructions inside the v2 binary. All of them are in glibc's runtime-dispatched `memcpy`/`strlen`/libm variants (`__memcpy_avx512_no_vzeroupper`, `__sincos_fma`, ...), which glibc only selects when the CPU reports the feature. None are in ggml. A true SSE4.2-only CPU has not been tested yet (no `qemu-x86_64` on the build host); the first real target gets `llama-bench -t 1 -p 32 -n 16` before anything else.

## Deploy

```
scp out/llama-x86-64-v2-<commit>.tar.gz <switch>:/mnt/flash/     # EOS: /mnt/flash, NX-OS: bootflash:, Junos Evo: /var/tmp
tar -xzf llama-x86-64-v2-<commit>.tar.gz
./llama-bench -m model.gguf -t 1 -p 128 -n 32              # smoke test, then size the model to the RAM cap
./llama-server -m model.gguf --host 127.0.0.1 --port 8080 -t 1 -c 2048 -np 1
```

Model budget by control-plane RAM (from `docs/tiers/switches-*.md`): 4 GB boxes get 135M to 800M Q8 or Q4_0; 8 GB boxes 2B Q4; 16 GB boxes 4B Q4. Junos Evolved caps a container at 2 GB and 20% of a core by default.

## Verification without a switch

`bench/bench_llamacpp.sh` can drive the static binary inside a minimal container by pointing `LLAMA_BIN` at a wrapper that runs `docker run --cpus 1 --memory 2g` with the HF cache mounted read-only (EOS 4.32+ is AlmaLinux 9 userland; `busybox` stands in for a scratch image). Results (2026-10-23, llama.cpp b11796, one thread, pp256 / tg64, `results/og128x01-static-v2-{almalinux,busybox}/`):

| model | almalinux:9-minimal | busybox:stable-glibc |
|---|---|---|
| SmolLM2-135M Q8_0 | 30.9 / 19.3 | 30.7 / 20.2 |
| LFM2.5-350M Q8_0 | 12.9 / 9.0 | 12.9 / 9.0 |
| Qwen3.5-0.8B Q4_0 | 8.2 / 4.6 | 8.3 / 4.8 |

The binary needs nothing from the image: busybox has no libc for it to find. Same numbers in both, so the container flavour is irrelevant and only the CPU budget matters. On this Ivy Bridge core; expect 2-3x less on a 2 GHz Atom control plane. The `deploy/junos/build-image.sh` scratch image is the same payload with a model baked in.
