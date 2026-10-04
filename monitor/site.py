"""Builds docs/index.html, a static page served by GitHub Pages. Charts are inline SVG; no external data at view time."""
import html
import math

INK, MUTED, RULE, BG, PANEL = "#14213D", "#5B6B80", "#E3E8EF", "#FFFFFF", "#F4F7FB"
ALERT, WATCH, CALM, TEAL = "#E04F4F", "#E3A21A", "#2563EB", "#0F9D8F"
PAST = "#A9B4C2"
STATE_COLOR = {"alert": ALERT, "watch": WATCH, "normal": CALM, "quiet": MUTED}


def esc(x):
    return html.escape(str(x))


def svg_bars(yearly, ref, w=720, h=150):
    ys = sorted(yearly)
    vals = [yearly[y][0] for y in ys]
    lo, hi = min(min(vals), ref["pre2024_min"], -0.1) * 1.25, max(max(vals), ref["pre2024_max"], 0.1) * 1.25
    pad_l, pad_b = 34, 20
    sx = (w - pad_l - 6) / len(ys)
    sy = lambda v: (hi - v) / (hi - lo) * (h - pad_b - 8) + 4
    out = [f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="Yearly gap of the lenders in AI sell-offs">']
    out.append(f'<rect x="{pad_l}" y="{sy(ref["pre2024_max"]):.1f}" width="{w-pad_l-6}" '
               f'height="{sy(ref["pre2024_min"]) - sy(ref["pre2024_max"]):.1f}" fill="{PANEL}"/>')
    out.append(f'<line x1="{pad_l}" x2="{w-6}" y1="{sy(0):.1f}" y2="{sy(0):.1f}" stroke="{MUTED}" stroke-width="0.8"/>')
    for i, (y, v) in enumerate(zip(ys, vals)):
        x = pad_l + i * sx + sx * 0.2
        col = (ALERT if v < ref["pre2024_min"] else CALM) if y >= 2024 else PAST
        y0, y1 = sorted([sy(0), sy(v)])
        out.append(f'<rect x="{x:.1f}" y="{y0:.1f}" width="{sx*0.6:.1f}" height="{max(y1-y0, 1):.1f}" rx="3" fill="{col}"/>')
        out.append(f'<text x="{x + sx*0.3:.1f}" y="{h-5}" font-size="10" text-anchor="middle" fill="{MUTED}">{y}{"*" if yearly[y][1] < 5 else ""}</text>')
    for v in (hi / 1.25, lo / 1.25):
        out.append(f'<text x="{pad_l-5}" y="{sy(v)+3:.1f}" font-size="10" text-anchor="end" fill="{MUTED}">{v:+.1f}</text>')
    out.append("</svg>")
    return "".join(out)


def svg_lines(series, w=720, h=160, unit="%", colors=None, zero=True, fmt="{:+.0f}"):
    keys = [k for k in series if len(series[k])]
    if not keys:
        return ""
    allv = [v for k in keys for v in series[k].values]
    lo, hi = (min(allv + [0]), max(allv + [0])) if zero else (min(allv), max(allv))
    span = (hi - lo) or 1
    lo, hi = lo - span * 0.08, hi + span * 0.08
    t0 = min(series[k].index.min() for k in keys).value
    t1 = max(series[k].index.max() for k in keys).value
    pad_l, pad_r = 40, 118
    sx = lambda t: pad_l + (t.value - t0) / max(t1 - t0, 1) * (w - pad_l - pad_r)
    sy = lambda v: (hi - v) / (hi - lo) * (h - 16) + 6
    colors = colors or {}
    out = [f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="Trace chart">',
           (f'<line x1="{pad_l}" x2="{w-pad_r}" y1="{sy(0):.1f}" y2="{sy(0):.1f}" stroke="{MUTED}" stroke-width="0.8"/>' if zero else "")]
    ends = sorted(((sy(series[k].iloc[-1]), k) for k in keys))
    lab, prev = {}, -99
    for y, k in ends:
        y = max(y, prev + 13); lab[k] = y; prev = y
    for k in keys:
        s = series[k]
        pts = " ".join(f"{sx(t):.1f},{sy(v):.1f}" for t, v in s.items())
        c = colors.get(k, INK)
        out.append(f'<polyline points="{pts}" fill="none" stroke="{c}" stroke-width="1.8" stroke-linejoin="round"/>')
        out.append(f'<text x="{w-pad_r+6}" y="{lab[k]+4:.1f}" font-size="11" fill="{c}">{esc(k)} {fmt.format(s.iloc[-1])}{unit}</text>')
    for v in (hi, lo):
        out.append(f'<text x="{pad_l-6}" y="{sy(v)+4:.1f}" font-size="10" text-anchor="end" fill="{MUTED}">{fmt.format(v)}</text>')
    out.append(f'<text x="{pad_l}" y="{h-1}" font-size="10" fill="{MUTED}">{series[keys[0]].index.min().date()}</text>')
    out.append("</svg>")
    return "".join(out)



def svg_hbars(rows, w=720):
    rows = rows[:12]
    h = 22 * len(rows) + 10
    mx = max(r["pct_of_value"] for r in rows) or 1
    out = [f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="Share of market value at stake">']
    for i, r in enumerate(rows):
        y = 6 + i * 22
        bw = (w - 330) * r["pct_of_value"] / max(mx, 1)
        c = ALERT if r["pct_of_value"] > 20 else (TEAL if r["tenant"] == "Anthropic" else PAST)
        out.append(f'<text x="200" y="{y+13}" font-size="11.5" text-anchor="end" fill="{INK}">{esc(r["company"])} [{esc(r["tenant"])}]</text>')
        out.append(f'<rect x="210" y="{y+2}" width="{max(bw, 1):.1f}" height="14" fill="{c}"/>')
        out.append(f'<text x="{216+bw:.1f}" y="{y+13}" font-size="11" fill="{INK}">{r["pct_of_value"]:g}% ({esc(r["kind"])})</text>')
    out.append("</svg>")
    return "".join(out)


def yearly_series(d):
    import pandas as pd
    if not d:
        return pd.Series(dtype=float)
    return pd.Series({pd.Timestamp(int(y), 7, 1): v for y, v in sorted(d.items(), key=lambda x: int(x[0]))})


LNAMES = {'BX': 'Blackstone', 'APO': 'Apollo', 'KKR': 'KKR', 'ARES': 'Ares', 'CG': 'Carlyle', 'BN': 'Brookfield', 'OWL': 'Blue Owl', 'BLK': 'BlackRock', 'JPM': 'JPMorgan', 'MS': 'Morgan Stanley', 'GS': 'Goldman Sachs', 'C': 'Citigroup', 'BAC': 'Bank of America', 'MUFG': 'MUFG', 'SMFG': 'Sumitomo Mitsui', 'MFG': 'Mizuho', 'MET': 'MetLife', 'PRU': 'Prudential'}


def svg_ranking(rows, w=720):
    h = 21 * len(rows) + 10
    lo = min([r["gap"] for r in rows] + [0]); hi = max([r["gap"] for r in rows] + [0])
    x0 = 170 + (w - 250) * (-lo) / max(hi - lo, 1e-9)
    sx = (w - 250) / max(hi - lo, 1e-9)
    out = [f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="Each lender against other financial stocks in AI sell-offs since 2024">']
    for i, r in enumerate(rows):
        y = 6 + i * 21
        x1 = x0 + r["gap"] * sx
        c = ALERT if r["gap"] <= -0.5 else (WATCH if r["gap"] <= -0.3 else PAST)
        out.append(f'<text x="160" y="{y+12}" font-size="11.5" text-anchor="end" fill="{INK}">{esc(LNAMES.get(r["ticker"], r["ticker"]))}</text>')
        out.append(f'<rect x="{min(x0, x1):.1f}" y="{y+2}" width="{max(abs(x1-x0), 1):.1f}" height="13" rx="3" fill="{c}"/>')
        out.append(f'<text x="{max(x0, x1)+6:.1f}" y="{y+12}" font-size="10.5" fill="{MUTED}">{r["gap"]:+.2f}</text>')
    out.append(f'<line x1="{x0:.1f}" x2="{x0:.1f}" y1="2" y2="{h-2}" stroke="{MUTED}" stroke-width="0.8"/>')
    out.append("</svg>")
    return "".join(out)

SCEN = [("strong", "Strong listing", "Listings above the last private round spread the risk and ease payment worries."),
        ("weak", "Weak listing", "A listing below the last round hits SoftBank first, then Oracle, CoreWeave and the chip suppliers."),
        ("delay", "Delay", "Private rounds continue and the risk stays with Oracle, CoreWeave and SoftBank."),
        ("fall", "Market fall", "A sharp fall stops the listings and leaves the tenants on private capital and suppliers.")]
SCOL = {"strong": CALM, "weak": ALERT, "delay": WATCH, "fall": INK}


def curve_y(x):
    base = 0.10 + 0.72 / (1 + math.exp(-(x - 0.38) * 14)) + 0.18 * max(0.0, x - 0.70)
    return base - 0.40 * math.exp(-((x - 0.665) / 0.045) ** 2)


def svg_curve(fc, tc, w=720, h=250):
    pad = 24
    X = lambda x: pad + x * (w - 2 * pad)
    Y = lambda y: h - 34 - y * (h - 70)
    pts = " ".join(f"{X(i/200):.1f},{Y(curve_y(i/200)):.1f}" for i in range(201))
    xn = min(0.25 + 0.30 * fc / 6 + 0.12 * tc / 6, 0.69)
    out = [f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="Phases of a technological revolution and where the signs place us">']
    for x0, x1 in ((0.55, 0.74),):
        out.append(f'<rect x="{X(x0):.1f}" y="14" width="{X(x1)-X(x0):.1f}" height="{h-48}" rx="10" fill="{PANEL}"/>')
    out.append(f'<polyline points="{pts}" fill="none" stroke="{CALM}" stroke-width="2.6" stroke-linecap="round"/>')
    for x, lab in ((0.16, "Installation"), (0.46, "Frenzy"), (0.645, "Turning point"), (0.87, "Deployment")):
        out.append(f'<text x="{X(x):.1f}" y="{h-12}" font-size="12" text-anchor="middle" fill="{MUTED}">{lab}</text>')
    out.append(f'<text x="{X(0.645):.1f}" y="30" font-size="10.5" text-anchor="middle" fill="{MUTED}">1847, 1873, 1929, 1982, 2000: earlier turning points</text>')
    xp, yp = X(xn), Y(curve_y(xn))
    out.append(f'<circle cx="{xp:.1f}" cy="{yp:.1f}" r="13" fill="{ALERT}" opacity="0.18"/><circle cx="{xp:.1f}" cy="{yp:.1f}" r="7" fill="{ALERT}"/>')
    out.append(f'<text x="{xp-12:.1f}" y="{yp-14:.1f}" font-size="12.5" text-anchor="end" fill="{ALERT}">Now: {fc} of 6 frenzy signs, {tc} of 6 turning-point signs</text>')
    out.append("</svg>")
    return "".join(out)


def sign_list(items):
    return "".join(f'<li class="{"on" if s["on"] else "off"}"><span class="mk" aria-hidden="true">{"●" if s["on"] else "○"}</span>'
                   f'{esc(s["text"])}{" <span class=src>(" + esc(s["source"]) + ")</span>" if s.get("source") else ""}'
                   f'<span class="sr">{" present" if s["on"] else " absent"}</span></li>' for s in items)


def scenario_block(sg, bets):
    counts = {k: sum(1 for s in sg["scenarios"] if s["scenario"] == k and s["on"]) for k, _, _ in SCEN}
    tot = sum(counts.values()) or 1
    bar = "".join(f'<div class="seg" style="flex:{max(counts[k], 0.15)};background:{SCOL[k]}" title="{esc(n)}: {counts[k]} signals"></div>'
                  for k, n, _ in SCEN)
    cols = []
    for k, n, d in SCEN:
        sig = "".join(f'<li>{esc(s["text"])}</li>' for s in sg["scenarios"] if s["scenario"] == k and s["on"]) or "<li>No current signal.</li>"
        bt = "".join(f'<li>{esc(b["who"])}: {esc(b["bet"])} <span class="src">({esc(b["source"])})</span></li>'
                     for b in bets if b["scenario"] == k) or "<li>No documented bet yet.</li>"
        cols.append(f'<div class="scen"><h3><span class="dot" style="background:{SCOL[k]}"></span>{esc(n)} '
                    f'<span class="cnt">{counts[k]} of {tot} signals</span></h3><p>{esc(d)}</p>'
                    f'<p class="sub">What the data show now</p><ul>{sig}</ul><p class="sub">Who has money on it</p><ul>{bt}</ul></div>')
    return f'<div class="bar" role="img" aria-label="Share of current signals pointing to each scenario">{bar}</div><div class="scens">{"".join(cols)}</div>'


CALC = """
<form id="calc" onsubmit="return false">
<p>Split your savings across these doors (rough percentages; they need not add up exactly).</p>
<div class="rows"></div>
<button type="button" id="go">Show the position my savings hold</button>
</form>
<div id="out" aria-live="polite"></div>
<script>
const V = [
 ["sp500","US stock index fund (S&P 500)",[1,-1,0,-2],"Large AI weight; the S&P 500 will not add OpenAI or Anthropic for at least twelve months and only with profits."],
 ["ndx","Nasdaq-100 or technology fund",[2,-2,0,-2],"Must buy new giant listings within about fifteen trading days, so it carries their first price swings."],
 ["glob","Global stock fund",[1,-1,0,-2],"Same channels as the S&P 500, diluted by other markets."],
 ["bonds","Investment-grade bond fund",[1,-1,0,-1],"AI groups are a leading source of new bonds and lengthen the index's duration."],
 ["pens","Pension plan or life insurance",[1,-1,0,-1],"Insurers and pension managers bought data-centre bonds and hold private credit."],
 ["pc","Private credit fund or listed BDC",[1,-1,-1,-2],"Sensitive to AI-dependent borrowers; some funds limited redemptions this year."],
 ["exp","Shares in Oracle, CoreWeave or SoftBank",[2,-2,-1,-2],"The three balance sheets that carry OpenAI's counterparty risk."],
 ["giants","Shares in Nvidia, Microsoft, Amazon or Alphabet",[1,-1,0,-2],"Large exposure in money, small relative to their value."],
 ["pre","Pre-IPO or private AI fund",[2,-2,-1,-2],"Bets directly on the listing price; hard to sell before it."],
 ["cash","Deposits, cash or government bonds",[0,0,0,1],"Outside the AI chain; government bonds tend to gain when equities fall."]
];
const S = ["the strong-listing position","the weak-listing position","the delay position","the market-fall position"];
const rows = document.querySelector("#calc .rows");
V.forEach(v => { rows.insertAdjacentHTML("beforeend",
  `<label class="row"><span>${v[1]}</span><input type="number" min="0" max="100" step="5" value="0" id="v_${v[0]}" inputmode="numeric"> %</label>`); });
document.getElementById("go").addEventListener("click", () => {
  const w = V.map(v => Math.max(0, Number(document.getElementById("v_"+v[0]).value) || 0));
  const tot = w.reduce((a,b)=>a+b,0);
  const out = document.getElementById("out");
  if (!tot) { out.innerHTML = "<p>Enter at least one percentage to see how each path would reach your savings.</p>"; return; }
  const sc = [0,1,2,3].map(j => V.reduce((a,v,i)=>a + w[i]/tot*v[2][j], 0));
  const best = sc.indexOf(Math.max(...sc)), worst = sc.indexOf(Math.min(...sc));
  const doors = V.map((v,i)=>[w[i],v]).filter(x=>x[0]>0).sort((a,b)=>b[0]-a[0])
     .map(x=>`<li>${x[1][1]} (${Math.round(x[0]/tot*100)}%): ${x[1][3]}</li>`).join("");
  const word = x => x>=1 ? "gains" : x>0.2 ? "leans to gain" : x>-0.2 ? "little affected" : x>-1 ? "leans to lose" : "loses";
  out.innerHTML = `<p class="team">Your savings sit closest to ${S[best]}, and are most exposed to ${S[worst]}.</p>
   <table><tr><th>Position</th><th>Your mix</th></tr>${S.map((n,j)=>`<tr><td>${n.replace("the ","").replace(" position","")}</td><td>${word(sc[j])}</td></tr>`).join("")}</table>
   <p class="sub">How each path reaches you</p><ul>${doors}</ul>
   <p class="src">A qualitative reading of the mechanisms documented in the paper, not a forecast of returns and not investment advice.</p>`;
});
</script>"""



def svg_history(hist, ai, w=760, h=340):
    pad_l, pad_r, pad_t, pad_b = 46, 190, 18, 34
    xmax = 10.0
    ys = [v for e in hist["episodes"].values() for v in e["y"]] + ai["y"]
    lo, hi = math.log(min(ys) * 0.85), math.log(max(ys) * 1.15)
    X = lambda x: pad_l + x / xmax * (w - pad_l - pad_r)
    Y = lambda v: pad_t + (hi - math.log(v)) / (hi - lo) * (h - pad_t - pad_b)
    out = [f'<svg viewBox="0 0 {w} {h}" id="hist" role="img" aria-label="Past booms aligned at the start of their frenzy, and the AI supply chain since ChatGPT">']
    for v in (50, 100, 200, 400):
        if lo < math.log(v) < hi:
            out.append(f'<line x1="{pad_l}" x2="{w-pad_r}" y1="{Y(v):.1f}" y2="{Y(v):.1f}" stroke="{RULE}" stroke-width="1"/>'
                       f'<text x="{pad_l-8}" y="{Y(v)+4:.1f}" font-size="10.5" text-anchor="end" fill="{MUTED}">{v}</text>')
    for yr in range(0, 11):
        out.append(f'<text x="{X(yr):.1f}" y="{h-12}" font-size="10.5" text-anchor="middle" fill="{MUTED}">{yr}</text>')
    out.append(f'<text x="{X(5):.1f}" y="{h}" font-size="10.5" text-anchor="middle" fill="{MUTED}">years since the start of the frenzy</text>')
    style = {"tech": ("#8C98A9", ""), "energy": ("#B39B7D", ' stroke-dasharray="5 3"'), "credit": ("#9A8FB5", ' stroke-dasharray="2 3"')}
    ends, labelled, placed = [], set(), []
    for name, e in hist["episodes"].items():
        gcol, dash = style.get(e.get("group", "tech"), style["tech"])
        grp = e.get("group", "tech")
        pts = " ".join(f"{X(x):.1f},{Y(y):.1f}" for x, y in zip(e["x"], e["y"]) if x <= xmax)
        out.append(f'<g class="ep g-{grp}"><polyline points="{pts}" fill="none" stroke="{gcol}" stroke-width="1.5"{dash} stroke-linejoin="round" opacity="0.9"/>')
        px, py = X(e["peak_years"]), Y(e["peak_level"])
        out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="3" fill="{gcol}"/>')
        yr = e["peak_date"][:4]
        if yr not in labelled:
            labelled.add(yr)
            ly = py - 8
            while any(abs(px - qx) < 46 and abs(ly - qy) < 12 for qx, qy in placed):
                ly -= 12
            placed.append((px, ly))
            out.append(f'<text x="{px:.1f}" y="{ly:.1f}" font-size="10" text-anchor="middle" fill="{MUTED}">peak {yr}</text>')
        out.append("</g>")
        last = [(x, y) for x, y in zip(e["x"], e["y"]) if x <= xmax][-1]
        ends.append((Y(last[1]), name, gcol, grp))
    prev_y = -99
    for y, name, gcol, grp in sorted(ends):
        y = max(y, prev_y + 13); prev_y = y
        out.append(f'<text class="ep g-{grp}" x="{X(xmax)+8:.1f}" y="{y+4:.1f}" font-size="10.5" fill="{gcol}">{esc(name)}</text>')
    pts = " ".join(f"{X(x):.1f},{Y(y):.1f}" for x, y in zip(ai["x"], ai["y"]))
    out.append(f'<polyline points="{pts}" fill="none" stroke="{CALM}" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>')
    tx, ty = X(ai["years_now"]), Y(ai["level_now"])
    out.append(f'<line x1="{tx:.1f}" x2="{tx:.1f}" y1="{pad_t}" y2="{h-pad_b}" stroke="{ALERT}" stroke-width="1" stroke-dasharray="3 3"/>')
    out.append(f'<circle cx="{tx:.1f}" cy="{ty:.1f}" r="12" fill="{ALERT}" opacity="0.18"/><circle cx="{tx:.1f}" cy="{ty:.1f}" r="6" fill="{ALERT}"/>')
    out.append(f'<text x="{tx-8:.1f}" y="{h-pad_b-26}" font-size="11.5" font-weight="600" text-anchor="end" fill="{ALERT}">Today, {ai["years_now"]:.1f} years in</text>')
    out.append(f'<text x="{tx-8:.1f}" y="{h-pad_b-11}" font-size="11" text-anchor="end" fill="{INK}">AI supply chain {ai["level_now"]/100:.2f}x since ChatGPT</text>')
    out.append("</svg>")
    toggles = ('<div class="tog" role="group" aria-label="Show or hide groups of past booms">'
               '<button type="button" aria-pressed="true" data-g="tech">Technology booms</button>'
               '<button type="button" aria-pressed="true" data-g="energy">Energy booms</button>'
               '<button type="button" aria-pressed="true" data-g="credit">Credit boom</button></div>'
               '<script>document.querySelectorAll(".tog button").forEach(b=>b.addEventListener("click",()=>{'
               'const on=b.getAttribute("aria-pressed")!=="true";b.setAttribute("aria-pressed",on);'
               'document.querySelectorAll("#hist .g-"+b.dataset.g).forEach(e=>e.style.display=on?"":"none");}));</script>')
    return toggles + "".join(out)

ICONS = {
 "bell": '<path d="M16 4c-5 0-8 4-8 9v6l-3 4h22l-3-4v-6c0-5-3-9-8-9z" fill="{c}"/><circle cx="16" cy="26" r="2.6" fill="{c}"/>',
 "crack": '<rect x="5" y="5" width="22" height="22" rx="4" fill="{c}"/><path d="M17 5l-4 8 5 4-4 10" stroke="#fff" stroke-width="2.2" fill="none" stroke-linejoin="round"/>',
 "hourglass": '<path d="M8 4h16v3c0 4-4 6-6 9 2 3 6 5 6 9v3H8v-3c0-4 4-6 6-9-2-3-6-5-6-9z" fill="{c}"/><path d="M12 25h8" stroke="#fff" stroke-width="2"/>',
 "storm": '<path d="M9 14a7 7 0 0 1 13-3 5 5 0 1 1 1 10H10a4 4 0 0 1-1-7z" fill="{c}"/><path d="M16 19l-3 6h4l-2 5" stroke="{c}" stroke-width="2.2" fill="none" stroke-linejoin="round"/>'}


def compass_svg(houses, sg, nd, course, size=300, w=480):
    """Four positions at the cardinal points; the needle is the sum of the current signals, not a probability.
    The trail shows where it pointed at each of the last updates (older points fainter)."""
    cx, c = w / 2, size / 2; R = size / 2 - 46
    pos = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0)}
    cnt = {k: sum(1 for s in sg["scenarios"] if s["scenario"] == k and s["on"]) for k in houses}
    out = [f'<svg viewBox="0 0 {w} {size}" class="compass" role="img" aria-label="Where the current signals point among the four positions">',
           f'<circle cx="{cx}" cy="{c}" r="{R}" fill="{PANEL}" stroke="{RULE}" stroke-width="1.5"/>',
           f'<circle cx="{cx}" cy="{c}" r="{R*0.5:.1f}" fill="none" stroke="{RULE}" stroke-dasharray="3 4"/>',
           f'<line x1="{cx-R}" y1="{c}" x2="{cx+R}" y2="{c}" stroke="{RULE}"/><line x1="{cx}" y1="{c-R}" x2="{cx}" y2="{c+R}" stroke="{RULE}"/>']
    for a in range(45, 360, 90):
        rad = math.radians(a)
        out.append(f'<line x1="{cx + math.sin(rad)*R*0.92:.1f}" y1="{c - math.cos(rad)*R*0.92:.1f}" x2="{cx + math.sin(rad)*R:.1f}" y2="{c - math.cos(rad)*R:.1f}" stroke="{MUTED}" stroke-width="1"/>')
    for k, h in houses.items():
        dx, dy = pos[h["point"]]
        x, y = cx + dx * (R + 16), c + dy * (R + 22)
        col = SCOL[k]
        out.append(f'<circle cx="{cx + dx*R:.1f}" cy="{c + dy*R:.1f}" r="7" fill="{col}"/>')
        anchor = "middle" if dx == 0 else ("start" if dx > 0 else "end")
        ty = y + (-2 if dy <= 0 else 10)
        out.append(f'<text x="{x:.1f}" y="{ty:.1f}" font-size="12" font-weight="600" text-anchor="{anchor}" fill="{col}">{esc(h["name"])}</text>')
        out.append(f'<text x="{x:.1f}" y="{ty+14:.1f}" font-size="10.5" text-anchor="{anchor}" fill="{MUTED}">{cnt[k]} signal{"s" if cnt[k] != 1 else ""}</text>')
    pts = [(cx + p["x"] * R * 0.85, c + p["y"] * R * 0.85) for p in course]
    if len(pts) > 1:
        out.append('<polyline points="' + " ".join(f"{a:.1f},{b:.1f}" for a, b in pts) + f'" fill="none" stroke="{MUTED}" stroke-width="1.2" stroke-dasharray="2 3"/>')
        for i, (a, b) in enumerate(pts[:-1]):
            out.append(f'<circle cx="{a:.1f}" cy="{b:.1f}" r="3.5" fill="{MUTED}" opacity="{0.25 + 0.6 * i / max(len(pts) - 1, 1):.2f}"/>')
    if nd["mag"] > 0.05:
        nx, ny = cx + nd["x"] * R * 0.85, c + nd["y"] * R * 0.85
        out.append(f'<line x1="{cx}" y1="{c}" x2="{nx:.1f}" y2="{ny:.1f}" stroke="{INK}" stroke-width="3.5" stroke-linecap="round"/>')
    out.append(f'<circle cx="{cx}" cy="{c}" r="7" fill="{INK}"/>')
    out.append("</svg>")
    if nd["mag"] <= 0.05:
        note = "Heading: centre. The signals balance out: the evidence has not chosen a path yet."
    else:
        note = f"Heading: {nd['point']}, {nd['reading']}."
    weeks = len(course)
    trail = (f" The dotted trail shows the heading over the last {weeks} updates." if weeks > 1 else
             " The trail of past headings will appear as updates accumulate.")
    return "".join(out), note + trail


def house_cards(houses, sg):
    out = []
    for key, n, _ in SCEN:
        hcfg = houses[key]
        c = SCOL[key]
        cnt = sum(1 for s in sg["scenarios"] if s["scenario"] == key and s["on"])
        sig = "".join(f"<li>{esc(s['text'])}</li>" for s in sg["scenarios"] if s["scenario"] == key and s["on"]) or "<li>No current signal.</li>"
        chars = "".join(f'<li><span class="who">{esc(a)}:</span> {esc(b)} <span class="src">({esc(src)})</span></li>' for a, b, src in hcfg["characters"])
        icon = ICONS[hcfg["icon"]].replace("{c}", c)
        out.append(f'''<article class="house" style="--hc:{c}"><div class="hhead"><svg viewBox="0 0 32 32" class="emb" aria-hidden="true">{icon}</svg>
<div><h3>{esc(hcfg["name"])}</h3><p class="motto">{esc(hcfg["motto"])}</p></div><span class="hcnt">{cnt} signal{"s" if cnt != 1 else ""}</span></div>
<p>{esc(hcfg["position"])}</p><p class="sub">Main characters</p><ul>{chars}</ul><p class="sub">What the data show now</p><ul>{sig}</ul></article>''')
    return "".join(out)


def _range_svg(k, w=240, h=38):
    lo, hi = k["lo"], k["hi"]
    if hi <= lo:
        hi = lo + 1
    X = lambda v: 6 + (min(max(v, lo), hi) - lo) / (hi - lo) * (w - 12)
    out = [f'<svg viewBox="0 0 {w} {h}" class="rb" aria-hidden="true"><rect x="6" y="12" width="{w-12}" height="8" rx="4" fill="#EEF2F7"/>']
    for a, b, c, _ in k["zones"]:
        if b > lo and a < hi:
            out.append(f'<rect x="{X(a):.1f}" y="12" width="{max(X(b)-X(a), 1):.1f}" height="8" rx="3" fill="{c}" opacity="0.55"/>')
    if k["value"] is not None:
        xv = X(k["value"])
        out.append(f'<path d="M{xv-6:.1f} 4 L{xv+6:.1f} 4 L{xv:.1f} 11 Z" fill="{INK}"/><rect x="{xv-1.2:.1f}" y="10" width="2.4" height="12" fill="{INK}"/>')
    f = lambda v: k["fmt"].format(v).replace("x", "") if "x" in k["fmt"] else k["fmt"].format(v)
    out.append(f'<text x="6" y="34" font-size="9.5" fill="{MUTED}">{esc(f(lo))}</text><text x="{w-6}" y="34" font-size="9.5" text-anchor="end" fill="{MUTED}">{esc(f(hi))}</text></svg>')
    return "".join(out)


def _gauge_svg(k, w=160, h=92):
    cx, cy, r = w / 2, 82, 66
    def pt(fr):
        a = math.pi * (1 - fr)
        return cx + r * math.cos(a), cy - r * math.sin(a)
    fr = (k["value"] or 0) / 6
    x0, y0 = pt(0); x1, y1 = pt(1); xf, yf = pt(fr)
    out = [f'<svg viewBox="0 0 {w} {h}" class="gg" aria-hidden="true">',
           f'<path d="M{x0:.1f} {y0:.1f} A{r} {r} 0 0 1 {x1:.1f} {y1:.1f}" fill="none" stroke="#EEF2F7" stroke-width="12" stroke-linecap="round"/>']
    if fr > 0:
        out.append(f'<path d="M{x0:.1f} {y0:.1f} A{r} {r} 0 0 1 {xf:.1f} {yf:.1f}" fill="none" stroke="{ALERT}" stroke-width="12" stroke-linecap="round"/>')
    for i in range(7):
        a, b = pt(i / 6), (cx + (r - 14) * math.cos(math.pi * (1 - i / 6)), cy - (r - 14) * math.sin(math.pi * (1 - i / 6)))
        out.append(f'<text x="{b[0]:.1f}" y="{b[1]+3:.1f}" font-size="9" text-anchor="middle" fill="{MUTED}">{i}</text>')
    out.append("</svg>")
    return "".join(out)


def kpi_tiles(kpis, hero=()):
    out = ['<div class="per" role="group" aria-label="Change over">'
           + "".join(f'<button type="button" data-p="{p}" aria-pressed="{"true" if p == "1W" else "false"}">{n}</button>'
                     for p, n in (("1W", "1 week"), ("1M", "1 month"), ("3M", "3 months"), ("YTD", "Year to date")))
           + '</div><div class="kpis">']
    order = [k for k in kpis if k["label"] in hero] + [k for k in kpis if k["label"] not in hero]
    for i, k in enumerate(order):
        if i == len([x for x in kpis if x["label"] in hero]) and hero:
            out.append('</div><details class="more"><summary>See the full panel: eight more numbers</summary><div class="kpis">')
        val = "n/a" if k["value"] is None else k["fmt"].format(k["value"])
        ch = k.get("changes") or {}
        attrs = " ".join(f'data-{p.lower()}="{"" if ch.get(p) is None else ch[p]}"' for p in ("1W", "1M", "3M", "YTD"))
        if k.get("yearly_prev") is not None:
            attrs += f' data-yearly="{round(k["value"] - k["yearly_prev"], 4)}"'
        vis = _gauge_svg(k) if k["kind"] == "gauge" else _range_svg(k)
        out.append(f'<div class="kpi" data-bad="{k.get("bad") or ""}" data-dfmt="{esc(k["dfmt"])}" {attrs}>'
                   f'<p class="kl">{esc(k["label"])}</p><p class="kv">{esc(val)} <span class="ku">{esc(k["unit"]) if k["kind"] == "gauge" else ""}</span></p>'
                   f'<p class="dl flat">no data yet</p>{vis}<p class="km">{esc(k["reading"])}</p><p class="ks">{esc(k["scale_note"])}</p></div>')
    out.append("</div>" + ("</details>" if hero else ""))
    out.append("""<script>
(function(){
 const fmt=(t,v)=>{const m=t.match(/\\{:([^}]*)\\}/);if(!m)return v;const sp=m[1];const pr=(sp.match(/\\.(\\d)/)||[0,2])[1];
   let s=Math.abs(v).toLocaleString('en-US',{minimumFractionDigits:+pr,maximumFractionDigits:+pr});return t.replace(m[0],s);};
 function show(p){document.querySelectorAll('.per button').forEach(b=>b.setAttribute('aria-pressed',b.dataset.p===p));
  document.querySelectorAll('.kpi').forEach(k=>{const el=k.querySelector('.dl');let v=k.dataset[p.toLowerCase()];
   if((v===undefined||v==='')&&k.dataset.yearly!==undefined){v=k.dataset.yearly;el.dataset.y='1';}
   if(v===undefined||v===''){el.className='dl flat';el.textContent='no data yet';return;}
   v=+v;if(Math.abs(v)<1e-9){el.className='dl flat';el.textContent='unchanged';return;}
   const bad=k.dataset.bad;const worse=bad==='down'?v<0:bad==='up'?v>0:false;
   el.className='dl '+(bad?(worse?'worse':'better'):'flat');
   el.textContent=(v>0?'▲ ':'▼ ')+fmt(k.dataset.dfmt,v)+(el.dataset.y?' vs last year':'');});}
 document.querySelectorAll('.per button').forEach(b=>b.addEventListener('click',()=>show(b.dataset.p)));show('1W');
})();
</script>""")
    return "".join(out)


def build(ind, path, lang="en"):
    g, sg = ind["lenders_gap"], ind["signs"]
    fc, tc = sg["frenzy_count"], sg["turning_count"]
    ai = ind["ai_path"]
    lead = (f"{ai['years_now']:.1f} years after ChatGPT, the AI build-out shows {fc} of 6 signs of a late frenzy and "
            + ("none of the signs of a turning point." if tc == 0 else f"{tc} of 6 signs of a turning point."))
    changes = "".join(f"<li>{esc(c)}</li>" for c in ind["changes"]) or "<li>No change since the previous update.</li>"
    reac = "".join(f'<tr><td>{esc(r["event_date"])}</td><td>{esc(r["description"])}</td><td class="num">{r["softbank_minus_topix"]:+.1f}</td></tr>' for r in ind["softbank"])
    ledger_rows = "".join(f'<tr><td>{esc(q)}</td><td class="num">{v.get("supplier_financing", 0):.0f}</td><td class="num">{v.get("outside_capital", 0):.0f}</td></tr>' for q, v in sorted(ind["ledger"].items()))
    ev = "".join(f'<li><span class="d">{esc(e["date"])}</span> {esc(e["company"])}: {esc(e["description"])}</li>' for e in sorted(ind["events"], key=lambda e: e["date"], reverse=True))
    fil = "".join(f'<li><span class="d">{esc(f["date"])}</span> {esc(f["company"])} {esc(f["form"])}: “{esc(f["sentence"][:260])}{"…" if len(f["sentence"]) > 260 else ""}” <a href="{esc(f["url"])}">filing</a></li>' for f in ind["filings"][:8]) or "<li>No new guarantee or off-balance-sheet language in the filings scanned so far.</li>"
    rt = ind["rates"]
    src = ", ".join(f"{k}: {v}" for k, v in ind["source_summary"].items())
    yrs = "".join(f'<tr><td>{y}</td><td class="num">{g["yearly"].get(y, [float("nan")])[0]:+.2f}</td><td class="num">{(ind["bdc_gap"].get(y) or [float("nan")])[0]:+.2f}</td></tr>' for y in sorted(set(g["yearly"]) | set(ind["bdc_gap"])))
    sens = ind["sensitivity"]
    tenants = "".join(f'<tr><td>{esc(t["tenant"])}</td><td>{esc(t["measure"])} <span class="src">({esc(t["source"])})</span></td><td class="num">{float(t["value_usd_bn"]):,.1f}</td></tr>' for t in ind["tenants"])
    debt = "".join(f'<tr><td>{esc(d["date"])}</td><td>{esc(d["measure"])} <span class="src">({esc(d["source"])})</span></td><td class="num">{float(d["amount_usd_bn"]):,.0f}</td></tr>' for d in ind["debt"])
    capab = "".join(f'<tr><td>{esc(c["date"])}</td><td>{esc(c["description"])}</td><td class="num">{c.get("Oracle", float("nan")):+.1f}</td><td class="num">{c.get("CoreWeave", float("nan")):+.1f}</td></tr>' for c in ind["capability"]) or '<tr><td colspan="4">No capability announcement on record yet.</td></tr>'
    page = f"""<!DOCTYPE html>
<html lang="{lang}"><head><meta charset="utf-8">
<link rel="alternate" hreflang="en" href="https://acedoo.github.io/chips-and-risk/"><link rel="alternate" hreflang="es" href="https://acedoo.github.io/chips-and-risk/es/">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Chips and Risk</title>
<meta name="description" content="{esc(ind["headline"])}">
<meta property="og:type" content="website"><meta property="og:site_name" content="Chips and Risk">
<meta property="og:title" content="{"Chips and Risk: quién carga con el riesgo de la inversión en IA" if lang == "es" else "Chips and Risk: who carries the risk of the AI build-out"}">
<meta property="og:description" content="{esc(ind["headline"])}">
<meta property="og:url" content="https://acedoo.github.io/chips-and-risk/{"es/" if lang == "es" else ""}">
<meta property="og:image" content="https://acedoo.github.io/chips-and-risk/{"es/" if lang == "es" else ""}share.png?v={esc(ind["updated"])}">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400&family=Instrument+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
:root {{ --ink:{INK}; --muted:{MUTED}; --rule:{RULE}; --panel:{PANEL}; --calm:{CALM}; --alert:{ALERT}; }}
* {{ box-sizing:border-box; }}
html {{ background:#fff; }}
body {{ margin:0; color:var(--ink); font:16px/1.6 'Instrument Sans', system-ui, -apple-system, sans-serif; -webkit-font-smoothing:antialiased; }}
main {{ max-width:68rem; margin:0 auto; padding:1.4rem 1.25rem 5rem; }}
.nav {{ position:sticky; top:0; z-index:5; background:rgba(255,255,255,.94); backdrop-filter:blur(6px); display:flex; gap:1.1rem; align-items:center; padding:.7rem 0; border-bottom:1px solid var(--rule); flex-wrap:wrap; }}
.nav a {{ color:var(--ink); text-decoration:none; font-size:.88rem; }} .nav a:hover {{ color:var(--calm); }}
.nav .brand {{ margin-right:auto; }}
.diff {{ margin:0 0 .3rem; font-size:.9rem; font-weight:600; color:var(--calm); }}
.tw, .hs {{ overflow-x:auto; -webkit-overflow-scrolling:touch; }}
.nav .lng {{ font-weight:600; border:1px solid var(--rule); border-radius:999px; padding:.1rem .55rem; }}
.first {{ margin-top:1.2rem; }}
.more {{ margin:.6rem 0 0; }} .more .kpis {{ margin-top:.8rem; }}
details > summary {{ font-weight:500; }}
.evd {{ border-top:1px solid var(--rule); padding:.9rem 0; margin:0; }}
.evd > summary {{ font-size:1.08rem; font-weight:600; color:var(--ink); list-style-position:outside; }}
.evd section {{ margin-top:1rem; }}
.top {{ display:flex; justify-content:space-between; align-items:baseline; gap:1rem; flex-wrap:wrap; border-bottom:1px solid var(--rule); padding-bottom:.7rem; }}
.brand {{ white-space:nowrap; font-weight:700; letter-spacing:-.01em; font-size:1.05rem; }}
.top p {{ margin:0; font-size:.82rem; color:var(--muted); }}
h1 {{ font-family:'Newsreader', Georgia, serif; font-weight:400; font-size:1.9rem; line-height:1.25; margin:.4rem 0 .6rem; max-width:56rem; letter-spacing:-.01em; }}
.card {{ background:var(--panel); border-radius:18px; padding:1.2rem 1.3rem; }}
.cap, .src {{ font-size:.8rem; color:var(--muted); }}
svg {{ width:100%; height:auto; display:block; font-family:'Instrument Sans', system-ui, sans-serif; }}
.kpis {{ display:grid; grid-template-columns:repeat(4, 1fr); gap:.8rem; margin:1rem 0 .4rem; }}
.kpi {{ background:#fff; border:1px solid var(--rule); border-radius:14px; padding:.8rem .9rem; }}
.kl {{ margin:0; font-size:.78rem; color:var(--muted); line-height:1.3; min-height:2.1em; }}
.kv {{ margin:.25rem 0 .1rem; font-size:1.7rem; font-weight:600; letter-spacing:-.02em; font-variant-numeric:tabular-nums; }}
.km {{ margin:.4rem 0 0; font-size:.78rem; line-height:1.4; color:var(--ink); border-top:1px solid var(--rule); padding-top:.45rem; }}
.per {{ display:flex; gap:.4rem; margin:1.2rem 0 .2rem; flex-wrap:wrap; }}
.per button {{ font-size:.8rem; font-weight:500; padding:.35rem .75rem; border-radius:999px; background:#fff; color:var(--ink); border:1px solid var(--rule); }}
.per button[aria-pressed="true"] {{ background:var(--ink); color:#fff; border-color:var(--ink); }}
.ku {{ font-size:.85rem; font-weight:400; color:var(--muted); }}
.rb {{ margin:.35rem 0 0; }} .gg {{ width:150px; margin:.2rem auto 0; }}
.ks {{ margin:.2rem 0 0; font-size:.7rem; color:#8A97A8; line-height:1.3; }}
.dl {{ font-size:.76rem; font-variant-numeric:tabular-nums; }} .dl.worse {{ color:var(--alert); }} .dl.better {{ color:var(--calm); }} .dl.flat {{ color:var(--muted); }}
details {{ margin:.6rem 0 0; font-size:.9rem; }} summary {{ cursor:pointer; color:var(--calm); font-weight:500; }}
.signs {{ display:grid; grid-template-columns:1fr 1fr; gap:1.4rem; margin-top:.8rem; }}
.signs ul {{ list-style:none; padding:0; margin:0; }}
.signs li {{ font-size:.88rem; margin:.3rem 0; padding-left:1.4rem; text-indent:-1.4rem; }}
.signs li.off {{ color:var(--muted); }} .mk {{ display:inline-block; width:1.4rem; text-indent:0; color:var(--alert); }}
.sr {{ position:absolute; left:-9999px; }}
section {{ margin-top:3rem; scroll-margin-top:4rem; }}
h2 {{ font-weight:600; font-size:1.35rem; line-height:1.3; margin:0 0 .35rem; letter-spacing:-.01em; }}
h3 {{ font-weight:600; font-size:1rem; margin:0; }}
section > p {{ margin:.2rem 0 .9rem; color:#33415C; max-width:48rem; }}
.cmp {{ display:flex; gap:1.5rem; align-items:center; flex-wrap:wrap; margin:.4rem 0 1.2rem; }} .compass {{ width:440px; max-width:100%; flex:none; }} .cmp .cap {{ flex:1; min-width:14rem; }}
.houses {{ display:grid; grid-template-columns:1fr 1fr; gap:1rem; }}
.house {{ border:1px solid var(--rule); border-top:4px solid var(--hc); border-radius:14px; padding:1rem 1.1rem; }}
.hhead {{ display:flex; align-items:center; gap:.75rem; }}
.emb {{ width:38px; height:38px; flex:none; }}
.motto {{ margin:0; font-size:.8rem; color:var(--muted); }}
.hcnt {{ margin-left:auto; font-size:.78rem; color:var(--hc); font-weight:600; white-space:nowrap; }}
.house > p {{ margin:.6rem 0 .3rem; font-size:.93rem; color:#33415C; }}
.house ul {{ padding-left:1.05rem; margin:.15rem 0 .5rem; font-size:.88rem; }}
.who {{ font-weight:500; color:var(--ink); }}
.sub {{ font-size:.78rem; font-weight:600; margin:.6rem 0 .1rem; color:var(--muted); }}
table {{ width:100%; border-collapse:collapse; font-size:.9rem; }}
td, th {{ text-align:left; padding:.5rem .45rem; border-bottom:1px solid var(--rule); vertical-align:top; }}
th {{ font-weight:500; color:var(--muted); font-size:.82rem; }}
.num {{ text-align:right; font-variant-numeric:tabular-nums; white-space:nowrap; }}
ul {{ padding-left:1.1rem; }} li {{ margin:.3rem 0; }}
.d {{ font-size:.82rem; color:var(--muted); margin-right:.35rem; font-variant-numeric:tabular-nums; }}
.grid2 {{ display:grid; grid-template-columns:1fr 1fr; gap:2rem; }}
#calc {{ background:var(--panel); border-radius:16px; padding:1.1rem 1.3rem; }}
.rows {{ display:grid; grid-template-columns:1fr 1fr; gap:.5rem 1.6rem; margin:.7rem 0 1.1rem; }}
.row {{ display:flex; justify-content:space-between; align-items:center; gap:.6rem; font-size:.9rem; }}
.row input {{ width:4.4rem; font:inherit; padding:.35rem .45rem; border:1px solid #CBD5E1; border-radius:8px; background:#fff; color:var(--ink); text-align:right; }}
button {{ font:inherit; font-weight:600; font-size:.95rem; padding:.65rem 1.1rem; background:var(--calm); color:#fff; border:0; border-radius:10px; cursor:pointer; }}
.team {{ font-size:1.2rem; font-weight:500; margin:1.1rem 0 .6rem; }}
a {{ color:var(--calm); text-underline-offset:2px; }}
a:focus-visible, button:focus-visible, input:focus-visible, summary:focus-visible {{ outline:3px solid #93B4F5; outline-offset:2px; }}
.ev h2 {{ font-size:1.12rem; }}
.tog {{ display:flex; gap:.5rem; flex-wrap:wrap; margin:0 0 .5rem; }}
.tog button {{ font-size:.8rem; font-weight:500; padding:.35rem .7rem; border-radius:999px; background:#fff; color:var(--ink); border:1px solid var(--rule); }}
.tog button[aria-pressed="true"] {{ background:var(--ink); color:#fff; border-color:var(--ink); }}
footer {{ margin-top:4rem; padding-top:1.2rem; border-top:1px solid var(--rule); font-size:.85rem; color:var(--muted); }}
@media (max-width:860px) {{ .kpis {{ grid-template-columns:repeat(2, 1fr); }} .houses, .grid2 {{ grid-template-columns:1fr; }} }}
@media (max-width:640px) {{ .nav {{ flex-wrap:nowrap; overflow-x:auto; white-space:nowrap; gap:.9rem; }} .per {{ flex-wrap:nowrap; overflow-x:auto; }} .per button {{ white-space:nowrap; }} #hist {{ min-width:620px; }} .card {{ overflow-x:auto; padding:1rem .8rem; }} .hs svg {{ min-width:560px; }} .cmp {{ justify-content:center; }} }}
@media (max-width:560px) {{ h1 {{ font-size:1.35rem; line-height:1.3; }} .kpis {{ grid-template-columns:1fr; }} .signs, .rows {{ grid-template-columns:1fr; }} .kv {{ font-size:1.5rem; }} main {{ padding:1rem .9rem 4rem; }} section {{ margin-top:2.2rem; }} }}
</style></head><body><main>
<nav class="nav"><span class="brand">Chips and Risk</span><a href="#now">Now</a><a href="#positions">Positions</a><a href="#savings">Your savings</a><a href="#history">History</a><a href="#evidence">Evidence</a><a href="method/">Method</a><a href="archive/">Archive</a>{'<a href="es/" hreflang="es" lang="es" class="lng">ES</a>' if lang == "en" else '<a href="../" hreflang="en" lang="en" class="lng">EN</a>'}</nav>

<section id="now" class="first">
<p class="diff">Not a bubble meter: it measures who carries the risk if the financing of AI breaks.</p>
<p class="stamp">Who carries the risk of the AI build-out, measured every week. Following “The Sharp End of AI Debt” (Acedo, 2026); prices updated every weekday, filings every week; last update {esc(ind["updated"])}.</p>
<h1>{esc(ind["headline"])}</h1>
{kpi_tiles(ind["kpis"], hero=("Lenders' gap in AI sell-offs, last 12 months", "Signs of a turning point", "Oracle's largest item with OpenAI, share of its value", "AI supply chain since ChatGPT"))}
<details><summary>What the twelve signs are, and which are present</summary>
<div class="signs"><div><h3>Signs of a late frenzy</h3><ul>{sign_list(sg["frenzy"])}</ul></div>
<div><h3>Signs of a turning point</h3><ul>{sign_list(sg["turning"])}</ul></div></div></details>
<details><summary>Everything that changed since the previous update</summary><ul>{changes}</ul></details>
</section>

<section id="positions"><h2>Four positions on the AI listings</h2>
<p>Like the four points of a compass: each position is one of the paper's listing paths, with who holds it, what they have at stake and what the data show for it now. Bets last recorded {esc(ind["freshness"].get("bets.csv", {}).get("latest", ""))}.</p>
<div class="cmp">{compass_svg(ind["houses"], sg, ind["needle"], ind["course"])[0]}<p class="cap">{esc(compass_svg(ind["houses"], sg, ind["needle"], ind["course"])[1])} The needle adds up the explicit signals listed in each position below; it is a count of evidence, not a probability.</p></div>
<div class="houses">{house_cards(ind["houses"], sg)}</div></section>

<section id="savings"><h2>Which position do your savings hold?</h2>{CALC}</section>

<section id="history"><h2>Where past booms went from here</h2>
<p>{lead}</p>
<div class="card">
{svg_history(ind["history"], ai)}
<p class="cap">Past booms from the start of their frenzy, rebased to 100, in calendar years: technology (electric utilities and the US market from July 1926; software, hardware, chips and telecoms from the Netscape listing in August 1995; US railroads from the end of the Civil War in April 1865 to beyond the Panic of 1873, monthly), energy (oil from January 1979, when the Shah left Iran; shale from January 2010) and credit (banks, finance and real estate from the Federal Reserve's cut to 1% in June 2003). Blue: the AI supply chain from the launch of ChatGPT, extended every week. The start dates are conventions, not forecasts: other dates would shift the curves. Total returns except the railroads (price index). The story begins earlier, with the printing press and the British railway mania of the 1840s, for which no price series is freely available. Sources: Kenneth French Data Library; F.R. Macaulay via NBER and FRED; daily prices.</p>
</div></section>

<section id="evidence"><h2>The evidence</h2>
<p>The measures behind every number above, one question each.</p>
<details class="evd"><summary>Do the AI-dependent lenders still lag when AI falls?</summary><section class="ev"><h2>Do the AI-dependent lenders still lag when AI falls?</h2>
<p>{esc(g["reading"])} Lenders to and investors in AI infrastructure against other financial stocks on the days the AI supply chain falls hardest, net of the market (points a day). Shaded: the 2016-2023 range (years with at least five sell-off days). Thresholds use only past data, so yearly values differ slightly from the paper.</p>
<div class="grid2"><div>{svg_bars(g["yearly"], g["reference"])}<p class="cap">When the AI chain falls 10%, the lenders now fall about {sens["since 2024"]["lenders"]}% and other financial stocks {sens["since 2024"]["others"]}%; in 2020-2023, {sens["2020-2023"]["lenders"]}% and {sens["2020-2023"]["others"]}%.</p></div>
<div><h3>Who lags, since 2024</h3><div class="hs">{svg_ranking(ind["ranking"])}</div></div></div></section>
</details>
<details class="evd"><summary>Is it the managers or their loan books, and since when?</summary><section class="ev"><div class="grid2"><div><h2>The managers, not their loan books</h2>
<p>The listed loan vehicles (BDCs) fall in AI sell-offs in almost every year; the managers' gap moved around zero before 2024 and has stayed negative since.</p>
<table><tr><th>Year</th><th class="num">Lenders</th><th class="num">BDCs</th></tr>{yrs}</table></div>
<div><h2>Since when, and through what</h2>
<p>The lenders' link to the AI chain beyond other financial stocks, net of the market and of the financial sector (equation 3), in hundredths of a correlation.</p>
{svg_lines({"Software": yearly_series(ind["specificity"].get("software", {}))*100, "Chips, power": yearly_series(ind["specificity"].get("chips_power", {}))*100}, h=170, unit="", colors={"Software": CALM, "Chips, power": ALERT}, fmt="{:+.1f}")}</div></div></section>
</details>
<details class="evd"><summary>Who carries OpenAI's and Anthropic's commitments?</summary><section class="ev"><h2>Who carries OpenAI's and Anthropic's commitments</h2>
<p>The largest documented item each listed counterparty has at stake with each tenant, as a share of its market value, updated weekly with prices. Items are different instruments and are not added.</p>
<div class="hs">{svg_hbars(ind["exposure"])}</div></section>
</details>
<details class="evd"><summary>How do the exposed companies and the listed tenants trade?</summary><section class="ev"><div class="grid2"><div><h2>How the three exposed companies trade</h2>
<p>Since January 2025: Oracle and CoreWeave against the rest of the chain, SoftBank against the Tokyo market (%).</p>
{svg_lines({ {"ORCL": "Oracle", "CRWV": "CoreWeave", "9984.T": "SoftBank"}.get(k, k): v for k, v in ind["exposed"].items()}, h=170, colors={"Oracle": ALERT, "CoreWeave": WATCH, "SoftBank": CALM})}</div>
<div><h2>Tenants that already have a public price</h2>
<p>Zhipu and MiniMax in Hong Kong since January, xAI inside SpaceX since June: change against the listing price (%).</p>
{svg_lines(ind["public_labs"], h=170, colors={"Zhipu": ALERT, "MiniMax": WATCH, "SpaceX (with xAI)": CALM}) or "<p class=cap>No price data yet for these listings.</p>"}</div></div></section>
</details>
<details class="evd"><summary>Does the news move them?</summary><section class="ev"><div class="grid2"><div><h2>Does SoftBank still move with OpenAI's news?</h2>
<p>SoftBank against the Tokyo market on the first session after each piece of news about OpenAI, in points. The paper predicts this fades if OpenAI lists.</p>
<table><tr><th>Date</th><th>News</th><th class="num">Pts</th></tr>{reac}</table></div>
<div><h2>Announcements against what the market does</h2>
<p>Oracle and CoreWeave against the rest of the chain over the sessions after each capability announcement (%).</p>
<table><tr><th>Date</th><th>Announcement</th><th class="num">Oracle</th><th class="num">CoreWeave</th></tr>{capab}</table></div></div></section>
</details>
<details class="evd"><summary>Cash, debt and supplier financing</summary><section class="ev"><div class="grid2"><div><h2>Cash against the story</h2>
<table><tr><th>Tenant</th><th>Measure</th><th class="num">$bn</th></tr>{tenants}</table></div>
<div><h2>The debt side: how far it has spread</h2>
<table><tr><th>Date</th><th>Measure</th><th class="num">$bn</th></tr>{debt}</table></div></div></section>
</details>
<details class="evd"><summary>Rates and the supplier warning sign</summary><section class="ev"><div class="grid2"><div><h2>Suppliers financing customers</h2>
<p>The warning sign of the telecoms boom: suppliers kept lending after outside capital left ($bn).</p>
<table><tr><th>Quarter</th><th class="num">Supplier financing</th><th class="num">Outside capital</th></tr>{ledger_rows}</table></div>
<div><h2>The ten-year Treasury yield</h2>
{"<p>No yield data this week.</p>" if rt["last"] is None else f"<p>{rt['last']:.2f}% on {esc(rt['date'])}" + ("" if rt["change_3m_bp"] is None else f", {rt['change_3m_bp']:+.0f} basis points in three months") + ". When last measured (2 October 2026), rising rates had not widened the lenders' gap.</p>"}
{svg_lines({"10-year": rt["series"]}, h=140, unit="%", colors={"10-year": INK}, zero=False, fmt="{:.2f}")}</div></div></section>
</details>
<details class="evd"><summary>What the filings and the record say</summary><section class="ev"><div class="grid2"><div><h2>What the new filings say</h2><ul>{fil}</ul></div>
<div><h2>Events on record</h2><ul>{ev}</ul></div></div></section>
</details>
</section>

<footer><p>Sources: daily prices from Stooq with Yahoo Finance as fallback; 10-year yield from FRED; filings from SEC EDGAR; past booms from the Kenneth French Data Library; events, bets and figures from the public record listed in the repository, each with its source. Data status: {esc(src)}. Manual files: {esc("; ".join(f"{f} last entry {v['latest']}" + (" (stale)" if v["stale"] else "") for f, v in ind["freshness"].items()))}.</p>
<p><a href="method/">Method</a> · <a href="archive/">Weekly archive</a></p>
<p>Code and definitions: <a href="https://github.com/Acedoo/chips-and-risk">github.com/Acedoo/chips-and-risk</a>. The positions' emblems are this site's own. This page describes public market data; it is not investment advice.</p>
<p>Built with the assistance of Claude (Anthropic). Anthropic is one of the companies tracked here; its figures follow the same rules and sources as the others.</p></footer>
</main></body></html>"""
    page = page.replace("<table>", '<div class="tw"><table>').replace("</table>", "</table></div>")
    if lang == "es":
        from monitor import i18n
        page = i18n.translate_scripts(i18n.translate_html(page))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(page, encoding="utf-8")
