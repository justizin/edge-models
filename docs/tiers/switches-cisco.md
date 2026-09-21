# Tier: Cisco NX-OS (Nexus 9000) and IOS-XE (Catalyst 9000)

Facts from `docs/research-2026-09-20.md` §5.

## NX-OS on Nexus 9000 (x86, Broadwell-DE / Xeon-D)
- Guest Shell 4.x = Rocky 9 / Python 3.9 (NX-OS 10.4+). Defaults are tiny (1% CPU / 400 MB / 200 MB rootfs); `guestshell resize` up to 620% CPU / 3,840 MB / 2,000 MB. Disabled by default on 4 GB boxes.
- `feature bash-shell` gives native bash; dnf from devhub.cisco.com; RPMs persist in `/bootflash/.rpmstore`.
- Docker CE 18.09 is bundled: needs ≥8 GB RAM, storage carved from bootflash (2000 MB default), `service docker start`, host networking OK, recommended `--cgroup-parent=/ext_ser/` (25% CPU per core).
- RAM: 9300-EX 24 GB, 93180YC-FX up to 32 GB, 93180YC-FX3 16 GB; NX-OS idle uses ~6.3 GB on a 16 GB box.
- Plan: guest shell resized to ~2 GB for the static `x86-64-v3` build (Xeon-D has AVX2) with a 0.8–2B model; or Docker with the same. Virtual: Nexus 9000v (Cisco.com login, likely service contract), containerlab `cisco_n9kv`, 4 vCPU / 10 GB.

## IOS-XE on Catalyst 9000 (IOx app hosting)
- Native Docker images since 16.12.1. **DNA Advantage license required.** 9200 and UADP-2.0 9500 not supported.
- Caps: 9300 = 2 GB RAM, 25% CPU (2 vCPU), model storage on the 120 GB USB 3.0 SSD in the rear port; 9300X = 8 GB / 4 vCPU; 9400/9500-HP/9600 = up to 8 GB, 25% CPU, M.2 SSD.
- Plan: only if a licensed unit with SSD is on hand. Package the static build as an IOx docker-type app; 2 GB cap means 0.8B Q8 or 2B Q4. Virtual Cat9kv exists only in the paid CML refplat, so real hardware is the first test.

## Console probe (both)
`show version`, `show inventory`, then from bash/guestshell: `nproc; free -m; grep -m1 flags /proc/cpuinfo; df -h /bootflash`. Record in `docs/inventory.md` and `results/<switch>/probe.json` (copy `bench/probe.sh` over the console session or paste its output).
