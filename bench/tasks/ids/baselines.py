"""Stdlib-only classical baselines for the IDS log-triage set, so they run on a Pi or a switch.
- rules(): hand-written regex rules (what a sysadmin would grep for)
- NaiveBayes: multinomial NB over tokens, trained on a split of the dataset
Both return label 1 (malicious) / 0 (benign)."""
import re, math, collections
RULES = [re.compile(p, re.I) for p in [
    r"invalid user", r"Accepted password for root from (?!10\.)", r"UNION(\s|%20)+SELECT|OR(\s|%20)+1=1|DROP(\s|%20)+TABLE|sqlmap",
    r"\.\./|%2e%2e|/etc/passwd|/\.env|/\.git/|wp-admin/setup", r"curl [^|]*\|\s*sh|wget [^|]*\|\s*sh",
    r"nc -e|/bin/sh -i|bash -i", r"name=(?!root)\S+, UID=0", r"DPT=(22|23|3389|445|1433) SYN",
]]
def rules(line: str) -> int:
    return int(any(r.search(line) for r in RULES))
TOK = re.compile(r"[A-Za-z_]{2,}|\d{1,3}(?:\.\d{1,3}){3}|[=/'|;]")
def tokens(line: str):
    # drop timestamp + pid digits; keep words, IPs, punctuation that matters
    return TOK.findall(line)
class NaiveBayes:
    def __init__(self, alpha=0.5): self.alpha = alpha
    def fit(self, lines, labels):
        self.c = {0: collections.Counter(), 1: collections.Counter()}; self.n = {0: 0, 1: 0}
        for l, y in zip(lines, labels):
            self.c[y].update(tokens(l)); self.n[y] += 1
        self.vocab = set(self.c[0]) | set(self.c[1])
        self.tot = {y: sum(self.c[y].values()) for y in (0, 1)}
        return self
    def predict(self, line) -> int:
        toks = tokens(line); V = len(self.vocab); s = {}
        for y in (0, 1):
            s[y] = math.log(self.n[y] / (self.n[0] + self.n[1]))
            for t in toks: s[y] += math.log((self.c[y][t] + self.alpha) / (self.tot[y] + self.alpha * V))
        return int(s[1] > s[0])
def prf(y_true, y_pred):
    tp = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 1)
    fp = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 1)
    fn = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 0)
    P = tp / (tp + fp) if tp + fp else 0.0; Rc = tp / (tp + fn) if tp + fn else 0.0
    F = 2 * P * Rc / (P + Rc) if P + Rc else 0.0
    return dict(precision=round(P, 3), recall=round(Rc, 3), f1=round(F, 3), tp=tp, fp=fp, fn=fn)
if __name__ == "__main__":
    import json, sys, time, os
    rows = [json.loads(l) for l in open(os.path.join(os.path.dirname(__file__), "dataset.jsonl"))]
    lines = [r["line"] for r in rows]; y = [r["label"] for r in rows]
    t = time.perf_counter(); pr = [rules(l) for l in lines]; dt = (time.perf_counter() - t) / len(lines)
    print("rules      ", prf(y, pr), f"{dt*1e6:.0f} us/line")
    # 5-fold CV for NB
    k = 5; preds = [None] * len(rows)
    for i in range(k):
        te = [j for j in range(len(rows)) if j % k == i]; tr = [j for j in range(len(rows)) if j % k != i]
        nb = NaiveBayes().fit([lines[j] for j in tr], [y[j] for j in tr])
        for j in te: preds[j] = nb.predict(lines[j])
    t = time.perf_counter(); nb.predict(lines[0]); dt = time.perf_counter() - t
    print("naive-bayes", prf(y, preds), f"{dt*1e6:.0f} us/line (5-fold CV)")
