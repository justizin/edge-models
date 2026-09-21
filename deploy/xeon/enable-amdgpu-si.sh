#!/bin/sh
# Move Southern Islands (GCN 1.0, e.g. Radeon HD 7970) cards from the legacy 'radeon' driver to 'amdgpu'
# so RADV Vulkan can drive them. Run as root: sudo sh deploy/xeon/enable-amdgpu-si.sh ; then reboot.
# Rollback: restore /etc/default/grub.bak-amdgpu-si and run update-grub.
set -e
f=/etc/default/grub
grep -q 'amdgpu.si_support=1' "$f" && { echo "already set"; grep '^GRUB_CMDLINE_LINUX_DEFAULT' "$f"; exit 0; }
cp -n "$f" "$f.bak-amdgpu-si"
sed -i 's/^GRUB_CMDLINE_LINUX_DEFAULT="\(.*\)"/GRUB_CMDLINE_LINUX_DEFAULT="\1 radeon.si_support=0 amdgpu.si_support=1"/' "$f"
grep '^GRUB_CMDLINE_LINUX_DEFAULT' "$f"
update-grub
echo "done; reboot to apply"
