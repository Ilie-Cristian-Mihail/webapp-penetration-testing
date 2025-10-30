# tech_fingerprint.py
import argparse, requests, json, re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

USER_AGENT = "tech-fingerprint/1.0 (+https://github.com/yourname)"

# simplu set de reguli/semnături (extensible)
SIGNATURES = {
    "WordPress": [r"wp-content", r"wp-emoji-release", r"wordpress", r"wp-includes"],
    "WooCommerce": [r"woocommerce"],
    "jQuery": [r"jquery(\.min)?\.js", r"jquery-"],
    "React": [r"react(\.min)?\.js", r"data-reactroot", r"__REACT_DEVTOOLS_GLOBAL_HOOK__"],
    "Angular": [r"angular", r"ng-version"],
    "Vue": [r"vue(\.min)?\.js", r"__VUE_DEVTOOLS_GLOBAL_HOOK__"],
    "Laravel": [r"laravel", r"XSRF-TOKEN", r"laravel_session"],
    "Django": [r"csrftoken", r"djangoproject", r"django"],
    "Express": [r"X-Powered-By: Express", r"express"],
    "PHP": [r"\.php", r"X-Powered-By: PHP"],
    "ASP.NET": [r"ASP\.NET_SessionId", r"X-Powered-By: ASP\.NET"],
    "Nginx": [r"server: nginx", r"nginx"],
    "Apache": [r"server: apache", r"server: Apache"],
}

def fetch(url):
    try:
        r = requests.get(url, timeout=8, headers={"User-Agent": USER_AGENT}, allow_redirects=True)
        return r
    except Exception as e:
        return None

def analyze_response(r, base_url):
    text = r.text or ""
    headers = {k.lower(): v for k,v in r.headers.items()}
    cookies = r.cookies.get_dict()
    soup = BeautifulSoup(text, "html.parser")
    scripts = " ".join([s.get("src","") or s.get_text() or "" for s in soup.find_all("script")])
    links = " ".join([l.get("href","") or "" for l in soup.find_all("link")])
    imgs = " ".join([i.get("src","") or "" for i in soup.find_all("img")])
    meta = " ".join([m.get("content","") or "" for m in soup.find_all("meta") if m.get("content")])
    combined = " ".join([text, scripts, links, imgs, meta, json.dumps(headers), json.dumps(cookies)])

    findings = {}
    for tech, patterns in SIGNATURES.items():
        for p in patterns:
            if re.search(p, combined, flags=re.IGNORECASE):
                findings.setdefault(tech, []).append(p)
    # add header-based hints
    if "x-powered-by" in headers:
        xp = headers["x-powered-by"]
        for tech in SIGNATURES:
            if tech.lower() in xp.lower():
                findings.setdefault(tech, []).append("header:x-powered-by:"+xp)
    if "server" in headers:
        srv = headers["server"]
        for tech in SIGNATURES:
            if tech.lower() in srv.lower():
                findings.setdefault(tech, []).append("header:server:"+srv)

    return {
        "url": r.url,
        "status_code": r.status_code,
        "headers": headers,
        "cookies": cookies,
        "detected": findings
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--url", help="Single URL to analyze")
    p.add_argument("--input", help="File with URLs, one per line")
    p.add_argument("--out", default="tech_report")
    args = p.parse_args()

    targets = []
    if args.url:
        targets = [args.url]
    elif args.input:
        with open(args.input) as f:
            targets = [l.strip() for l in f if l.strip()]

    reports = []
    for t in targets:
        print(f"[+] Fetching {t}")
        r = fetch(t)
        if not r:
            reports.append({"url": t, "error": "fetch_failed"})
            continue
        rep = analyze_response(r, t)
        reports.append(rep)

    # write JSON
    with open(args.out + ".json", "w", encoding="utf-8") as f:
        json.dump(reports, f, indent=2)
    # write markdown summary
    md = "# Tech Fingerprint Report\n\n"
    for r in reports:
        md += f"## {r.get('url')}\n\n"
        if r.get("error"):
            md += f"- Error: {r['error']}\n\n"
            continue
        detected = r.get("detected",{})
        if not detected:
            md += "- No known tech signatures detected (basic set).\n\n"
        else:
            md += "- Detected technologies:\n"
            for tech, sigs in detected.items():
                md += f"  - **{tech}** (matches: {len(sigs)}): {', '.join(sigs[:3])}\n"
            md += "\n"
    with open(args.out + ".md", "w", encoding="utf-8") as f:
        f.write(md)
    print(f"[+] Wrote {args.out}.json and {args.out}.md")

if __name__ == "__main__":
    main()
