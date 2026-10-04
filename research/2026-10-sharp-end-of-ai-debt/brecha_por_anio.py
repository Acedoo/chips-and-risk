"""Descriptivo para la nota: distancia financiadores - control en el 5 % peor de días de la cadena de CADA año."""
import json
import pandas as pd
exec(open('quien_cae.py').read().split("res = {}")[0])
filas = []
for y in range(2016, 2027):
    c = cad[str(y)].dropna()
    if y == 2026: c = c[:'2026-10-01']
    dias = c[c <= c.quantile(0.05)].index
    A = ab.loc[dias]
    filas.append(dict(year=y, n=len(dias), cadena=round(float(c.loc[dias].mean() * 100), 2),
                      gap=round(float((A[TRAT].mean(axis=1) - A[CTRL].mean(axis=1)).mean() * 100), 2)))
df = pd.DataFrame(filas); print(df.to_string(index=False))
df.to_csv('brecha_por_anio.csv', index=False)
