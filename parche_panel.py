#!/usr/bin/env python3
"""
parche_panel.py

Se corre en chips-and-risk, una sola vez. Convierte la señal F2 de estatica a
MEDIDA y deja el dato cargado para el indicador con escala.

QUE CAMBIA Y POR QUE. F2 dice "Large commitments sit off balance sheet" y esta
puesta a mano, citando al Financial Times y a Nikkei. La afirmacion es correcta
pero nadie puede comprobarla desde el panel, y tampoco puede apagarse si el dato
cambia. Ahora la decide la medicion propia: la señal se enciende cuando el
compromiso firmado y no reconocido SUPERA a la deuda declarada de las mismas
empresas. Ese corte no es un umbral calibrado, es la paridad: mas fuera que
dentro. Se dice asi en la propia señal.

El recuento de señales no cambia hoy, porque F2 ya estaba encendida. Lo que
cambia es que ahora puede apagarse.

TOCA TRES FICHEROS, cada uno en un sitio exacto:
  run.py          carga commitment.csv junto a los demas
  indicators.py   la regla commitment_over_reported
  config/signs.json  F2 pasa de "static" a esa regla, con su fuente

Hace copia de seguridad de los tres antes de tocarlos.

USO:
  python3 parche_panel.py
  python3 parche_panel.py --deshacer
"""
import argparse
import json
import shutil
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
FICHEROS = ["monitor/run.py", "monitor/indicators.py", "config/signs.json"]

ANCLA_RUN = '        "debt": pd.read_csv(ROOT / "debt.csv").fillna("").to_dict("records"),'
NUEVO_RUN = ANCLA_RUN + """
        "commitment": (pd.read_csv(ROOT / "commitment.csv").fillna("").to_dict("records")
                       if (ROOT / "commitment.csv").exists() else []),"""

ANCLA_IND = '        if kind == "rates_up":'
NUEVO_IND = '''        if kind == "commitment_over_reported":
            # Signed lease commitments not yet recognised as debt, against the
            # reported financial debt of the same companies, latest quarter.
            # The cut is parity, not a calibrated threshold: more off the
            # balance sheet than on it. Measured from the filings; if the
            # series is missing the sign stays off rather than defaulting on.
            rows = ind.get("commitment") or []
            if not rows:
                return False
            last = sorted(rows, key=lambda r: str(r.get("date", "")))[-1]
            try:
                rep = float(last["reported_usd_bn"])
                nyc = float(last["not_commenced_usd_bn"])
            except (KeyError, TypeError, ValueError):
                return False
            return rep > 0 and nyc > rep
''' + ANCLA_IND

F2_NUEVA = {
    "id": "F2",
    "text": "Large commitments sit off balance sheet",
    "rule": "commitment_over_reported",
    "source": ("Measured from 10-K and 10-Q filings: signed leases not yet "
               "commenced against reported financial debt, five companies. "
               "The sign is on while the unrecognised part is the larger of "
               "the two."),
    "text_es": "Hay grandes compromisos fuera de balance",
}


def deshacer():
    for f in FICHEROS:
        bak = RAIZ / (f + ".bak")
        if bak.exists():
            shutil.copy(bak, RAIZ / f)
            print("restaurado", f)
        else:
            print("sin copia de", f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--deshacer", action="store_true")
    a = ap.parse_args()
    if a.deshacer:
        return deshacer()

    for f in FICHEROS:
        p = RAIZ / f
        if not p.exists():
            print("NO ESTA:", f, "(¿estas en chips-and-risk?)")
            return
        shutil.copy(p, RAIZ / (f + ".bak"))

    # run.py
    p = RAIZ / "monitor/run.py"
    s = p.read_text()
    if '"commitment"' in s:
        print("run.py: ya estaba")
    elif ANCLA_RUN not in s:
        print("run.py: no encuentro la linea de debt.csv, no toco nada")
        return
    else:
        p.write_text(s.replace(ANCLA_RUN, NUEVO_RUN, 1))
        print("run.py: carga commitment.csv")

    # indicators.py
    p = RAIZ / "monitor/indicators.py"
    s = p.read_text()
    if "commitment_over_reported" in s:
        print("indicators.py: ya estaba")
    elif ANCLA_IND not in s:
        print("indicators.py: no encuentro la regla rates_up, no toco nada")
        return
    else:
        p.write_text(s.replace(ANCLA_IND, NUEVO_IND, 1))
        print("indicators.py: regla commitment_over_reported")

    # signs.json
    p = RAIZ / "config/signs.json"
    d = json.loads(p.read_text())
    hecho = False
    for i, s_ in enumerate(d.get("frenzy", [])):
        if s_.get("id") == "F2":
            d["frenzy"][i] = F2_NUEVA
            hecho = True
    if not hecho:
        print("signs.json: no encuentro F2, no toco nada")
        return
    p.write_text(json.dumps(d, indent=1, ensure_ascii=False))
    print("signs.json: F2 pasa de estatica a medida")

    print("\nAhora: copia commitment.csv a esta carpeta y corre el panel.")
    print("Lo que hay que mirar: F2 sigue encendida (el compromiso supera a la")
    print("deuda declarada), y el recuento de señales de frenesi no cambia.")
    print("Si cambia, algo se ha roto y hay que mirarlo antes de publicar.")


if __name__ == "__main__":
    main()
