# security_headers_check.py
import argparse, requests, json
from datetime import datetime

REQUIRED = {
    "content-security-policy": "Prevent XSS by specifying allowed sources",
    "strict-transport-security": "Enforce HTTPS (HSTS)",
    "x-frame-options": "Prevent clickjacking",
    "x-content-type-options": "Prevent MIME-sniffing",
    "referrer-policy": "Control referrer header info"
}

def check_url(url):
    try:
        r = requests.get(url, timeout=8)
    except Exception as e:
        return {"url": url, "error": str(e)}
    headers = {k.lower(): v for k,v in r.headers.items()}
    missing = {h:REQUIRED[h] for h in REQUIRED if h not in headers}
    present = {h: headers[h] for h in REQUIRED if h in headers}
    return {
        "url": url,
        "status_code": r.status_code,
        "missing": missing,
        "present": present,
        "checked_at": datetime.utcnow().isoformat() + "Z"
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--url", help="Single URL to check")
    p.add_argument("--input", help="File with URLs, one per line")
    args = p.parse_args()
    targets = []
    if args.url:
        targets = [args.url]
    elif args.input:
        with open(args.input) as f:
            targets = [l.strip() for l in f if l.strip()]
    else:
        print("Provide --url or --input")
        return

    results = [check_url(u) for u in targets]
    with open("headers_report.json","w") as f:
        json.dump(results, f, indent=2)
    # simple markdown
    md = "# Security Headers Report\n\n"
    for r in results:
        if "error" in r:
            md += f"- **{r['url']}**: ERROR {r['error']}\n"
            continue
        md += f"## {r['url']} (HTTP {r['status_code']})\n"
        if r['missing']:
            md += f"- Missing headers: {', '.join(r['missing'].keys())}\n"
        else:
            md += "- All required headers present (basic set).\n"
        md += "\n"
    with open("headers_report.md","w") as f:
        f.write(md)
    print("Report written: headers_report.json / headers_report.md")

if __name__ == "__main__":
    main()
