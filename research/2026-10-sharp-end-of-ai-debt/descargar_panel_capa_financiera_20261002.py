# Descarga para la capa financiera de la cadena de la IA (pre-registro PREREGISTRO_CAPA_FINANCIERA.md).
# Uso en el Mac:  python3 -m pip install --user yfinance pandas   y luego   python3 descargar_panel_capa_financiera_20261002.py
# Guarda panel_capa_financiera_20261002.csv (cierres ajustados, de 2015-12-01 a hoy). Subelo tal cual.
import time
import pandas as pd
import yfinance as yf
TICKERS = ['AAPL', 'ACGL', 'ACN', 'ADBE', 'ADI', 'ADSK', 'AEE', 'AEP', 'AES', 'AKAM', 'AMAT', 'AMD', 'AME', 'AMZN', 'ANET', 'APH', 'ATO', 'AVGO', 'CDNS', 'CDW', 'CEG', 'CMI', 'CMS', 'CNP', 'CRM', 'CSCO', 'CTSH', 'D', 'DELL', 'DLR', 'DOV', 'DUK', 'ED', 'EIX', 'EMR', 'EPAM', 'EQIX', 'ES', 'ETN', 'ETR', 'EXC', 'FE', 'FICO', 'FIS', 'FSLR', 'FTNT', 'GDDY', 'GEV', 'GLW', 'GNRC', 'GOOGL', 'GPN', 'GRMN', 'HPE', 'HPQ', 'IBM', 'INTC', 'INTU', 'IR', 'IT', 'ITW', 'JCI', 'KEYS', 'KLAC', 'LNT', 'LRCX', 'MA', 'MCHP', 'META', 'MPWR', 'MSFT', 'MSI', 'MU', 'NEE', 'NI', 'NOW', 'NRG', 'NTAP', 'NVDA', 'NXPI', 'ON', 'ORCL', 'PANW', 'PH', 'PNW', 'PPL', 'PTC', 'PWR', 'PYPL', 'QCOM', 'ROK', 'ROP', 'SMCI', 'SNPS', 'SO', 'SRE', 'STX', 'SWKS', 'TDY', 'TEL', 'TER', 'TRMB', 'TXN', 'TYL', 'V', 'VRSN', 'VST', 'WDC', 'WEC', 'XEL', 'ZBRA', 'BX', 'APO', 'KKR', 'ARES', 'CG', 'BN', 'OWL', 'BLK', 'JPM', 'MS', 'GS', 'C', 'BAC', 'MUFG', 'SMFG', 'MFG', 'MET', 'PRU', 'USB', 'PNC', 'TFC', 'FITB', 'KEY', 'RF', 'HBAN', 'CFG', 'TRV', 'CB', 'ALL', 'PGR', 'HIG', 'CINF', 'L', 'CME', 'ICE', 'NDAQ', 'TROW', 'BEN', 'IVZ', 'AXP', 'COF', 'SYF', 'SPY']
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
panel.to_csv("panel_capa_financiera_20261002.csv")
faltan = [t for t in TICKERS if t not in series]
print("HECHO:", panel.shape, "desde", panel.index[0], "hasta", panel.index[-1])
print("sin datos:", faltan)
