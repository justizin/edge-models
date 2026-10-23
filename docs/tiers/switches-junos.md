# Tier: Juniper Junos and Junos Evolved

Facts from `docs/research-2026-09-20.md` §5.

## Junos (FreeBSD-based: FreeBSD 12 from 21.1, FreeBSD 14 from 24.2R1)
**The static-binary plan is dead on classic Junos.** Veriexec blocks unsigned executables, there is no Linux compat layer, and JET only allows unsigned *Python*; signed C/C++ needs a Juniper certificate plus the JET VM.

What is left on-box:
- Python 3 scripts (`set system scripts language python3`), root-owned, run as op/event/commit scripts or from `start shell`.
- So the realistic on-box workload is the **stdlib classical IDS baseline**: `bench/tasks/ids/baselines.py` (regex rules + naive Bayes) runs in pure Python with no dependencies. Target: an event script that scores syslog lines and raises a custom syslog / SNMP trap on a MALICIOUS verdict.
- Any LLM work is off-box: export syslog / sFlow to a Pi or the Xeon.

## Junos Evolved (Linux, Yocto; kernel 5.15 on 24.4)
Only ACX7k, PTX10k, QFX5130/5220/5230/5240/5700. No EX platform runs Evolved.
- Docker present (`docker.service` must be enabled), images in `/var/extensions`, default cap **2 GB RAM / 20% of one core** (tunable via `/etc/extensions/platform_attributes`), `--net=host`, survives upgrades. Native (non-container) binaries must be IMA-signed, so container is the only path.
- Plan: package the `x86-64-v2` static llama.cpp build (`deploy/static/build.sh`) plus a 0.3–0.8B Q8/Q4_0 model into a scratch container; 2 GB cap means 0.8B Q8 (0.83 GB) plus KV cache fits, 2B Q4 (1.3 GB) is tight.
- Virtual: vJunosEvolved / cJunosEvolved are free, no account, containerlab kinds `juniper_vjunosevolved` / `juniper_cjunosevolved` (4 vCPU / 8 GB, needs KVM). Use this to test the container packaging before real hardware.

## Inventory questions for the user's Juniper gear
Model and Junos version decide everything: EX/QFX on classic Junos = Python-only path; QFX5k/PTX/ACX on Evolved = container path. Also: RAM and free space in `/var`.

## Virtual lab and packaging status (2026-10-23)

- `labs/junos-evolved/`: containerlab topology, plain-docker fallback (`run.sh`) and README for cJunosEvolved 26.2R1. The image is free but behind a click-through EULA, so the 1.9 GB download is a manual step; the host also needs `/dev/kvm` access. Not booted yet (issue #6).
- `deploy/junos/build-image.sh <model-id>` builds the payload: a `FROM scratch` image with the static x86-64-v2 `llama-server`/`llama-completion`/`llama-bench` plus one GGUF. With Qwen3.5-0.8B Q4_0 the saved image is 585 MB.
- Measured on og128x01 under the default Junos Evolved cap (`--memory 2g --cpus 0.2`, one thread): **1.6 tok/s prompt, 0.9 tok/s generation** for the 0.8B. At a full core (`--cpus 1`) the same model does 8.2 / 4.6, LFM2.5-350M 12.9 / 9.0, SmolLM2-135M 30.9 / 19.3. So the 20%-core default makes any LLM interactive-useless on Evolved; raising the cap in `/etc/extensions/platform_attributes` is a prerequisite, and even then only sub-400M models answer in seconds. The stdlib IDS baseline remains the realistic on-box workload; the LLM's job there is explaining flagged lines, not scanning them.
