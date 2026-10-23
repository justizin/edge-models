# Junos Evolved virtual lab (cJunosEvolved)

Purpose: prove the Junos Evolved container path (`docs/tiers/switches-junos.md`) before touching real QFX/PTX/ACX gear: Docker present on the control plane, `/var/extensions` layout, the 2 GB / 20%-core cap, and a scratch image with the static llama.cpp running under that cap.

## Image

cJunosEvolved is free (no Juniper account) but sits behind a click-through EULA, so the download is a manual step:

1. Open https://support.juniper.net/support/downloads/?p=cjunos-evolved, pick version **26.2R1** (25.4 and 25.2 are also listed), then under *Container* choose **Docker Tarball - AMD64** (1,910,463,309 bytes, sha256 `7523c50bbc28ec02f68e520c2f8424560dfa5024092520b323bd07b840c2aeea`). Accept the EULA.
2. Save it as `labs/junos-evolved/images/cJunosEvolved-26.2R1-EVO.tar.gz` (the directory is gitignored).
3. `sha256sum` it against the value above, then `docker load -i labs/junos-evolved/images/cJunosEvolved-26.2R1-EVO.tar.gz` and `docker tag <loaded image> cjunosevolved:latest`.

The same portal entry lists two *Sample Docker Compose deploy YAML* files with the official run flags; download them into `labs/junos-evolved/images/` as well.

Metadata without a browser: `https://webdownload.juniper.net/swdl/web/site/1/platform/cjunos-evolved/content.json` lists releases, sizes and checksums. The file itself is served only after the EULA form.

## Host prerequisites (sudo, once)

```
sudo usermod -aG kvm sneakernaut
echo "deb [trusted=yes] https://netdevops.fury.site/apt/ /" | sudo tee /etc/apt/sources.list.d/netdevops.list
sudo apt update && sudo apt install containerlab
```

Log out and back in afterwards. The docker daemon runs as root, so `run.sh` (plain `docker run --device /dev/kvm`) works even without the `kvm` group; containerlab is only needed for the topology file.

## Run

- containerlab: `containerlab deploy -t labs/junos-evolved/junos-evolved.clab.yml`, node `clab-evo-evo1`.
- plain docker: `sh labs/junos-evolved/run.sh`, container `evo1`, SSH on 127.0.0.1:2222.
- Boot takes about 5 minutes: `docker logs -f <container>`. Login `admin` / `admin@123`. `docker exec -ti <container> cli` for Junos, `bash` for the Linux side.

## What to check on the node

```
show version
start shell
docker ps; systemctl status docker; cat /etc/extensions/platform_attributes; df -h /var/extensions
```

Then load `deploy/junos/out/llama-<model>.tar` (built by `deploy/junos/build-image.sh`) with `docker load`, run it with the default cap, and bench with `llama-bench -t 1 -p 128 -n 32` inside it. Results go to `results/cjunosevolved-26.2R1/`.

## Status 2026-10-23

Topology, run script and image builder written; not booted yet. Blocked on the EULA download above and on the host `kvm` group / containerlab install. Tracked in issue #6.
