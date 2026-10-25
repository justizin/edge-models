#!/usr/bin/env bash
# Run every lesson script in order. Each script ends with assertions, so this doubles as the test suite.
# Usage: learn/run_all.sh            (from the repo root; uses .venv/bin/python)
set -euo pipefail
cd "$(dirname "$0")/.."
PY=${PY:-.venv/bin/python}
export MPLBACKEND=Agg
fail=0
for f in learn/[0-9][0-9]-*/*.py; do
  case "$(basename "$f")" in gen_*|_*) continue;; esac   # data generators run on demand, not here
  printf '\n=== %s\n' "$f"
  if ! "$PY" "$f" > /tmp/learn-run.log 2>&1; then
    echo "FAILED: $f"; tail -20 /tmp/learn-run.log; fail=1
  else
    tail -3 /tmp/learn-run.log
  fi
done
[ "$fail" = 0 ] && echo && echo "all lessons passed"
exit $fail
