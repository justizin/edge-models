# Shared helpers. Source from bench scripts.
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HF_HOME="${HF_HOME:-$HOME/.cache/huggingface}"
LLAMA_BIN="${LLAMA_BIN:-$HOME/src/llama.cpp/build/bin}"
HOSTTAG="${HOSTTAG:-$(hostname -s)}"
RESULTS="$ROOT/results/$HOSTTAG"
PY="${PY:-$ROOT/.venv/bin/python}"; [ -x "$PY" ] || PY=python3
HF="${HF:-$ROOT/.venv/bin/hf}"; [ -x "$HF" ] || HF=hf
mkdir -p "$RESULTS"
stamp() { date -u +%Y%m%dT%H%M%SZ; }
# select_models [id|tag ...] -> ids from manifest (all if no args)
select_models() {
  "$PY" - "$ROOT/models/manifest.yaml" "$@" <<'PYX'
import yaml,sys
mf,*sel=sys.argv[1:]
for m in yaml.safe_load(open(mf))["models"]:
    if not sel or m["id"] in sel or set(sel)&set(m["tags"]): print(m["id"])
PYX
}
# model_path <id> -> absolute path of first shard from the HF cache, or "" if not downloaded
model_path() {
  "$PY" - "$ROOT/models/manifest.yaml" "$HF_HOME" "$1" <<'PYX'
import yaml,sys,os,glob
mf,hf,mid=sys.argv[1:]
m=next((m for m in yaml.safe_load(open(mf))["models"] if m["id"]==mid),None)
if not m: sys.exit("unknown model id "+mid)
hits=glob.glob(os.path.join(hf,"hub","models--"+m["repo"].replace("/","--"),"snapshots","*",m["files"][0]))
print(hits[0] if hits else "")
PYX
}
