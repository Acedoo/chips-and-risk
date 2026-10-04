"""Adenda 7: rendimientos anormales de financiadores y control en los peores días de la cadena de la IA."""
import json
import numpy as np
import pandas as pd
px = pd.read_csv('panel_capa_financiera_20261002.csv', index_col=0, parse_dates=True).sort_index()
R = px.pct_change().iloc[1:]
g = open('grupos_capa_financiera.txt').read().split('\n')
TRAT, CTRL = g[0].split()[1:], g[1].split()[1:]; FIN = TRAT + CTRL
de = json.load(open('definicion_cadena_20261002.json'))
CAD = de['semis'] + de['equipo'] + de['utilities'] + de['software']
cad = R[CAD].mean(axis=1); spy = R['SPY']
# anormal con beta de los 250 días previos
ab = pd.DataFrame(index=R.index, columns=FIN, dtype=float)
for f in FIN:
    cov = R[f].rolling(250).cov(spy).shift(1); var = spy.rolling(250).var().shift(1)
    ab[f] = R[f] - (cov / var) * spy
def peores(desde, hasta, q=0.05):
    c = cad[desde:hasta].dropna(); return c[c <= c.quantile(q)].index
def dif(dias, it, ic):
    A = ab.loc[dias]
    return float((A[it].mean(axis=1) - A[ic].mean(axis=1)).mean() * 100)
res = {}
rng = np.random.default_rng(20261002)
for nombre, dias in (('peores_2024_26', peores('2024-01-01', '2026-10-01')), ('peores_2016_23', peores('2016-01-01', '2023-12-31'))):
    dias = [d for d in dias if ab.loc[d, FIN].notna().sum() > 30]
    obs = dif(dias, TRAT, CTRL)
    null = []
    for _ in range(200):
        p = rng.permutation(FIN); null.append(dif(dias, list(p[:len(TRAT)]), list(p[len(TRAT):])))
    res[nombre] = dict(n_dias=len(dias), cadena_media_pct=float(cad.loc[dias].mean() * 100), dif_pp=obs,
                       p=(1 + sum(n <= obs for n in null)) / 201,
                       trat_pp=float(ab.loc[dias, TRAT].mean(axis=1).mean() * 100), ctrl_pp=float(ab.loc[dias, CTRL].mean(axis=1).mean() * 100))
otros = [d for d in cad['2024-01-01':'2026-10-01'].index if d not in peores('2024-01-01', '2026-10-01')]
res['resto_dias_2024_26_dif_pp'] = dif(otros, TRAT, CTRL)
r = res['peores_2024_26']
res['regla'] = 'PASA: hay artículo' if (r['dif_pp'] <= -0.5 and r['p'] < 0.05) else 'NO PASA: nota y LinkedIn, sin FT'
d24 = peores('2024-01-01', '2026-10-01')
ranking = (ab.loc[d24, FIN].mean() * 100).sort_values()
res['ranking_pp'] = {k: round(float(v), 2) for k, v in ranking.items()}
ds = pd.Timestamp('2025-01-27')
res['deepseek'] = dict(cadena_pct=round(float(cad.loc[ds] * 100), 2),
                       trat_pct=round(float(R.loc[ds, TRAT].mean() * 100), 2), ctrl_pct=round(float(R.loc[ds, CTRL].mean() * 100), 2),
                       spy_pct=round(float(spy.loc[ds] * 100), 2),
                       por_empresa={k: round(float(v) * 100, 2) for k, v in R.loc[ds, FIN].sort_values().items()})
json.dump(res, open('quien_cae_resultados.json', 'w'), indent=1)
print(json.dumps({k: v for k, v in res.items() if k not in ('ranking_pp', 'deepseek')}, indent=1))
print('RANKING (anormal medio en los peores días 2024-26, pp):'); print(ranking.round(2).to_string())
print('DEEPSEEK:', {k: v for k, v in res['deepseek'].items() if k != 'por_empresa'})
