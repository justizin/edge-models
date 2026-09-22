#!/bin/sh
# Move Southern Islands (GCN 1.0, e.g. Radeon HD 7970) cards from the legacy 'radeon' driver to 'amdgpu'
# so RADV Vulkan can drive them. Run as root: sudo sh deploy/xeon/enable-amdgpu-si.sh ; then reboot.
# Rollback: restore /etc/default/grub.bak-amdgpu-si and run update-grub.
set -e
f=/etc/default/grub
if grep -q 'amdgpu.si_support=1' "$f"; then
  echo "parameters already in $f; regenerating grub.cfg"
else
  cp -n "$f" "$f.bak-amdgpu-si"
  sed -i 's/^GRUB_CMDLINE_LINUX_DEFAULT="\(.*\)"/GRUB_CMDLINE_LINUX_DEFAULT="\1 radeon.si_support=0 amdgpu.si_support=1"/' "$f"
fi
grep '^GRUB_CMDLINE_LINUX_DEFAULT' "$f"
update-grub
grep -c 'amdgpu.si_support=1' /boot/grub/grub.cfg >/dev/null && echo "grub.cfg now contains the parameters" || { echo "ERROR: grub.cfg still lacks the parameters"; exit 1; }
echo "done; reboot to apply"
