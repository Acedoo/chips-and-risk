"""PASO 1 pre-registrado: interacción entre el choque de tipos y el de la IA en la brecha de los financiadores."""
import json, sys
import numpy as np
import pandas as pd
PANEL = '../panel_capa_financiera_20261002.csv'; TIPOS = sys.argv[1] if len(sys.argv) > 1 else 'tipos_20261002.csv'
P = pd.read_csv(PANEL, index_col=0, parse_dates=True).sort_index()
de = json.load(open('../definicion_cadena_20261002.json'))
CAD = de['semis'] + de['equipo'] + de['utilities'] + de['software']
g = open('../grupos_capa_financiera.txt').read().split('\n')
L, O = g[0].split()[1:], g[1].split()[1:]
FIN = L + O
r = P.pct_change(fill_method=None)
rm = r['SPY']
# beta a 250 días previos (sin información posterior a t)
cov = r[FIN].rolling(250, min_periods=200).cov(rm).shift(1)
var = rm.rolling(250, min_periods=200).var().shift(1)
AR = r[FIN] - cov.div(var, axis=0).mul(rm, axis=0)
T = pd.read_csv(TIPOS, index_col=0, parse_dates=True).sort_index()['^TNX'].dropna()
esc = 10 if T.median() > 20 else 100                  # ^TNX en % (x100 -> pb) o en % x10 (x10 -> pb)
Rt = (T.diff() * esc).reindex(r.index)                 # puntos básicos
AIt = -(r[CAD].mean(axis=1) - rm)                       # positivo cuando la IA cae más que el mercado
def ajustar(G, a, b):
    d = pd.concat([G, a, b], axis=1).dropna(); d.columns = ['G', 'A', 'R']
    X = np.column_stack([np.ones(len(d)), d.A, d.R, d.A * d.R])
    coef = np.linalg.lstsq(X, d.G.values, rcond=None)[0]
    return coef, d
res = {}
rng = np.random.default_rng(20261002)
for nombre, (ini, fin) in {'2024-2026': ('2024-01-02', '2026-09-30'), '2016-2023': ('2016-01-01', '2023-12-31')}.items():
    sl = slice(ini, fin)
    G = (AR.loc[sl, L].mean(axis=1) - AR.loc[sl, O].mean(axis=1))
    coef, d = ajustar(G, AIt.loc[sl], Rt.loc[sl])
    a90, r90 = d.A.quantile(0.9), d.R.quantile(0.9)
    efecto = coef[3] * a90 * r90 * 100
    nul = []
    for _ in range(2000):
        perm = rng.permutation(FIN); Lp, Op = list(perm[:18]), list(perm[18:])
        Gp = AR.loc[sl, Lp].mean(axis=1) - AR.loc[sl, Op].mean(axis=1)
        nul.append(ajustar(Gp, AIt.loc[sl], Rt.loc[sl])[0][3])
    p = float((np.array(nul) <= coef[3]).mean())
    conj = d[(d.A >= a90) & (d.R >= r90)].index
    orcl = (AR.loc[conj, 'ORCL'] if 'ORCL' in AR else pd.Series(dtype=float))
    res[nombre] = dict(n_dias=int(len(d)), b1_IA=round(float(coef[1]*100), 4), b2_tipos_por_pb=round(float(coef[2]*100), 5),
                       b3_interaccion=round(float(coef[3]*100), 6), p_b3=round(p, 4),
                       efecto_conjunto_p90_pp=round(float(efecto), 3), p90_IA_pp=round(float(a90*100), 3), p90_tipos_pb=round(float(r90), 2),
                       dias_conjuntos=int(len(conj)), brecha_media_dias_conjuntos_pp=round(float(d.loc[conj, 'G'].mean()*100), 3) if len(conj) else None)
pr = res['2024-2026']
res['regla'] = ('LOS DOS GOLPES SE MULTIPLICAN' if (pr['b3_interaccion'] < 0 and pr['p_b3'] < 0.05 and pr['efecto_conjunto_p90_pp'] <= -0.20)
                else 'NO SE MULTIPLICAN (se suman o no hay interacción)')
json.dump(res, open('tipos_ia_resultados.json', 'w'), indent=1, ensure_ascii=False)
print(json.dumps(res, indent=1, ensure_ascii=False))
