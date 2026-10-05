"""Weekly run: download data, compute indicators, scan new filings, write docs/index.html and docs/indicators.json."""
import datetime
import json
import os
from collections import Counter
from pathlib import Path

import pandas as pd

from monitor import pages, share, alerts as alertmod, data, edgar, indicators, kpis as kpimod, site

ROOT = Path(__file__).resolve().parents[1]


def main():
    cfg = json.loads((ROOT / "config" / "settings.json").read_text())
    ch = json.loads((ROOT / "config" / "chain.json").read_text())
    chain = ch["semis"] + ch["equipo"] + ch["utilities"] + ch["software"]
    tickers = sorted(set(chain + cfg["lenders"] + cfg["other_financials"] + [cfg["market"]] + cfg["exposed_us"]
                         + [cfg["softbank"], cfg["topix"]] + ch["neutra"] + cfg["bdcs"] + list(cfg["public_labs"])))
    P, status = data.prices(tickers)
    P, n_bad = data.clean(P)
    y10, y_status = data.treasury_10y()
    events = pd.read_csv(ROOT / "events.csv")
    print("Prices done; reading Treasury yield and SEC filings", flush=True)
    if os.environ.get("MONITOR_OFFLINE"):
        ed = {"status": "skipped (offline)", "new_filings_scanned": 0}
    elif os.environ.get("MONITOR_MODE", "weekly") == "daily":
        ed = {"status": "weekly only", "new_filings_scanned": 0}
    else:
        ed = edgar.scan(cfg)
    found = json.loads((ROOT / "data" / "edgar_findings.json").read_text()) if (ROOT / "data" / "edgar_findings.json").exists() else []
    prev_path = ROOT / "docs" / "indicators.json"
    prev = json.loads(prev_path.read_text()) if prev_path.exists() else None
    bets = pd.read_csv(ROOT / "bets.csv").fillna("").to_dict("records")
    signs = json.loads((ROOT / "config" / "signs.json").read_text())
    ind = {
        "bets": bets,
        "updated": datetime.date.today().isoformat(),
        "lenders_gap": indicators.lenders_gap(P, cfg, chain),
        "exposed": indicators.exposed_vs_chain(P, cfg, chain),
        "softbank": indicators.softbank_reactions(P, cfg, events),
        "ledger": indicators.financing_ledger(events),
        "rates": indicators.rates(y10),
        "bdc_gap": indicators.group_gap(P, cfg, chain, cfg["bdcs"]),
        "public_labs": indicators.public_labs(P, cfg),
        "ranking": indicators.lender_ranking(P, cfg, chain),
        "ai_path": indicators.ai_path(P, chain),
        "history": json.loads((ROOT / "config" / "history.json").read_text()),
        "houses": json.loads((ROOT / "config" / "houses.json").read_text()),
        "sensitivity": indicators.sensitivity(P, cfg, chain),
        "capability": indicators.capability_vs_credit(P, cfg, chain, events),
        "specificity": indicators.specificity_channels(P, cfg, ch),
        "exposure": indicators.exposure_now(P, json.loads((ROOT / "config" / "exposures.json").read_text())),
        "debt": pd.read_csv(ROOT / "debt.csv").fillna("").to_dict("records"),
        "tenants": pd.read_csv(ROOT / "tenants.csv").fillna("").to_dict("records"),
        "events": events.fillna("").to_dict("records"),
        "filings": sorted(found, key=lambda f: f["date"], reverse=True),
        "source_summary": dict(Counter(status.values()), treasury=y_status, sec=ed["status"], bad_prints_removed=n_bad),
    }
    ind["signs"] = indicators.evaluate_signs(signs, ind, events, ind["updated"])
    ind["changes"], ind["changes_es"] = changes(prev, ind, events, found)
    ind["kpis"] = kpimod.build(ind, ind["updated"])
    ind["freshness"] = alertmod.freshness()
    ind["alerts"] = alertmod.build(ind, status, ind["kpis"], getattr(kpimod.build, "previous_zones", {}), ind["freshness"])
    ind["headline"], ind["headline_es"] = headline(ind)
    ind["needle"] = needle(ind)
    ind["course"] = course(ind["needle"], ind["updated"])
    ind["weekly"] = weekly(ind, events)
    (ROOT / "data" / "weekly_digest.md").write_text(digest(ind), encoding="utf-8")
    (ROOT / "docs").mkdir(exist_ok=True)
    site.build(ind, ROOT / "docs" / "index.html")
    site.build(spanish(ind), ROOT / "docs" / "es" / "index.html", lang="es")
    arch = pages.update_archive(ind)
    pages.build(arch, ROOT / "docs")
    from monitor import i18n
    cnt = {k: sum(1 for s in ind["signs"]["scenarios"] if s["scenario"] == k and s["on"]) for k in ind["houses"]}
    lab_en = {"listing": "Listing", "delay": "Delay", "fav": "Favourable", "adv": "Adverse"}
    lab_es = {"listing": "Salida", "delay": "Aplazamiento", "fav": "Favorables", "adv": "Adversas"}
    share.make_card(ROOT / "docs" / "share.png", ind["headline"], ind["needle"],
                    {k: {"point": v["point"], "name": v["name"]} for k, v in ind["houses"].items()}, cnt,
                    "Week of " + datetime.date.fromisoformat(ind["updated"]).strftime("%-d %B %Y"), "Who carries the risk of the AI build-out", lab_en)
    share.make_card(ROOT / "docs" / "es" / "share.png", ind["headline_es"], ind["needle"],
                    {k: {"point": v["point"], "name": v.get("name_es", v["name"])} for k, v in ind["houses"].items()}, cnt,
                    "Semana del " + i18n.fecha(ind["updated"]), "Quién carga con el riesgo de la inversión en IA", lab_es)
    out = {k: v for k, v in ind.items() if k not in ("exposed", "rates", "events", "filings", "bets", "debt", "tenants", "public_labs", "history", "houses", "ai_path", "course", "weekly")}
    out["alerts"] = ind["alerts"]
    out["ai_now"] = {k: ind["ai_path"][k] for k in ("years_now", "level_now", "date_now")}
    print("ALERTS:", len(ind["alerts"]))
    out["n_filings"] = len(found)
    out["rates"] = {k: v for k, v in ind["rates"].items() if k != "series"}
    out["exposed_last"] = {k: float(s.iloc[-1]) for k, s in ind["exposed"].items() if len(s)}
    out["missing_tickers"] = [t for t, s in status.items() if s == "missing"]
    (ROOT / "docs" / "indicators.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({"updated": ind["updated"], "reading": ind["lenders_gap"]["reading"], "sources": ind["source_summary"],
                      "missing": out["missing_tickers"]}, indent=1))


def spanish(ind):
    """Copy of the indicators with the hand-kept Spanish fields swapped in (English where a row has none)."""
    import copy
    e = copy.deepcopy({k: v for k, v in ind.items() if k not in ("exposed", "public_labs")})
    e["exposed"], e["public_labs"] = ind["exposed"], ind["public_labs"]
    pick = lambda d, a, b: d.get(b) if isinstance(d.get(b), str) and d.get(b) else d.get(a)
    for r in e["events"]:
        r["description"] = pick(r, "description", "description_es")
    for r in e["bets"]:
        r["bet"] = pick(r, "bet", "bet_es")
    for r in e["debt"] + e["tenants"]:
        r["measure"] = pick(r, "measure", "measure_es")
    for grp in ("frenzy", "turning", "scenarios"):
        for x in e["signs"][grp]:
            x["text"] = x.get("text_es") or x["text"]
    for h in e["houses"].values():
        h["name"], h["motto"], h["position"] = h.get("name_es", h["name"]), h.get("motto_es", h["motto"]), h.get("position_es", h["position"])
        h["characters"] = h.get("characters_es", h["characters"])
    e["headline"], e["changes"] = ind["headline_es"], ind["changes_es"]
    e["needle"] = dict(ind["needle"], note_en=ind["needle"]["note_es"], short_en=ind["needle"]["short_es"])
    if e.get("weekly", {}).get("needle_prev"):
        e["weekly"]["needle_prev"] = dict(e["weekly"]["needle_prev"], short_en=e["weekly"]["needle_prev"].get("short_es", e["weekly"]["needle_prev"].get("short_en")))
    e["weekly"]["needle_now"] = e["needle"]
    e["weekly"]["signs_on"], e["weekly"]["signs_off"] = ind["weekly"]["signs_on_es"], ind["weekly"]["signs_off_es"]
    for x in e["weekly"]["events"]:
        x["description"] = x.get("description_es") or x["description"]
    for r in e["softbank"]:
        r["description"] = next((x.get("description_es") or x["description"] for x in ind["events"] if x["description"] == r["description"]), r["description"])
    for c in e["capability"]:
        c["description"] = next((x.get("description_es") or x["description"] for x in ind["events"] if x["description"] == c["description"]), c["description"])
    return e


def kpis(ind, prev):
    """Headline numbers, each with its previous value and a line saying what a rise or a fall means."""
    pk = {k["label"]: k["value"] for k in (prev or {}).get("kpis", [])}
    exp = lambda comp, ten: next((r["pct_of_value"] for r in ind["exposure"] if r["company"] == comp and r["tenant"] == ten), None)
    last = lambda k: float(ind["exposed"][k].iloc[-1]) if k in ind["exposed"] and len(ind["exposed"][k]) else None
    cp = ind["specificity"].get("chips_power", {})
    chips = 100 * cp[max(cp, key=int)] if cp else None
    raised = next((float(d["amount_usd_bn"]) for d in ind["debt"] if "2026 so far" in d["measure"] and "Barclays" in d["source"]), None)
    rows = [
        ("Lenders' gap in AI sell-offs, last 12 months (pts a day)", ind["lenders_gap"]["trailing_12m"], "{:+.2f}", "{:.2f} pts", "down", 0.005,
         "More negative: the market singles out the AI-dependent lenders more when AI falls."),
        ("AI supply chain since ChatGPT", ind["ai_path"]["level_now"] / 100, "{:.2f}x", "{:.2f}x", None, 0.005,
         "Higher: the build-out keeps rising. In past booms the turn came as a fall from the peak."),
        ("Signs of a late frenzy", ind["signs"]["frenzy_count"], "{:.0f} of 6", "{:.0f}", "up", 0.5,
         "Higher: more features of a late frenzy are present."),
        ("Signs of a turning point", ind["signs"]["turning_count"], "{:.0f} of 6", "{:.0f}", "up", 0.5,
         "Higher: more features of a turning point are present."),
        ("Oracle against the AI chain since Jan 2025", last("ORCL"), "{:+.0f}%", "{:.0f} pts", "down", 0.5,
         "Lower: the market weighs Oracle's OpenAI contracts as a burden."),
        ("CoreWeave against the AI chain since Jan 2025", last("CRWV"), "{:+.0f}%", "{:.0f} pts", "down", 0.5,
         "Lower: the same for the smallest of the three exposed companies."),
        ("SoftBank against Tokyo since Jan 2025", last("9984.T"), "{:+.0f}%", "{:.0f} pts", "down", 0.5,
         "Lower: OpenAI's unpriced risk weighs on its largest debt-funded shareholder."),
        ("Oracle's OpenAI contracts, share of its value", exp("Oracle", "OpenAI"), "{:.0f}%", "{:.0f} pts", "up", 0.5,
         "Higher: more of Oracle's value rests on a single tenant."),
        ("Broadcom's Anthropic leases, share of its value", exp("Broadcom", "Anthropic"), "{:.1f}%", "{:.1f} pts", "up", 0.05,
         "Higher: more of Broadcom's value rests on Anthropic. Under 10% means it could absorb it."),
        ("Lenders' link to chips and power, this year", chips, "{:+.1f}", "{:.1f}", "up", 0.05,
         "Higher: the lenders move more with chips and power beyond the market. It appeared in 2024."),
        ("Capital raised for AI in 2026 so far ($bn)", raised, "{:,.0f}", "{:,.0f}", "up", 0.5,
         "Higher: the debt keeps spreading. Updated from published estimates."),
        ("10-year Treasury yield", ind["rates"]["last"], "{:.2f}%", "{:.2f} pts", "up", 0.005,
         "Higher: dearer refinancing for a build-out financed with debt.")]
    return [{"label": l, "value": (None if v is None else round(float(v), 4)), "fmt": f, "dfmt": df, "bad": b, "eps": e,
             "meaning": m, "prev": pk.get(l)} for l, v, f, df, b, e, m in rows]


def _word(v, words):
    for lim, w in words:
        if v <= lim:
            return w
    return words[-1][1]


T_EN = [(-0.6, "listing"), (-0.2, "leaning towards a listing"), (0.2, "undecided"), (0.6, "leaning towards a delay"), (9, "delayed")]
T_ES = [(-0.6, "en marcha"), (-0.2, "inclinada a salir"), (0.2, "sin decidir"), (0.6, "inclinada al aplazamiento"), (9, "aplazada")]
C_EN = [(-0.6, "favourable"), (-0.2, "improving"), (0.2, "mixed"), (0.6, "deteriorating"), (9, "adverse")]
C_ES = [(-0.6, "favorables"), (-0.2, "mejorando"), (0.2, "mixtas"), (0.6, "deteriorándose"), (9, "adversas")]
CORNER_EN = {"strong": "the strong-listing position", "weak": "the weak-listing position", "delay": "the delay position", "fall": "the market-fall position"}
CORNER_ES = {"strong": "la posición de salida fuerte", "weak": "la posición de salida débil", "delay": "la posición de aplazamiento", "fall": "la posición de caída del mercado"}


def needle(ind):
    """Two-axis compass. x: timing of OpenAI's listing (+1 delay, -1 listing). y: market conditions (+1 adverse, -1 favourable).
    Each explicit signal moves its axis one step; each axis is normalised to [-1, 1]. Not a probability."""
    import math
    ax = ind["signs"]["axis"]
    def axis(name):
        on = [x for x in ax if x["axis"] == name and x["on"]]
        n = max(sum(1 for x in ax if x["axis"] == name and x["dir"] > 0), sum(1 for x in ax if x["axis"] == name and x["dir"] < 0), 1)
        return max(-1.0, min(1.0, (sum(1 for x in on if x["dir"] > 0) - sum(1 for x in on if x["dir"] < 0)) / n))   # every signal weighs the same
    x, y = round(axis("timing"), 4), round(axis("conditions"), 4)
    an_x = min([a["x"] for a in ind["signs"]["anthropic"] if a["on"]] or [0.0])
    tw_en, tw_es, cw_en, cw_es = _word(x, T_EN), _word(x, T_ES), _word(y, C_EN), _word(y, C_ES)
    if abs(x) > 0.2 and abs(y) > 0.2:
        k = ("delay" if x > 0 else "strong" if y < 0 else "weak") if not (x > 0 and y > 0) else "fall"
        if x < 0 and y > 0:
            k = "weak"
        where_en, where_es = f"The needle points to {CORNER_EN[k]}.", f"La aguja apunta a {CORNER_ES[k]}."
    elif abs(x) > 0.2:
        pair_en = "the delay and market-fall positions" if x > 0 else "the strong and weak listing positions"
        pair_es = "las posiciones de aplazamiento y de caída del mercado" if x > 0 else "las posiciones de salida fuerte y salida débil"
        where_en, where_es = f"The needle sits between {pair_en}.", f"La aguja queda entre {pair_es}."
    elif abs(y) > 0.2:
        where_en = "The timing is open; conditions decide between " + ("a weak listing and a market fall." if y > 0 else "a strong listing and a calm delay.")
        where_es = "El calendario está abierto; las condiciones deciden entre " + ("una salida débil y una caída del mercado." if y > 0 else "una salida fuerte y un aplazamiento tranquilo.")
    else:
        where_en, where_es = "The needle is near the centre: no clear path yet.", "La aguja está cerca del centro: todavía no hay un camino claro."
    act = sum(1 for a in ax if a["on"])
    return {"nv": 2, "x": x, "y": y, "mag": round(min(1.0, math.hypot(x, y)), 4), "anthropic_x": an_x,
            "short_en": f"listing {tw_en}, conditions {cw_en}", "short_es": f"salida {tw_es}, condiciones {cw_es}",
            "note_en": f"OpenAI's listing: {tw_en}. Market conditions: {cw_en}. {where_en} {act} of {len(ax)} signals are active.",
            "note_es": f"Salida a bolsa de OpenAI: {tw_es}. Condiciones del mercado: {cw_es}. {where_es} Hay {act} de {len(ax)} señales activas.",
            "point": f"{x:+.2f},{y:+.2f}", "reading": f"listing {tw_en}, conditions {cw_en}"}


def course(nd, today):
    """Keep one needle position per update in data/kpi_history.json and return the last twelve, oldest first."""
    p = ROOT / "data" / "kpi_history.json"
    hist = json.loads(p.read_text()) if p.exists() else []
    for h in hist:
        if h["date"] == today:
            h["needle"] = nd
    p.write_text(json.dumps(hist[-260:]))
    return [{"date": h["date"], **h["needle"]} for h in hist if h.get("needle", {}).get("nv") == 2][-12:]


def weekly(ind, events):
    """This week against the last: each headline number a week ago and now, zone changes, signals switched on or off,
    the compass heading and the events recorded in the last seven days. Built from the daily snapshots."""
    p = ROOT / "data" / "kpi_history.json"
    hist = json.loads(p.read_text()) if p.exists() else []
    today = pd.Timestamp(ind["updated"])
    now = next((h for h in hist if h["date"] == ind["updated"]), None)
    prev = [h for h in hist if pd.Timestamp(h["date"]) <= today - pd.Timedelta(days=7)]
    prev = prev[-1] if prev else None
    rows = []
    for k in ind["kpis"]:
        lab = k["label"]
        b = prev["values"].get(lab) if prev else None
        rows.append({"label": lab, "fmt": k["fmt"], "dfmt": k["dfmt"], "bad": k.get("bad"), "now": k["value"], "prev": b,
                     "change": None if b is None or k["value"] is None else round(k["value"] - b, 4),
                     "zone_prev": (prev or {}).get("zones", {}).get(lab), "zone_now": k.get("zone", "")})
    ids = {x["id"]: x for grp in ("frenzy", "turning") for x in ind["signs"][grp]}
    on, off = [], []
    if prev and prev.get("signs"):
        for i, x in ids.items():
            was = prev["signs"].get(i)
            if was is False and x["on"]:
                on.append((x["text"], x.get("text_es") or x["text"]))
            if was is True and not x["on"]:
                off.append((x["text"], x.get("text_es") or x["text"]))
    ev = events.copy()
    ev["date"] = pd.to_datetime(ev["date"])
    new_ev = ev[ev["date"] > today - pd.Timedelta(days=7)]
    return {"prev_date": prev["date"] if prev else None, "rows": rows, "signs_on": [a for a, b in on], "signs_off": [a for a, b in off],
            "signs_on_es": [b for a, b in on], "signs_off_es": [b for a, b in off],
            "needle_prev": (prev or {}).get("needle"), "needle_now": ind["needle"],
            "events": [{"date": str(r.date.date()), "company": r.company, "description": r.description,
                        "description_es": getattr(r, "description_es", None)} for r in new_ev.itertuples()]}


def digest(ind):
    """Plain-text weekly digest, sent as a GitHub issue on Monday runs."""
    w = ind["weekly"]
    lines = [f"# Chips and Risk, week to {ind['updated']}", "", ind["headline"], ""]
    if not w["prev_date"]:
        lines.append("First week: no earlier week to compare with yet.")
    else:
        lines += [f"Against {w['prev_date']}:", "", "| Number | A week ago | Now | Change |", "|---|---|---|---|"]
        for r in w["rows"]:
            f = lambda v: "n/a" if v is None else r["fmt"].format(v)
            ch = "" if r["change"] is None else ("+" if r["change"] > 0 else "") + r["dfmt"].format(r["change"]).replace("+", "")
            z = f" (zone: {r['zone_prev']} to {r['zone_now']})" if r["zone_prev"] and r["zone_now"] and r["zone_prev"] != r["zone_now"] else ""
            lines.append(f"| {r['label']} | {f(r['prev'])} | {f(r['now'])} | {ch}{z} |")
    for t, xs in (("Signals switched on", w["signs_on"]), ("Signals switched off", w["signs_off"])):
        if xs:
            lines += ["", t + ":"] + [f"- {x}" for x in xs]
    np_, nn = w["needle_prev"] or {}, w["needle_now"]
    lines += ["", f"Compass: {np_.get('short_en', 'n/a')} a week ago; {nn['short_en']} now."]
    if w["events"]:
        lines += ["", "Events recorded this week:"] + [f"- {e['date']} {e['company']}: {e['description']}" for e in w["events"]]
    lines += ["", "Website: https://acedoo.github.io/chips-and-risk/"]
    return "\n".join(lines)


def headline(ind):
    """The sentence at the top of the page, built with fixed rules from the data (no generated text)."""
    k = {x["label"]: x for x in ind["kpis"]}
    parts, partes = [], []
    g = k.get("Lenders' gap in AI sell-offs, last 12 months")
    if g:
        parts.append({"the 2024-2026 range": "the AI-dependent lenders still lag the rest of finance when AI falls",
                      "the 2016-2023 range": "the lenders' lag in AI sell-offs is back inside its pre-2024 range",
                      "beyond every year since 2024": "the lenders' lag in AI sell-offs is wider than in any year since 2024"}.get(g["zone"], "the lenders' gap is outside its usual ranges"))
        partes.append({"the 2024-2026 range": "los prestamistas de la IA siguen quedándose por detrás del resto del sector financiero en las peores jornadas del sector",
                       "the 2016-2023 range": "el rezago de los prestamistas de la IA en sus peores jornadas ha vuelto a niveles anteriores a 2024",
                       "beyond every year since 2024": "el rezago de los prestamistas de la IA en sus peores jornadas es el mayor desde 2024"}.get(g["zone"], "el rezago de los prestamistas de la IA está fuera de sus rangos habituales"))
    movers = []
    for lab, name in (("Oracle against the AI chain since Jan 2025", "Oracle"), ("CoreWeave against the AI chain since Jan 2025", "CoreWeave"),
                      ("SoftBank against the Tokyo market since Jan 2025", "SoftBank")):
        c = (k.get(lab) or {}).get("changes") or {}
        if c.get("1W") is not None:
            movers.append((abs(c["1W"]), name, c["1W"]))
    if movers:
        _, name, ch = max(movers)
        if abs(ch) >= 2:
            parts.append(f"{name} {'rose' if ch > 0 else 'fell'} {abs(ch):.0f} points against its reference in a week")
            ref_es = "la bolsa de Tokio" if name == "SoftBank" else "el resto de la cadena"
            partes.append(f"{name} {'ganó' if ch > 0 else 'perdió'} {abs(ch):.0f} puntos frente a {ref_es}")
    t = ind["signs"]["turning_count"]
    parts.append("no sign of a turning point has appeared" if t == 0 else f"{t} of the six signs of a turning point are present")
    partes.append("no ha aparecido ninguna señal de punto de inflexión" if t == 0 else f"aparecen {t} de las seis señales de punto de inflexión")
    return "This week: " + "; ".join(parts) + ".", "Esta semana: " + "; ".join(partes) + "."


def changes(prev, ind, events, found):
    """Plain-language list of what changed since the previous weekly update."""
    if not prev:
        return ["First update of the monitor."], ["Primera actualización de la web."]
    out, es, g, pg = [], [], ind["lenders_gap"], prev.get("lenders_gap", {})
    if g.get("last_selloff") != pg.get("last_selloff"):
        out.append(f"New AI sell-off day on {g['last_selloff']}."); es.append(f"Nueva jornada de fuerte caída de la IA: {g['last_selloff']}.")
    if g.get("trailing_12m") is not None and pg.get("trailing_12m") is not None and abs(g["trailing_12m"] - pg["trailing_12m"]) >= 0.02:
        out.append(f"The lenders' twelve-month gap moved from {pg['trailing_12m']:+.2f} to {g['trailing_12m']:+.2f} points a day.")
        es.append(f"El rezago de doce meses de los prestamistas pasó de {pg['trailing_12m']:+.2f} a {g['trailing_12m']:+.2f} puntos al día.".replace(".", ",").rstrip(",") + ".")
    ps = prev.get("signs", {})
    for key, name in (("frenzy_count", "frenzy"), ("turning_count", "turning-point")):
        if ps.get(key) is not None and ind["signs"][key] != ps[key]:
            out.append(f"Signs of a {name}: {ps[key]} to {ind['signs'][key]} of 6.")
            es.append(f"Señales de {'frenesí' if name == 'frenzy' else 'punto de inflexión'}: de {ps[key]} a {ind['signs'][key]} de 6.")
    newev = events[pd.to_datetime(events["date"]) > pd.Timestamp(prev.get("updated", "1900-01-01"))]
    out += [f"New event: {r.company}, {r.description} ({r.date})." for r in newev.itertuples()]
    es += [f"Nuevo hecho registrado: {r.company}, {getattr(r, 'description_es', None) or r.description} ({r.date})." for r in newev.itertuples()]
    if len(found) > prev.get("n_filings", 0):
        out.append(f"{len(found) - prev.get('n_filings', 0)} new sentences on guarantees in SEC filings.")
        es.append(f"{len(found) - prev.get('n_filings', 0)} frases nuevas sobre garantías en los documentos presentados ante la SEC.")
    for k, name in (("ORCL", "Oracle"), ("CRWV", "CoreWeave"), ("9984.T", "SoftBank")):
        a, b = prev.get("exposed_last", {}).get(k), ind["exposed"].get(k)
        if a is not None and b is not None and len(b) and abs(float(b.iloc[-1]) - a) >= 5:
            out.append(f"{name} moved {float(b.iloc[-1]) - a:+.0f} points against its reference.")
            es.append(f"{name}: {float(b.iloc[-1]) - a:+.0f} puntos frente a su referencia.")
    return out, es


if __name__ == "__main__":
    main()
