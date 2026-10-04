"""Paso 2 pre-registrado: contrapartes exclusivas de OpenAI frente a la cadena en 5 noticias de duda sobre OpenAI."""
import json
import numpy as np
import pandas as pd
main = pd.read_csv('../panel_capa_financiera_20261002.csv', index_col=0, parse_dates=True).sort_index()
p2 = pd.read_csv('panel_paso2_20261002.csv', index_col=0, parse_dates=True).sort_index()
c2 = pd.read_csv('../panel_capa2_20261002.csv', index_col=0, parse_dates=True).sort_index()
de = json.load(open('../definicion_cadena_20261002.json'))
CAD = de['semis'] + de['equipo'] + de['utilities'] + de['software']
TRAT = ['ORCL', 'CRWV', 'AMD', 'CBRS']
us = pd.concat([main[CAD], p2[['CRWV', 'CBRS', 'GOOGL']].reindex(main.index)], axis=1)
R = us.pct_change(fill_method=None)
cesta = R[[c for c in CAD if c not in TRAT]].mean(axis=1)            # cadena sin las tratadas
EXC = R.sub(cesta, axis=0)                                            # exceso sobre la cadena
EVENTOS = {'E1 backstop': ['2025-11-05', '2025-11-06'], 'E2 code red': ['2025-12-01', '2025-12-02'],
           'E3 Nvidia congela': ['2026-02-02'], 'E4 objetivos incumplidos': ['2026-04-28'], 'E5 aplaza la OPV': ['2026-06-26']}
def ventana(dias, cols):
    X = EXC.loc[pd.to_datetime(dias), cols].sum(min_count=1)
    return X
res = {'por_evento': {}}
vals = []
for k, dias in EVENTOS.items():
    x = ventana(dias, TRAT); g = ventana(dias, ['GOOGL'])
    m = float(x.dropna().mean() * 100); vals.append(m)
    res['por_evento'][k] = dict(dias=dias, media_tratadas_pp=round(m, 2), por_empresa={c: (round(float(v) * 100, 2) if pd.notna(v) else None) for c, v in x.items()},
                                cadena_pp=round(float(cesta.loc[pd.to_datetime(dias)].sum() * 100), 2), GOOGL_pp=round(float(g.iloc[0] * 100), 2))
obs = float(np.mean(vals)); res['exceso_medio_eventos_pp'] = round(obs, 2)
# días malos de la IA 2024-2026 (peor 5 % de la cadena completa), sin eventos, desde que cotiza CRWV
cad_full = R[CAD].mean(axis=1)
c = cad_full['2024-01-01':'2026-10-01'].dropna(); malos = c[c <= c.quantile(0.05)].index
ev_all = set(pd.to_datetime(sum(EVENTOS.values(), [])))
idx = list(R.index)
malos = [d for d in malos if d >= pd.Timestamp('2025-04-01') and d not in ev_all and idx.index(d) + 1 < len(idx)]
def exc_dia(d, dos):
    ds = [d] + ([idx[idx.index(d) + 1]] if dos else [])
    return float(EXC.loc[ds, TRAT].sum(min_count=1).dropna().mean() * 100)
res['dias_malos_disponibles'] = len(malos)
res['exceso_medio_en_dias_malos_pp'] = round(float(np.mean([exc_dia(d, False) for d in malos])), 2)
rng = np.random.default_rng(20261002); null = []
for _ in range(2000):
    s = rng.choice(len(malos), size=5, replace=False)
    null.append(np.mean([exc_dia(malos[j], k < 2) for k, j in enumerate(s)]))
null = np.array(null)
res['p'] = round(float((null <= obs).mean()), 4)
res['nulo_percentiles_pp'] = {q: round(float(np.percentile(null, q)), 2) for q in (5, 50, 95)}
res['regla'] = 'PASA: el mercado lee los contratos de OpenAI' if (obs <= -1.5 and res['p'] < 0.05) else 'NO PASA: todo cotiza como un bloque de la IA en estos datos'
# SoftBank en Tokio, descriptivo
jp = pd.concat([p2['9984.T'], c2['1306.T']], axis=1).dropna(); Rj = jp.pct_change()
sb = {}
for k, dias in EVENTOS.items():
    t = Rj.index[Rj.index.searchsorted(pd.Timestamp(dias[0]))]
    sb[k] = dict(sesion=str(t.date()), softbank_menos_topix_pp=round(float((Rj.loc[t, '9984.T'] - Rj.loc[t, '1306.T']) * 100), 2))
res['softbank_tokio'] = sb
json.dump(res, open('paso2_resultados.json', 'w'), indent=1, ensure_ascii=False)
print(json.dumps(res, indent=1, ensure_ascii=False))
