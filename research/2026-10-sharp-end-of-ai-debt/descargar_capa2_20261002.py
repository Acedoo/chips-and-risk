# Descarga para la adenda 8 (BDC de EE. UU. y bancos japoneses en Tokio). Uso en el Mac:
#   python3 -m pip install yfinance pandas    (si no lo tienes ya)
#   python3 descargar_capa2_20261002.py      -> guarda panel_capa2_20261002.csv; subemelo.
import time
import pandas as pd
import yfinance as yf
TICKERS = ["ARCC", "OBDC", "BXSL", "FSK", "GBDC", "MAIN", "HTGC", "PSEC", "TSLX", "OCSL", "GSBD", "NMFC", "CGBD", "TCPC", "BCSF", "MFIC",
           "8306.T", "8316.T", "8411.T", "8331.T", "8354.T", "7186.T", "8418.T", "8385.T", "8359.T", "8377.T", "8366.T", "8341.T",
           "8334.T", "7167.T", "8524.T", "1306.T"]
series = {}
for i in range(0, len(TICKERS), 5):
    lote = TICKERS[i:i+5]
    for intento in range(4):
        try:
            d = yf.download(lote, start="2015-12-01", auto_adjust=True, progress=False, threads=False, group_by="ticker")
            for t in lote:
                try:
                    s = d[t]["Close"] if len(lote) > 1 else d["Close"]
                    s = s.dropna()
                    if len(s) > 0:
                        series[t] = s
                except Exception:
                    pass
            break
        except Exception as e:
            print("reintento", lote, e)
            time.sleep(5)
    print("lote", i // 5 + 1, "de", (len(TICKERS) + 4) // 5, "valores con datos:", len(series), flush=True)
    time.sleep(1)
panel = pd.DataFrame(series).sort_index()
panel.index.name = "Date"
panel.to_csv("panel_capa2_20261002.csv")
print("HECHO:", panel.shape, "desde", panel.index[0], "hasta", panel.index[-1])
print("sin datos:", [t for t in TICKERS if t not in series])
