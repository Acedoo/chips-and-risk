#!/usr/bin/env python3
"""
indice_precios.py

Cierra los dos pendientes declarados en las limitaciones del texto: deflactar el
indice de precios por IPC y ponderarlo por capitalizacion, en vez de la media
simple nominal.

Devuelve las CUATRO variantes para que se vea cuanto cambia la cifra y cual se
decide usar:
  nominal, media simple        (la del texto actual: 62,6%)
  real, media simple
  nominal, ponderado
  real, ponderado

EL PROBLEMA DE LOS DESDOBLAMIENTOS, Y COMO SE RESUELVE AQUI. Las acciones en
circulacion que publica la SEC son las declaradas en cada momento, mientras que
los precios de la serie estan ajustados por desdoblamiento. Multiplicar un
precio ajustado de 2015 por las acciones declaradas en 2015 da una
capitalizacion equivocada en cuanto haya habido un desdoblamiento por medio
(Amazon hizo uno de 20 a 1 en 2022). Para no mezclar las dos bases, los pesos
se fijan en el ULTIMO trimestre y se mantienen constantes hacia atras: un
indice de pesos fijos. Es una eleccion, no la unica posible, y se dice.

Un indice de pesos fijos responde a "cuanto se han revalorizado estas empresas,
pesando cada una por lo que vale hoy". Un indice de pesos variables responderia
a otra pregunta y necesitaria precios sin ajustar, que no tenemos.

IPC: serie CPIAUCSL de FRED, mensual, tomada a cierre de trimestre.

USO:
  python3 indice_precios.py --series zona_roja_v4_series.csv
"""
import argparse
import io
import json
import time
import urllib.request

import numpy as np
import pandas as pd

AGENTE = {"User-Agent": "Alberto Acedo acedo@biomemakers.com"}
UMBRAL = 26.56       # % log a tres anos, percentil 66,7 del articulo
TRIMESTRES = 12

ACCIONES = [
    ("dei", "EntityCommonStockSharesOutstanding"),
    ("us-gaap", "CommonStockSharesOutstanding"),
    ("us-gaap", "CommonStockSharesIssued"),
    ("us-gaap", "WeightedAverageNumberOfDilutedSharesOutstanding"),
]


def baja(url, reintentos=3):
    for i in range(reintentos):
        try:
            return urllib.request.urlopen(
                urllib.request.Request(url, headers=AGENTE), timeout=90).read()
        except Exception:
            if i == reintentos - 1:
                raise
            time.sleep(2)


def ipc():
    crudo = baja("https://fred.stlouisfed.org/graph/fredgraph.csv?id=CPIAUCSL")
    p = pd.read_csv(io.StringIO(crudo.decode("utf-8", "ignore")))
    fecha = p.columns[0]
    p[fecha] = pd.to_datetime(p[fecha])
    p["ipc"] = pd.to_numeric(p["CPIAUCSL"], errors="coerce")
    p = p.dropna(subset=["ipc"])
    p["trimestre"] = p[fecha].dt.to_period("Q").astype(str)
    return p.sort_values(fecha).groupby("trimestre", as_index=False)["ipc"].last()


def cik_por_ticker():
    d = json.loads(baja("https://www.sec.gov/files/company_tickers.json"))
    return {v["ticker"].upper(): f"{v['cik_str']:010d}" for v in d.values()}


def acciones_ultimas(cik):
    """Acciones en circulacion mas recientes declaradas, en millones."""
    facts = json.loads(baja(
        f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"))
    for tax, etiqueta in ACCIONES:
        info = facts.get("facts", {}).get(tax, {}).get(etiqueta)
        if not info:
            continue
        filas = []
        for unidad in ("shares",):
            for u in info.get("units", {}).get(unidad, []):
                filas.append({"fin": u.get("end", ""), "n": u["val"] / 1e6,
                              "filed": u.get("filed", "")})
        if not filas:
            continue
        f = pd.DataFrame(filas).sort_values(["filed", "fin"])
        return float(f.n.iloc[-1]), f"{tax}:{etiqueta}", f.fin.iloc[-1]
    return None, "(no declara)", ""


def crecimiento3(serie):
    return 100.0 * (np.log(serie) - np.log(serie.shift(TRIMESTRES)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--series", default="zona_roja_v4_series.csv")
    ap.add_argument("--salida", default="indice_precios.csv")
    a = ap.parse_args()

    d = pd.read_csv(a.series)[["empresa", "trimestre", "precio"]].dropna()
    empresas = sorted(d.empresa.unique())

    ciks = cik_por_ticker()
    pesos, detalle = {}, []
    for e in empresas:
        if e not in ciks:
            continue
        n, etiqueta, fin = acciones_ultimas(ciks[e])
        if n is None:
            continue
        ult = d[d.empresa == e].sort_values("trimestre").iloc[-1]
        cap = n * ult.precio / 1000.0        # miles de millones de dolares
        pesos[e] = cap
        detalle.append((e, n, ult.precio, cap, etiqueta, fin))

    total = sum(pesos.values())
    print("PESOS FIJOS, capitalizacion del ultimo trimestre con precio")
    print(f"{'empresa':<9}{'acciones (M)':>14}{'precio':>10}{'cap (MM$)':>12}"
          f"{'peso':>8}  etiqueta")
    for e, n, pr, cap, etiqueta, fin in detalle:
        print(f"{e:<9}{n:>14,.0f}{pr:>10,.2f}{cap:>12,.0f}"
              f"{cap / total:>8.3f}  {etiqueta} ({fin})")
    print(f"{'TOTAL':<9}{'':>14}{'':>10}{total:>12,.0f}{1.0:>8.3f}")

    # panel ancho de precios
    w = d.pivot(index="trimestre", columns="empresa", values="precio").sort_index()
    cpi = ipc().set_index("trimestre")["ipc"]
    w = w.join(cpi, how="left")
    sin_ipc = w["ipc"].isna().sum()
    if sin_ipc:
        print(f"\ntrimestres sin IPC: {sin_ipc} (se caen de las variantes reales)")

    cols = [c for c in w.columns if c != "ipc"]
    con_peso = [c for c in cols if c in pesos]

    res = pd.DataFrame(index=w.index)
    res["simple_nominal"] = np.exp(np.log(w[cols]).mean(axis=1))
    res["simple_real"] = res["simple_nominal"] / w["ipc"]
    pw = pd.Series({c: pesos[c] / sum(pesos[c] for c in con_peso)
                    for c in con_peso})
    # los pesos se renormalizan entre las empresas con precio en cada
    # trimestre: CoreWeave no cotiza antes de 2025 y exigirlas todas dejaria
    # la serie entera vacia. La composicion cambia cuando entra una empresa,
    # y eso se dice en el texto.
    lp = np.log(w[con_peso])
    presente = lp.notna()
    pesos_fila = presente.mul(pw, axis=1)
    pesos_fila = pesos_fila.div(pesos_fila.sum(axis=1), axis=0)
    lw = (lp.fillna(0.0) * pesos_fila).sum(axis=1)
    lw[presente.sum(axis=1) == 0] = np.nan
    res["pond_nominal"] = np.exp(lw)
    res["n_en_indice"] = presente.sum(axis=1)
    res["pond_real"] = res["pond_nominal"] / w["ipc"]

    for c in list(res.columns):
        res[f"g3_{c}"] = crecimiento3(res[c])
    res.to_csv(a.salida)

    u = res.dropna(subset=["g3_simple_nominal"]).iloc[-1]
    print(f"\nPATA DE PRECIOS a {res.index[-1]}, crecimiento log a tres años")
    print(f"umbral del articulo: {UMBRAL}%\n")
    print(f"{'variante':<28}{'g3 (%)':>10}{'vs umbral':>12}")
    nombres = {"simple_nominal": "media simple, nominal",
               "simple_real": "media simple, real (IPC)",
               "pond_nominal": "ponderado, nominal",
               "pond_real": "ponderado, real (IPC)"}
    for k, nombre in nombres.items():
        v = u[f"g3_{k}"]
        if pd.isna(v):
            print(f"{nombre:<28}{'.':>10}{'':>12}")
            continue
        print(f"{nombre:<28}{v:>10.1f}{'por encima' if v >= UMBRAL else 'por debajo':>12}")

    print("\nLa variante que el texto debe citar es la ponderada y real, y las")
    print("otras tres quedan como comprobacion de robustez: si las cuatro estan")
    print("del mismo lado del umbral, la eleccion de indice no sostiene nada.")
    print(f"\n-> {a.salida}")


if __name__ == "__main__":
    main()
