# subdomain_enum.py
import argparse, requests, socket
from concurrent.futures import ThreadPoolExecutor
import json

CRT_SH = "https://crt.sh/?q=%25.{domain}&output=json"

def fetch_crtsh(domain):
    url = CRT_SH.format(domain=domain)
    r = requests.get(url, timeout=10)
    if r.status_code != 200:
        return []
    try:
        data = r.json()
    except Exception:
        return []
    subs = {entry.get("name_value").strip() for entry in data if entry.get("name_value")}
    # crt.sh returns entries with newlines; split them
    cleaned = set()
    for s in subs:
        for part in s.splitlines():
            cleaned.add(part.strip().lower())
    return sorted([s for s in cleaned if s.endswith(domain)])

def resolve(host):
    try:
        socket.gethostbyname(host)
        return True
    except Exception:
        return False

def http_alive(host):
    try:
        r = requests.get("http://" + host, timeout=5, allow_redirects=True)
        return True
    except Exception:
        try:
            r = requests.get("https://" + host, timeout=5, verify=False)
            return True
        except Exception:
            return False

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--domain", required=True)
    p.add_argument("--workers", type=int, default=10)
    args = p.parse_args()

    subs = fetch_crtsh(args.domain)
    with open("subdomains.txt", "w") as f:
        for s in subs:
            f.write(s+"\n")
    alive = []
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        for host, ok in zip(subs, ex.map(resolve, subs)):
            if ok:
                alive.append(host)
    # further check HTTP responsiveness
    http_ok = []
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        for host, ok in zip(alive, ex.map(http_alive, alive)):
            if ok:
                http_ok.append(host)
    with open("alive.txt", "w") as f:
        for h in http_ok:
            f.write(h+"\n")
    print(f"Found {len(subs)} subdomains, {len(http_ok)} alive (written to alive.txt)")

if __name__ == "__main__":
    main()
