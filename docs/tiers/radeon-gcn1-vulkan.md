# Tier: FirePro D700 / Radeon HD 7970 (Tahiti, GCN 1.0) via Vulkan

og128x01 is a **Mac Pro 6,1** (2013 cylinder): two FirePro D700s, which are Tahiti XT with **6 GB VRAM each** (12 GB total; the kernel reports them as Radeon HD 7970). This is the exact configuration in llama.cpp issues #19610/#19615 and the echalupa Mac Pro 6,1 blog cited in `docs/research-2026-09-20.md`. GCN 1.0 is unsupported by ROCm; the only compute path llama.cpp offers is its Vulkan backend on top of Mesa RADV.

## State log
- 2026-09-20: cards bound to legacy `radeon`; `vulkaninfo` shows only llvmpipe. `/etc/default/grub` already had the parameters (edited Sep 3) but `update-grub` had never been run.
- 2026-09-22: `update-grub` + reboot done. Both cards on `amdgpu`, 6 GB VRAM each, 64 GB GTT. RADV still finds no device because the user is not in the `render` group (`/dev/dri/renderD*` are root:render 0660). Fix: `sudo usermod -aG render <user>`.
- `~/src/llama.cpp` is built with `GGML_VULKAN=ON`.

## Unlock procedure (needs approval: GRUB edit + reboot)
1. Edit `/etc/default/grub`: append `radeon.si_support=0 amdgpu.si_support=1` to `GRUB_CMDLINE_LINUX_DEFAULT`.
2. `sudo update-grub && sudo reboot`.
3. Verify: `vulkaninfo --summary | grep deviceName` shows two `AMD Radeon HD 7970 (RADV TAHITI)` entries and `sh bench/probe.sh` records `gpu_driver: amdgpu`.
4. Rollback if display or boot misbehaves: remove the two parameters, `update-grub`, reboot.

## Bench plan
- With 6 GB per card: single-card runs up to 7B Q4 (4.7 GB) plus KV; 9B Q4 (5.7 GB) is tight; 14B Q4 split across both.
- Known RADV GFX6 bug: DeviceLost past ~500 tokens of context. Run everything with `RADV_DEBUG=novm,syncshaders,zerovram` and `-ub 256`; keep `-fa off`; all-or-nothing offload (`-ngl 99`). Bench with p=512 first to see whether the bug bites on kernel 6.12.
- Env: `GGML_VK_VISIBLE_DEVICES=0` for single-card rows, both cards with `-sm layer`.
- Compare against the CPU rows in README; decision rule: GPU wins only if generation tok/s more than doubles at equal quality.

## Results
_pending reboot_
