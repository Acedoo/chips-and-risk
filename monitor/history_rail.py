"""Adds the US railroad boom (Macaulay's monthly index of American railroad stock prices, NBER Macrohistory m11005, via FRED)
to config/history.json the first time it runs online. Start: April 1865, end of the Civil War; the boom ended in the Panic of
1873 (failure of Jay Cooke & Co., September 1873). Monthly data, plotted in calendar years like the other episodes."""
import io
import json
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
NAME = "US railroads, 1865-75"


def ensure():
    p = ROOT / "config" / "history.json"
    H = json.loads(p.read_text())
    if NAME in H["episodes"]:
        return "present"
    try:
        r = requests.get("https://fred.stlouisfed.org/graph/fredgraph.csv?id=M11005USM293NNBR",
                         headers={"User-Agent": "Mozilla/5.0 (Chips and Risk monitor; research)"}, timeout=30)
        r.raise_for_status()
        df = pd.read_csv(io.StringIO(r.text))
        df.columns = ["date", "value"]
        s = pd.to_numeric(df["value"], errors="coerce")
        s.index = pd.to_datetime(df["date"])
        t0 = pd.Timestamp("1865-04-01")
        s = s.dropna()[t0: t0 + pd.DateOffset(years=10)]
        lvl = 100 * s / s.iloc[0]
        t = (lvl.index - t0).days / 365.25
        peak = lvl.idxmax()
        H["episodes"][NAME] = {"x": [round(float(x), 3) for x in t], "y": [round(float(v), 2) for v in lvl.values],
                               "peak_years": round(float((peak - t0).days / 365.25), 2), "peak_date": str(peak.date()),
                               "peak_level": round(float(lvl.max()), 1), "trough_after_peak": round(float(lvl[peak:].min()), 1),
                               "group": "tech", "monthly": True}
        H.setdefault("starts", {})[NAME] = "Apr 1865, end of the Civil War; the boom ended in the Panic of 1873"
        H["source_railroads"] = ("F.R. Macaulay, American railroad stock prices (NBER Macrohistory m11005), monthly, retrieved from "
                                 "FRED, Federal Reserve Bank of St. Louis, series M11005USM293NNBR. Price index without dividends.")
        p.write_text(json.dumps(H))
        return "added"
    except Exception as e:
        return f"not available ({type(e).__name__})"
