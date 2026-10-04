"""The dashboard numbers: value, reference scale with documented zones, changes over four periods, and a reading that
depends on where the value falls. Price-based numbers have their own history; the others use the weekly snapshots kept in
data/kpi_history.json, so their changes appear as weeks accumulate."""
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SNAP = ROOT / "data" / "kpi_history.json"
PERIODS = {"1W": 7, "1M": 30, "3M": 91}
BLUE, CORAL, AMBER, PALE = "#2563EB", "#E04F4F", "#E3A21A", "#DCE3EC"


def _changes_from_series(s):
    s = s.dropna()
    if s.empty:
        return {}
    t, v = s.index[-1], float(s.iloc[-1])
    out = {}
    for k, d in PERIODS.items():
        prev = s[s.index <= t - pd.Timedelta(days=d)]
        out[k] = None if prev.empty else round(v - float(prev.iloc[-1]), 4)
    prev = s[s.index < pd.Timestamp(t.year, 1, 1)]
    out["YTD"] = None if prev.empty else round(v - float(prev.iloc[-1]), 4)
    return out


def _snap_series(hist, label):
    pts = {pd.Timestamp(h["date"]): h["values"].get(label) for h in hist if h["values"].get(label) is not None}
    return pd.Series(pts).sort_index() if pts else pd.Series(dtype=float)


def build(ind, today):
    hist = json.loads(SNAP.read_text()) if SNAP.exists() else []
    g = ind["lenders_gap"]
    ref = g["reference"]
    from monitor import indicators as I
    gap = getattr(I.lenders_gap, "daily", pd.Series(dtype=float))
    trailing = pd.Series({d: gap[(gap.index > d - pd.Timedelta(days=365)) & (gap.index <= d)].mean()
                          for d in pd.date_range("2017-01-01", gap.index.max(), freq="W-FRI")}).dropna() if len(gap) else pd.Series(dtype=float)
    since = [v[0] for y, v in g["yearly"].items() if int(y) >= 2024 and v[1] >= 5]
    ai = getattr(I.ai_path, "series", pd.Series(dtype=float)) / 100
    y10 = getattr(I.rates, "full", pd.Series(dtype=float))
    rows = []

    # 1. lenders' gap
    v = g["trailing_12m"]
    lo24 = min(since) if since else ref["pre2024_min"]
    zones = [(min(trailing.min() if len(trailing) else lo24, lo24) - 0.05, lo24, CORAL, "beyond every year since 2024"),
             (lo24, ref["pre2024_min"], AMBER, "the 2024-2026 range"),
             (ref["pre2024_min"], ref["pre2024_max"], BLUE, "the 2016-2023 range")]
    zone = next((z[3] for z in zones if v is not None and z[0] <= v <= z[1]), "above the 2016-2023 range")
    reading = {"the 2016-2023 range": "Back inside its pre-2024 range: the market no longer singles out the lenders.",
               "the 2024-2026 range": "Inside its 2024-2026 range: the market still singles out the AI-dependent lenders.",
               "beyond every year since 2024": "Wider than any year since 2024: the lenders are lagging more than ever."}.get(zone, "Above its usual range.")
    zone_gap = zone
    rows.append(dict(zone=zone_gap, label="Lenders' gap in AI sell-offs, last 12 months", unit="pts a day", value=v, fmt="{:+.2f}", dfmt="{:.2f}", bad="down",
                     kind="range", lo=zones[0][0], hi=ref["pre2024_max"] + 0.05, zones=zones, reading=reading,
                     scale_note="Zones from its own history (2016-2023 and 2024-2026)", changes=_changes_from_series(trailing)))

    # 2. AI chain against past booms at the same age
    age = ind["ai_path"]["years_now"]
    lv = []
    for e in ind["history"]["episodes"].values():
        xs = [x for x in e["x"] if x <= age]
        if xs:
            lv.append(e["y"][len(xs) - 1] / 100)
    v = ind["ai_path"]["level_now"] / 100
    peak = float(ai.max()) if len(ai) else v
    dd = (v / peak - 1) * 100
    lo, hi = (min(lv + [v]) * 0.9, max(lv + [v]) * 1.1) if lv else (0.5, v * 1.2)
    zones = [(min(lv), max(lv), PALE, "range of past booms at the same age")] if lv else []
    reading = (f"Within the range of past booms at {age:.1f} years. " if lv and min(lv) <= v <= max(lv) else
               f"{'Above' if lv and v > max(lv) else 'Below'} the range of past booms at {age:.1f} years. ") + \
              (f"{abs(dd):.0f}% below its peak: past the 20% mark that defines a bear market." if dd <= -20 else
               f"{abs(dd):.0f}% below its peak." if dd < -1 else "At its peak.")
    zai = ("above past booms" if lv and v > max(lv) else "below past booms" if lv and v < min(lv) else "within past booms") + ("; bear market" if dd <= -20 else "")
    rows.append(dict(zone=zai, label="AI supply chain since ChatGPT", unit="times its level at launch", value=v, fmt="{:.2f}x", dfmt="{:.2f}x", bad=None,
                     kind="range", lo=lo, hi=hi, zones=zones, reading=reading, scale_note="Grey band: past booms at the same age (chart above)",
                     changes=_changes_from_series(ai)))

    # 3-4. signs, as gauges
    for key, lab, bad in (("frenzy_count", "Signs of a late frenzy", "up"), ("turning_count", "Signs of a turning point", "up")):
        v = ind["signs"][key]
        reading = ("All six features of a late frenzy are present." if key == "frenzy_count" and v == 6 else
                   f"{v} of the six features are present." if v else "None of the six features is present yet.")
        rows.append(dict(zone=f"{v} of 6", label=lab, unit="of 6", value=v, fmt="{:.0f}", dfmt="{:.0f}", bad=bad, kind="gauge", lo=0, hi=6, zones=[],
                         reading=reading, scale_note="Each sign tied to a data series or a sourced event", changes=None))

    # 5-7. exposed companies, 52-week range of their relative line
    for t, name, refname in (("ORCL", "Oracle", "the AI chain"), ("CRWV", "CoreWeave", "the AI chain"), ("9984.T", "SoftBank", "the Tokyo market")):
        s = ind["exposed"].get(t)
        if s is None or not len(s):
            continue
        last = s[s.index > s.index[-1] - pd.Timedelta(days=365)]
        v, lo, hi = float(s.iloc[-1]), float(last.min()), float(last.max())
        pct = 0 if hi == lo else (v - lo) / (hi - lo)
        reading = ("Near the bottom of its 52-week range: the market keeps weighing its exposure to OpenAI." if pct < 0.2 else
                   "Near the top of its 52-week range." if pct > 0.8 else "In the middle of its 52-week range.")
        zx = "bottom of 52-week range" if pct < 0.2 else "top of 52-week range" if pct > 0.8 else "middle of 52-week range"
        rows.append(dict(zone=zx, label=f"{name} against {refname} since Jan 2025", unit="%", value=v, fmt="{:+.0f}%", dfmt="{:.0f} pts", bad="down",
                         kind="range", lo=lo, hi=hi, zones=[], reading=reading, scale_note="Bar: its 52-week range", changes=_changes_from_series(s)))

    # 8-9. share of value at stake
    for comp, ten in (("Oracle", "OpenAI"), ("Broadcom", "Anthropic")):
        v = next((r["pct_of_value"] for r in ind["exposure"] if r["company"] == comp and r["tenant"] == ten), None)
        if v is None:
            continue
        zones = [(0, 10, BLUE, "could absorb it"), (10, 20, AMBER, "between"), (20, 100, CORAL, "exposed")]
        reading = ("Under 10% of its value: in the zone of the companies that could absorb a failure." if v < 10 else
                   "Over 20% of its value rests on one tenant: in the zone of the exposed companies." if v >= 20 else
                   "Between the two groups of Table 3: worth watching.")
        zx = "could absorb" if v < 10 else "exposed" if v >= 20 else "between"
        rows.append(dict(zone=zx, label=f"{comp}'s largest item with {ten}, share of its value", unit="%", value=v, fmt="{:.1f}%", dfmt="{:.1f} pts", bad="up",
                         kind="range", lo=0, hi=100, zones=zones,
                         reading=reading,
                         scale_note="Zones are this paper's reading of Table 3: the giants sit under 10%, the exposed above 20%",
                         changes=_changes_from_series(_snap_series(hist, f"{comp}'s largest item with {ten}, share of its value"))))

    # 10. lenders' link to chips and power
    cp = {int(k): v * 100 for k, v in ind["specificity"].get("chips_power", {}).items()}
    if cp:
        yr = max(cp)
        pre = [v for y, v in cp.items() if y <= 2023]
        v = cp[yr]
        zones = [(min(pre), max(pre), BLUE, "2016-2023 range")]
        reading = ("Back inside its pre-2024 range: the link to chips and power has faded." if min(pre) <= v <= max(pre) else
                   "Above its pre-2024 range: the lenders still move with chips and power beyond the market.")
        rows.append(dict(zone=("inside pre-2024 range" if min(pre) <= v <= max(pre) else "above pre-2024 range"), label="Lenders' link to chips and power, this year", unit="hundredths of a correlation", value=v, fmt="{:+.1f}", dfmt="{:.1f}",
                         bad="up", kind="range", lo=min(cp.values()) - 0.5, hi=max(cp.values()) + 0.5, zones=zones, reading=reading,
                         scale_note="Blue band: its 2016-2023 range", changes=None, yearly_prev=cp.get(yr - 1)))

    # 11. capital raised
    raised = next((float(d["amount_usd_bn"]) for d in ind["debt"] if "2026 so far" in d["measure"] and "Barclays" in d["source"]), None)
    full25 = next((float(d["amount_usd_bn"]) for d in ind["debt"] if "in 2025" in d["measure"] and "Barclays" in d["source"]), None)
    if raised is not None:
        rows.append(dict(zone="", label="Capital raised for AI in 2026 so far", unit="$bn", value=raised, fmt="{:,.0f}", dfmt="{:,.0f}", bad="up", kind="range",
                         lo=0, hi=max(raised, full25 or 0) * 1.2, zones=[(0, full25, PALE, "all of 2025")] if full25 else [],
                         reading=f"{raised / full25:.1f} times all of 2025, with the year not over." if full25 else "",
                         scale_note="Grey band: all of 2025 (Barclays)", changes=None))

    # 12. 10-year yield
    if len(y10):
        w = y10[y10.index > y10.index[-1] - pd.DateOffset(years=20)]
        v = float(y10.iloc[-1])
        higher = w[w >= v]
        since_ = None
        before = y10[(y10.index < y10.index[-1] - pd.Timedelta(days=30)) & (y10 >= v)]
        since_ = before.index[-1].year if len(before) else None
        rows.append(dict(zone="", label="10-year Treasury yield", unit="%", value=v, fmt="{:.2f}%", dfmt="{:.2f} pts", bad="up", kind="range",
                         lo=float(w.min()), hi=float(w.max()), zones=[],
                         reading=(f"Highest since {since_}: dearer refinancing for a build-out financed with debt." if since_ and since_ < y10.index[-1].year - 1
                                  else "Dearer refinancing matters for a build-out financed with debt."),
                         scale_note="Bar: its 20-year range (FRED)", changes=_changes_from_series(y10)))

    # snapshot for the numbers that have no history of their own
    snap = {"date": today, "values": {r["label"]: r["value"] for r in rows if r["value"] is not None},
            "zones": {r["label"]: r.get("zone", "") for r in rows}}
    previous = [h for h in hist if h["date"] != today]
    build.previous_zones = previous[-1].get("zones", {}) if previous else {}
    hist = previous + [snap]
    SNAP.write_text(json.dumps(hist[-260:]))
    for r in rows:
        if r["changes"] is None and r["kind"] == "gauge":
            r["changes"] = _changes_from_series(_snap_series(hist, r["label"]))
        r["value"] = None if r["value"] is None else round(float(r["value"]), 4)
    return rows
