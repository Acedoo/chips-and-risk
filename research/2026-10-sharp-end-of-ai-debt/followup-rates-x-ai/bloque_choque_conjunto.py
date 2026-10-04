"""PASO 2 pre-registrado: el arnés público del bloque Omega con UN solo cambio, el objetivo: rendimiento medio en los días del
año siguiente con choque conjunto (IA en su quintil peor frente al mercado y tipos en su quintil de mayor subida).
Todas las demás fórmulas se copian de validate_omega_block.py sin tocarlas."""
import json, sys
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.model_selection import KFold
VENT, PASO = 250, 21
rng = np.random.default_rng(7)
def modelo():
    return HistGradientBoostingRegressor(max_iter=300, max_depth=3, learning_rate=0.05, random_state=0)
def r2_cv(F, y):
    kf = KFold(5, shuffle=True, random_state=0); sr = st = 0.0
    for tr, te in kf.split(F):
        m = modelo(); m.fit(F[tr], y[tr]); p = m.predict(F[te])
        sr += ((y[te]-p)**2).sum(); st += ((y[te]-y[te].mean())**2).sum()
    return 1 - sr/st
TIPOS = sys.argv[1] if len(sys.argv) > 1 else 'tipos_20261002.csv'
full = pd.read_csv('../panel_capa_financiera_20261002.csv', index_col=0, parse_dates=True).sort_index()
de = json.load(open('../definicion_cadena_20261002.json')); CAD = de['semis'] + de['equipo'] + de['utilities'] + de['software']
P = full.drop(columns=['SPY']); P = P.loc[:, P.notna().mean() >= 0.95]          # como el arnés
R = np.log(P).diff().iloc[1:].fillna(0.0)
X, fechas, n = R.values, R.index, R.shape[1]
rs = full.pct_change(fill_method=None).reindex(fechas)
AIt = (-(rs[CAD].mean(axis=1) - rs['SPY'])).values
T = pd.read_csv(TIPOS, index_col=0, parse_dates=True).sort_index()['^TNX'].dropna()
esc = 10 if T.median() > 20 else 100
Rt_real = (T.diff() * esc).reindex(fechas).values
def ventana(t, Rt):
    W = X[t-VENT:t]; F = X[t:t+VENT]
    mw = W.mean(1)
    beta = np.array([np.cov(W[:, i], mw)[0, 1] for i in range(n)])/mw.var()
    mes_p = W[mw <= np.quantile(mw, 0.05)].mean(0)
    A = np.abs(np.corrcoef(W.T)); np.fill_diagonal(A, 0)
    s = A.sum(1); A2 = A@A; tri = (A2*A).sum(1)
    E = s**2*(s**2).sum()**2/(s.sum()**3)
    base = np.column_stack([beta, W[-21:].std(0), W.std(0), W[:-21].sum(0), W[-21:].sum(0), mes_p, s])
    om = np.column_stack([tri, (tri-E)/np.maximum(E, 1e-12)])
    a, rr = AIt[t:t+VENT], Rt[t:t+VENT]
    ok = np.isfinite(a) & np.isfinite(rr)
    if ok.sum() < 200: return None
    conj = ok & (a >= np.nanquantile(a[ok], 0.8)) & (rr >= np.nanquantile(rr[ok], 0.8))   # ÚNICO cambio: el objetivo
    if conj.sum() < 8: return None
    return base, om, F[conj].mean(0), int(conj.sum())
def correr(Rt, con_placebo):
    d_om, d_pl, ndias = [], [], []
    for t in range(VENT, len(fechas)-VENT+1, PASO):
        v = ventana(t, Rt)
        if v is None: continue
        b, o, y, k = v
        rb = r2_cv(b, y)
        d_om.append(r2_cv(np.column_stack([b, o]), y) - rb); ndias.append(k)
        if con_placebo:
            d_pl.append(r2_cv(np.column_stack([b, rng.standard_normal((n, 5))]), y) - rb)
    return np.array(d_om), np.array(d_pl), ndias
d_om, d_pl, ndias = correr(Rt_real, True)
barajados = []
for sem in (1, 2, 3):                                   # ENMIENDA 1: control con los tipos barajados en el tiempo
    Rb = Rt_real.copy(); fin = np.isfinite(Rb)
    Rb[fin] = np.random.default_rng(sem).permutation(Rb[fin])
    barajados.append(float(correr(Rb, False)[0].mean()))
def ic(v, blq=12, B=2000):
    nb = int(np.ceil(len(v)/blq)); out = np.empty(B)
    for bb in range(B):
        s0 = rng.integers(0, len(v)-blq+1, nb)
        idx = np.concatenate([np.arange(x, x+blq) for x in s0])[:len(v)]
        out[bb] = v[idx].mean()
    return np.percentile(out, [2.5, 97.5])
io, ip = ic(d_om), ic(d_pl)
pass_arnes = bool(io[0] > 0 and io[0] > ip[1])
ok = bool(pass_arnes and d_om.mean() > max(barajados) and io[0] > np.mean(barajados))
res = dict(ventanas=int(len(d_om)), activos=int(n), dias_conjuntos_mediana=float(np.median(ndias)),
           dR2_bloque=round(float(d_om.mean()), 4), ic95_bloque=[round(float(io[0]), 4), round(float(io[1]), 4)],
           dR2_placebo=round(float(d_pl.mean()), 4), ic95_placebo=[round(float(ip[0]), 4), round(float(ip[1]), 4)],
           pass_arnes=pass_arnes, dR2_tipos_barajados=[round(x, 4) for x in barajados],
           regla='PASS: el bloque atribuye el choque conjunto' if ok else 'FAIL')
json.dump(res, open('bloque_choque_conjunto_resultados.json', 'w'), indent=1)
print(json.dumps(res, indent=1))
