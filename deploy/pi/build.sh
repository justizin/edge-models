#!/bin/sh
# Build llama.cpp natively on a Raspberry Pi (or any arm64 Linux). Run ON the Pi.
# Pi 5 (Cortex-A76): dotprod + fp16 kernels light up automatically via -march=native.
# Pi 4 (Cortex-A72): no dotprod; expect ~3-4x slower generation than Pi 5 at the same model.
set -e
sudo apt-get install -y git cmake build-essential libcurl4-openssl-dev
mkdir -p ~/src && cd ~/src
[ -d llama.cpp ] || git clone --depth 1 https://github.com/ggml-org/llama.cpp
cd llama.cpp
cmake -B build -DGGML_NATIVE=ON -DLLAMA_CURL=ON -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release -j"$(nproc)" --target llama-bench llama-server llama-completion
echo "built: $(ls build/bin)"
echo "next:  git clone <edge-models repo>; sh bench/probe.sh; sh bench/bench_llamacpp.sh /path/to/model.gguf"
