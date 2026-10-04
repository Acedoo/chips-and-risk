# PRE-REGISTRO: ¿se acoplaron los financiadores a la cadena de las telecos antes del estallido? (2-oct-2026, antes de datos)

Datos: carteras diarias de 49 industrias de Kenneth French (construidas con CRSP, incluyen empresas luego desaparecidas) y
factores diarios de Fama-French (mercado). Rendimientos ponderados por valor. Descarga: descargar_french_20261002.py.
Grupos de industrias (nombres de la biblioteca):
- Cadena tecnológica (la misma en las dos épocas): Telcm (telecomunicaciones), Chips (equipo electrónico; incluye fabricantes
  de equipo de telecomunicaciones), Hardw (ordenadores), Softw (software), ElcEq (equipo eléctrico).
- Financieras: Banks, Fin, Insur.
- Resto: las demás industrias (excluidas RlEst y Other por heterogéneas).
Medida (como en el estudio por empresas): ventanas de 250 días, paso 10; para cada industria financiera, acoplamiento medio |corr|
a la cadena menos acoplamiento medio al resto; se promedian las tres. Versión principal sobre residuos de mercado (Mkt-RF),
porque en el estudio por empresas el mercado explicaba unas cuatro quintas partes del efecto bruto. Se reporta también la bruta.
Paso 1, CALIBRACIÓN (2016-2026): ¿reproduce el nivel de industria la subida desde 2024? Media de ventanas con final desde
2024-01-01 menos media de las de final hasta 2022-12-31, con IC95 por bootstrap de bloques móviles (bloque 10 ventanas).
Si el IC no excluye el cero, el nivel de industria es demasiado grueso: se PARA y no se interpreta la época de las telecos.
Paso 2, solo si pasa la calibración (1994-2004): auge (ventanas con final en 1998-2000) menos antes (final en 1994-1996), con el
mismo IC; y se describe el estallido (2001-2002). "Precedente" solo si el IC del auge excluye el cero y es positivo.
Cautelas fijadas: las industrias son amplias (Banks son todos los bancos, no solo los que prestaron a las telecos), así que el
efecto puede diluirse; la cadena de 1999 no es la de 2025 (antes eran operadores y equipo, ahora chips y energía).
