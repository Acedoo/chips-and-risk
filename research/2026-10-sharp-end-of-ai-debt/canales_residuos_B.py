"""Descriptivo para la nota: especificidad por canal sobre residuos de mercado + factor financiero (versión B de la adenda 5)."""
import json
import numpy as np
import pandas as pd
VENT, PASO = 250, 10
px = pd.read_csv('panel_capa_financiera_20261002.csv', index_col=0, parse_dates=True).sort_index()
R = np.log(px).diff().iloc[1:]
g = open('grupos_capa_financiera.txt').read().split('\n')
TRAT, CTRL = g[0].split()[1:], g[1].split()[1:]; FIN = TRAT + CTRL
de = json.load(open('definicion_cadena_20261002.json'))
INFRA = de['semis'] + de['equipo'] + de['utilities']; SOFT = de['software']; NEUTRA = de['neutra']
fechas, out = [], {'infra': [], 'soft': []}
for s in range(0, len(R) - VENT + 1, PASO):
    sub = R.iloc[s:s + VENT]; ok = list(sub.columns[sub.notna().all()])
    X = np.column_stack([np.ones(VENT), sub['SPY'].values, sub[[f for f in FIN if f in ok]].mean(axis=1).values])
    cols = [c for c in ok if c != 'SPY']; Y = sub[cols].values
    B, *_ = np.linalg.lstsq(X, Y, rcond=None); E = pd.DataFrame(Y - X @ B, columns=cols)
    Z = (E - E.mean()) / E.std(); fo = [f for f in FIN if f in cols]
    def ac(l):
        cc = [c for c in l if c in cols]; C = (Z[fo].T.values @ Z[cc].values) / (VENT - 1)
        return pd.Series(np.abs(C).mean(1), index=fo)
    neu = ac(NEUTRA)
    for k, l in (('infra', INFRA), ('soft', SOFT)):
        sp = ac(l) - neu
        out[k].append(sp[[t for t in TRAT if t in fo]].mean() - sp[[t for t in CTRL if t in fo]].mean())
    fechas.append(sub.index[-1])
df = pd.DataFrame(out, index=pd.DatetimeIndex(fechas))
anual = df.resample('YE').mean().round(4); anual.index = anual.index.year
nuevo, viejo = df.index >= '2024-01-01', df.index <= '2022-12-31'
res = dict(por_anio=anual.to_dict(), infra_2016_22=float(df.infra[viejo].mean()), infra_2024_26=float(df.infra[nuevo].mean()),
           soft_2016_22=float(df.soft[viejo].mean()), soft_2024_26=float(df.soft[nuevo].mean()))
json.dump(res, open('canales_residuos_B_resultados.json', 'w'), indent=1)
print(anual.to_string()); print({k: round(v, 4) for k, v in res.items() if k != 'por_anio'})
