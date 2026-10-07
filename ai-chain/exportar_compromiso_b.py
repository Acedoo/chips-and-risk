#!/usr/bin/env python3
"""
exportar_compromiso_b.py

Igual que exportar_compromiso.py, con el arrastre que le faltaba.

EL PROBLEMA. Las empresas no presentan sus informes el mismo dia, asi que en un
trimestre dado puede faltar alguna. La primera version contaba solo las que
traian dato, y el agregado iba de cuatro empresas a cinco y volvia a cuatro:
el total subia y bajaba por quien habia presentado, no porque cambiase el
compromiso. El ultimo trimestre salia con 356,7 y 830,5 en vez de 381,5 y
871,2, que es lo que dice el texto tomando el ultimo dato de cada empresa.

EL ARREGLO. Se arrastra el ultimo dato conocido de cada empresa hasta que
publique otro, que es lo que hace cualquier serie trimestral con informes
desfasados. La fila guarda dos cuentas: cuantas empresas aporta el trimestre
(companies) y cuantas traen dato FRESCO (companies_fresh). Si una empresa
lleva varios trimestres sin publicar, se ve ahi.

USO, en ai-chain:
  python3 exportar_compromiso_b.py --series zona_roja_v4_series.csv
  cp commitment.csv ../chips-and-risk/
"""
import argparse

import pandas as pd

FUENTE = ("Measured from 10-K and 10-Q filings; last reported figure per "
          "company carried forward until it files again")
FUENTE_ES = ("Medido sobre los informes 10-K y 10-Q; el ultimo dato de cada "
             "empresa se arrastra hasta que vuelve a presentar")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--series", default="zona_roja_v4_series.csv")
    ap.add_argument("--salida", default="commitment.csv")
    ap.add_argument("--desde", default="2023Q1")
    a = ap.parse_args()

    d = pd.read_csv(a.series)
    d = d[["empresa", "trimestre", "deuda_declarada", "fuera_balance"]].copy()
    d = d[d.trimestre >= a.desde]

    # un dato solo cuenta desde que la empresa declara la partida
    d = d[d.fuera_balance > 0]
    if d.empty:
        print("sin trimestres con la partida")
        return

    rejilla = pd.period_range(min(d.trimestre), max(d.trimestre), freq="Q").astype(str)
    anchos = {}
    for col in ("deuda_declarada", "fuera_balance"):
        w = d.pivot(index="trimestre", columns="empresa", values=col).reindex(rejilla)
        anchos[col] = w
    fresco = anchos["fuera_balance"].notna()
    for col in anchos:
        anchos[col] = anchos[col].ffill()

    g = pd.DataFrame({
        "quarter": rejilla,
        "companies": anchos["fuera_balance"].notna().sum(axis=1).values,
        "companies_fresh": fresco.sum(axis=1).values,
        "reported_usd_bn": (anchos["deuda_declarada"].sum(axis=1) / 1000).round(1).values,
        "not_commenced_usd_bn": (anchos["fuera_balance"].sum(axis=1) / 1000).round(1).values,
    })
    g["date"] = pd.PeriodIndex(g.quarter, freq="Q").to_timestamp(how="end").date
    g["committed_usd_bn"] = (g.reported_usd_bn + g.not_commenced_usd_bn).round(1)
    g["on_balance_share"] = (100 * g.reported_usd_bn / g.committed_usd_bn).round(1)
    g["source"] = FUENTE
    g["source_es"] = FUENTE_ES

    cols = ["date", "quarter", "companies", "companies_fresh", "reported_usd_bn",
            "not_commenced_usd_bn", "committed_usd_bn", "on_balance_share",
            "source", "source_es"]
    g[cols].to_csv(a.salida, index=False)

    print(f"{len(g)} trimestres -> {a.salida}\n")
    print(f"{'trimestre':<10}{'empresas':>9}{'frescas':>9}{'declarado':>11}"
          f"{'sin comenzar':>14}{'comprometido':>14}{'% en balance':>14}")
    for _, r in g.tail(8).iterrows():
        print(f"{r['quarter']:<10}{r['companies']:>9}{r['companies_fresh']:>9}"
              f"{r['reported_usd_bn']:>11,.1f}{r['not_commenced_usd_bn']:>14,.1f}"
              f"{r['committed_usd_bn']:>14,.1f}{r['on_balance_share']:>14.1f}")
    print("\nimportes en miles de millones de dolares")
    print("El ultimo trimestre debe dar 381,5 y 871,2, que es lo que dice el texto.")


if __name__ == "__main__":
    main()
