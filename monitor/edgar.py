"""Weekly scan of new SEC filings (10-K, 10-Q, 8-K) of the thirteen companies for guarantee and off-balance-sheet language.

Terms are those of the September 2026 extractor (research/2026-09-guarantees-note in this repository).
New sentences are appended to data/edgar_findings.json; already scanned filings are listed in data/edgar_seen.json.
The SEC asks automated clients to identify themselves and to stay under ten requests per second.
"""
import html
import json
import re
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
SEEN = ROOT / "data" / "edgar_seen.json"
FOUND = ROOT / "data" / "edgar_findings.json"
FORMS = {"10-K", "10-Q", "8-K"}
AMOUNT = re.compile(r"\$\s?[\d,]+(?:\.\d+)?\s*(?:billion|million|trillion)?", re.I)


def _get(url, ua):
    r = requests.get(url, headers={"User-Agent": ua, "Accept-Encoding": "gzip, deflate"}, timeout=40)
    r.raise_for_status()
    time.sleep(0.25)
    return r


def _text(raw):
    raw = re.sub(r"(?is)<(script|style).*?</\1>", " ", raw)
    raw = re.sub(r"(?s)<[^>]+>", " ", raw)
    return re.sub(r"\s+", " ", html.unescape(raw))


def scan(cfg, since="2026-09-01", max_filings=40):
    seen = set(json.loads(SEEN.read_text())) if SEEN.exists() else set()
    found = json.loads(FOUND.read_text()) if FOUND.exists() else []
    ua, terms = cfg["edgar_user_agent"], cfg["edgar_terms"]
    status, n = "ok", 0
    try:
        for tk, cik in cfg["edgar_companies"].items():
            sub = _get(f"https://data.sec.gov/submissions/CIK{int(cik):010d}.json", ua).json()
            rec = sub["filings"]["recent"]
            for form, acc, date, doc in zip(rec["form"], rec["accessionNumber"], rec["filingDate"], rec["primaryDocument"]):
                if form not in FORMS or date < since or acc in seen or n >= max_filings:
                    continue
                url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc.replace('-', '')}/{doc}"
                try:
                    txt = _text(_get(url, ua).text)
                except Exception:
                    continue
                seen.add(acc)
                n += 1
                for sent in re.split(r"(?<=[.;])\s+", txt):
                    low = sent.lower()
                    hit = [t for t in terms if t in low]
                    if hit and 40 < len(sent) < 900:
                        found.append({"company": tk, "form": form, "date": date, "url": url, "terms": hit,
                                      "amounts": AMOUNT.findall(sent)[:4], "sentence": sent.strip()[:600]})
    except Exception as e:
        status = f"partial ({type(e).__name__})"
    SEEN.write_text(json.dumps(sorted(seen)))
    FOUND.write_text(json.dumps(found, indent=1))
    return {"status": status, "new_filings_scanned": n, "total_findings": len(found)}
