"""Small original coding problems for pass@1 scoring. Each: id, prompt (signature+docstring), entry, tests (asserts).
Deliberately simple: this measures 'can it write a correct 5-15 line function', the bar for a low-end coding helper."""
P = []
def add(id, prompt, entry, tests, kind="write"): P.append(dict(id=id, prompt=prompt.strip()+"\n", entry=entry, tests=tests.strip(), kind=kind))

add("rle", '''
def rle(s: str) -> str:
    """Run-length encode: 'aaabcc' -> 'a3b1c2'. Empty string -> ''."""
''', "rle", '''
assert rle("aaabcc") == "a3b1c2"
assert rle("") == ""
assert rle("a") == "a1"
assert rle("abab") == "a1b1a1b1"
''')
add("is_balanced", '''
def is_balanced(s: str) -> bool:
    """Return True if brackets ()[]{} in s are balanced and properly nested. Other chars ignored."""
''', "is_balanced", '''
assert is_balanced("([]{})")
assert not is_balanced("([)]")
assert is_balanced("")
assert not is_balanced("((")
assert is_balanced("a(b)c[d]")
''')
add("word_freq", '''
def word_freq(text: str) -> dict:
    """Case-insensitive word counts. Words are separated by whitespace; strip leading/trailing punctuation .,!?;: from each word."""
''', "word_freq", '''
assert word_freq("Hi, hi! HI.") == {"hi": 3}
assert word_freq("") == {}
assert word_freq("a b a") == {"a": 2, "b": 1}
''')
add("chunk", '''
def chunk(xs: list, n: int) -> list:
    """Split xs into consecutive chunks of size n; last chunk may be shorter. n>=1."""
''', "chunk", '''
assert chunk([1,2,3,4,5], 2) == [[1,2],[3,4],[5]]
assert chunk([], 3) == []
assert chunk([1,2,3], 3) == [[1,2,3]]
''')
add("parse_kv", '''
def parse_kv(s: str) -> dict:
    """Parse 'k1=v1;k2=v2' into a dict. Whitespace around keys/values is stripped. Empty string -> {}."""
''', "parse_kv", '''
assert parse_kv("a=1; b = two") == {"a": "1", "b": "two"}
assert parse_kv("") == {}
assert parse_kv("x=y=z") == {"x": "y=z"}
''')
add("second_largest", '''
def second_largest(xs: list) -> int | None:
    """Return the second largest distinct value in xs, or None if it does not exist."""
''', "second_largest", '''
assert second_largest([3,1,2]) == 2
assert second_largest([5,5,5]) is None
assert second_largest([1]) is None
assert second_largest([2,9,9,4]) == 4
''')
add("roman", '''
def to_roman(n: int) -> str:
    """Convert 1 <= n <= 3999 to a Roman numeral."""
''', "to_roman", '''
assert to_roman(1) == "I"
assert to_roman(4) == "IV"
assert to_roman(1994) == "MCMXCIV"
assert to_roman(3999) == "MMMCMXCIX"
''')
add("ip_valid", '''
def is_ipv4(s: str) -> bool:
    """True if s is a dotted-quad IPv4 address with 4 decimal octets 0-255 and no leading zeros (except '0' itself)."""
''', "is_ipv4", '''
assert is_ipv4("192.168.0.1")
assert not is_ipv4("256.1.1.1")
assert not is_ipv4("01.1.1.1")
assert not is_ipv4("1.1.1")
assert is_ipv4("0.0.0.0")
assert not is_ipv4("a.b.c.d")
''')
add("cidr_contains", '''
def cidr_contains(cidr: str, ip: str) -> bool:
    """True if IPv4 address ip is inside the network cidr, e.g. cidr_contains('10.0.0.0/8', '10.2.3.4')."""
''', "cidr_contains", '''
assert cidr_contains("10.0.0.0/8", "10.2.3.4")
assert not cidr_contains("10.0.0.0/8", "11.0.0.1")
assert cidr_contains("192.168.1.0/24", "192.168.1.255")
assert not cidr_contains("192.168.1.0/24", "192.168.2.0")
assert cidr_contains("0.0.0.0/0", "8.8.8.8")
''')
add("merge_intervals", '''
def merge_intervals(iv: list) -> list:
    """Merge overlapping or touching [start, end] intervals; return sorted list of merged intervals."""
''', "merge_intervals", '''
assert merge_intervals([[1,3],[2,6],[8,10],[15,18]]) == [[1,6],[8,10],[15,18]]
assert merge_intervals([[1,4],[4,5]]) == [[1,5]]
assert merge_intervals([]) == []
''')
add("flatten", '''
def flatten(xs) -> list:
    """Flatten arbitrarily nested lists into a single flat list. Non-list items are kept as-is."""
''', "flatten", '''
assert flatten([1,[2,[3,[4]]],5]) == [1,2,3,4,5]
assert flatten([]) == []
assert flatten([[["a"]]]) == ["a"]
''')
add("caesar", '''
def caesar(s: str, k: int) -> str:
    """Shift letters by k positions (wrapping), preserving case; leave non-letters unchanged. k may be negative or > 26."""
''', "caesar", '''
assert caesar("abc xyz", 3) == "def abc"
assert caesar("Hello, World!", 13) == "Uryyb, Jbeyq!"
assert caesar("abc", -1) == "zab"
assert caesar("abc", 29) == "def"
''')
add("median", '''
def median(xs: list) -> float:
    """Median of a non-empty list of numbers (mean of the two middle values when even length)."""
''', "median", '''
assert median([3,1,2]) == 2
assert median([1,2,3,4]) == 2.5
assert median([7]) == 7
''')
add("dedupe_keep_order", '''
def dedupe(xs: list) -> list:
    """Remove duplicates keeping first occurrence order."""
''', "dedupe", '''
assert dedupe([1,2,1,3,2]) == [1,2,3]
assert dedupe([]) == []
assert dedupe(["a","a"]) == ["a"]
''')
add("parse_syslog", '''
def parse_syslog(line: str) -> dict:
    """Parse 'Mon DD HH:MM:SS host proc[pid]: message' into {'ts','host','proc','pid','msg'}; pid is int or None if absent."""
''', "parse_syslog", '''
r = parse_syslog("Sep 20 06:01:02 web1 sshd[1234]: Failed password for root from 1.2.3.4 port 22 ssh2")
assert r["host"] == "web1" and r["proc"] == "sshd" and r["pid"] == 1234 and r["ts"] == "Sep 20 06:01:02"
assert r["msg"].startswith("Failed password")
r = parse_syslog("Sep  1 00:00:00 h cron: job done")
assert r["proc"] == "cron" and r["pid"] is None and r["msg"] == "job done"
''')
add("top_n", '''
def top_n(counts: dict, n: int) -> list:
    """Return the n (key, count) pairs with the highest counts, ties broken by key ascending."""
''', "top_n", '''
assert top_n({"a": 3, "b": 5, "c": 3}, 2) == [("b", 5), ("a", 3)]
assert top_n({}, 3) == []
assert top_n({"x": 1}, 5) == [("x", 1)]
''')
add("bin_search", '''
def bsearch(xs: list, target) -> int:
    """Binary search sorted xs; return index of target or -1."""
''', "bsearch", '''
assert bsearch([1,3,5,7], 5) == 2
assert bsearch([1,3,5,7], 4) == -1
assert bsearch([], 1) == -1
assert bsearch([2], 2) == 0
''')
add("hex_dump", '''
def hexdump(b: bytes) -> str:
    """Return space-separated lowercase two-digit hex of each byte, e.g. b'\\x01\\xff' -> '01 ff'. Empty -> ''."""
''', "hexdump", '''
assert hexdump(b"\\x01\\xff") == "01 ff"
assert hexdump(b"") == ""
assert hexdump(b"ABC") == "41 42 43"
''')
# fix-the-bug problems: prompt contains buggy code
add("fix_avg", '''
# The function below has a bug. Return a corrected version with the same name and signature.
def avg(xs: list) -> float:
    """Average of a list; return 0.0 for an empty list."""
    total = 0
    for x in xs:
        total += x
    return total / len(xs)
''', "avg", '''
assert avg([]) == 0.0
assert avg([1,2,3]) == 2.0
''', kind="fix")
add("fix_offbyone", '''
# The function below has a bug. Return a corrected version with the same name and signature.
def last_n(xs: list, n: int) -> list:
    """Return the last n items of xs (all of xs if n >= len(xs); [] if n <= 0)."""
    if n <= 0:
        return []
    return xs[-n+1:]
''', "last_n", '''
assert last_n([1,2,3,4], 2) == [3,4]
assert last_n([1,2], 5) == [1,2]
assert last_n([1,2], 0) == []
assert last_n([1,2,3], 1) == [3]
''', kind="fix")
add("fix_mutable_default", '''
# The function below has a bug. Return a corrected version with the same name and signature.
def append_item(item, bucket=[]):
    """Append item to bucket and return bucket; a fresh list is used when bucket is not given."""
    bucket.append(item)
    return bucket
''', "append_item", '''
assert append_item(1) == [1]
assert append_item(2) == [2]
b = []; assert append_item(3, b) is b and b == [3]
''', kind="fix")
add("fix_strip_prefix", '''
# The function below has a bug. Return a corrected version with the same name and signature.
def strip_prefix(s: str, prefix: str) -> str:
    """Remove prefix from the start of s if present, otherwise return s unchanged."""
    return s.lstrip(prefix)
''', "strip_prefix", '''
assert strip_prefix("foobar", "foo") == "bar"
assert strip_prefix("ffoo", "f") == "foo"
assert strip_prefix("bar", "foo") == "bar"
assert strip_prefix("", "x") == ""
''', kind="fix")
