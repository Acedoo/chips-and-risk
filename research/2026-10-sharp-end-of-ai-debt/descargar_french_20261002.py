# Descarga las carteras diarias de 49 industrias y los factores diarios de Fama-French (biblioteca de Kenneth French).
# Uso en el Mac:  python3 descargar_french_20261002.py   -> deja dos ficheros .zip en la carpeta. Subelos tal cual.
import urllib.request
base = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"
for nombre in ["49_Industry_Portfolios_daily_CSV.zip", "F-F_Research_Data_Factors_daily_CSV.zip"]:
    print("descargando", nombre, flush=True)
    peticion = urllib.request.Request(base + nombre, headers={"User-Agent": "Mozilla/5.0"})
    datos = urllib.request.urlopen(peticion, timeout=120).read()
    open(nombre, "wb").write(datos)
    print("  guardado,", len(datos), "bytes")
print("HECHO. Subeme los dos .zip")
