"""Pre-registro PREREGISTRO_TELECOS_INDUSTRIAS.md. Paso 1 calibración 2016-2026; paso 2 telecos 1994-2004 solo si pasa."""
import io, json
import numpy as np
import pandas as pd
txt = open('french/49_Industry_Portfolios_Daily.csv').read().replace('\r', '')
ini = txt.index('Average Value Weighted Returns -- Daily'); fin = txt.index('Average Equal Weighted Returns -- Daily')
bloque = txt[ini:fin].split('\n', 1)[1].strip()
ind = pd.read_csv(io.StringIO(bloque), index_col=0)
ind.index = pd.to_datetime(ind.index.astype(str).str.strip(), format='%Y%m%d'); ind.columns = ind.columns.str.strip()
ind = ind.replace(-99.99, np.nan) / 100
ft = open('french/F-F_Research_Data_Factors_daily.csv').read().replace('\r', '')
a = ft.index(',Mkt-RF'); b = ft.index('Copyright')
fac = pd.read_csv(io.StringIO(ft[a:b].strip()), index_col=0)
fac.index = pd.to_datetime(fac.index.astype(str).str.strip(), format='%Y%m%d'); fac = fac / 100
CAD = ['Telcm', 'Chips', 'Hardw', 'Softw', 'ElcEq']; FIN = ['Banks', 'Fin', 'Insur']
RESTO = [c for c in ind.columns if c not in CAD + FIN + ['RlEst', 'Other']]
VENT, PASO = 250, 10

def serie(desde, hasta, residuos):
    X = ind.loc[desde:hasta]; m = fac.loc[X.index, 'Mkt-RF']
    out = []
    for s in range(0, len(X) - VENT + 1, PASO):
        sub = X.iloc[s:s + VENT]; ok = [c for c in sub.columns if sub[c].notna().all()]
        Y = sub[ok]
        if residuos:
            Z = np.column_stack([np.ones(VENT), m.iloc[s:s + VENT].values])
            B, *_ = np.linalg.lstsq(Z, Y.values, rcond=None); Y = pd.DataFrame(Y.values - Z @ B, columns=ok)
        C = Y.corr().abs()
        cad = [c for c in CAD if c in ok]; res = [c for c in RESTO if c in ok]
        out.append((sub.index[-1], float(np.mean([C.loc[f, cad].mean() - C.loc[f, res].mean() for f in FIN]))))
    return pd.Series(dict(out))

def boot_dif(s, a, b, bloque=10, n=4000, seed=7):
    rng = np.random.default_rng(seed)
    def rem(x):
        m = len(x); idx = []
        while len(idx) < m:
            k = rng.integers(0, max(1, m - bloque + 1)); idx.extend(range(k, min(k + bloque, m)))
        return x[idx[:m]].mean()
    xa, xb = s[a].values, s[b].values
    d = [rem(xa) - rem(xb) for _ in range(n)]
    return float(xa.mean() - xb.mean()), [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))]

res = {}
for nombre, residuos in (('residuos_mercado', True), ('bruta', False)):
    s = serie('2015-01-01', '2026-08-31', residuos)
    nuevo = s.index >= '2024-01-01'; viejo = s.index <= '2022-12-31'
    dif, ic = boot_dif(s, nuevo, viejo)
    res['calibracion_' + nombre] = dict(nuevo=float(s[nuevo].mean()), viejo=float(s[viejo].mean()), diferencia=dif, ic95=ic,
                                       por_anio={str(k.year): round(float(v), 4) for k, v in s.resample('YE').mean().items()})
cal = res['calibracion_residuos_mercado']
res['paso1'] = 'PASA' if cal['ic95'][0] > 0 else 'NO PASA: se para'
print(json.dumps(res, indent=1), flush=True)
if res['paso1'] == 'PASA':
    for nombre, residuos in (('residuos_mercado', True), ('bruta', False)):
        s = serie('1993-01-01', '2004-12-31', residuos)
        auge = (s.index >= '1998-01-01') & (s.index <= '2000-12-31'); antes = (s.index >= '1994-01-01') & (s.index <= '1996-12-31')
        crash = (s.index >= '2001-01-01') & (s.index <= '2002-12-31')
        dif, ic = boot_dif(s, auge, antes)
        res['telecos_' + nombre] = dict(antes_1994_96=float(s[antes].mean()), auge_1998_2000=float(s[auge].mean()),
                                        estallido_2001_02=float(s[crash].mean()), auge_menos_antes=dif, ic95=ic,
                                        por_anio={str(k.year): round(float(v), 4) for k, v in s.resample('YE').mean().items()})
    t = res['telecos_residuos_mercado']
    res['paso2'] = 'PRECEDENTE' if t['ic95'][0] > 0 else 'SIN PRECEDENTE CLARO'
    print(json.dumps({k: v for k, v in res.items() if k.startswith('telecos') or k == 'paso2'}, indent=1))
json.dump(res, open('analisis_french_resultados.json', 'w'), indent=1)
