"""Alerts written to data/alerts.json after each run. The workflow opens a GitHub issue when there is any, so the owner
gets an email: sources that failed, manual files gone stale, and numbers that changed zone."""
import datetime
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
STALE_DAYS = {"bets.csv": 60, "debt.csv": 60, "tenants.csv": 90, "events.csv": 45}


def freshness():
    """Latest date in each manual file and whether it has gone stale."""
    out = {}
    today = pd.Timestamp(datetime.date.today())
    for f, days in STALE_DAYS.items():
        p = ROOT / f
        if not p.exists():
            continue
        d = pd.to_datetime(pd.read_csv(p)["date"], errors="coerce").max()
        age = int((today - d).days) if pd.notna(d) else None
        out[f] = {"latest": None if pd.isna(d) else str(d.date()), "age_days": age, "limit_days": days,
                  "stale": age is not None and age > days}
    return out


def build(ind, status, kpis, previous_zones, fresh):
    alerts = []
    missing = [t for t, s in status.items() if s == "missing"]
    cached = [t for t, s in status.items() if s == "cache"]
    if missing:
        alerts.append(f"Missing price data for {len(missing)} series: {', '.join(missing[:12])}.")
    if len(cached) > 10:
        alerts.append(f"{len(cached)} series fell back to cached data; a source may be down.")
    for k, v in ind["source_summary"].items():
        if k in ("treasury", "sec", "railroads") and isinstance(v, str) and ("missing" in v or "partial" in v or "not available" in v):
            alerts.append(f"Source {k}: {v}.")
    for f, info in fresh.items():
        if info["stale"]:
            alerts.append(f"{f} is stale: last entry {info['latest']}, {info['age_days']} days ago (limit {info['limit_days']}).")
    for k in kpis:
        old, new = previous_zones.get(k["label"]), k.get("zone", "")
        if old is not None and new and old != new:
            alerts.append(f"Zone change, {k['label']}: from '{old}' to '{new}'.")
    (ROOT / "data" / "alerts.json").write_text(json.dumps({"date": ind["updated"], "alerts": alerts}, indent=1))
    return alerts
