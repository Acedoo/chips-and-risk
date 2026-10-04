# Descarga de los rendimientos diarios del Tesoro de EE. UU. a 10 y 30 años. Uso en el Mac:
#   python3 descargar_tipos_20261002.py   -> guarda tipos_20261002.csv; súbemelo.
import time
import pandas as pd
import yfinance as yf
series = {}
for t in ["^TNX", "^TYX"]:
    for intento in range(4):
        try:
            d = yf.download(t, start="2015-11-01", auto_adjust=False, progress=False, threads=False)
            s = d["Close"]
            if hasattr(s, "columns"):
                s = s.iloc[:, 0]
            series[t] = s.dropna()
            break
        except Exception as e:
            print("reintento", t, e); time.sleep(5)
    print(t, "filas:", len(series.get(t, [])))
df = pd.DataFrame(series).sort_index(); df.index.name = "Date"
df.to_csv("tipos_20261002.csv")
print("HECHO:", df.shape, "| último valor 10 años:", round(float(df['^TNX'].dropna().iloc[-1]), 3))
