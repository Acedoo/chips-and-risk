# RESULTADO: la capa financiera de la cadena de la IA (2-oct-2026). Según PREREGISTRO_CAPA_FINANCIERA.md y adendas 1-4.
Panel: 154 valores, 2015-12-01 a 2026-10-01; 248 ventanas de 250 días, paso 10 (69 en 2024-2026, 154 en 2016-2022).
Cadena: definición nueva de la adenda 4 (mismos tamaños de bloque que agosto). 200 permutaciones; p mínimo posible 0,005.

## Principal (regla de publicación): PASA
Especificidad del acoplamiento a la cadena (financiadores menos financieras de control, descontado el acoplamiento a la cesta neutra):
- Nivel 2024-2026: +0,063, p = 0,005 (ninguna de las 200 permutaciones lo alcanza)
- Cambio frente a 2016-2022: +0,045, p = 0,005
Por año: 2016 +0,008 · 2017 +0,008 · 2018 +0,014 · 2019 +0,029 · 2020 +0,015 · 2021 +0,018 · 2022 +0,024 · 2023 +0,022 ·
2024 +0,056 · 2025 +0,075 (máximo) · 2026 +0,057. Última ventana (28-sep-2026): +0,043. Pico en 2025 y bajando, como el
acoplamiento interno de la cadena en el artículo de agosto (pico en el primer trimestre de 2025).

## Robustez (obligatoria antes de contacto externo): las tres pasan, todas p = 0,005
sin japoneses +0,059 (cambio +0,041) · sin BLK +0,064 (+0,047) · solo gestores alternativos (8) +0,080 (+0,059)

## Canales (adenda 1)
Nivel 2024-2026: infraestructura +0,063, software +0,062; diferencia +0,001, IC95 [-0,004, +0,009] (bloque 10) y
[-0,002, +0,009] (bloque 25). NO SE SEPARAN en el nivel actual (lo pre-registrado dice que, en ese caso, se dice).
Descriptivo, no pre-registrado como decisión: en 2016-2022 la especificidad era mayor con el software (+0,033) que con la
infraestructura (+0,013); en 2024-2026 las dos están en ~+0,063. La infraestructura se ha multiplicado por cinco y el software
por dos (cambios +0,050 y +0,029, ambos p < 0,05). Lectura: el vínculo histórico de los financiadores era con el software (a
quien prestan); lo nuevo desde 2024 es el vínculo con chips y energía, que ha alcanzado al del software.

## Elasticidad (adenda 3, cifra para comunicar; descriptiva)
Rendimiento del grupo por cada 1 % de la cadena: 2016-2019 financiadores 0,73 / control 0,59 · 2020-2023 0,86 / 0,79 ·
2024-2026 0,74 / 0,44. OJO a la lectura honesta: los financiadores se mueven con la cadena como siempre (~0,74); lo que ha
cambiado es que las demás financieras se han DESENGANCHADO (0,79 a 0,44). Frase correcta: "una caída del 10 % en la cadena va
hoy con un 7,4 % en los financiadores y un 4,4 % en las demás financieras; hace cuatro años la diferencia casi no existía".

## Cautelas que van con el resultado
- Co-movimiento no es exposición contractual: mide cómo los trata el mercado, no cuánto deben.
- Un factor común de apetito por riesgo que cargue más en gestores alternativos y en la cadena que en la cesta neutra no está
  descartado; comprobarlo con un modelo de factores antes de escribir.
- Definición de cadena nueva (la de agosto no se conserva); asignación de grupos por juicio; panel de supervivientes.
- Describe el presente; el pico fue 2025.
Pendiente: análisis secundario del bloque Omega (adenda 2); comprobación de factores; barrido bibliográfico antes de escribir.

## COMPROBACIÓN DE FACTORES (adenda 5): EL TITULAR SE MANTIENE, MUY MATIZADO
| | bruto | residuo de mercado (A) | residuo de mercado + financiero (B) |
|---|---|---|---|
| nivel 2024-2026 | +0,063 | +0,013 | +0,020 |
| cambio frente a 2016-2022 | +0,045 | +0,017 | +0,020 |
| p (200 permutaciones) | 0,005 | 0,005 | 0,005 |
Por año, B: 2016 -0,000 · 2017 -0,002 · 2018 -0,002 · 2019 +0,003 · 2020 +0,002 · 2021 -0,001 · 2022 +0,002 · 2023 +0,010 ·
2024 +0,014 · 2025 +0,031 · 2026 +0,013. En A, 2018-2023 es ligeramente negativo y 2024-2026 positivo todos los años.
Lectura: unas cuatro quintas partes del efecto bruto eran beta de mercado; queda un componente específico, pequeño en valor
absoluto, prácticamente nulo hasta 2023 y positivo desde 2024 (máximo 2025), que no explican ni el mercado ni el sector
financiero. Mensaje correcto: no "los prestamistas se mueven con la IA" (se mueven con todo), sino "desde 2024 aparece un
vínculo propio con la cadena que antes no existía". La elasticidad 0,74 frente a 0,44 es bruta: usarla solo con esa aclaración.

## ANÁLISIS SECUNDARIO: BLOQUE OMEGA EN LOS DÍAS DE ESTRÉS DE LA CADENA (adenda 6): NO CONCLUYENTE, MISMA DIRECCIÓN
248 días de estrés (peor decil del rendimiento a 10 días de la cadena; umbral -4,3 %), 65 desde 2024. 17 financiadores (sin OWL)
frente a 24 de control. Fórmulas del arnés público sin cambios.
| medida | diferencia | p (200 perm.) | antes de 2024 | desde 2024 |
|---|---|---|---|---|
| cuota de triángulos | +0,136 | 0,065 | +0,081 | +0,289 |
| exceso triádico | +0,018 | 0,10 | +0,012 | +0,033 |
| cuota de grado | +0,062 | 0,08 | +0,032 | +0,146 |
Spearman triángulos-grado entre financieras: 0,99. Lectura fijada: los triángulos replican al grado; el exceso triádico va en la
dirección del resultado principal pero no es significativo. Para la nota: una frase en métodos o limitaciones, no en el titular.

## CANALES DESCONTANDO MERCADO Y SECTOR FINANCIERO (descriptivo, para la nota; canales_residuos_B.py)
Por año, infraestructura / software: 2016 +0,002/-0,008 · 2017 -0,002/-0,002 · 2018 +0,000/-0,008 · 2019 +0,003/+0,004 ·
2020 -0,005/+0,025 · 2021 -0,005/+0,011 · 2022 -0,004/+0,018 · 2023 +0,004/+0,027 · 2024 +0,013/+0,018 · 2025 +0,027/+0,044 ·
2026 +0,006/+0,035. Medias: infraestructura -0,002 (2016-22) frente a +0,016 (2024-26); software +0,008 frente a +0,032.
Lectura para la nota: descontados los factores, el vínculo con el SOFTWARE es el mayor y existe desde 2020 (el canal que documentó
el BIS en marzo de 2026); el vínculo con CHIPS Y ENERGÍA es nulo hasta 2023 y aparece en 2024 (máximo 2025). Corrige la lectura
en bruto ("hoy igual por los dos canales"): neto, el software pesa más y la infraestructura es lo nuevo.

## QUIÉN CAE CUANDO CAE LA IA (adenda 7): LA REGLA PASA, POR POCO, Y CON UN MATIZ
35 peores días de la cadena 2024-2026 (cadena -3,4 % de media). Rendimiento anormal (beta al SPY de los 250 días previos).
- Financiadores -0,12 pp/día; control +0,42; diferencia -0,54 pp/día, p = 0,005 (umbral fijado: -0,5). REGLA: PASA.
- 2016-2023 (92 peores días): diferencia +0,04, p = 0,75: no había nada. Resto de días 2024-2026: +0,01: nada.
- MATIZ (comprobación hecha DESPUÉS de ver los datos, descriptiva): las financieras defensivas (aseguradoras de daños y mercados)
  suben esos días (+0,69 pp; +0,035 en 2016-23). Sin ellas en el control: diferencia -0,34 pp/día, p = 0,005; 2016-23 +0,05.
- Nombres (anormal medio en esos días, pp): OWL -0,60; MFG -0,47; SMFG -0,47; ARES -0,46; CG -0,38; MUFG -0,32; GS -0,17;
  APO -0,08; JPM -0,07; MS -0,07; C -0,05; BLK -0,03; BX +0,07; BAC +0,07; KKR +0,09; BN +0,14; PRU +0,27; MET +0,31.
- DeepSeek (27-ene-2025): cadena -4,9 %; SPY -1,41 %; financiadores -0,57 % (media bruta); demás financieras +1,26 %.
Mensaje honesto: desde 2024, en los días malos de la IA, sus financiadores ya no se comportan como el resto de las finanzas: caen
con ella mientras el resto aguanta o sube; antes de 2024 no pasaba. NO decir "caen el doble": su anormal propio es pequeño.
Gancho: los tres megabancos japoneses entre los más expuestos (regulador japonés, 25-sep).

## QUIÉN MÁS ESTÁ EN EL BARCO (adenda 8)
A) BDC (16, EE. UU.): REGLA PASA en 2024-26 (-0,55 pp/día, p = 0,005; BDC -0,14, control +0,42), PERO en 2016-23 ya era
   -0,47 pp/día (p = 0,005; BDC -0,45, control +0,02). NO ES NUEVO: sensibilidad de siempre al estrés de crédito.
   Lectura: lo nuevo desde 2024 está en las acciones de gestoras y prestamistas, no en sus vehículos de préstamo.
   Por BDC (pp): TCPC -0,53; HTGC -0,25; OCSL -0,21; MAIN, PSEC, OBDC -0,19; ... ARCC -0,02; TSLX +0,05.
B) Megabancos japoneses en Tokio (sesión siguiente): NO PASA. Mega -0,69, regionales -0,44, diferencia -0,25 pp/día,
   p = 0,055 (364 combinaciones exhaustivas, 11 regionales; 8385.T sin datos por cambio de código en 2022). 2016-23: -0,10.
   Por banco (pp): Mizuho -0,80; SMFG -0,77; MUFG -0,51; regionales entre -0,76 y +0,01.
   Lectura: en casa no se distinguen claramente de la banca regional; lo visto en sus ADR es cómo los valora EE. UU.
NOTA corregida: punto clave 2, párrafo de nombres (Tokio) y párrafo nuevo de las BDC.

## BRECHA AÑO POR AÑO EN LOS PEORES DÍAS (descriptivo, 5 % peor de cada año; brecha_por_anio.py)
2016 -0,24 · 2017 -0,20 · 2018 -0,06 · 2019 +0,09 · 2020 +0,27 · 2021 -0,17 · 2022 -0,14 · 2023 -0,07 · 2024 -0,67 · 2025 -0,46 ·
2026 -0,48 (pp/día, financiadores menos control). Los tres años desde 2024 quedan por debajo de cualquier año anterior.
Nota: entra como figura 1; frase de Burry (24-sep: amortizaciones en 2028-29; 28-sep: acorta plazos) con referencias [14] y [15].
