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
    r = requests.get(url, headers=UA, timeout=10)
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


def _yahoo_batch(tickers, chunk=60):
    """Download many tickers from Yahoo Finance at once, in chunks. Returns {ticker: Series}."""
    import yfinance as yf
    out = {}
    for i in range(0, len(tickers), chunk):
        part = tickers[i:i + chunk]
        try:
            d = yf.download(part, start="2015-11-01", auto_adjust=True, progress=False, threads=True, group_by="column")
        except Exception as e:
            print(f"  Yahoo batch {i // chunk + 1} failed: {type(e).__name__}", flush=True)
            continue
        if d is None or d.empty:
            continue
        close = d["Close"] if "Close" in d.columns.get_level_values(0) else d
        if not hasattr(close, "columns"):
            close = close.to_frame(part[0])
        for t in part:
            if t in close.columns:
                ser = close[t].dropna()
                if len(ser) > 20:
                    ser.name = t
                    out[t] = ser
        print(f"  Yahoo batch {i // chunk + 1}: {sum(t in out for t in part)}/{len(part)} series", flush=True)
    return out


def prices(tickers):
    """Return a DataFrame of daily closes and a status dict {ticker: 'yahoo'|'stooq'|'cache'|'missing'}.
    Yahoo Finance first, in batches (fast); Stooq only for what is missing, with a short timeout and a circuit
    breaker so that a blocked source cannot stall the run; the local cache as last resort."""
    off = os.environ.get("MONITOR_OFFLINE")
    if off:
        return _offline_prices(tickers, Path(off))
    tickers = list(dict.fromkeys(tickers))
    print(f"Downloading {len(tickers)} price series", flush=True)
    got = _yahoo_batch(tickers)
    status = {t: "yahoo" for t in got}
    fails = 0
    for t in [t for t in tickers if t not in got]:
        if fails >= 3:
            break
        try:
            got[t] = _from_stooq(t)
            status[t] = "stooq"
            fails = 0
        except Exception:
            fails += 1
        time.sleep(0.3)
    print(f"  Stooq filled {sum(v == 'stooq' for v in status.values())}; circuit breaker {'tripped' if fails >= 3 else 'not tripped'}", flush=True)
    out = {}
    for t in tickers:
        if t in got:
            _save(got[t], t)
            out[t] = got[t]
        else:
            c = _load(t)
            status[t] = "cache" if c is not None else "missing"
            if c is not None:
                out[t] = c
    print(f"  Prices: {len(out)}/{len(tickers)} series, missing: {[t for t, v in status.items() if v == 'missing'][:15]}", flush=True)
    return pd.DataFrame(out).sort_index(), status


def treasury_10y():
    """10-year Treasury yield in percent, from FRED."""
    off = os.environ.get("MONITOR_OFFLINE")
    if off:
        d = pd.read_csv(Path(off) / "tipos_20261002.csv", index_col=0, parse_dates=True)["^TNX"].dropna()
        return d, "offline"
    try:
        r = requests.get("https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10",
                         headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko)"}, timeout=20)
        r.raise_for_status()
        df = pd.read_csv(io.StringIO(r.text))
        df.columns = ["date", "value"]
        s = pd.to_numeric(df["value"], errors="coerce")
        s.index = pd.to_datetime(df["date"])
        s = s.dropna()
        if len(s) < 100:
            raise ValueError("short FRED series")
        _save(s, "DGS10")
        return s, "fred"
    except Exception as e:
        print(f"  FRED unavailable ({type(e).__name__}); trying Yahoo ^TNX", flush=True)
    try:
        s = _from_yahoo("^TNX")
        if s.median() > 20:          # older quotes at ten times the yield
            s = s / 10
        _save(s, "DGS10")
        return s, "yahoo"
    except Exception as e:
        print(f"  Yahoo ^TNX unavailable ({type(e).__name__}); using cache if any", flush=True)
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
