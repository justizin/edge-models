"""Score a model's coding answers. extract_code(text) pulls the first python code block (or whole text);
run_tests(code, tests, entry) executes in a subprocess with a timeout. Returns True on pass."""
import re, subprocess, sys, tempfile, os
def extract_code(text: str) -> str:
    m = re.findall(r"```(?:python|py)?\s*\n(.*?)```", text, re.S)
    if m:
        # prefer the block that defines a function
        for b in m:
            if "def " in b: return b
        return m[0]
    return text
SYSTEM = "You are a coding assistant. Reply with only a single Python code block containing the complete function. No explanations, no example usage, no tests."
def run_tests(code: str, tests: str, entry: str, timeout=10) -> tuple[bool, str]:
    src = code + "\n\n" + f"assert callable({entry})\n" + tests + "\nprint('PASS')\n"
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(src); path = f.name
    try:
        r = subprocess.run([sys.executable, "-I", path], capture_output=True, text=True, timeout=timeout)
        ok = r.returncode == 0 and "PASS" in r.stdout
        return ok, (r.stderr.strip().splitlines() or [""])[-1]
    except subprocess.TimeoutExpired:
        return False, "timeout"
    finally:
        os.unlink(path)
