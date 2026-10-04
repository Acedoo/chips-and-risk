"""Indicators, with the definitions of 'The Sharp End of AI Debt' (Acedo, 2026).

Every quantity uses only information available on the day it refers to:
betas over the previous 250 sessions, sell-off thresholds over the previous 500 sessions.
"""
import numpy as np
import pandas as pd


def returns(P):
    return P.pct_change(fill_method=None)


def abnormal(r, cols, market):
    """Return beyond what the market predicts (equation 1): r_i - beta_i r_m, beta over the previous 250 days."""
    rm = r[market]
    cov = r[cols].rolling(250, min_periods=200).cov(rm).shift(1)
    var = rm.rolling(250, min_periods=200).var().shift(1)
    return r[cols] - cov.div(var, axis=0).mul(rm, axis=0)


def selloff_days(chain_ret):
    """AI sell-off days: chain return at or below the 5th percentile of the previous 500 sessions."""
    thr = chain_ret.rolling(500, min_periods=250).quantile(0.05).shift(1)
    return chain_ret[chain_ret <= thr].index


def lenders_gap(P, cfg, chain):
    """Equation (2): mean abnormal return of lenders minus other financials on AI sell-off days."""
    r = returns(P)
    L = [c for c in cfg["lenders"] if c in r]
    O = [c for c in cfg["other_financials"] if c in r]
    C = [c for c in chain if c in r]
    AR = abnormal(r, L + O, cfg["market"])
    chain_ret = r[C].mean(axis=1)
    days = selloff_days(chain_ret)
    gap = (AR.loc[days, L].mean(axis=1) - AR.loc[days, O].mean(axis=1)).dropna() * 100
    yearly = gap.groupby(gap.index.year).agg(["mean", "count"])
    last = gap.index.max()
    trailing = gap[gap.index > last - pd.Timedelta(days=365)]
    pre = yearly.loc[[y for y in yearly.index if y <= 2023 and yearly.loc[y, "count"] >= 5]]   # years with too few sell-off days do not set the band
    since = gap[gap.index >= "2024-01-01"]
    ref = {"pre2024_min": float(pre["mean"].min()), "pre2024_max": float(pre["mean"].max()),
           "since2024_mean": float(since.mean()) if len(since) else None}
    t = float(trailing.mean()) if len(trailing) else None
    if t is None:
        reading = "No AI sell-off day in the last twelve months."
        state = "quiet"
    elif t < ref["pre2024_min"]:
        reading = (f"In the last twelve months the lenders lagged other financial stocks by {abs(t):.2f} points a day "
                   f"when AI fell hardest, beyond any year before 2024.")
        state = "alert" if t <= -0.4 else "watch"
    elif t <= ref["pre2024_max"]:
        reading = (f"In the last twelve months the gap was {t:+.2f} points a day, back inside the range of 2016-2023.")
        state = "normal"
    else:
        reading = f"In the last twelve months the lenders did better than other financial stocks in AI sell-offs ({t:+.2f})."
        state = "normal"
    lenders_gap.daily = gap
    return {"yearly": {int(k): [round(float(v["mean"]), 3), int(v["count"])] for k, v in yearly.iterrows()},
            "trailing_12m": None if t is None else round(t, 3), "trailing_days": int(len(trailing)),
            "reference": {k: (None if v is None else round(v, 3)) for k, v in ref.items()},
            "reading": reading, "state": state, "last_selloff": str(last.date()) if len(gap) else None}


def exposed_vs_chain(P, cfg, chain, start="2025-01-02"):
    """Cumulative return of the three companies most exposed to OpenAI against their reference since `start`."""
    r = returns(P)
    C = [c for c in chain if c in r and c not in cfg["exposed_us"]]
    ref_us = r[C].mean(axis=1)
    out = {}
    for t in cfg["exposed_us"]:
        if t in r:
            x = (r[t] - ref_us)[start:].dropna()
            out[t] = (100 * ((1 + x).cumprod() - 1)).round(2)
    sb, tp = cfg["softbank"], cfg["topix"]
    if sb in r and tp in r:
        jp = pd.concat([P[sb], P[tp]], axis=1).dropna().pct_change()
        x = (jp[sb] - jp[tp])[start:].dropna()
        out[sb] = (100 * ((1 + x).cumprod() - 1)).round(2)
    return out


def softbank_reactions(P, cfg, events):
    """SoftBank minus TOPIX on the first Tokyo session after each OpenAI news event (prediction 1 of the paper)."""
    sb, tp = cfg["softbank"], cfg["topix"]
    if sb not in P or tp not in P:
        return []
    jp = pd.concat([P[sb], P[tp]], axis=1).dropna().pct_change().dropna()
    rows = []
    for _, e in events[events["type"] == "openai_news"].iterrows():
        d = pd.Timestamp(e["date"]) + pd.Timedelta(days=1)
        k = jp.index.searchsorted(d)
        if k < len(jp):
            s = jp.index[k]
            rows.append({"event_date": str(pd.Timestamp(e["date"]).date()), "session": str(s.date()),
                         "description": e["description"], "softbank_minus_topix": round(float((jp.loc[s, sb] - jp.loc[s, tp]) * 100), 2)})
    return rows


def financing_ledger(events):
    """Supplier financing against outside capital, by quarter, from the events file (the telecoms warning sign)."""
    e = events[events["type"].isin(["supplier_financing", "outside_capital"])].copy()
    if e.empty:
        return {}
    e["q"] = pd.to_datetime(e["date"]).dt.to_period("Q").astype(str)
    t = e.pivot_table(index="q", columns="type", values="amount_usd_bn", aggfunc="sum").fillna(0)
    return {q: {c: float(v) for c, v in row.items()} for q, row in t.iterrows()}


def rates(y10):
    if y10 is None or len(y10.dropna()) == 0:
        rates.full = pd.Series(dtype=float)
        return {"last": None, "date": None, "change_3m_bp": None, "series": pd.Series(dtype=float)}
    y10 = y10.dropna()
    rates.full = y10
    last = y10.index.max()
    prev = y10[y10.index <= last - pd.Timedelta(days=91)]
    ch = None if prev.empty else round(float((y10.iloc[-1] - prev.iloc[-1]) * 100), 1)
    return {"last": round(float(y10.iloc[-1]), 3), "date": str(last.date()), "change_3m_bp": ch,
            "series": y10["2024-01-01":].resample("W").last().round(3)}


def evaluate_signs(signs, ind, events, today):
    """Evaluate the frenzy, turning-point and scenario signals. Every rule is explicit and documented in config/signs.json."""
    ev = events.copy()
    ev["date"] = pd.to_datetime(ev["date"])
    recent = ev[ev["date"] > pd.Timestamp(today) - pd.Timedelta(days=365)]
    g = ind["lenders_gap"]
    yr = {int(k): v for k, v in g["yearly"].items()}
    since = [v[0] for y, v in yr.items() if y >= 2024 and v[1] >= 5]
    led = ind["ledger"]

    def exposed_all_down():
        res = []
        for s in ind["exposed"].values():
            if len(s) < 70:
                return False
            a, b = 1 + s.iloc[-1] / 100, 1 + s.iloc[-64] / 100
            res.append(a / b - 1 < 0)
        return bool(res) and all(res)

    def ledger_turn():
        """Supplier financing up and outside capital down, last 180 days against the previous 180.
        Needs at least two events of each kind in each window; otherwise there is not enough evidence and the sign stays off."""
        t = pd.Timestamp(today)
        w1 = ev[(ev["date"] > t - pd.Timedelta(days=180))]
        w0 = ev[(ev["date"] > t - pd.Timedelta(days=360)) & (ev["date"] <= t - pd.Timedelta(days=180))]
        cnt = lambda w, k: int((w["type"] == k).sum())
        if min(cnt(w, k) for w in (w0, w1) for k in ("supplier_financing", "outside_capital")) < 2:
            return False
        tot = lambda w, k: float(w.loc[w["type"] == k, "amount_usd_bn"].fillna(0).sum())
        return tot(w1, "supplier_financing") > tot(w0, "supplier_financing") and tot(w1, "outside_capital") < tot(w0, "outside_capital")

    def check(rule, partial=None):
        kind, _, arg = rule.partition(":")
        if kind == "static":
            return True
        if kind in ("event_12m", "event_any", "no_event"):
            typ, _, comp = arg.partition(":")
            pool = recent if kind == "event_12m" else ev
            m = pool[pool["type"] == typ]
            if comp:
                m = m[m["company"] == comp]
            return m.empty if kind == "no_event" else not m.empty
        if kind == "gap_state":
            return g["state"] in ("alert", "watch")
        if kind == "gap_normal":
            return g["state"] == "normal"
        if kind == "gap_beyond_2024":
            return g["trailing_12m"] is not None and bool(since) and g["trailing_12m"] < min(since)
        if kind == "exposed_all_down":
            return exposed_all_down()
        if kind == "ledger_turn":
            return ledger_turn()
        if kind == "rates_up":
            return (ind["rates"]["change_3m_bp"] or 0) > 50
        if kind == "turning_ge2":
            return (partial or 0) >= 2
        return False

    fr = [dict(s, on=check(s["rule"])) for s in signs["frenzy"]]
    tu = [dict(s, on=check(s["rule"])) for s in signs["turning"]]
    nt = sum(s["on"] for s in tu)
    sc = [dict(s, on=check(s["rule"], nt)) for s in signs["scenario_signals"]]
    return {"frenzy": fr, "turning": tu, "scenarios": sc,
            "frenzy_count": sum(s["on"] for s in fr), "turning_count": nt}


def group_gap(P, cfg, chain, group):
    """Equation (2) for any group against the other financial stocks, by year (used for the loan vehicles, the BDCs)."""
    r = returns(P)
    G = [c for c in group if c in r]
    O = [c for c in cfg["other_financials"] if c in r]
    C = [c for c in chain if c in r]
    if len(G) < 5:
        return {}
    AR = abnormal(r, G + O, cfg["market"])
    days = selloff_days(r[C].mean(axis=1))
    gap = (AR.loc[days, G].mean(axis=1) - AR.loc[days, O].mean(axis=1)).dropna() * 100
    yearly = gap.groupby(gap.index.year).agg(["mean", "count"])
    return {int(k): [round(float(v["mean"]), 3), int(v["count"])] for k, v in yearly.iterrows()}


def exposure_now(P, exp):
    """Largest documented item each counterparty has at stake with each tenant, as % of its current market value.
    Current value = base value x price change since the base date."""
    rows = []
    base = pd.Timestamp(exp["base_date"])
    for t, c in exp["companies"].items():
        scale, note = 1.0, "base value"
        if t in P:
            s = P[t].dropna()
            b, n = s[s.index <= base], s
            if len(b) and len(n):
                scale, note = float(n.iloc[-1] / b.iloc[-1]), f"scaled to {n.index[-1].date()}"
        cap = c["base_cap_bn"] * scale
        for tenant in sorted({i[0] for i in c["items"]}):
            its = [i for i in c["items"] if i[0] == tenant]
            top = max(its, key=lambda i: i[2])
            rows.append({"company": c["name"], "tenant": tenant, "kind": top[1], "amount_bn": top[2],
                         "pct_of_value": round(100 * top[2] / cap, 1), "value_note": note})
    return sorted(rows, key=lambda r: -r["pct_of_value"])


def specificity_channels(P, cfg, ch, step=10, win=250):
    """Equation (3) net of the market and of an equal-weighted financial index, lenders minus other financials,
    separately for the software block and for chips, equipment and power, by year."""
    r = returns(P)
    L = [c for c in cfg["lenders"] if c in r]
    O = [c for c in cfg["other_financials"] if c in r]
    soft = [c for c in ch["software"] if c in r]
    hard = [c for c in ch["semis"] + ch["equipo"] + ch["utilities"] if c in r]
    neu = [c for c in ch["neutra"] if c in r]
    if len(neu) < 20:
        return {}
    cols = L + O + soft + hard + neu
    R = r[cols + [cfg["market"]]].dropna(how="all")
    fin = R[L + O].mean(axis=1)
    out = {"software": {}, "chips_power": {}}
    idx = R.index
    for end in range(win, len(idx) + 1, step):
        W = R.iloc[end - win:end]
        W = W.loc[:, W.notna().mean() > 0.95].fillna(0.0)
        if cfg["market"] not in W:
            continue
        X = np.column_stack([np.ones(len(W)), W[cfg["market"]].values, fin.iloc[end - win:end].fillna(0.0).values])
        Y = W.drop(columns=[cfg["market"]])
        B, *_ = np.linalg.lstsq(X, Y.values, rcond=None)
        E = Y.values - X @ B
        E = (E - E.mean(0)) / np.where(E.std(0) > 0, E.std(0), 1)
        names = list(Y.columns)
        ix = {n: i for i, n in enumerate(names)}
        def blk(a, b):
            ia, ib = [ix[x] for x in a if x in ix], [ix[x] for x in b if x in ix]
            if not ia or not ib:
                return None
            return np.abs(E[:, ia].T @ E[:, ib] / len(E)).mean(axis=1)
        yr = W.index[-1].year
        for key, chan in (("software", soft), ("chips_power", hard)):
            sL, sO = blk(L, chan), blk(O, chan)
            nL, nO = blk(L, neu), blk(O, neu)
            if sL is None or sO is None or nL is None or nO is None:
                continue
            out[key].setdefault(yr, []).append(float((sL - nL).mean() - (sO - nO).mean()))
    return {k: {y: round(float(np.mean(v)), 4) for y, v in d.items()} for k, d in out.items()}


def public_labs(P, cfg):
    """AI tenants that already have a public price, against their listing price (%)."""
    out = {}
    for t, c in cfg.get("public_labs", {}).items():
        if t in P:
            s = P[t].dropna()
            s = s[s.index >= c["listing_date"]]
            if len(s):
                out[c["name"]] = (100 * (s / c["listing_price"] - 1)).round(1)
    return out


def capability_vs_credit(P, cfg, chain, events, horizon=10):
    """Oracle and CoreWeave against the rest of the chain over the sessions after each capability announcement (%)."""
    r = returns(P)
    C = [c for c in chain if c in r and c not in cfg["exposed_us"]]
    ref = r[C].mean(axis=1)
    rows = []
    for _, e in events[events["type"] == "capability"].iterrows():
        d = pd.Timestamp(e["date"])
        win = r.index[r.index > d][:horizon]
        if len(win) < 3:
            continue
        row = {"date": str(d.date()), "description": e["description"], "sessions": int(len(win))}
        for t, n in (("ORCL", "Oracle"), ("CRWV", "CoreWeave")):
            if t in r:
                x = (r.loc[win, t] - ref.loc[win]).dropna()
                row[n] = round(float(((1 + x).prod() - 1) * 100), 1)
        rows.append(row)
    return rows


def lender_ranking(P, cfg, chain, since="2024-01-01"):
    """Each lender's abnormal return minus the mean of other financial stocks on AI sell-off days since `since` (points a day)."""
    r = returns(P)
    L = [c for c in cfg["lenders"] if c in r]
    O = [c for c in cfg["other_financials"] if c in r]
    C = [c for c in chain if c in r]
    AR = abnormal(r, L + O, cfg["market"])
    days = [d for d in selloff_days(r[C].mean(axis=1)) if d >= pd.Timestamp(since)]
    if not days:
        return []
    ref = AR.loc[days, O].mean(axis=1)
    out = [{"ticker": t, "gap": round(float((AR.loc[days, t] - ref).mean() * 100), 2)} for t in L]
    return sorted(out, key=lambda x: x["gap"])


def sensitivity(P, cfg, chain):
    """How much the lenders and other financial stocks fall when the AI chain falls 10%: daily betas on the chain basket."""
    r = returns(P)
    L = [c for c in cfg["lenders"] if c in r]
    O = [c for c in cfg["other_financials"] if c in r]
    C = [c for c in chain if c in r]
    ch, lr, orr = r[C].mean(axis=1), r[L].mean(axis=1), r[O].mean(axis=1)
    def b(y, a, z):
        x = pd.concat([ch, y], axis=1)[a:z].dropna()
        return float(np.cov(x.iloc[:, 0], x.iloc[:, 1])[0, 1] / x.iloc[:, 0].var()) if len(x) > 100 else None
    res = {}
    for k, (a, z) in {"2020-2023": ("2020-01-01", "2023-12-31"), "since 2024": ("2024-01-01", None)}.items():
        bl, bo = b(lr, a, z), b(orr, a, z)
        res[k] = {"lenders": None if bl is None else round(10 * bl, 1), "others": None if bo is None else round(10 * bo, 1)}
    return res


def ai_path(P, chain, start="2022-11-30"):
    """Equal-weighted AI supply-chain basket since the launch of ChatGPT, rebased to 100, against years since the start."""
    r = returns(P)
    C = [c for c in chain if c in r]
    x = r[C].mean(axis=1)[start:].dropna()
    lvl = 100 * (1 + x).cumprod()
    t = np.asarray((lvl.index - pd.Timestamp(start)).days / 365.25)   # calendar years, comparable across eras
    s = pd.Series(lvl.values, index=t).iloc[::5]
    s = pd.concat([s, pd.Series([lvl.iloc[-1]], index=[t[-1]])])
    ai_path.series = lvl
    return {"x": [round(float(v), 3) for v in s.index], "y": [round(float(v), 2) for v in s.values],
            "years_now": round(float(t[-1]), 2), "level_now": round(float(lvl.iloc[-1]), 1), "date_now": str(lvl.index[-1].date()),
            "peak_level": round(float(lvl.max()), 1), "peak_date": str(lvl.idxmax().date())}
