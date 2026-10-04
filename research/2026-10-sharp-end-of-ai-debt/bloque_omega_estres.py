"""Análisis secundario con las fórmulas del arnés público del bloque Omega (adenda 6). Sin cambios en las fórmulas."""
import json
import numpy as np
import pandas as pd
VENT, NPERM, SEMILLA = 250, 200, 20261002
P = pd.read_csv('panel_capa_financiera_20261002.csv', parse_dates=[0], index_col=0).sort_index()
P = P.drop(columns=['SPY'])
P = P.loc[:, P.notna().mean() >= 0.95]                       # como el arnés
R = np.log(P).diff().iloc[1:].fillna(0.0)                   # como el arnés
X, fechas, cols = R.values, R.index, list(R.columns)
g = open('grupos_capa_financiera.txt').read().split('\n')
TRAT = [t for t in g[0].split()[1:] if t in cols]; CTRL = [t for t in g[1].split()[1:] if t in cols]
de = json.load(open('definicion_cadena_20261002.json'))
CAD = [c for c in de['semis'] + de['equipo'] + de['utilities'] + de['software'] if c in cols]
cad_ret = R[CAD].mean(axis=1).rolling(10).sum()
umbral = cad_ret.iloc[VENT:].quantile(0.10)
dias = [i for i in range(VENT - 1, len(fechas)) if cad_ret.iloc[i] <= umbral]
iT = [cols.index(t) for t in TRAT]; iC = [cols.index(t) for t in CTRL]
filas = []
for d in dias:
    W = X[d - VENT + 1:d + 1]
    A = np.abs(np.corrcoef(W.T)); np.fill_diagonal(A, 0)     # fórmulas del arnés
    s = A.sum(1); A2 = A @ A; tri = (A2 * A).sum(1)
    E = s**2 * (s**2).sum()**2 / (s.sum()**3)
    exc = (tri - E) / np.maximum(E, 1e-12)
    filas.append(dict(fecha=fechas[d], tri=tri / tri.mean(), exc=exc, grado=s / s.mean()))
def dif(nombre, it, ic, subset=None):
    sel = filas if subset is None else [f for f in filas if subset(f['fecha'])]
    return float(np.mean([f[nombre][it].mean() - f[nombre][ic].mean() for f in sel]))
res = dict(dias_estres=len(dias), umbral_10d=float(umbral), n_trat=len(TRAT), n_ctrl=len(CTRL))
idx = iT + iC; rng = np.random.default_rng(SEMILLA)
perms = [rng.permutation(idx) for _ in range(NPERM)]
for nombre in ('tri', 'exc', 'grado'):
    obs = dif(nombre, iT, iC)
    null = [dif(nombre, list(p[:len(iT)]), list(p[len(iT):])) for p in perms]
    res[nombre] = dict(diferencia=obs, p=(1 + sum(n >= obs for n in null)) / (1 + NPERM),
                       antes_2024=dif(nombre, iT, iC, lambda f: f < pd.Timestamp('2024-01-01')),
                       desde_2024=dif(nombre, iT, iC, lambda f: f >= pd.Timestamp('2024-01-01')))
tri_all = np.concatenate([f['tri'][idx] for f in filas]); gr_all = np.concatenate([f['grado'][idx] for f in filas])
res['spearman_tri_grado_financieras'] = float(pd.Series(tri_all).corr(pd.Series(gr_all), method='spearman'))
res['dias_estres_desde_2024'] = int(sum(f['fecha'] >= pd.Timestamp('2024-01-01') for f in filas))
json.dump(res, open('bloque_omega_estres_resultados.json', 'w'), indent=1)
print(json.dumps(res, indent=1))
