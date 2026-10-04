"""Comprobación de factores (adenda 5). Repite el análisis principal sobre residuos de mercado (A) y de mercado + financiero (B)."""
import json
import numpy as np
import pandas as pd
VENT, PASO, NPERM, SEMILLA = 250, 10, 200, 20261002
px = pd.read_csv('panel_capa_financiera_20261002.csv', index_col=0, parse_dates=True).sort_index()
R = np.log(px).diff().iloc[1:]
g = open('grupos_capa_financiera.txt').read().split('\n')
TRAT, CTRL = g[0].split()[1:], g[1].split()[1:]
FIN = TRAT + CTRL
de = json.load(open('definicion_cadena_20261002.json'))
CADENA = de['semis'] + de['equipo'] + de['utilities'] + de['software']
NEUTRA = de['neutra']

def residuos(sub, ok, modo):
    X = [sub['SPY'].values]
    if modo == 'B':
        X.append(sub[[f for f in FIN if f in ok]].mean(axis=1).values)
    X = np.column_stack([np.ones(len(sub))] + X)
    cols = [c for c in ok if c != 'SPY']
    Y = sub[cols].values
    B, *_ = np.linalg.lstsq(X, Y, rcond=None)
    return pd.DataFrame(Y - X @ B, index=sub.index, columns=cols)

out = {}
for modo in ('A', 'B'):
    fechas, M = [], []
    for s in range(0, len(R) - VENT + 1, PASO):
        sub = R.iloc[s:s + VENT]
        ok = list(sub.columns[sub.notna().all()])
        E = residuos(sub, ok, modo)
        Z = (E - E.mean()) / E.std()
        fin_ok = [f for f in FIN if f in Z.columns]
        def acop(lista):
            cols = [c for c in lista if c in Z.columns]
            C = (Z[fin_ok].T.values @ Z[cols].values) / (VENT - 1)
            return pd.Series(np.abs(C).mean(axis=1), index=fin_ok)
        M.append((acop(CADENA) - acop(NEUTRA)).reindex(FIN).values)
        fechas.append(sub.index[-1])
    fechas = pd.DatetimeIndex(fechas); M = np.array(M)
    nuevo, viejo = fechas >= '2024-01-01', fechas <= '2022-12-31'
    def est(it, ic):
        d = np.nanmean(M[:, it], axis=1) - np.nanmean(M[:, ic], axis=1)
        return float(d[nuevo].mean()), float(d[nuevo].mean() - d[viejo].mean()), d
    idx = list(range(len(FIN))); it, ic = idx[:len(TRAT)], idx[len(TRAT):]
    L, Dl, d = est(it, ic)
    rng = np.random.default_rng(SEMILLA); pl = pc = 0
    for _ in range(NPERM):
        p = rng.permutation(idx); Lp, Dp, _ = est(list(p[:len(TRAT)]), list(p[len(TRAT):]))
        pl += Lp >= L; pc += Dp >= Dl
    anual = pd.Series(d, index=fechas).resample('YE').mean().round(4)
    out[modo] = dict(nivel_2024_26=L, cambio=Dl, p_nivel=(1 + pl) / (1 + NPERM), p_cambio=(1 + pc) / (1 + NPERM),
                     por_anio={str(k.year): float(v) for k, v in anual.items()})
    print(modo, json.dumps(out[modo]), flush=True)
pasa = all(out[m]['nivel_2024_26'] > 0 and out[m]['cambio'] > 0 and out[m]['p_nivel'] < 0.05 and out[m]['p_cambio'] < 0.05 for m in ('A', 'B'))
out['regla'] = 'SE MANTIENE' if pasa else 'NO SE MANTIENE'
json.dump(out, open('capa_financiera_factores_resultados.json', 'w'), indent=1)
print(out['regla'])
