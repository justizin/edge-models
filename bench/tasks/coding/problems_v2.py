"""Coding set v2: harder original problems for pass@1 scoring, written 2026-10-23 because v1 saturates at 3B.
Same record schema as problems.py (id, prompt, entry, tests, kind) plus max_tokens and timeout. Each solution is
15-60 lines: stateful classes, parsers, small algorithms, and bug reports phrased the way a user would phrase them.
Hidden asserts hit the edge cases the docstring implies rather than the happy path only."""
P = []
def add(id, prompt, entry, tests, kind="write", max_tokens=1024, timeout=15):
    P.append(dict(id=id, prompt=prompt.strip() + "\n", entry=entry, tests=tests.strip(), kind=kind, max_tokens=max_tokens, timeout=timeout))

# ---- stateful / multi-function -------------------------------------------------------------------------
add("lru_ttl", '''
class LRUCache:
    """LRU cache with per-entry expiry.
    LRUCache(capacity, ttl, clock) where clock() returns the current time in seconds (injected for testing).
    get(key) -> value or None; a hit refreshes recency. Expired entries (age >= ttl) behave as missing and are dropped.
    put(key, value) inserts or updates (refreshing recency and the timestamp); when over capacity, evict the least
    recently used live entry, but evict expired entries first if any exist.
    __len__ counts live (unexpired) entries only."""
''', "LRUCache", '''
t = [0]
clk = lambda: t[0]
c = LRUCache(2, 10, clk)
c.put("a", 1); c.put("b", 2)
assert c.get("a") == 1
c.put("c", 3)                      # evicts b (a was refreshed)
assert c.get("b") is None and c.get("c") == 3 and c.get("a") == 1
t[0] = 10                          # a and c were written at t=0 -> expired
assert c.get("a") is None and len(c) == 0
c.put("d", 4); t[0] = 15; c.put("e", 5)
t[0] = 20                          # d expired (age 10), e alive (age 5)
assert len(c) == 1 and c.get("e") == 5 and c.get("d") is None
c.put("f", 6); c.put("g", 7)       # capacity 2: e (older use) goes
assert c.get("e") is None and c.get("f") == 6 and c.get("g") == 7
c.put("f", 60)
assert c.get("f") == 60
''')
add("token_bucket", '''
class TokenBucket:
    """Token-bucket rate limiter. TokenBucket(rate, capacity, clock): tokens refill continuously at `rate` per
    second up to `capacity`; the bucket starts full. clock() returns seconds (float) and is injected.
    allow(n=1) -> True and consume n tokens if at least n are available at the current time, else False
    (consuming nothing). available() -> current token count as a float, never above capacity."""
''', "TokenBucket", '''
t = [0.0]
b = TokenBucket(2.0, 4, lambda: t[0])
assert b.available() == 4
assert b.allow(3) and b.allow(1) and not b.allow(1)
t[0] = 0.5
assert abs(b.available() - 1.0) < 1e-9 and not b.allow(2) and b.allow(1)
t[0] = 100.0
assert b.available() == 4 and b.allow(4) and not b.allow()
t[0] = 100.25
assert not b.allow(1)
t[0] = 100.5
assert b.allow(1)
''')
add("merge_event_batches", '''
def merge_events(batches: list) -> list:
    """Each batch is a list of events, each event a dict with keys 'ts' (int), 'id' (str), 'data'.
    Batches arrive out of order and may overlap. Return a single list sorted by ts, then id, with duplicates
    (same id) collapsed: keep the event with the highest ts; on a tie keep the one seen last in input order.
    Do not mutate the input batches."""
''', "merge_events", '''
b1 = [{"ts": 5, "id": "x", "data": 1}, {"ts": 2, "id": "y", "data": 2}]
b2 = [{"ts": 5, "id": "x", "data": 9}, {"ts": 7, "id": "z", "data": 3}, {"ts": 1, "id": "w", "data": 0}]
out = merge_events([b1, b2])
assert [e["id"] for e in out] == ["w", "y", "x", "z"]
assert out[2]["data"] == 9
assert b1[0]["data"] == 1 and len(b1) == 2
assert merge_events([]) == []
assert merge_events([[{"ts": 3, "id": "a", "data": 1}], [{"ts": 9, "id": "a", "data": 2}], [{"ts": 4, "id": "a", "data": 3}]]) == [{"ts": 9, "id": "a", "data": 2}]
assert [e["id"] for e in merge_events([[{"ts": 1, "id": "b", "data": 0}, {"ts": 1, "id": "a", "data": 0}]])] == ["a", "b"]
''')
add("undo_stack", '''
class Editor:
    """Minimal text editor with undo/redo. Starts with empty text.
    insert(pos, s): insert s at index pos. delete(pos, n): delete n chars starting at pos (clamped to the text).
    undo() reverts the most recent edit; redo() re-applies the most recently undone edit. A new edit after undo
    discards the redo history. text() returns the current text. undo/redo with nothing to do are no-ops."""
''', "Editor", '''
e = Editor()
e.insert(0, "hello"); e.insert(5, " world"); e.delete(0, 1)
assert e.text() == "ello world"
e.undo(); assert e.text() == "hello world"
e.undo(); assert e.text() == "hello"
e.redo(); assert e.text() == "hello world"
e.redo(); assert e.text() == "ello world"
e.redo(); assert e.text() == "ello world"
e.undo(); e.insert(0, "J"); assert e.text() == "Jhello world"
e.redo(); assert e.text() == "Jhello world"
e.delete(100, 5); assert e.text() == "Jhello world"
e.delete(10, 50); assert e.text() == "Jhello wor"
e.undo(); e.undo(); e.undo(); e.undo(); e.undo(); assert e.text() == ""
''')

# ---- parsing ---------------------------------------------------------------------------------------------
add("nginx_stats", '''
def access_stats(lines: list) -> dict:
    """Parse nginx combined-format access log lines:
    '1.2.3.4 - - [10/Oct/2026:13:55:36 +0000] "GET /path?x=1 HTTP/1.1" 200 2326 "ref" "agent"'
    Return {'requests': total parsed, 'by_status': {status:int -> count}, 'by_path': {path (query string stripped) -> count},
    'bytes': sum of response bytes ('-' counts as 0), 'top_ip': the client ip with most requests (ties -> lexicographically smallest)}.
    Lines that do not parse are skipped (not counted). Empty input -> requests 0, empty dicts, bytes 0, top_ip None."""
''', "access_stats", '''
L = ['1.2.3.4 - - [10/Oct/2026:13:55:36 +0000] "GET /a?x=1 HTTP/1.1" 200 100 "-" "curl"',
     '1.2.3.4 - - [10/Oct/2026:13:55:37 +0000] "POST /b HTTP/1.1" 404 - "-" "curl"',
     '9.9.9.9 - bob [10/Oct/2026:13:55:38 +0000] "GET /a HTTP/2.0" 200 50 "http://r" "Mozilla/5.0 (X11; Linux; rv:1.0) Gecko"',
     'garbage line',
     '5.5.5.5 - - [10/Oct/2026:13:55:39 +0000] "GET / HTTP/1.1" 301 0 "-" "-"']
s = access_stats(L)
assert s["requests"] == 4 and s["by_status"] == {200: 2, 404: 1, 301: 1}
assert s["by_path"] == {"/a": 2, "/b": 1, "/": 1} and s["bytes"] == 150 and s["top_ip"] == "1.2.3.4"
e = access_stats([])
assert e["requests"] == 0 and e["by_status"] == {} and e["bytes"] == 0 and e["top_ip"] is None
assert access_stats([L[2], L[4]])["top_ip"] == "5.5.5.5"
''')
add("ini_interp", '''
def parse_ini(text: str) -> dict:
    """Parse INI text into {section: {key: value}}. Rules: '[name]' starts a section; 'key = value' lines (whitespace
    trimmed); lines starting with ';' or '#' and blank lines are ignored; keys before any section go under 'DEFAULT'.
    Values may reference other keys as ${key} (same section, falling back to DEFAULT) or ${section:key}; resolve
    them recursively after parsing. Unknown references are left as-is. Raise ValueError on a reference cycle."""
''', "parse_ini", '''
r = parse_ini("""
; comment
root = /srv
[app]
name = demo
home = ${root}/${name}
log = ${home}/log
[db]
path = ${app:home}/db
host=localhost
# another comment
""")
assert r["DEFAULT"] == {"root": "/srv"}
assert r["app"]["home"] == "/srv/demo" and r["app"]["log"] == "/srv/demo/log"
assert r["db"] == {"path": "/srv/demo/db", "host": "localhost"}
assert parse_ini("[s]\\nk = ${nope}")["s"]["k"] == "${nope}"
assert parse_ini("") == {}
try:
    parse_ini("[s]\\na = ${b}\\nb = ${a}"); assert False
except ValueError: pass
''')
add("cidr_aggregate", '''
def aggregate(cidrs: list) -> list:
    """Given IPv4 CIDR strings (prefix may be omitted, meaning /32), return the minimal list of CIDRs covering
    exactly the same addresses: remove networks contained in others, merge adjacent sibling networks into their
    parent (repeatedly), and return sorted by network address then prefix length, in 'a.b.c.d/n' form.
    Normalize host bits (e.g. '10.0.0.5/8' -> '10.0.0.0/8')."""
''', "aggregate", '''
assert aggregate(["10.0.0.0/25", "10.0.0.128/25"]) == ["10.0.0.0/24"]
assert aggregate(["10.0.0.0/24", "10.0.0.0/25", "10.0.1.0/24"]) == ["10.0.0.0/23"]
assert aggregate(["192.168.1.1", "192.168.1.0"]) == ["192.168.1.0/31"]
assert aggregate(["10.0.0.5/8", "11.0.0.0/8"]) == ["10.0.0.0/7"]
assert aggregate(["10.0.0.0/24", "10.0.2.0/24"]) == ["10.0.0.0/24", "10.0.2.0/24"]
assert aggregate([]) == []
assert aggregate(["0.0.0.0/1", "128.0.0.0/1"]) == ["0.0.0.0/0"]
''')
add("cron_field", '''
def expand(field: str, lo: int, hi: int) -> list:
    """Expand one cron field into a sorted list of ints within [lo, hi]. Supported: '*', single values, ranges 'a-b',
    steps '*/n' and 'a-b/n' and 'a/n' (a to hi stepping n), and comma-separated combinations of those.
    Values outside [lo, hi], a step of 0, or unparsable text raise ValueError. Duplicates are removed."""
''', "expand", '''
assert expand("*", 0, 5) == [0, 1, 2, 3, 4, 5]
assert expand("*/15", 0, 59) == [0, 15, 30, 45]
assert expand("1-5/2,10,20-22", 0, 59) == [1, 3, 5, 10, 20, 21, 22]
assert expand("50/5", 0, 59) == [50, 55]
assert expand("5,1,5", 1, 7) == [1, 5]
for bad in ["60", "*/0", "x", "5-3", "1-60"]:
    try: expand(bad, 0, 59); assert False, bad
    except ValueError: pass
''')
add("kv_log_query", '''
def query(lines: list, where: dict, select: list) -> list:
    """lines are 'key=value key2="quoted value with spaces" ...' logfmt strings. Parse each (values may be bare tokens
    or double-quoted with \\" escapes; a key with no '=' is a flag with value True). Return, for lines where every
    where[k] == value[k] (missing key never matches), the list of values for `select` keys in order (None if absent).
    Preserve input order."""
''', "query", '''
L = ['level=info msg="user login" user=bob ok',
     r'level=error msg="disk \\"full\\"" user=alice',
     'level=info msg=ping',
     'level=info user=bob msg="user logout"']
assert query(L, {"user": "bob"}, ["msg"]) == [["user login"], ["user logout"]]
assert query(L, {"level": "error"}, ["msg", "user", "nope"]) == [['disk "full"', "alice", None]]
assert query(L, {"ok": True}, ["user"]) == [["bob"]]
assert query(L, {"user": "carol"}, ["msg"]) == []
assert query([], {}, ["x"]) == []
assert query(L, {}, ["level"]) == [["info"], ["error"], ["info"], ["info"]]
''')

# ---- algorithms ------------------------------------------------------------------------------------------
add("toposort_cycle", '''
def toposort(deps: dict) -> list:
    """deps maps node -> list of nodes it depends on (dependencies must come first). Nodes that appear only as
    dependencies are included. Return a topological order; whenever several nodes have all their dependencies
    satisfied, emit the lexicographically smallest of them next (Kahn's algorithm with a min-heap). If there is a cycle, raise ValueError whose message contains the cycle as
    'a -> b -> a' (any rotation of the cycle is acceptable, but it must start and end on the same node)."""
''', "toposort", '''
assert toposort({"c": ["a", "b"], "b": ["a"], "a": []}) == ["a", "b", "c"]
assert toposort({"x": ["y"], "z": []}) == ["y", "x", "z"]
assert toposort({}) == []
assert toposort({"a": [], "b": [], "c": ["b"]}) == ["a", "b", "c"]
try:
    toposort({"a": ["b"], "b": ["c"], "c": ["a"], "d": []}); assert False
except ValueError as e:
    m = str(e)
    assert any(s in m for s in ("a -> b -> c -> a", "b -> c -> a -> b", "c -> a -> b -> c", "a -> c -> b -> a", "c -> b -> a -> c", "b -> a -> c -> b")), m
''')
add("schedule_rooms", '''
def min_rooms(meetings: list) -> tuple:
    """meetings are (start, end) with start < end, end exclusive. Return (rooms_needed, assignment) where
    assignment[i] is the room index (0-based) for meetings[i], rooms are reused when free, rooms_needed is the
    minimum possible, and a meeting always takes the lowest-numbered free room when processed in order of start
    time (ties by end time, then input index)."""
''', "min_rooms", '''
assert min_rooms([(0, 30), (5, 10), (15, 20)]) == (2, [0, 1, 1])
assert min_rooms([(7, 10), (2, 4)]) == (1, [0, 0])
assert min_rooms([]) == (0, [])
assert min_rooms([(1, 5), (5, 9), (1, 2)]) == (2, [1, 0, 0])
r = min_rooms([(0, 10), (0, 10), (0, 10), (10, 11)])
assert r[0] == 3 and r[1][:3] == [0, 1, 2] and r[1][3] == 0
''')
add("dijkstra_path", '''
def shortest_path(edges: list, src: str, dst: str) -> tuple:
    """edges are (u, v, w) undirected with w > 0. Return (distance, path) with path a list of nodes from src to dst,
    choosing lexicographically smallest path among equal-length ones (compare node lists). If unreachable return
    (None, []). src == dst gives (0, [src]). Unknown src or dst counts as unreachable."""
''', "shortest_path", '''
E = [("a", "b", 1), ("b", "c", 2), ("a", "c", 4), ("c", "d", 1), ("a", "d", 4), ("e", "f", 1)]
assert shortest_path(E, "a", "d") == (4, ["a", "b", "c", "d"])
assert shortest_path(E, "a", "e") == (None, [])
assert shortest_path(E, "c", "c") == (0, ["c"])
assert shortest_path(E, "a", "zz") == (None, [])
assert shortest_path([("a", "b", 1), ("a", "c", 1), ("b", "d", 1), ("c", "d", 1)], "a", "d") == (2, ["a", "b", "d"])
''')
add("diff_hunks", '''
def diff(a: list, b: list) -> list:
    """Line diff. Return a list of ops in order: ('=', line) for common lines, ('-', line) for lines only in a,
    ('+', line) for lines only in b, based on a longest common subsequence so the number of +/- ops is minimal.
    Where several LCS alignments exist, emit deletions before insertions at the same position."""
''', "diff", '''
assert diff(["a", "b", "c"], ["a", "c", "d"]) == [("=", "a"), ("-", "b"), ("=", "c"), ("+", "d")]
assert diff([], ["x"]) == [("+", "x")]
assert diff(["x"], []) == [("-", "x")]
assert diff(["a", "a"], ["a", "a"]) == [("=", "a"), ("=", "a")]
d = diff(["k", "i", "t", "t", "e", "n"], ["s", "i", "t", "t", "i", "n", "g"])
assert sum(1 for o, _ in d if o != "=") == 5 and [l for o, l in d if o == "="] == ["i", "t", "t", "n"]
assert diff(["a"], ["b"]) == [("-", "a"), ("+", "b")]
''')
add("knapsack_items", '''
def best_subset(items: list, budget: int) -> tuple:
    """items are (name, cost, value) with non-negative ints. Choose a subset with total cost <= budget maximizing
    total value. Return (total_value, names) where names is sorted alphabetically. Ties on value: prefer lower
    total cost; then the alphabetically smallest names list. budget >= 0."""
''', "best_subset", '''
assert best_subset([("a", 2, 3), ("b", 3, 4), ("c", 4, 5), ("d", 5, 6)], 5) == (7, ["a", "b"])
assert best_subset([("x", 1, 1), ("y", 1, 1)], 1) == (1, ["x"])
assert best_subset([("x", 10, 100)], 5) == (0, [])
assert best_subset([], 10) == (0, [])
assert best_subset([("a", 0, 5), ("b", 3, 0)], 3) == (5, ["a"])
assert best_subset([("a", 2, 4), ("b", 1, 2), ("c", 1, 2)], 2) == (4, ["a"])
''')

# ---- strings ---------------------------------------------------------------------------------------------
add("glob_match", '''
def glob_match(pattern: str, name: str) -> bool:
    """Shell-style match of the whole name: '*' any run of chars (including empty), '?' exactly one char,
    '[abc]' / '[a-z]' char classes, '[!abc]' negated class, and backslash escapes the next pattern char.
    A '[' with no closing ']' is a literal '['."""
''', "glob_match", '''
assert glob_match("*.py", "a.py") and not glob_match("*.py", "a.pyc")
assert glob_match("a?c", "abc") and not glob_match("a?c", "ac")
assert glob_match("[a-c]x", "bx") and not glob_match("[a-c]x", "dx")
assert glob_match("[!a-c]x", "dx") and not glob_match("[!a-c]x", "ax")
assert glob_match("a\\\\*b", "a*b") and not glob_match("a\\\\*b", "axb")
assert glob_match("[x", "[x") and not glob_match("[x", "x")
assert glob_match("*", "") and glob_match("a*b*c", "aXbYc") and not glob_match("a*b*c", "aXcYb")
assert glob_match("**a", "a")
''')
add("expr_eval", '''
def evaluate(expr: str) -> float:
    """Evaluate an arithmetic expression with + - * / % ** , unary minus, parentheses, integers and decimals.
    Precedence: ** (right-assoc, binds tighter than unary minus so -2**2 == -4) > unary minus > * / % > + -.
    Whitespace is ignored. Division by zero raises ZeroDivisionError; anything malformed raises ValueError.
    Do not use eval/exec/ast.literal_eval."""
''', "evaluate", '''
assert evaluate("1 + 2 * 3") == 7
assert evaluate("(1 + 2) * 3") == 9
assert evaluate("-2 ** 2") == -4 and evaluate("2 ** 3 ** 2") == 512
assert evaluate("10 % 4 + 7 / 2") == 5.5
assert evaluate("-(3 - 5) * -2") == -4
assert evaluate("1.5*4") == 6
try: evaluate("1 / 0"); assert False
except ZeroDivisionError: pass
for bad in ["1 +", "(1", "2 3", "", "a+1"]:
    try: evaluate(bad); assert False, bad
    except ValueError: pass
''')
add("template_render", '''
def render(tpl: str, ctx: dict) -> str:
    """Render '{{ name }}' placeholders from ctx (whitespace inside braces optional). Dotted names walk nested dicts
    and list indexes: '{{ user.name }}', '{{ items.0 }}'. '{{ x | upper }}' and '| lower' filters are supported, as is
    '| default:text' used when the value is missing. A missing value without a default raises KeyError. '\\{{' is a
    literal '{{'. Values are converted with str()."""
''', "render", '''
assert render("Hi {{ name }}!", {"name": "Bo"}) == "Hi Bo!"
assert render("{{user.name|upper}} {{ items.1 }}", {"user": {"name": "al"}, "items": [1, 2]}) == "AL 2"
assert render("{{ missing | default:none }}", {}) == "none"
assert render("\\\\{{ not }} {{ a }}", {"a": 1}) == "{{ not }} 1"
assert render("{{ n | lower }}", {"n": "ABC"}) == "abc"
try: render("{{ nope }}", {}); assert False
except KeyError: pass
assert render("plain", {}) == "plain"
''')

# ---- fix-the-bug, phrased as reports --------------------------------------------------------------------
add("fix_pagination", '''
# Bug report: "Page 2 of a 25-item list with page_size 10 shows items 10-19, which is right, but the last page
# (page 3) is empty and total_pages says 2. Also page 0 or negative crashes with a slice error." Fix the function
# below; keep its name and signature. Pages are 1-based; a page below 1 or above total_pages raises ValueError.
# An empty list has total_pages 1, and page 1 of it returns no items.
def paginate(items: list, page: int, page_size: int) -> dict:
    """Return {'items': [...], 'page': page, 'total_pages': n}."""
    total_pages = len(items) // page_size
    start = (page - 1) * page_size
    return {"items": items[start:start + page_size], "page": page, "total_pages": total_pages}
''', "paginate", '''
xs = list(range(25))
assert paginate(xs, 3, 10) == {"items": [20, 21, 22, 23, 24], "page": 3, "total_pages": 3}
assert paginate(xs, 2, 10)["items"] == list(range(10, 20))
assert paginate([], 1, 10) == {"items": [], "page": 1, "total_pages": 1}
assert paginate(list(range(20)), 2, 10)["total_pages"] == 2
for bad in (0, -1, 4):
    try: paginate(xs, bad, 10); assert False, bad
    except ValueError: pass
''', kind="fix")
add("fix_naive_datetime", '''
# Bug report: "Our 'expires_in' shows wrong values for users outside UTC, and it crashes with 'can't subtract
# offset-naive and offset-aware datetimes' when the expiry string has a +02:00 suffix." The stored expiry is an
# ISO-8601 string, either with an offset (e.g. '2026-10-23T12:00:00+02:00') or without (meaning UTC).
# Fix the function; keep name and signature. `now` is an aware datetime. Return whole seconds remaining
# (negative if already expired).
from datetime import datetime, timezone
def seconds_until(expiry_iso: str, now: datetime) -> int:
    exp = datetime.fromisoformat(expiry_iso)
    return int((exp - now.replace(tzinfo=None)).total_seconds())
''', "seconds_until", '''
from datetime import datetime, timezone, timedelta
now = datetime(2026, 10, 23, 10, 0, 0, tzinfo=timezone.utc)
assert seconds_until("2026-10-23T12:00:00+02:00", now) == 0
assert seconds_until("2026-10-23T11:00:00", now) == 3600
assert seconds_until("2026-10-23T09:59:30+00:00", now) == -30
local_now = datetime(2026, 10, 23, 12, 0, 0, tzinfo=timezone(timedelta(hours=2)))
assert seconds_until("2026-10-23T10:00:10", local_now) == 10
''', kind="fix")
add("fix_shared_state", '''
# Bug report: "Every Counter sees every other Counter's events. Creating two counters and adding to one changes
# both. Also total() for an empty counter returns a weird object instead of 0, and most_common() sorts wrong when
# counts tie (we expect alphabetical)." Fix the class; keep names and signatures.
class Counter:
    events = {}
    def add(self, key, n=1):
        self.events[key] = self.events.get(key, 0) + n
    def total(self):
        return sum(self.events.values()) or self.events
    def most_common(self, k):
        return sorted(self.events.items(), key=lambda kv: kv[1])[:k]
''', "Counter", '''
a, b = Counter(), Counter()
a.add("x"); a.add("y", 2); b.add("z")
assert a.total() == 3 and b.total() == 1 and Counter().total() == 0
assert a.most_common(1) == [("y", 2)]
a.add("x")
assert a.most_common(2) == [("x", 2), ("y", 2)]
assert b.most_common(5) == [("z", 1)]
''', kind="fix")
add("fix_float_money", '''
# Bug report: "Splitting 100.00 three ways returns [33.33, 33.33, 33.33] and we lose a cent; splitting 0.3 into
# 3 gives 0.09999999 entries; and amounts like 10.005 round inconsistently." Amounts are decimal strings; return a
# list of decimal strings with 2 places that sum exactly to the input, remainder cents going to the earliest
# shares. Fix the function; keep name and signature. n >= 1.
def split_amount(amount: str, n: int) -> list:
    each = round(float(amount) / n, 2)
    return [f"{each:.2f}" for _ in range(n)]
''', "split_amount", '''
assert split_amount("100.00", 3) == ["33.34", "33.33", "33.33"]
assert split_amount("0.3", 3) == ["0.10", "0.10", "0.10"]
assert split_amount("10.005", 2) == ["5.01", "5.00"] or split_amount("10.005", 2) == ["5.00", "5.00"]
assert split_amount("1", 1) == ["1.00"]
assert split_amount("0.05", 4) == ["0.02", "0.01", "0.01", "0.01"]
from decimal import Decimal
assert sum(Decimal(x) for x in split_amount("12345.67", 7)) == Decimal("12345.67")
''', kind="fix")
add("fix_mutating_iteration", '''
# Bug report: "prune() sometimes raises 'dictionary changed size during iteration', and when it does not crash it
# leaves some expired sessions behind because nested groups are not visited. Also it should return how many
# sessions it removed." Sessions is {group: {session_id: expires_at}} where a group value may itself contain
# nested groups (dict values) mixed with sessions (int values). Fix; keep name and signature.
def prune(sessions: dict, now: int) -> int:
    for g, members in sessions.items():
        for sid, exp in members.items():
            if exp <= now:
                del members[sid]
    return None
''', "prune", '''
s = {"web": {"a": 5, "b": 20, "sub": {"c": 1, "d": 30}}, "api": {"e": 10}}
assert prune(s, 10) == 3
assert s == {"web": {"b": 20, "sub": {"d": 30}}, "api": {}}
assert prune(s, 100) == 2 and s == {"web": {"sub": {}}, "api": {}}
assert prune({}, 0) == 0
''', kind="fix")
add("refactor_retry_kwarg", '''
# Change request: retry() below works but callers now need (1) an optional `on_error(exc, attempt)` callback
# called before each retry sleep, (2) exponential backoff: the delay doubles after each failure, capped at
# `max_delay`, (3) `exceptions` to restrict which exception types are retried; others propagate immediately.
# Keep existing positional behavior: retry(fn, attempts, delay, sleep) must still work. Return fn()'s result;
# after the last failed attempt re-raise the last exception. Keep the name `retry`.
def retry(fn, attempts=3, delay=0.1, sleep=None):
    import time
    sleep = sleep or time.sleep
    last = None
    for i in range(attempts):
        try:
            return fn()
        except Exception as e:
            last = e
            if i < attempts - 1:
                sleep(delay)
    raise last
''', "retry", '''
calls = []; slept = []; seen = []
def flaky():
    calls.append(1)
    if len(calls) < 4: raise ValueError("no")
    return "ok"
assert retry(flaky, 5, 1, slept.append, on_error=lambda e, a: seen.append(a), max_delay=3) == "ok"
assert slept == [1, 2, 3] and seen == [1, 2, 3]
calls.clear(); slept.clear()
try:
    retry(flaky, 2, 0.5, slept.append); assert False
except ValueError: pass
assert slept == [0.5]
calls.clear()
def typed():
    calls.append(1); raise KeyError("k")
try:
    retry(typed, 3, 0.1, slept.append, exceptions=(ValueError,)); assert False
except KeyError: pass
assert len(calls) == 1
assert retry(lambda: 42) == 42
''', kind="fix")
