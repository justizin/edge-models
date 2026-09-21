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
