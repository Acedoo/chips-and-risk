# The Sharp End of AI Debt

Companion material to the working paper *The Sharp End of AI Debt: market evidence on where the
off-balance-sheet risk of the AI build-out sits, 2016-2026* (Alberto Acedo, Biome Makers Inc., October 2026), in `paper/`.

It follows two earlier pieces in this repository's `ai-chain` folder: the August paper *Chips and Megawatts*
(SSRN 7307362), which measured from prices where structural weight in the AI supply chain had moved, and the September
note on off-balance-sheet guarantees (`NOTA_GARANTIAS.pdf`), which read the filings.

## Main results

- In the 35 sharpest one-day sell-offs of a 46-company AI supply-chain basket since January 2024, 18 listed lenders to and
  investors in AI infrastructure did 0.54 percentage points a day worse than 24 other financial stocks, beyond market
  beta (permutation p = 0.005). In the 92 comparable sell-offs of 2016-2023 the gap was +0.04 (p = 0.75).
- The gap is concentrated in Blue Owl, Ares, Carlyle and Japan's megabanks as traded in New York; Blackstone, KKR and the
  life insurers behave like the rest of finance. The listed loan vehicles (BDCs) fell as much before 2024 as after.
- A correlation-specificity measure over all days dates an AI-specific link to 2023-2024, net of the market and the
  financial sector; mostly through software since 2020 and through chips and power since 2024.
- At industry level (Kenneth French portfolios), financial industries tied themselves to the technology chain early in
  the telecoms boom and stayed tied through the 2000-2002 crash.

## Files

| file | content |
|---|---|
| `paper/` | the paper (PDF and HTML source), its five figures and `mkfig_oct.py`, which draws them |
| `PREREGISTRO_*.md` | the dated pre-registrations, written before each analysis was run (working documents, in Spanish) |
| `REGISTRO_CADENA_IA.md` | the dated log of every step, including checks that weakened the results (Spanish) |
| `RESULTADO_*.md`, `BARRIDO_BIBLIOGRAFICO_20261002.md` | result logs and the literature sweep (Spanish) |
| `grupos_capa_financiera.txt`, `definicion_cadena_20261002.json` | the groups and the chain definition, fixed before results |
| `descargar_*.py` | download scripts for all input data |
| `capa_financiera.py` | correlation-specificity measure, permutation inference, channels, robustness, elasticity |
| `capa_financiera_factores.py`, `canales_residuos_B.py` | the same net of the market and of the financial sector |
| `quien_cae.py`, `brecha_por_anio.py` | the sell-off test (main result), the names and the year-by-year gap |
| `quien_mas_en_el_barco.py` | BDCs, and Japan's megabanks against regional banks in Tokyo |
| `bloque_omega_estres.py` | secondary test with a triangle-based network attribution (inconclusive) |
| `analisis_french.py` | the telecoms comparison with industry portfolios |
| `*_resultados.json`, `serie_D_20261002.csv`, `brecha_por_anio.csv` | results and derived series as produced |

## Tenant map and Table 3

`tenant-map/` holds the map of documented obligations between listed companies and the main AI tenants (OpenAI, Anthropic, xAI,
Meta's off-balance-sheet vehicles), each link with its source; the table behind Table 3 of the paper (who could absorb a failure
of OpenAI); and a pre-registered test of whether OpenAI's exclusive counterparties react specifically to OpenAI news. That test
did not pass (they fall no more than on any bad day for AI) and is kept here as part of the record. The download script for its
prices is included; the prices themselves are not redistributed.

## Reproducing

Requirements: Python 3.9 or later with `pandas`, `numpy`, `matplotlib` and `yfinance`.

```bash
python3 descargar_panel_capa_financiera_20261002.py   # 154 US-listed shares and ADRs -> panel_capa_financiera_20261002.csv
python3 descargar_capa2_20261002.py                   # BDCs and Tokyo-listed banks   -> panel_capa2_20261002.csv
python3 descargar_french_20261002.py                  # Kenneth French industry portfolios and factors (two zip files)
mkdir -p french && unzip -o '*.zip' -d french         # the analysis reads them from french/

python3 capa_financiera.py
python3 capa_financiera_factores.py
python3 canales_residuos_B.py
python3 quien_cae.py
python3 brecha_por_anio.py
python3 quien_mas_en_el_barco.py
python3 bloque_omega_estres.py
python3 analisis_french.py
cd paper && python3 mkfig_oct.py
```

Raw prices are not redistributed; the download scripts regenerate them. Adjusted prices from the public source are revised
over time, so a fresh download can differ slightly from the archived results.

## Licence and contact

Code under the MIT licence. Not investment advice. Contact: acedo@biomemakers.com
