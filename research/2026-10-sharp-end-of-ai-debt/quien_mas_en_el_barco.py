"""Adenda 8: BDC de EE. UU. y megabancos japoneses en Tokio en los peores días de la cadena de la IA."""
import json, itertools
import numpy as np
import pandas as pd
main = pd.read_csv('panel_capa_financiera_20261002.csv', index_col=0, parse_dates=True).sort_index()
cap2 = pd.read_csv('panel_capa2_20261002.csv', index_col=0, parse_dates=True).sort_index()
g = open('grupos_capa_financiera.txt').read().split('\n'); CTRL = g[1].split()[1:]
de = json.load(open('definicion_cadena_20261002.json'))
CAD = de['semis'] + de['equipo'] + de['utilities'] + de['software']
R = main.pct_change().iloc[1:]
cad = R[CAD].mean(axis=1)
def peores(desde, hasta, q=0.05):
    c = cad[desde:hasta].dropna(); return c[c <= c.quantile(q)].index
D24, D16 = peores('2024-01-01', '2026-10-01'), peores('2016-01-01', '2023-12-31')
def anormal(ret, mkt):
    out = pd.DataFrame(index=ret.index, columns=ret.columns, dtype=float)
    for c in ret.columns:
        cov = ret[c].rolling(250, min_periods=200).cov(mkt).shift(1); var = mkt.rolling(250, min_periods=200).var().shift(1)
        out[c] = ret[c] - cov / var * mkt
    return out
res = {}
# A) BDC
BDC = ['ARCC', 'OBDC', 'BXSL', 'FSK', 'GBDC', 'MAIN', 'HTGC', 'PSEC', 'TSLX', 'OCSL', 'GSBD', 'NMFC', 'CGBD', 'TCPC', 'BCSF', 'MFIC']
us = pd.concat([main[CTRL + ['SPY']], cap2[BDC].reindex(main.index)], axis=1)
Ru = us.pct_change(fill_method=None).iloc[1:]
AB = anormal(Ru[BDC + CTRL], Ru['SPY'])
def dif(A, dias, it, ic):
    X = A.loc[dias]; return float((X[it].mean(axis=1) - X[ic].mean(axis=1)).mean() * 100)
rng = np.random.default_rng(20261002); pool = BDC + CTRL
for nom, dias in (('2024_26', D24), ('2016_23', D16)):
    obs = dif(AB, dias, BDC, CTRL); null = []
    for _ in range(200):
        p = list(rng.permutation(pool)); null.append(dif(AB, dias, p[:len(BDC)], p[len(BDC):]))
    res['A_bdc_' + nom] = dict(dif_pp=obs, p=(1 + sum(n <= obs for n in null)) / 201,
                               bdc_pp=float(AB.loc[dias, BDC].mean(axis=1).mean() * 100), ctrl_pp=float(AB.loc[dias, CTRL].mean(axis=1).mean() * 100))
res['A_regla'] = 'PASA' if (res['A_bdc_2024_26']['dif_pp'] <= -0.5 and res['A_bdc_2024_26']['p'] < 0.05) else 'NO PASA'
res['A_por_bdc_pp'] = {k: round(float(v), 2) for k, v in (AB.loc[D24, BDC].mean() * 100).sort_values().items()}
# B) Japón
MEGA = ['8306.T', '8316.T', '8411.T']
REG = [c for c in ['8331.T', '8354.T', '7186.T', '8418.T', '8385.T', '8359.T', '8377.T', '8366.T', '8341.T', '8334.T', '7167.T', '8524.T'] if c in cap2.columns]
jp = cap2[MEGA + REG + ['1306.T']].dropna(subset=['1306.T'])
Rj = jp.pct_change(fill_method=None).iloc[1:]
ABj = anormal(Rj[MEGA + REG], Rj['1306.T'])
def a_tokio(dias):
    idx = ABj.index; out = []
    for d in dias:
        k = idx.searchsorted(d, side='right')
        if k < len(idx): out.append(idx[k])
    return sorted(set(out))
for nom, dias in (('2024_26', a_tokio(D24)), ('2016_23', a_tokio(D16))):
    obs = dif(ABj, dias, MEGA, REG); todos = MEGA + REG; null = []
    for comb in itertools.combinations(todos, 3):
        null.append(dif(ABj, dias, list(comb), [c for c in todos if c not in comb]))
    res['B_japon_' + nom] = dict(n_dias=len(dias), dif_pp=obs, p=sum(n <= obs for n in null) / len(null), n_combinaciones=len(null),
                                 mega_pp=float(ABj.loc[dias, MEGA].mean(axis=1).mean() * 100), regionales_pp=float(ABj.loc[dias, REG].mean(axis=1).mean() * 100))
res['B_regla'] = 'PASA' if (res['B_japon_2024_26']['dif_pp'] <= -0.5 and res['B_japon_2024_26']['p'] < 0.05) else 'NO PASA'
res['B_por_banco_pp'] = {k: round(float(v), 2) for k, v in (ABj.loc[a_tokio(D24), MEGA + REG].mean() * 100).sort_values().items()}
res['B_regionales_usados'] = REG
json.dump(res, open('quien_mas_en_el_barco_resultados.json', 'w'), indent=1)
print(json.dumps(res, indent=1))
