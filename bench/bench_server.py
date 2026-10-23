#!/usr/bin/env python3
"""Run a task set (coding | ids) against llama-server's OpenAI-compatible API and record score + latency.
usage:
  bench_server.py --task coding|coding-v2 --model-id qwen3.5-0.8b-q8 [--threads 12] [--ngl 0] [--limit N]
  bench_server.py --task ids --url http://127.0.0.1:8080 --model-id <label>      # use an already running server
Spawns llama-server itself when --model-id or --model-path is given (stdlib only; no manifest needed for --model-path).
Writes results/<host>/task-<stamp>-<task>-<model_id>.json"""
import argparse, json, os, sys, time, subprocess, socket, statistics, urllib.request, glob, platform
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "bench", "tasks", "coding")); sys.path.insert(0, os.path.join(ROOT, "bench", "tasks", "ids"))
def manifest_path(mid):
    import yaml
    hf = os.environ.get("HF_HOME", os.path.expanduser("~/.cache/huggingface"))
    for m in yaml.safe_load(open(os.path.join(ROOT, "models", "manifest.yaml")))["models"]:
        if m["id"] == mid:
            hits = glob.glob(os.path.join(hf, "hub", "models--" + m["repo"].replace("/", "--"), "snapshots", "*", m["files"][0]))
            if not hits: sys.exit(f"{mid} not downloaded")
            return hits[0]
    sys.exit("unknown model id " + mid)
def free_port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p
def start_server(model, threads, ngl, ctx, extra):
    port = free_port()
    bin = os.path.join(os.environ.get("LLAMA_BIN", os.path.expanduser("~/src/llama.cpp/build/bin")), "llama-server")
    cmd = [bin, "-m", model, "--host", "127.0.0.1", "--port", str(port), "-t", str(threads), "-ngl", str(ngl), "-c", str(ctx), "-np", "1", "--jinja"] + extra
    log = open(os.path.join(ROOT, "results", "server.log"), "w")
    p = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT)
    url = f"http://127.0.0.1:{port}"
    for _ in range(600):
        if p.poll() is not None: sys.exit("llama-server exited; see results/server.log")
        try:
            if urllib.request.urlopen(url + "/health", timeout=2).status == 200: return p, url
        except Exception: time.sleep(0.5)
    sys.exit("server did not become healthy")
def chat(url, system, user, max_tokens, temperature=0.0):
    body = json.dumps({"messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
                       "max_tokens": max_tokens, "temperature": temperature, "chat_template_kwargs": {"enable_thinking": False}}).encode()
    req = urllib.request.Request(url + "/v1/chat/completions", data=body, headers={"Content-Type": "application/json"})
    t = time.perf_counter(); r = json.load(urllib.request.urlopen(req, timeout=1800)); dt = time.perf_counter() - t
    return r["choices"][0]["message"]["content"], dt, r.get("usage", {})
def run_coding(url, limit, log, version="v1"):
    import score
    problems = __import__("problems_v2" if version == "v2" else "problems")
    items = problems.P[:limit] if limit else problems.P
    ok = 0; lat = []; per = []
    for p in items:
        text, dt, usage = chat(url, score.SYSTEM, p["prompt"], p.get("max_tokens", 512))
        code = score.extract_code(text); passed, err = score.run_tests(code, p["tests"], p["entry"], timeout=p.get("timeout", 10))
        ok += passed; lat.append(dt); per.append(dict(id=p["id"], kind=p["kind"], passed=passed, err=err, s=round(dt, 2), out_tokens=usage.get("completion_tokens")))
        log(f"  {'PASS' if passed else 'FAIL'} {p['id']:<22} {dt:6.1f}s {'' if passed else err[:60]}")
    return dict(score=round(ok / len(items), 3), n=len(items), passed=ok, median_latency_s=round(statistics.median(lat), 2), items=per)
def run_ids(url, limit, log):
    import prompt as ip, baselines
    rows = [json.loads(l) for l in open(os.path.join(ROOT, "bench", "tasks", "ids", "dataset.jsonl"))]
    if limit: rows = rows[:limit]
    y = [r["label"] for r in rows]; pred = []; lat = []; per = []; unparsed = 0
    for r in rows:
        text, dt, _ = chat(url, ip.SYSTEM, "Log line: " + r["line"], 8)
        lab = ip.parse(text); unparsed += lab < 0; lab = max(lab, 0)
        pred.append(lab); lat.append(dt); per.append(dict(family=r["family"], label=r["label"], pred=lab, raw=text.strip()[:40], s=round(dt, 3)))
        if lab != r["label"]: log(f"  MISS {r['family']:<22} truth={r['label']} pred={lab} raw={text.strip()[:30]!r}")
    m = baselines.prf(y, pred)
    fam = {}
    for p in per:
        f = fam.setdefault(p["family"], [0, 0]); f[1] += 1; f[0] += p["pred"] == p["label"]
    return dict(score=m["f1"], n=len(rows), metrics=m, unparsed=unparsed, median_latency_s=round(statistics.median(lat), 3),
                per_family_acc={k: round(v[0] / v[1], 2) for k, v in fam.items()}, items=per)
def main():
    a = argparse.ArgumentParser(); a.add_argument("--task", required=True, choices=["coding", "coding-v2", "ids"])
    a.add_argument("--model-id"); a.add_argument("--model-path"); a.add_argument("--url")
    a.add_argument("--threads", type=int, default=os.cpu_count()); a.add_argument("--ngl", type=int, default=0); a.add_argument("--ctx", type=int, default=4096)
    a.add_argument("--limit", type=int, default=0); a.add_argument("--notes", default=""); a.add_argument("--server-args", default="")
    o = a.parse_args()
    host = os.environ.get("HOSTTAG", platform.node().split(".")[0]); os.makedirs(os.path.join(ROOT, "results", host), exist_ok=True)
    mid = o.model_id or (os.path.basename(o.model_path).replace(".gguf", "") if o.model_path else "external")
    proc = None; url = o.url
    if not url:
        path = o.model_path or manifest_path(o.model_id)
        proc, url = start_server(path, o.threads, o.ngl, o.ctx, o.server_args.split())
    print(f"== {o.task} on {mid} via {url}")
    try:
        if o.task == "ids": res = run_ids(url, o.limit, print)
        else: res = run_coding(url, o.limit, print, version="v2" if o.task == "coding-v2" else "v1")
    finally:
        if proc: proc.terminate(); proc.wait(timeout=30)
    res.update(task=o.task, model_id=mid, host=host, threads=o.threads, ngl=o.ngl, notes=o.notes, date=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    out = os.path.join(ROOT, "results", host, f"task-{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}-{o.task}-{mid}.json")
    json.dump(res, open(out, "w"), indent=1)
    print(f"score={res['score']} n={res['n']} median_latency={res['median_latency_s']}s -> {out}")
if __name__ == "__main__": main()
