# Descarga para el paso 2 (contrapartes exclusivas de OpenAI que faltan en el panel). Uso en el Mac:
#   python3 descargar_paso2_20261002.py   -> guarda panel_paso2_20261002.csv; subemelo.
import time
import pandas as pd
import yfinance as yf
TICKERS = ["CRWV", "CBRS", "9984.T", "ORCL", "AMD", "GOOGL"]
series = {}
for t in TICKERS:
    for intento in range(4):
        try:
            d = yf.download(t, start="2023-12-01", auto_adjust=True, progress=False, threads=False)
            s = d["Close"]
            if hasattr(s, "columns"):
                s = s.iloc[:, 0]
            s = s.dropna()
            if len(s) > 0:
                series[t] = s
            break
        except Exception as e:
            print("reintento", t, e)
            time.sleep(5)
    print(t, "filas:", len(series.get(t, [])), flush=True)
    time.sleep(1)
panel = pd.DataFrame(series).sort_index()
panel.index.name = "Date"
panel.to_csv("panel_paso2_20261002.csv")
print("HECHO:", panel.shape, "sin datos:", [t for t in TICKERS if t not in series])
