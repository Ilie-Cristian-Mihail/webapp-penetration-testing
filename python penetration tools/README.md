# Webapp Recon Toolkit — subdomain_enum.py, security_headers.py, tech_fingerprint.py

Small, safe, non-intrusive recon utilities for web-application reconnaissance — meant for portfolio / learning and to speed up preparation before a pentest. Each tool performs **read-only** actions (HTTP GETs, DNS lookups, static JS/HTML analysis). **Do not run these tools against systems you do not own or do not have written permission to test.**

---

## Quick start

```bash
# clone
git clone https://github.com/yourname/webapp-recon-toolkit.git
cd webapp-recon-toolkit

# create venv and install
python -m venv venv
source venv/bin/activate      # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
```

Suggested `requirements.txt`
```
requests
beautifulsoup4
dnspython
tldextract
jinja2      # optional (not required for basic usage)
```

---

# Tools & usage

All tools are simple CLI scripts. Run `python <script> --help` for full options.

---

## `subdomain_enum.py`
Enumerates subdomains via Certificate Transparency (`crt.sh`), resolves DNS and checks which hosts respond over HTTP/HTTPS. **No brute-forcing**.

**Purpose:** quick OSINT recon to find potential targets (alive subdomains).

**Usage**
```bash
python subdomain_enum.py --domain example.com
# optional
python subdomain_enum.py --domain example.com --workers 20
```

**Outputs**
- `subdomains.txt` — all subdomains discovered via crt.sh
- `alive.txt` — subdomains that resolve and respond over HTTP/HTTPS

**Notes**
- Screenshots/headless browsing are disabled by default (optional extension).
- Be mindful of rate limits; script uses modest defaults.

---

## `security_headers.py`
Checks HTTP response headers for basic security headers and produces a short report with missing headers and remediation hints.

**Purpose:** fast verification of essential HTTP security headers (CSP, HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy).

**Usage**
```bash
# single URL
python security_headers.py --url https://example.com

# multiple URLs from file (one URL per line)
python security_headers.py --input hosts.txt --out report_basename
```

**Outputs**
- `report_basename.json` — raw structured results (status code, present/missing headers)
- `report_basename.md` — human friendly markdown summary

**What it checks**
- Content-Security-Policy
- Strict-Transport-Security
- X-Frame-Options
- X-Content-Type-Options
- Referrer-Policy

---

## `tech_fingerprint.py`
Heuristic technology fingerprinting: inspects response headers, HTML, scripts, cookies and common paths to detect frameworks/technologies (WordPress, jQuery, React, Laravel, Nginx, Apache, etc.).

**Purpose:** fast identification of stack/technologies so you can pick the right tools and tests later.

**Usage**
```bash
python tech_fingerprint.py --url https://example.com --out example-tech
# or multiple:
python tech_fingerprint.py --input urls.txt --out bulk-tech
```

**Outputs**
- `example-tech.json` — structured detection output
- `example-tech.md` — readable summary listing detected techs and matched signatures

**Limitations**
- Heuristic-based; false positives/negatives possible. Use as a guide, not an oracle.

---

# Recommended workflow (example)
1. Run `subdomain_enum.py` to find alive subdomains.
2. Run `tech_fingerprint.py` against alive hosts to identify technologies.
3. Run `security_headers.py` to check for basic hardening gaps.
4. Combine outputs to prepare a focused, non-intrusive test plan (or to build an OpenAPI map / Postman collection with a separate tool).

---

# Repo structure (suggested)
```
webapp-recon-toolkit/
├─ README.md
├─ requirements.txt
├─ subdomain_enum.py
├─ security_headers.py
├─ tech_fingerprint.py
├─ examples/
│  ├─ urls.txt
│  └─ sample_outputs/
└─ LICENSE
```

---

# Security & Legal
- **Only use with explicit authorization.** Running these scripts against third-party targets without permission may be illegal.  
- The tools are intentionally non-intrusive and avoid active exploitation, brute force or fuzzing — but that is not a legal shield. Always get written consent (scope, allowed time windows, targets) before testing.  
- When saving screenshots, PoC or logs, redact any sensitive customer data before publishing.

---

# README / Portfolio tips
- Add a short demo GIF or screenshots in `examples/sample_outputs/` (redacted).  
- Include a short `ABOUT.md` describing your role/skills and link to a redacted sample report (PDF) generated from safe, self-hosted targets.  
- Add a prominent legal disclaimer at the top of the repo: `⚠️ Use responsibly: do not run on systems you don't own or have permission to test.`

---

# Contributing
PRs welcome — keep new features safe and non-destructive. Add tests for parsing logic and avoid adding exploits to the main repo.

---

# License
Pick a permissive license (MIT recommended). Example `LICENSE` file with MIT.
