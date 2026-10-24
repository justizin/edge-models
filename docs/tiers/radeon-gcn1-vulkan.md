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

## Results (2026-09-22, llama.cpp 6a1a922d2, RADV on Mesa 25.0.7, kernel 6.12.107)

Setup: `sg render -c ...`, `-ngl 99 -ub 256 -fa off`, 4 CPU threads. `RADV_DEBUG=novm,syncshaders,zerovram` was set for the ladder but turned out unnecessary (see below).

### Single card (pp512 / tg128 tok/s; CPU best in parentheses)
| model | quant | GPU | CPU |
|---|---|---|---|
| Gemma 3 270M | Q8_0 | 4268 / 105 | 578 / 58 |
| SmolLM2-360M | Q8_0 | 2027 / 98 | 279 / 46 |
| Qwen3.5-0.8B | Q4_0 | 333 / 66 | 186 / 30 |
| Qwen3.5-0.8B | Q8_0 | 318 / 70 | 151 / 23 |
| Llama 3.2 1B | Q4_K_M | 957 / 84 | 140 / 33 |
| Qwen2.5-Coder-1.5B | Q4_K_M | 189 / 54 | 100 / 27 |
| Qwen3.5-2B | Q4_K_M | 147 / 15 | 79 / 18 |
| Gemma 4 E2B | Q4_K_M | 445 / 30 | 65 / 16 |
| Qwen2.5-Coder-3B | Q4_K_M | 345 / 37 | 48 / 14 |
| Granite 4.1-3B | Q4_K_M | 297 / 31 | 42 / 13 |
| Qwen3.5-4B | Q4_K_M | 61 / 25 | 31 / 8 |
| Gemma 4 E4B | Q4_K_M | 229 / 22 | 32 / 8 |
| Qwen2.5-Coder-7B | Q4_K_M (4.7 GB) | 38 / 21 | 21 / 6 |
| Qwen2.5-Coder-7B | Q4_0 (4.4 GB) | 174 / 25 | 17.5 / 6 |
| Qwen3.5-9B | Q4_K_M (5.7 GB) | 33 / 18 | 17 / 5 |

### Both cards, `-sm layer`
| model | quant | GPU x2 |
|---|---|---|
| Qwen2.5-Coder-7B | Q4_0 | 221 / 24 |
| Qwen2.5-Coder-7B | Q4_K_M | 73 / 14 |
| Qwen2.5-Coder-7B | Q8_0 | 81 / 16 |
| Qwen3.5-9B | Q4_K_M | 52 / 17 |
| Qwen2.5-Coder-14B | Q4_K_M | 35 / 9.4 |

### Task runs on GPU
| task | model | config | score | median s | CPU equivalent |
|---|---|---|---|---|---|
| coding | Qwen2.5-Coder-7B Q4_0 | 1 card | 0.91 | 4.5 | 0.91 @ 12.7 s |
| coding | Qwen2.5-Coder-14B Q4_K_M | 2 cards | 0.95 | 13.8 | not run (3 tok/s) |
| ids | Qwen3.5-4B Q4_K_M | 1 card | 0.91 | 1.7 | 0.92 @ 3.6 s |

### Findings
- **It works and it is worth it.** For the Llama / Qwen2.5 / Granite / Gemma families a single D700 gives 6–8x prompt processing and 2.5–3x generation over the 24-thread Xeon. A 7B coder at 25 tok/s with a 512-token prompt in 3 s is a usable editor assistant; on the CPU it was not.
- **The Qwen3.5 family does not accelerate well on GFX6.** Qwen3.5-2B generates slower on the GPU (15 tok/s) than on the CPU (18); Qwen3.5-4B prompt processing is 61 vs Gemma 4 E4B's 229. Hypothesis: the hybrid gated-delta-net layers in Qwen3.5 lack efficient Vulkan kernels (or run on CPU via the scheduler) on a GPU with no fp16, no int-dot, and no coopmat. Not verified at the op level. On these cards prefer Qwen2.5 / Granite / Gemma.
- **Use Q4_0 for anything over ~4 GB.** 7B Q4_0 does 174 tok/s prompt on one card vs 38 for Q4_K_M; on two cards, with everything resident, still 221 vs 73. So K-quant shaders are genuinely slower on GFX6 *and* the 4.7 GB Q4_K_M spills out of the usable VRAM heap on one card. Generation is barely affected (25 vs 21).
- **Two cards buy capacity, not speed.** Layer split makes 14B Q4_K_M (9 GB) and 7B Q8_0 fit; generation does not improve because layers execute sequentially. 14B at 9.4 tok/s is 3x the CPU and the first time 14B is usable on this box.
- **The RADV DeviceLost bug (llama.cpp #19610) did not reproduce.** 2048-token prompts on the 3B ran clean with and without `RADV_DEBUG=novm,syncshaders,zerovram` (323 vs 329 tok/s). Kernel 6.12.107 + Mesa 25.0.7 appear unaffected; the reports were on kernel 6.19. Keep `-fa off` (fp16 flash-attention is unavailable anyway).
- 30B-A3B MoE (17.7 GB) does not fit 12 GB; `-ncmoe` hybrid results in Phase 2b below.

## Phase 2b follow-ups (2026-09-22)
| experiment | result | verdict |
|---|---|---|
| 3B, 2048-token prompt, no `RADV_DEBUG` | 329 / 40 tok/s, no DeviceLost | workaround not needed on kernel 6.12 + Mesa 25.0.7 |
| Qwen3-Coder-30B-A3B, experts on CPU (`-ncmoe 48`), attention on 2 GPUs | 11 / 6.9 | worse than pure CPU (41 / 11.5) |
| same, `-ncmoe 36` | 13.7 / 8.1 | still worse; PCIe round trips per layer dominate |
| gpt-oss-20b, `-ncmoe 24` hybrid | 51 / 8.9 | prompt up, generation down vs CPU (37 / 10.4) |
| gpt-oss-20b fully on 2 GPUs (12.1 GB MXFP4) | **109 / 23** | fits; 2.2x CPU generation, best 20B-class number on this box |

Conclusion: MoE offload only pays when the whole model fits in VRAM. The 30B-A3B coders stay on the CPU; gpt-oss-20b becomes a GPU model. Phase 2c adds Q4_0 rows for the 3B/4B/14B models and a GPU coding run for gpt-oss-20b.

## Phase 2c: Q4_0 variants and GPU coding runs (2026-09-22)
| model | quant | config | pp / tg tok/s | vs Q4_K_M |
|---|---|---|---|---|
| Qwen2.5-Coder-3B | Q4_0 | 1 card | 373 / 43 | 345 / 37 |
| Granite 4.1-3B | Q4_0 | 1 card | 327 / 37 | 297 / 31 |
| Gemma 4 E4B | Q4_0 | 1 card | 251 / 25 | 229 / 22 |
| Qwen2.5-Coder-14B | Q4_0 | 2 cards | **109 / 13.8** | 35 / 9.4 |

| task | model | config | score | median s |
|---|---|---|---|---|
| coding | Granite 4.1-3B Q4_0 | 1 card | 0.91 | **3.8** |
| coding | Qwen2.5-Coder-14B Q4_0 | 2 cards | 0.91 | 10.2 |
| coding | gpt-oss-20b MXFP4 | 2 cards | 0.86 | 15.6 |

- Q4_0 gives ~10% over Q4_K_M when the model fits comfortably, and 3x on prompt processing when it does not (14B). Rule for these cards: Q4_0 above ~4 GB, either below.
- gpt-oss-20b is fast on the GPUs but its built-in reasoning burns the 512-token answer budget; it scores lower than on CPU and stays slow per problem. Not a fit for terse coding prompts without raising `max_tokens` or disabling reasoning.

## Coding task v2 on the GPUs (2026-10-23)
| model | config | v2 pass | median s |
|---|---|---|---|
| Qwen2.5-Coder-14B Q4_0 | 2 cards | **0.48** | 25 |
| gpt-oss-20b MXFP4 | 2 cards | 0.26 | 50 |
| Qwen2.5-Coder-7B Q4_0 | 1 card | 0.13 | 12 |
| Granite 4.1-3B Q4_0 | 1 card | 0.13 | 9 |

The 14B across both cards is the best coder this box can run at interactive speed: 0.48 on v2 in 25 s per problem, versus the CPU's Qwen3.6-35B-A3B at 0.65 in 145 s. gpt-oss-20b again spends its budget on reasoning (14 of 23 answers hit the 1024-token cap). The 3B single-card model that serves on port 8081 is a boilerplate assistant (0.13), not a component writer.

## Recommendation for this tier
- Coding assistant: **Granite 4.1-3B Q4_0 on one card** (37 tok/s, v1 0.91 / v2 0.13, 3.8 s/problem) for snappy completions; **Qwen2.5-Coder-14B Q4_0 across both cards** (13.8 tok/s, v1 0.91 / v2 0.48) when quality per answer matters more than speed. Qwen2.5-Coder-7B Q4_0 on one card sits between them (25 tok/s, 0.91, 4.5 s). Leave the 30B-A3B MoE on the CPU.
- Log triage: same verdict as the CPU tier; the GPU only makes the wrong tool faster.
- Serve with `deploy/xeon/llama-coder.service` variants: add `-ngl 99 -ub 256 -fa off`, run the unit with `SupplementaryGroups=render`, and set `GGML_VK_VISIBLE_DEVICES=0` for single-card units.

## Serving (enabled 2026-10-23)

`deploy/xeon/llama-coder-gpu.service` is enabled as a user unit on og128x01 (`systemctl --user enable --now llama-coder-gpu`; the user instance already carried the `render` group and lingering is on, so it survives logout and reboot). Granite 4.1-3B Q4_0 on the first Vulkan device (`GGML_VK_VISIBLE_DEVICES=0`, which is DRM `card1`: 3.0 GB of its VRAM in use while serving, card0 idle), OpenAI-compatible API at `http://127.0.0.1:8081/v1`, 8192 context, one slot.

Smoke test the same day: `/health` answered within 4 s of start; a 54-token completion for a short docstring-to-function prompt came back correct in 2.0 s (26.5 tok/s end to end, including prompt processing). Nothing else uses card 0; Nomad's CPU-only llama.cpp job on this host is unaffected. The fleet-level version of this (a Vulkan engine job in outpost) is tracked at https://github.com/justizin/outpost/issues/10.
