"""Data download for the monitor.

Prices: Stooq daily CSV (free, no key), with Yahoo Finance (yfinance) as fallback.
Rates: 10-year US Treasury yield from FRED (series DGS10, free CSV, no key).
Each series is cached in data/cache/ so that a failed download keeps the last good data
instead of breaking the page; the status of every source is reported on the site.
Offline mode (for testing): set MONITOR_OFFLINE to a folder with local CSV panels.
"""
import io
import json
import os
import time
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "cache"
UA = {"User-Agent": "Mozilla/5.0 (Chips and Risk monitor; research)"}


def _stooq_symbol(t):
    if t.endswith(".T"):
        return t[:-2].lower() + ".jp"
    return t.lower().replace(".", "-") + ".us"


def _from_stooq(t):
    if t.endswith(".HK"):
        raise ValueError("Hong Kong listings are taken from Yahoo Finance")
    url = f"https://stooq.com/q/d/l/?s={_stooq_symbol(t)}&i=d"
    r = requests.get(url, headers=UA, timeout=30)
    r.raise_for_status()
    df = pd.read_csv(io.StringIO(r.text))
    if "Close" not in df.columns or df.empty:
        raise ValueError("no data from Stooq")
    s = pd.Series(df["Close"].values, index=pd.to_datetime(df["Date"]), name=t)
    return s.sort_index()


def _from_yahoo(t):
    import yfinance as yf
    d = yf.download(t, start="2015-11-01", auto_adjust=True, progress=False, threads=False)
    s = d["Close"]
    if hasattr(s, "columns"):
        s = s.iloc[:, 0]
    s = s.dropna()
    if s.empty:
        raise ValueError("no data from Yahoo")
    s.name = t
    return s


def _cache_path(name):
    return CACHE / f"{name.replace('^', '').replace('/', '_')}.csv"


def _save(s, name):
    CACHE.mkdir(parents=True, exist_ok=True)
    s.to_frame("value").to_csv(_cache_path(name))


def _load(name):
    p = _cache_path(name)
    if p.exists():
        d = pd.read_csv(p, index_col=0, parse_dates=True)["value"]
        d.name = name
        return d
    return None


def clean(P):
    """Drop isolated bad prints: a close below 40% or above 250% of the median of the previous ten closes
    (for example a day quoted at one tenth of its level after a faulty split adjustment). Returns cleaned prices and a count."""
    med = P.rolling(10, min_periods=5).median().shift(1)
    bad = (P < 0.4 * med) | (P > 2.5 * med)
    return P.mask(bad), int(bad.sum().sum())


def prices(tickers):
    """Return a DataFrame of daily closes and a status dict {ticker: 'stooq'|'yahoo'|'cache'|'missing'}."""
    off = os.environ.get("MONITOR_OFFLINE")
    if off:
        return _offline_prices(tickers, Path(off))
    out, status = {}, {}
    for t in tickers:
        s = None
        for nombre, f in (("stooq", _from_stooq), ("yahoo", _from_yahoo)):
            for intento in range(2):
                try:
                    s = f(t)
                    status[t] = nombre
                    break
                except Exception:
                    time.sleep(2)
            if s is not None:
                break
        if s is not None:
            _save(s, t)
        else:
            s = _load(t)
            status[t] = "cache" if s is not None else "missing"
        if s is not None:
            out[t] = s
        time.sleep(0.3)
    return pd.DataFrame(out).sort_index(), status


def treasury_10y():
    """10-year Treasury yield in percent, from FRED."""
    off = os.environ.get("MONITOR_OFFLINE")
    if off:
        d = pd.read_csv(Path(off) / "tipos_20261002.csv", index_col=0, parse_dates=True)["^TNX"].dropna()
        return d, "offline"
    try:
        r = requests.get("https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10", headers=UA, timeout=30)
        r.raise_for_status()
        df = pd.read_csv(io.StringIO(r.text))
        df.columns = ["date", "value"]
        s = pd.to_numeric(df["value"], errors="coerce")
        s.index = pd.to_datetime(df["date"])
        s = s.dropna()
        _save(s, "DGS10")
        return s, "fred"
    except Exception:
        s = _load("DGS10")
        return s, ("cache" if s is not None else "missing")


def _offline_prices(tickers, folder):
    frames = []
    for f in ("panel_capa_financiera_20261002.csv", "panel_paso2_20261002.csv", "panel_capa2_20261002.csv"):
        p = folder / f
        if p.exists():
            frames.append(pd.read_csv(p, index_col=0, parse_dates=True))
    allp = pd.concat(frames, axis=1)
    allp = allp.loc[:, ~allp.columns.duplicated()]
    cols = [t for t in tickers if t in allp.columns]
    status = {t: ("offline" if t in allp.columns else "missing") for t in tickers}
    return allp[cols].sort_index(), status
