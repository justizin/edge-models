#!/bin/sh
# Fingerprint this host -> results/<host>/probe.json. Works on Linux, BSD, macOS, busybox.
. "$(dirname "$0")/common.sh"
out="$RESULTS/probe.json"
kv() { printf '  "%s": "%s",\n' "$1" "$(printf '%s' "$2" | tr -d '"' | tr '\n' ' ' | sed 's/  */ /g;s/ $//')"; }
{
echo "{"
kv host "$HOSTTAG"
kv date "$(stamp)"
kv os "$(uname -s)"
kv kernel "$(uname -r)"
kv arch "$(uname -m)"
kv distro "$( (. /etc/os-release 2>/dev/null && echo "$PRETTY_NAME") || sw_vers -productName 2>/dev/null || echo unknown)"
kv cpu_model "$( (grep -m1 -E 'model name|Hardware|Model' /proc/cpuinfo 2>/dev/null | cut -d: -f2-) || sysctl -n machdep.cpu.brand_string hw.model 2>/dev/null | head -1)"
kv cpu_count "$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null)"
kv cpu_flags "$( (grep -m1 -E '^(flags|Features)' /proc/cpuinfo 2>/dev/null | cut -d: -f2- | tr ' ' '\n' | grep -E -x 'sse4_2|avx|avx2|fma|f16c|avx512f|avx512_vnni|amx_int8|asimd|asimddp|asimdhp|i8mm|sve|neon' | tr '\n' ' ') )"
kv mem_total_mb "$( (grep MemTotal /proc/meminfo 2>/dev/null | awk '{print int($2/1024)}') || sysctl -n hw.memsize hw.physmem 2>/dev/null | head -1 | awk '{print int($1/1048576)}')"
kv gpu "$( (lspci 2>/dev/null | grep -iE 'vga|3d|display' | sed 's/^[^ ]* //' | tr '\n' ';') )"
kv gpu_driver "$( for c in /sys/class/drm/card[0-9]; do [ -e "$c/device/driver" ] && basename "$(readlink "$c/device/driver")"; done 2>/dev/null | sort -u | tr '\n' ' ')"
kv vulkan "$( (timeout 10 vulkaninfo --summary 2>/dev/null | grep deviceName | sed 's/.*= //' | tr '\n' ';') )"
kv disk_free_gb "$(df -Pk "$ROOT" 2>/dev/null | awk 'NR==2{print int($4/1048576)}')"
kv llama_bin "$LLAMA_BIN"
kv llama_commit "$(git -C "$(dirname "$LLAMA_BIN")/.." rev-parse --short HEAD 2>/dev/null)"
printf '  "_": null\n}\n'
} > "$out"
echo "wrote $out"; cat "$out"
