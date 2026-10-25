# Roadmap

Status of each phase and the work that can proceed without hardware. Each open item is a GitHub issue; results land in `results/<host>/` and the tier docs under `docs/tiers/`.

## Phases

| phase | tier | status | issue |
|---|---|---|---|
| 1 | Xeon E5-2697 v2, AVX only (`docs/tiers/xeon-avx.md`) | done 2026-09-21 | |
| 1b | quant-format comparison, MoE and gpt-oss on the Xeon | done 2026-09-22 | |
| 2 / 2b / 2c | 2x FirePro D700 via RADV Vulkan (`docs/tiers/radeon-gcn1-vulkan.md`) | done 2026-09-22 | |
| 3 | Raspberry Pi (`docs/tiers/raspberry-pi.md`) | awaiting device list | [#1](https://github.com/justizin/edge-models/issues/1) |
| 4 | iOS devices (`docs/tiers/ios.md`) | awaiting device list | [#2](https://github.com/justizin/edge-models/issues/2) |
| 5 | switch control planes (`docs/tiers/switches-*.md`) | awaiting inventory | [#3](https://github.com/justizin/edge-models/issues/3) |
| 6 | other devices (`docs/tiers/other-devices.md`) | open-ended | [#4](https://github.com/justizin/edge-models/issues/4) |

What unblocks phases 3 to 5: for each device, the model, RAM, OS version, and how to reach it (SSH host, USB serial path, or "will plug it in"). Add it to `docs/inventory.md`.

## Work that needs no hardware

| item | status | issue |
|---|---|---|
| static x86-64 llama.cpp build for switch control planes (`deploy/static/`) | done 2026-10-23 | [#5](https://github.com/justizin/edge-models/issues/5) |
| Junos Evolved virtual lab (cJunosEvolved) to prove container packaging (`labs/junos-evolved/`) | scaffolding done; blocked on EULA download and host KVM access | [#6](https://github.com/justizin/edge-models/issues/6) |
| coding task set v2 that separates the 3B / 7B / MoE models | done 2026-10-23 (`docs/tasks/coding.md`) | [#7](https://github.com/justizin/edge-models/issues/7) |
| GPU coder service on the Mac Pro (`deploy/xeon/llama-coder-gpu.service`) | enabled 2026-10-23 | [#8](https://github.com/justizin/edge-models/issues/8) |
| IDS task v2 on real log samples | open | [#9](https://github.com/justizin/edge-models/issues/9) |
| neural-network learning track: numpy + torch twins from a single neuron to flow IDS and adversarial examples (`learn/`) | batch 1 (lessons 01-04, 06) 2026-10-25 | |

The fleet-level variant of the GPU service (a Nomad job in [justizin/outpost](https://github.com/justizin/outpost) using the `server-vulkan` image with `/dev/dri` passthrough) is tracked there.
