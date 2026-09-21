SYSTEM = ("You are a security analyst triaging Linux and web server log lines. "
          "For the given log line answer with exactly one word: MALICIOUS if it indicates an attack, intrusion, "
          "brute force, injection, scanning, privilege abuse, or malware activity; otherwise BENIGN. "
          "Failed logins from internal 10.x addresses by known users are benign typos. Answer with one word only.")
def parse(text: str) -> int:
    t = text.strip().upper()
    if "MALICIOUS" in t and "BENIGN" not in t: return 1
    if "BENIGN" in t and "MALICIOUS" not in t: return 0
    # both or neither: take the first occurrence
    i, j = t.find("MALICIOUS"), t.find("BENIGN")
    if i < 0 and j < 0: return -1
    return 1 if (j < 0 or (i >= 0 and i < j)) else 0
