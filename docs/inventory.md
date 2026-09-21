# Hardware inventory

Devices available for this project. Add a row when a device is identified; `bench/probe.sh` fills the details once it is reachable.

| device | class | cpu / soc | ram | os / version | reach (ssh, serial, usb) | status |
|---|---|---|---|---|---|---|
| og128x01 | x86 server | Xeon E5-2697 v2 (Ivy Bridge, AVX only) | 125 GB | Debian 13, kernel 6.12 | local | probed |
| og128x01 GPUs | 2x Radeon HD 7970 (Tahiti, GCN 1.0, 3 GB) | | | bound to `radeon`; needs amdgpu for Vulkan | local | pending reboot |
| Raspberry Pi(s) | arm64 sbc | ? | ? | ? | ? | awaiting list |
| iOS devices | phone / tablet | ? | ? | ? | usb | awaiting list |
| Arista switch(es) | switch | ? | ? | EOS ? | serial/usb | awaiting list |
| Cisco switch(es) | switch | ? | ? | NX-OS / IOS-XE ? | serial/usb | awaiting list |
| Juniper switch(es) | switch | ? | ? | Junos / Evolved ? | serial/usb | awaiting list |
| other boards | | | | | | "all the motherboards" |
