#!/usr/bin/env python3
"""
parche_panel_kpi.py

Segunda parte: añade el indicador con escala del credito comprometido, y
arregla un problema de la serie que se vio al exportarla.

EL INDICADOR. Mide que parte del credito comprometido de la cadena esta
reconocida en el balance, en por ciento. Hoy 30. La escala va de 0 a 100 y
tiene una sola zona marcada, la paridad en 50: por encima, la mayor parte del
compromiso esta reconocida; por debajo, no. La paridad no es un umbral
calibrado y la nota de escala lo dice; no hay historia con la que calibrar
otra cosa, y ponerla a ojo seria inventarsela.

Va con la flecha hacia abajo como lo malo: cuanto menos enseña el balance, mas
credito hay que no cuenta ninguna medida agregada.

EL ARREGLO DE LA SERIE. Las empresas no presentan informes el mismo dia, asi
que en un trimestre dado puede faltar alguna: la serie exportada va de 4
empresas a 5 y vuelve a 4, y el total sube y baja por eso y no porque cambie
el compromiso. Se arrastra el ultimo dato conocido de cada empresa hasta que
publique otro, que es lo que hace cualquier serie trimestral con informes
desfasados, y la fila guarda cuantas empresas traen dato fresco.

TOCA DOS FICHEROS:
  monitor/kpis.py            el indicador
  exportar_compromiso.py     en ai-chain, el arrastre (se parchea aparte)

USO, en chips-and-risk:
  python3 parche_panel_kpi.py
  python3 parche_panel_kpi.py --deshacer
"""
import argparse
import shutil
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
OBJ = RAIZ / "monitor/kpis.py"

ANCLA = "    # 12. 10-year yield"

NUEVO = '''    # 11b. credit committed but not recognised
    com = sorted((ind.get("commitment") or []), key=lambda r: str(r.get("date", "")))
    if com:
        last = com[-1]
        try:
            share = float(last["on_balance_share"])
            rep = float(last["reported_usd_bn"])
            nyc = float(last["not_commenced_usd_bn"])
        except (KeyError, TypeError, ValueError):
            share = None
        if share is not None:
            hist = pd.Series({pd.Timestamp(r["date"]): float(r["on_balance_share"])
                              for r in com if r.get("on_balance_share") not in ("", None)}).sort_index()
            zone = "most of it recognised" if share >= 50 else "most of it unrecognised"
            rows.append(dict(zone=zone, label="Committed credit recognised on the balance sheet",
                             unit="%", value=share, fmt="{:.0f}%", dfmt="{:.0f} pts", bad="down",
                             kind="range", lo=0, hi=100,
                             zones=[(50, 100, PALE, "more recognised than not")],
                             reading=(f"${rep + nyc:,.0f}bn committed, of which ${nyc:,.0f}bn is signed "
                                      f"and not yet debt: the balance sheet shows {share:.0f}% of it."),
                             scale_note="Grey band: more than half recognised. The 50% line is parity, not a calibrated threshold",
                             changes=_changes_from_series(hist)))

''' + ANCLA


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--deshacer", action="store_true")
    a = ap.parse_args()

    bak = RAIZ / "monitor/kpis.py.bak2"
    if a.deshacer:
        if bak.exists():
            shutil.copy(bak, OBJ)
            print("restaurado monitor/kpis.py")
        else:
            print("sin copia")
        return

    if not OBJ.exists():
        print("no encuentro monitor/kpis.py, ¿estas en chips-and-risk?")
        return
    s = OBJ.read_text()
    if "Committed credit recognised" in s:
        print("ya estaba")
        return
    if ANCLA not in s:
        print("no encuentro el bloque del bono a 10 anos, no toco nada")
        return
    shutil.copy(OBJ, bak)
    OBJ.write_text(s.replace(ANCLA, NUEVO, 1))
    print("monitor/kpis.py: indicador del credito comprometido añadido")
    print("\nCorre el panel y mira: el indicador nuevo debe decir 30% con la")
    print("lectura de los importes, y los demas indicadores no deben moverse.")


if __name__ == "__main__":
    main()
