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

### v2 results (2026-10-23, llama.cpp b11796, pass@1 of 23, median seconds per problem)

| model | where | v2 | v1 | s |
|---|---|---|---|---|
| Qwen3.6-35B-A3B Q4_K_M | CPU 24t | **0.65** | 1.00 | 145 |
| Qwen2.5-Coder-14B Q4_0 | 2x D700 | 0.48 | 0.91 | 25 |
| Qwen3.5-9B Q4_K_M | CPU 24t | 0.39 | 0.91 | 138 |
| Qwen3-Coder-30B-A3B Q4 | CPU 24t | 0.30 | 0.95 | 50 |
| gpt-oss-20b MXFP4 | 2x D700 | 0.26 | 0.86 | 50 |
| Qwen3.5-4B Q4_K_M | CPU 24t | 0.22 | 0.95 | 140 |
| Qwen2.5-Coder-7B Q4_K_M | CPU 24t | 0.17 | 0.91 | 37 |
| Qwen2.5-Coder-7B Q4_0 | 1x D700 | 0.13 | 0.91 | 12 |
| Granite 4.1-3B Q4_0 | 1x D700 | 0.13 | 0.91 | 9 |
| Granite 4.1-3B Q4_K_M | CPU 24t | 0.09 | 0.95 | 22 |
| Qwen2.5-Coder-3B Q4_K_M | CPU 24t | 0.09 | 0.91 | 18 |
| Qwen2.5-Coder-1.5B Q4_K_M | CPU 24t | 0.00 | 0.73 | 12 |

What v2 shows that v1 could not:
- The ranking is now monotone in capability rather than flat: 1.5B 0, 3B ~0.1, 7B 0.13-0.17, 4B/9B dense Qwen3.5 0.22/0.39, 14B 0.48, Qwen3.6-35B-A3B 0.65. Five models that tied on v1 now span 0.09 to 0.65.
- Qwen3.6-35B-A3B is the only model that reads specs: it is the sole solver of `undo_stack` and `template_render` and passes 5 of 6 bug reports. Qwen3-Coder-30B-A3B (older, coding-tuned) loses to the general 9B dense model here.
- Qwen3.5 dense models write long: 4B hit the 1024-token cap on 5 problems, 9B on 1, the 35B on 4 (all `SyntaxError` from truncated code: `dijkstra_path`, `diff_hunks`, `knapsack_items`, `expr_eval`). gpt-oss-20b hit it on 14 of 23 because its reasoning shares the budget. The cap is deliberate: an assistant that needs more than 1024 tokens for a 40-line function is slow on this hardware anyway. A later v2.1 could raise it to 1536 for the algorithm problems to separate "cannot" from "verbose".
- Nothing solved `ini_interp`, `glob_match`, `expr_eval` or `fix_pagination`. `fix_pagination` was partly the spec's fault (the empty-list case was ambiguous); it was clarified in `problems_v2.py` after this run, which changes no score since no model passed it. The other three are legitimately hard for this size class.
- The easiest v2 problems are the bug reports whose symptom names the fix (`fix_naive_datetime` 9/12 runs, `fix_shared_state` 7/12); the hardest are the engines (glob, expression evaluator, templating) where one missed rule fails every assert.
- Cost: v2 at 24 CPU threads takes 2.5 h for the ladder (long answers at 5-11 tok/s); the GPU rows took 10-50 s per problem.
