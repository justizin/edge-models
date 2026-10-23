#!/bin/sh
# Fallback without containerlab: boot cJunosEvolved with plain docker. Needs /dev/kvm on the host (the docker daemon
# runs as root, so the invoking user does not need the kvm group). Image: `docker load -i cJunosEvolved-*.tar.gz`,
# then `docker tag <image> cjunosevolved:latest`.
#   sh labs/junos-evolved/run.sh            # start, then: docker logs -f evo1   (~5 min until the login prompt)
#   docker exec -ti evo1 cli                # Junos CLI (admin / admin@123)
#   docker exec -ti evo1 bash               # Linux shell of the control plane
#   docker rm -f evo1                       # stop
set -e
IMAGE="${IMAGE:-cjunosevolved:latest}"
docker run -d --name evo1 --privileged --device /dev/kvm -p 2222:22 -p 8830:830 "$IMAGE"
echo "started evo1 from $IMAGE; ssh -p 2222 admin@127.0.0.1 once booted"
