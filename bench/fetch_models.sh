#!/bin/sh
# Download manifest models into the HF cache with the hf CLI.
# usage: fetch_models.sh [id|tag ...]   (no args = everything in the manifest)
. "$(dirname "$0")/common.sh"
for id in $(select_models "$@"); do
  if [ -n "$(model_path "$id")" ]; then echo "have   $id"; continue; fi
  "$PY" - "$ROOT/models/manifest.yaml" "$id" <<'PYX' | while read -r repo f; do echo "fetch  $id $repo/$f"; "$HF" download "$repo" "$f" >/dev/null || echo "FAILED $id $f"; done
import yaml,sys
mf,mid=sys.argv[1:]
m=next(m for m in yaml.safe_load(open(mf))["models"] if m["id"]==mid)
for f in m["files"]: print(m["repo"],f)
PYX
done
