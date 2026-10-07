# ai-chain

Measurement behind "The Uncommenced Lease", the note accompanying "The Sharp
End of AI Debt" (SSRN 7561480).

Everything here is read from SEC filings and recomputable from EDGAR. Every
lease amount carries the sentence it was extracted from and the filename of its
source filing, so any figure can be traced to the paragraph that states it.

## Run order

    python3 bajar_proveedores.py
        Downloads 10-K and 10-Q filings into informes/ (not in the repository:
        180 files, ~1 GB). Thirteen companies on both sides of the chain.

    python3 extraer_no_iniciados_b.py --informes informes \
            --salida no_iniciados_b.csv
        Leases signed and not yet commenced, read from the text. Three drafting
        patterns: two amounts to be added (Microsoft, Alphabet), one amount in
        a sentence (Meta, CoreWeave), a table row (Amazon). Verified against
        118 of 118 manually checked amounts.

    python3 serie_credito_c.py --precios <prices> --salida zona_roja_series_c.csv
        Reported financial debt from the SEC XBRL company-facts API, under the
        definition written in the file header: long-term debt, its current
        portion and short-term borrowings. No leases, no guarantees. Prints
        which tag supplied how many quarters.

    python3 zona_roja_v4.py --series zona_roja_series_d.csv \
            --no-iniciados no_iniciados_b.csv
        Per-company series on a complete quarterly grid. Reported against
        committed credit, and the ratio between them.

    python3 zona_roja_v5.py --series zona_roja_v4_series.csv --pib pib_usa.csv
        Chain aggregate in the units of Greenwood, Hanson, Shleifer and
        Sorensen (2022): percentage points of US GDP, three-year change.

    python3 indice_precios_b.py --series zona_roja_v4_series.csv
        Price leg, four constructions: equal-weighted and capitalisation-
        weighted, nominal and CPI-deflated.

    python3 extraer_plazos_b.py --informes informes --salida plazos_b.csv
        When the signed leases begin and how long they run, where disclosed.
        Microsoft, Amazon and Oracle disclose neither.

    python3 serie_concentracion_c.py --informes informes \
            --salida concentracion_series_c.csv
        Customer concentration on the supplier side: who borrowed against the
        promise, and how much of their revenue depends on it.

    python3 figuras_credito.py
        The three figures in the note.

    python3 exportar_compromiso_b.py --series zona_roja_v4_series.csv
        Writes commitment.csv for the dashboard, carrying each company's last
        reported figure forward until it files again.

## Figures and series

| file | what it holds |
| --- | --- |
| no_iniciados_b.csv | one row per filing: amount, period, mode, source sentence |
| zona_roja_v4_series.csv | per company and quarter: reported, uncommenced, ratio |
| zona_roja_v5_series.csv | chain aggregate as a share of US GDP |
| plazos_b.csv | start and term where the filing states them |
| concentracion_series_c.csv | customer concentration, with the sentence |
| indice_precios_b.csv | the four price-index constructions |
| commitment.csv | the series the dashboard reads |
| credito_nivel, credito_var3, ratio_empresa | the figures |

## What this does not measure

Oracle states that it has uncommenced lease commitments and publishes no
amount. Blue Owl discloses no customer concentration. Guarantees and
residual-value guarantees are a separate channel and are deliberately out of
scope: they are not debt of the guarantor until called. Private credit raised
to buy compute is a third channel with no systematic public source.

## Prior counts

The amount is not new. Moody's puts hyperscalers' uncommenced future leases at
about $660bn; the Wall Street Journal tallies $904bn for the four largest; and
Van Nieuwerburgh (NBER WP 35865, note 6) adds uncommenced leases to reported
debt for those four, discounted by 0.75, and finds leverage rising from 20% to
48%. The June 2026 figure here, $871bn undiscounted across five companies,
sits between the published counts. What did not exist is the quarterly series,
the traceability to the sentence, and the calendar.

## anterior/

Earlier work on the same chain: the guarantees note and its extraction, and
figures from the SSRN paper. Kept for reference, not part of this measurement.
