#!/bin/sh
# Build a scratch-based container image holding the static x86-64-v2 llama.cpp plus one small GGUF, for Junos
# Evolved's Docker (default cap 2 GB RAM / 20% of one core; images live in /var/extensions). Also a fair stand-in
# for the EOS container-manager payload. Output: deploy/junos/out/llama-<model>.tar (docker save).
#   sh deploy/junos/build-image.sh qwen3.5-0.8b-q4_0        # model id from models/manifest.yaml
# On the switch:  docker load -i llama-<model>.tar
#   docker run -d --net=host --memory 2g --cpus 0.2 llama-edge:<model> --host 127.0.0.1 --port 8080 -t 1 -c 2048
set -e
cd "$(dirname "$0")/../.." || exit 1; ROOT="$(pwd)"
. bench/common.sh
MID="${1:-qwen3.5-0.8b-q4_0}"
MP="$(model_path "$MID")"; [ -n "$MP" ] || { echo "$MID not downloaded"; exit 1; }
TAR="$(ls -t deploy/static/out/llama-x86-64-v2-*.tar.gz 2>/dev/null | head -1)"; [ -n "$TAR" ] || { echo "run ARCH=x86-64-v2 sh deploy/static/build.sh first"; exit 1; }
CTX="$(mktemp -d)"; trap 'rm -rf "$CTX"' EXIT
mkdir -p "$CTX/llama"; tar -xzf "$TAR" -C "$CTX/llama"; cp "$MP" "$CTX/model.gguf"
cat > "$CTX/Dockerfile" <<DF
FROM scratch
COPY llama/llama-server llama/llama-completion llama/llama-bench /usr/bin/
COPY model.gguf /model.gguf
ENTRYPOINT ["/usr/bin/llama-server", "-m", "/model.gguf"]
CMD ["--host", "127.0.0.1", "--port", "8080", "-t", "1", "-c", "2048", "-np", "1"]
DF
docker build -q -t "llama-edge:$MID" "$CTX"
mkdir -p deploy/junos/out; docker save "llama-edge:$MID" -o "deploy/junos/out/llama-$MID.tar"
ls -lh "deploy/junos/out/llama-$MID.tar"
