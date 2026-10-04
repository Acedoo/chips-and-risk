"""Parte 2 (pre-registrada): predicción fuera de pliegue del arnés en la ventana que termina el 29-dic-2023, base frente a
base + bloque, y su relación con lo que cada financiera hizo en las caídas bruscas de la IA de 2024-2026."""
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.model_selection import KFold
VENT = 250
P = pd.read_csv('/home/claude/panel_bloque_ia.csv', parse_dates=[0], index_col=0).sort_index()
P = P.loc[:, P.notna().mean() >= 0.95]                     # como el arnés
R = np.log(P).diff().iloc[1:].fillna(0.0)
X, fechas, cols, n = R.values, R.index, list(R.columns), R.shape[1]
def modelo():
    return HistGradientBoostingRegressor(max_iter=300, max_depth=3, learning_rate=0.05, random_state=0)
t = fechas.get_loc(pd.Timestamp('2023-12-29')) + 1         # W = X[t-250:t] termina el 29-dic-2023
W = X[t - VENT:t]; F = X[t:t + VENT]
mw, mf = W.mean(1), F.mean(1)
beta = np.array([np.cov(W[:, i], mw)[0, 1] for i in range(n)]) / mw.var()
mes_p = W[mw <= np.quantile(mw, 0.05)].mean(0)
A = np.abs(np.corrcoef(W.T)); np.fill_diagonal(A, 0)
s = A.sum(1); A2 = A @ A; tri = (A2 * A).sum(1)
E = s**2 * (s**2).sum()**2 / (s.sum()**3)
base = np.column_stack([beta, W[-21:].std(0), W.std(0), W[:-21].sum(0), W[-21:].sum(0), mes_p, s])
om = np.column_stack([tri, (tri - E) / np.maximum(E, 1e-12)])
y = F[mf <= np.quantile(mf, 0.05)].mean(0)
def oof(Fm):
    pred = np.zeros(n); kf = KFold(5, shuffle=True, random_state=0)
    for tr, te in kf.split(Fm):
        m = modelo(); m.fit(Fm[tr], y[tr]); pred[te] = m.predict(Fm[te])
    return pred
pb, pf = oof(base), oof(np.column_stack([base, om]))
d = pd.Series(pf - pb, index=cols)                          # negativo = el bloque empeora la pérdida de cola predicha
g = open('../grupos_capa_financiera.txt').read().split('\n')
FIN = [c for c in g[0].split()[1:] + g[1].split()[1:] if c in cols]
real = pd.Series(json.load(open('../quien_cae_resultados.json'))['ranking_pp'])[FIN]
x = d[FIN]
rho = float(x.rank().corr(real.rank()))
rng = np.random.default_rng(20261002)
null = [float(x.rank().corr(pd.Series(rng.permutation(real.values), index=real.index).rank())) for _ in range(2000)]
p = float((np.array(null) >= rho).mean())
out = dict(ventana_hasta='2023-12-29', n_financieras=len(FIN), spearman=round(rho, 3), p=round(p, 4),
           regla='PASA: demostración de producto' if (rho > 0 and p < 0.05) else 'NO PASA: se archiva',
           mas_senaladas_por_el_bloque={k: round(v * 100, 3) for k, v in x.sort_values().head(10).items()},
           menos_senaladas={k: round(v * 100, 3) for k, v in x.sort_values().tail(5).items()})
json.dump(out, open('parte2_resultados.json', 'w'), indent=1, ensure_ascii=False)
print(json.dumps(out, indent=1, ensure_ascii=False))
