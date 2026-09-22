#!/bin/sh
# Run llama-bench -> results/<host>/bench-<stamp>-<id>.json
# EXTRA="-ub 256 -fa off" adds raw llama-bench args. usage: bench_llamacpp.sh [-t threads] [-ngl N] [-p 512] [-n 128] [-r 3] [id|tag|/path/to/model.gguf ...]
# Bare .gguf paths work without the manifest (for Pis, switches, phones).
. "$(dirname "$0")/common.sh"
T="${THREADS:-$(nproc 2>/dev/null || echo 4)}"; NGL="${NGL:-0}"; P="${NP:-512}"; N="${NG:-128}"; R="${REPS:-3}"
while [ $# -gt 0 ]; do case "$1" in
  -t) T="$2"; shift 2;; -ngl) NGL="$2"; shift 2;; -p) P="$2"; shift 2;; -n) N="$2"; shift 2;; -r) R="$2"; shift 2;;
  *) break;; esac; done
targets=""
for a in "$@"; do
  case "$a" in *.gguf) targets="$targets $a";; *) targets="$targets $a";; esac
done
[ -z "$targets" ] && targets="$(select_models)"
for t in $targets; do
  case "$t" in
    *.gguf) mp="$t"; id="$(basename "$t" .gguf)";;
    *) ids="$(select_models "$t")"; [ -z "$ids" ] && { echo "unknown $t"; continue; }
       # a tag may expand to several ids: recurse
       if [ "$(echo "$ids" | wc -w)" -gt 1 ]; then THREADS="$T" NGL="$NGL" NP="$P" NG="$N" REPS="$R" sh "$0" $ids; continue; fi
       id="$ids"; mp="$(model_path "$id")";;
  esac
  [ -z "$mp" ] && { echo "skip   $id (not downloaded)"; continue; }
  out="$RESULTS/bench-$(stamp)-$id.json"
  echo "== $id  t=$T ngl=$NGL p=$P n=$N r=$R"
  "$LLAMA_BIN/llama-bench" -m "$mp" -t "$T" -ngl "$NGL" -p "$P" -n "$N" -r "$R" $EXTRA -o json 2>"$out.err" \
    | "$PY" -c "
import json,sys; rows=json.load(sys.stdin)
for r in rows: r.update(model_id='$id', host='$HOSTTAG')
json.dump(rows,open('$out','w'),indent=1)
for r in rows: print(f\"   {r['n_prompt']:>5}p {r['n_gen']:>4}g  t={r['n_threads']:<3} ngl={r['n_gpu_layers']:<3} {r['avg_ts']:8.2f} tok/s  ({r['model_type']} {r['model_size']/1e9:.2f}GB)\")
" || { echo "   FAILED, see $out.err"; tail -3 "$out.err"; }
done
