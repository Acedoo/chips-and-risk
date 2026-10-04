"""Capa financiera de la cadena de la IA. Análisis según PREREGISTRO_CAPA_FINANCIERA.md (con sus adendas 1 a 4).
Uso: python3 capa_financiera.py  (lee panel_capa_financiera_20261002.csv, grupos_capa_financiera.txt y definicion_cadena_20261002.json)"""
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
INFRA = de['semis'] + de['equipo'] + de['utilities']
SOFT = de['software']
CADENA = INFRA + SOFT
NEUTRA = de['neutra']

fechas, spec = [], {'cadena': [], 'infra': [], 'soft': []}
elas = {k: [] for k in ('trat_cadena', 'ctrl_cadena', 'trat_infra', 'ctrl_infra', 'trat_soft', 'ctrl_soft')}
for s in range(0, len(R) - VENT + 1, PASO):
    sub = R.iloc[s:s + VENT]
    ok = sub.columns[sub.notna().all()]
    Z = (sub[ok] - sub[ok].mean()) / sub[ok].std()
    fin_ok = [f for f in FIN if f in ok]
    def acop(lista):
        cols = [c for c in lista if c in ok]
        C = (Z[fin_ok].T.values @ Z[cols].values) / (VENT - 1)
        return pd.Series(np.abs(C).mean(axis=1), index=fin_ok)
    neutro = acop(NEUTRA)
    for k, lista in (('cadena', CADENA), ('infra', INFRA), ('soft', SOFT)):
        spec[k].append((acop(lista) - neutro).reindex(FIN).values)
    def ew(lista):
        return sub[[c for c in lista if c in ok]].mean(axis=1)
    for grupo, nombre in ((TRAT, 'trat'), (CTRL, 'ctrl')):
        y = ew(grupo)
        for k, lista in (('cadena', CADENA), ('infra', INFRA), ('soft', SOFT)):
            x = ew(lista)
            elas[nombre + '_' + k].append(float(np.cov(y, x)[0, 1] / np.var(x, ddof=1)))
    fechas.append(sub.index[-1])
fechas = pd.DatetimeIndex(fechas)
S = {k: np.array(v) for k, v in spec.items()}           # ventanas x 42
per_nuevo = fechas >= '2024-01-01'
per_viejo = fechas <= '2022-12-31'

def D(M, it, ic):
    return np.nanmean(M[:, it], axis=1) - np.nanmean(M[:, ic], axis=1)

def estad(M, it, ic):
    d = D(M, it, ic)
    return float(np.mean(d[per_nuevo])), float(np.mean(d[per_nuevo]) - np.mean(d[per_viejo])), d

def prueba(M, trat, ctrl, nombre):
    todos = trat + ctrl
    idx = [FIN.index(t) for t in todos]
    it = idx[:len(trat)]; ic = idx[len(trat):]
    L, Dl, d = estad(M, it, ic)
    rng = np.random.default_rng(SEMILLA)
    pl, pd_ = 0, 0
    for _ in range(NPERM):
        p = rng.permutation(idx)
        Lp, Dp, _ = estad(M, list(p[:len(trat)]), list(p[len(trat):]))
        pl += Lp >= L; pd_ += Dp >= Dl
    r = dict(prueba=nombre, nivel_2024_26=L, cambio_frente_2016_22=Dl,
             p_nivel=(1 + pl) / (1 + NPERM), p_cambio=(1 + pd_) / (1 + NPERM), n_trat=len(trat), n_ctrl=len(ctrl))
    return r, d

res = {}
r, d_cad = prueba(S['cadena'], TRAT, CTRL, 'principal: cadena completa')
res['principal'] = r
regla = r['nivel_2024_26'] > 0 and r['cambio_frente_2016_22'] > 0 and r['p_nivel'] < 0.05 and r['p_cambio'] < 0.05
res['regla_publicacion'] = 'PASA' if regla else 'NO PASA'

# canales
it = [FIN.index(t) for t in TRAT]; ic = [FIN.index(t) for t in CTRL]
dI = D(S['infra'], it, ic); dS = D(S['soft'], it, ic)
dif = (dI - dS)[per_nuevo]
def bootstrap(x, bloque, n=2000, seed=1):
    rng = np.random.default_rng(seed); m = len(x); medias = []
    for _ in range(n):
        idx = []
        while len(idx) < m:
            a = rng.integers(0, m - bloque + 1); idx.extend(range(a, a + bloque))
        medias.append(np.mean(x[idx[:m]]))
    return [float(np.percentile(medias, 2.5)), float(np.percentile(medias, 97.5))]
res['canales'] = dict(D_infra_2024_26=float(np.mean(dI[per_nuevo])), D_soft_2024_26=float(np.mean(dS[per_nuevo])),
                      infra_menos_soft=float(np.mean(dif)), ic95_bloque10=bootstrap(dif, 10), ic95_bloque25=bootstrap(dif, 25),
                      D_infra_2016_22=float(np.mean(dI[per_viejo])), D_soft_2016_22=float(np.mean(dS[per_viejo])))
for k in ('infra', 'soft'):
    res['canal_' + k] = prueba(S[k], TRAT, CTRL, 'canal ' + k)[0]

# robustez
jap = ['MUFG', 'SMFG', 'MFG']
alt = ['BX', 'APO', 'KKR', 'ARES', 'CG', 'BN', 'OWL', 'BLK']
res['robustez'] = [prueba(S['cadena'], [t for t in TRAT if t not in jap], CTRL, 'sin japoneses')[0],
                   prueba(S['cadena'], [t for t in TRAT if t != 'BLK'], CTRL, 'sin BLK')[0],
                   prueba(S['cadena'], alt, CTRL, 'solo gestores alternativos')[0]]

# elasticidad descriptiva por periodos
E = pd.DataFrame(elas, index=fechas)
tramos = {'2016-2019': (E.index <= '2019-12-31'), '2020-2023': (E.index >= '2020-01-01') & (E.index <= '2023-12-31'),
          '2024-2026': (E.index >= '2024-01-01')}
res['elasticidad'] = {t: {k: round(float(E[k][m].mean()), 3) for k in E.columns} for t, m in tramos.items()}
res['ventanas'] = dict(total=len(fechas), periodo_2024_26=int(per_nuevo.sum()), periodo_2016_22=int(per_viejo.sum()),
                       primera=str(fechas[0].date()), ultima=str(fechas[-1].date()))
pd.DataFrame({'fecha': fechas, 'D_cadena': d_cad, 'D_infra': dI, 'D_soft': dS}).to_csv('serie_D_20261002.csv', index=False)
json.dump(res, open('capa_financiera_resultados.json', 'w'), indent=1)
print(json.dumps(res, indent=1))
