# Tier: Radeon HD 7970 (Tahiti, GCN 1.0) via Vulkan

Two cards, 3 GB VRAM each, in og128x01. GCN 1.0 is unsupported by ROCm; the only compute path llama.cpp offers is its Vulkan backend on top of Mesa RADV.

## Current state
- Kernel binds the cards to the legacy `radeon` driver (`/sys/class/drm/card*/device/driver -> radeon`).
- RADV requires `amdgpu`, so `vulkaninfo --summary` lists only `llvmpipe`.
- `~/src/llama.cpp` is already built with `GGML_VULKAN=ON`.

## Unlock procedure (needs approval: GRUB edit + reboot)
1. Edit `/etc/default/grub`: append `radeon.si_support=0 amdgpu.si_support=1` to `GRUB_CMDLINE_LINUX_DEFAULT`.
2. `sudo update-grub && sudo reboot`.
3. Verify: `vulkaninfo --summary | grep deviceName` shows two `AMD Radeon HD 7970 (RADV TAHITI)` entries and `sh bench/probe.sh` records `gpu_driver: amdgpu`.
4. Rollback if display or boot misbehaves: remove the two parameters, `update-grub`, reboot.

## Bench plan
- `NGL=99 sh bench/bench_llamacpp.sh gpu3g` for models that fit one card (0.1B to 4B at Q4/Q8).
- 7B/9B Q4 split across both cards: `llama-bench -ngl 99 -sm layer` (add `-mg`/`-ts` variants).
- If RADV on GFX6 lacks 16-bit storage, try `GGML_VK_DISABLE_F16=1`; record any env vars needed.
- Compare against the CPU rows in README; decision rule: GPU wins only if generation tok/s more than doubles at equal quality.

## Results
_pending reboot_
