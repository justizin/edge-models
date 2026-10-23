# Task: simple coding assistant

Measures whether a model can act as a low-end coding helper: write a short correct function from a signature + docstring, or fix an obvious bug.

- Set: `bench/tasks/coding/problems.py`, 22 original problems (18 write, 4 fix). Original so nothing is memorized from HumanEval/MBPP; the bar is deliberately low.
- Prompting: system prompt demands a single Python code block; temperature 0; max 512 tokens; thinking disabled where the template supports it.
- Scoring: `bench/tasks/coding/score.py` extracts the first code block and runs hidden asserts in an isolated subprocess with a 10 s timeout. Metric: pass@1.
- Latency: wall time per problem against `llama-server` on the same host, recorded per item.
- Run: `.venv/bin/python bench/bench_server.py --task coding --model-id <id> --threads 12`

Interpretation guide: below ~0.5 the model is not useful as an assistant; 0.7+ on this set is "fine for boilerplate"; the fix problems separate models that read code from ones that pattern-match.

## v2 set (2026-10-23)

v1 saturates at 3B: on the Xeon, Granite 4.1-3B, Qwen3-Coder-30B-A3B, Qwen3.5-4B, Qwen2.5-Coder-3B/7B and Qwen3.5-9B all land within one problem of each other. v2 exists to spread them.

- Set: `bench/tasks/coding/problems_v2.py`, 23 original problems (17 write, 6 fix/refactor). Solutions run 15-60 lines: stateful classes with injected clocks (LRU+TTL, token bucket, undo stack), parsers (nginx combined log, INI with `${}` interpolation and cycle detection, CIDR aggregation, cron fields, logfmt), small algorithms (Kahn toposort with cycle report, meeting rooms, Dijkstra with lexicographic ties, LCS diff, knapsack), string engines (glob, expression evaluator with precedence and `**`, templating with filters and escapes), and bug reports phrased the way a user would write them (pagination, naive vs aware datetimes, class-level mutable state, float money, dict mutated during iteration, a backwards-compatible refactor adding keyword arguments).
- Every hidden test was verified against a reference solution before any model saw it (23/23).
- Prompting: same system prompt as v1; max 1024 tokens per answer; tests get a 15 s timeout.
- Run: `.venv/bin/python bench/bench_server.py --task coding-v2 --model-id <id> --threads 24`. Results carry `task = coding-v2` in the README table.

Interpretation guide: the edge cases are in the docstrings, so a model that reads the spec scores far above one that writes the obvious version. Below 0.3 the model writes plausible but untested code; 0.5 is "a real assistant for small components"; above 0.7 it is reading specs carefully. The fix problems distinguish models that locate the described symptom from ones that rewrite the function.
