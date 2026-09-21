#!/bin/sh
# Build a fully static, portable x86-64 llama.cpp (llama-bench, llama-completion, llama-server) for switch
# control planes and other boxes where we cannot install packages. Run on og128x01 (or any glibc Linux).
#
#   ARCH=x86-64-v2  (default) SSE4.2/POPCNT only: safe for Atom C2000/C3000, old Xeon-D, Ivy Bridge and up
#   ARCH=x86-64-v3           AVX2/FMA: for Xeon-D 1500+, Atom P-series, anything Haswell+
# Output: deploy/static/out/llama-<arch>-<commit>.tar.gz
set -e
ARCH="${ARCH:-x86-64-v2}"
SRC="${LLAMA_SRC:-$HOME/src/llama.cpp}"
HERE="$(cd "$(dirname "$0")" && pwd)"
B="$HERE/build-$ARCH"
cmake -S "$SRC" -B "$B" -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=OFF -DGGML_STATIC=ON \
  -DGGML_NATIVE=OFF -DGGML_VULKAN=OFF -DGGML_OPENMP=OFF -DLLAMA_CURL=OFF -DLLAMA_BUILD_TESTS=OFF -DLLAMA_BUILD_EXAMPLES=OFF \
  -DCMAKE_C_FLAGS="-march=$ARCH" -DCMAKE_CXX_FLAGS="-march=$ARCH" \
  -DCMAKE_EXE_LINKER_FLAGS="-static" \
  $( [ "$ARCH" = x86-64-v3 ] && echo "-DGGML_AVX2=ON -DGGML_FMA=ON -DGGML_F16C=ON -DGGML_AVX=ON" || echo "-DGGML_AVX=OFF -DGGML_AVX2=OFF -DGGML_FMA=OFF -DGGML_F16C=OFF -DGGML_SSE42=ON" )
cmake --build "$B" -j"$(nproc)" --target llama-bench llama-completion llama-server
commit="$(git -C "$SRC" rev-parse --short HEAD)"
mkdir -p "$HERE/out"; out="$HERE/out/llama-$ARCH-$commit.tar.gz"
tar -C "$B/bin" -czf "$out" llama-bench llama-completion llama-server
file "$B/bin/llama-bench"; ls -lh "$out"
