#!/usr/bin/env python3
"""Regenerate the results tables in README.md from results/**.json.
Everything between <!-- results:start --> and <!-- results:end --> is replaced."""
import json, glob, os, re, sys, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load():
    probes, rows, tasks = {}, [], []
    for host in sorted(os.listdir(os.path.join(ROOT, "results"))):
        d = os.path.join(ROOT, "results", host)
        if not os.path.isdir(d): continue
        p = os.path.join(d, "probe.json")
        if os.path.exists(p): probes[host] = json.load(open(p))
        for f in sorted(glob.glob(os.path.join(d, "bench-*.json"))):
            try: rows += json.load(open(f))
            except Exception as e: print("bad", f, e, file=sys.stderr)
        for f in sorted(glob.glob(os.path.join(d, "task-*.json"))):
            try: tasks.append(json.load(open(f)))
            except Exception as e: print("bad", f, e, file=sys.stderr)
    return probes, rows, tasks
def hosts_table(probes):
    out = ["| host | cpu | cores | simd | ram | gpu (driver) | llama.cpp |", "|---|---|---|---|---|---|---|"]
    for h, p in probes.items():
        gpu = (p.get("gpu") or "-").split(";")[0].replace("VGA compatible controller: ", "")[:60]
        out.append(f"| {h} | {p.get('cpu_model','').strip()} | {p.get('cpu_count')} | {p.get('cpu_flags')} | {int(p.get('mem_total_mb') or 0)//1024} GB | {gpu} ({p.get('gpu_driver') or '-'}) | {p.get('llama_commit')} |")
    return "\n".join(out)
def bench_table(rows):
    # best (host, model, ngl) over threads: pick max avg_ts for pp and tg separately, note threads used
    best = {}
    for r in rows:
        key = (r["host"], r["model_id"], r["n_gpu_layers"])
        kind = "pp" if r["n_prompt"] > 0 else "tg"
        cur = best.setdefault(key, {})
        if kind not in cur or r["avg_ts"] > cur[kind][0]:
            cur[kind] = (r["avg_ts"], r["n_threads"], r["model_size"] / 1e9, r["model_type"], r["n_prompt"] or r["n_gen"])
    out = ["| host | model | quant/size | ngl | prompt tok/s (threads) | gen tok/s (threads) |", "|---|---|---|---|---|---|"]
    for (h, m, ngl), v in sorted(best.items()):
        pp = v.get("pp"); tg = v.get("tg"); mt = (pp or tg)[3]; sz = (pp or tg)[2]
        out.append(f"| {h} | {m} | {mt.split(' ')[-1]} {sz:.2f} GB | {ngl} | " + (f"{pp[0]:.1f} (t={pp[1]})" if pp else "-") + " | " + (f"{tg[0]:.1f} (t={tg[1]})" if tg else "-") + " |")
    return "\n".join(out)
def task_table(tasks):
    if not tasks: return "_no task runs yet_"
    out = ["| host | task | model | score | n | median latency s | notes |", "|---|---|---|---|---|---|---|"]
    for t in tasks:
        out.append(f"| {t.get('host')} | {t.get('task')} | {t.get('model_id')} | {t.get('score')} | {t.get('n')} | {t.get('median_latency_s','-')} | {t.get('notes','')} |")
    return "\n".join(out)
def main():
    probes, rows, tasks = load()
    body = "\n".join(["### Hosts probed", "", hosts_table(probes), "", "### llama-bench throughput (best over thread counts)", "",
                      bench_table(rows), "", "### Task scores", "", task_table(tasks), ""])
    readme = os.path.join(ROOT, "README.md")
    txt = open(readme).read()
    new = re.sub(r"<!-- results:start -->.*<!-- results:end -->", "<!-- results:start -->\n" + body + "<!-- results:end -->", txt, flags=re.S)
    open(readme, "w").write(new)
    print(f"{len(probes)} hosts, {len(rows)} bench rows, {len(tasks)} task runs -> README.md")
if __name__ == "__main__": main()
