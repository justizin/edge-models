# Task: simple coding assistant

Measures whether a model can act as a low-end coding helper: write a short correct function from a signature + docstring, or fix an obvious bug.

- Set: `bench/tasks/coding/problems.py`, 22 original problems (18 write, 4 fix). Original so nothing is memorized from HumanEval/MBPP; the bar is deliberately low.
- Prompting: system prompt demands a single Python code block; temperature 0; max 512 tokens; thinking disabled where the template supports it.
- Scoring: `bench/tasks/coding/score.py` extracts the first code block and runs hidden asserts in an isolated subprocess with a 10 s timeout. Metric: pass@1.
- Latency: wall time per problem against `llama-server` on the same host, recorded per item.
- Run: `.venv/bin/python bench/bench_server.py --task coding --model-id <id> --threads 12`

Interpretation guide: below ~0.5 the model is not useful as an assistant; 0.7+ on this set is "fine for boilerplate"; the fix problems separate models that read code from ones that pattern-match.
