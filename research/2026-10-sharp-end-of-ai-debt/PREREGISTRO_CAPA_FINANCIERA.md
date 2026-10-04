# PRE-REGISTRO: ¿se ha acoplado a la cadena de la IA la capa que la financia? (2-oct-2026, antes de ver datos)

## Pregunta
El artículo de agosto (SSRN 7307362) midió con precios que el peso estructural de la cadena de la IA se movió de los
compradores de cómputo hacia sus proveedores y hacia la energía. La nota de septiembre (repositorio TSI-OmegaS, carpeta
ai-chain) documentó con los documentos registrados el mecanismo: garantías y arrendamientos fuera de balance. Las noticias de
septiembre y octubre (regulador japonés vigilando a sus bancos y aseguradoras, Carlyle avisando de concentración en el crédito
privado) apuntan a que el riesgo se ha desplazado hacia quien financia. Pregunta: ¿se ve ese desplazamiento en los precios de
los financiadores cotizados, más que en los de otras financieras comparables?

## Grupos (fijados ahora; la asignación es un juicio y se declarará como limitación)
- TRATAMIENTO, financiadores nombrados en la cobertura o grandes actores del crédito privado (18): gestores alternativos y de
  crédito privado BX, APO, KKR, ARES, CG, BN, OWL (cotiza desde 2021), BLK (socio de infraestructura de IA); bancos prestamistas
  JPM, MS, GS, C, BAC; megabancos japoneses MUFG, SMFG, MFG; aseguradoras con gestoras de crédito privado MET, PRU.
- CONTROL, otras financieras sin ese papel destacado (24): bancos regionales USB, PNC, TFC, FITB, KEY, RF, HBAN, CFG;
  aseguradoras de daños TRV, CB, ALL, PGR, HIG, CINF, L; mercados CME, ICE, NDAQ; gestoras tradicionales TROW, BEN, IVZ;
  financiación al consumo AXP, COF, SYF.
- CADENA: las 46 del artículo de agosto. CESTA NEUTRA: las 60 del grupo de control de agosto (fuera de la cadena).
- Datos: cierres ajustados de diciembre de 2015 a hoy, una sola descarga (descargar_panel_capa_financiera_20261002.py).

## Medida principal (doble diferencia, para que no la explique la beta de mercado)
Ventanas de 250 días, paso 10, como en agosto. En cada ventana y para cada financiera f:
  acoplamiento a la cadena  = media de |corr(f, j)| sobre las 46 de la cadena
  acoplamiento neutro        = media de |corr(f, j)| sobre las 60 de la cesta neutra
  especificidad(f)           = acoplamiento a la cadena − acoplamiento neutro
Medida principal por ventana: D = media de la especificidad en TRATAMIENTO − media en CONTROL.
Restar el acoplamiento neutro quita lo que una financiera de beta alta se mueve con todo; restar el control quita lo que
cualquier financiera se mueve con la tecnología.

## Inferencia
Permutación de etiquetas entre las 42 financieras (200 permutaciones, manteniendo 18 y 24), sobre:
  (1) el nivel medio de D en el periodo 2024-2026 (desde enero de 2024, el arranque de la financiación fuera de balance),
  (2) el cambio de D entre 2016-2022 y 2024-2026.
OWL entra solo en las ventanas con historia completa.

## Regla de publicación (fijada ahora)
- ARTÍCULO solo si (1) y (2) son positivos con p < 0,05 por permutación.
- Si no: no hay artículo; como mucho una actualización en LinkedIn de las cifras de agosto con datos hasta octubre.
- Antes de escribir a nadie de fuera (Financial Times incluido): el resultado tiene que haber pasado esta regla y una
  comprobación de robustez (quitar los japoneses; quitar BLK; usar solo gestores alternativos).

## Lo que esta medida no puede decir
Co-movimiento de precios no es exposición contractual: mide si el mercado ya trata a los financiadores como parte de la cadena,
no cuánto deben ni a quién. Y como en agosto, describe el presente, no avisa del futuro.

## ADENDA (2-oct-2026, ANTES de ver datos): los dos canales de la IA en el crédito privado
La revisión de la cobertura muestra que el mercado atribuye las caídas de los gestores de crédito privado a la IA por dos canales
de signo económico opuesto: (A) financiación de infraestructura (centros de datos, chips, energía), cuyo riesgo crece si la IA
decepciona; y (B) préstamos a empresas de software que la IA puede volver obsoletas, cuyo riesgo crece si la IA triunfa
(Blue Owl atribuyó sus reembolsos a la preocupación por la disrupción de la IA). La medida principal mezcla los dos.
Análisis secundario fijado ahora (no cambia la regla de publicación, decide qué se cuenta):
- Especificidad por bloque: la misma doble diferencia, calculada por separado contra (A) semis y hardware + equipo eléctrico +
  utilities, y (B) hyperscalers y software, con los bloques del artículo de agosto.
- Lectura: si D(A) > D(B) con el intervalo de la diferencia fuera de cero, el mercado trata a los financiadores como parte de la
  infraestructura; si D(B) > D(A), el riesgo que ve el mercado es el de sus prestatarios de software; si no se separan, se dice.
- Antes de escribir el artículo: barrido bibliográfico completo de mediciones previas (no afirmar novedad sin él).

## ADENDA 2 (2-oct-2026, ANTES de ver datos): el bloque Omega como análisis secundario, y la regla de comunicación
- Bloque Omega: se usará el código público tal cual (repositorio BiomeMakers/Omega-block, validate_omega_block.py), sin tocar
  la fórmula, sobre el panel ampliado. Pregunta: en los episodios de estrés de la cadena (peor decil del rendimiento a 10 días de
  la cesta equiponderada de las 46), ¿cuánto estrés atribuye el bloque a los financiadores frente a las financieras de control?
  Comparación tratamiento frente a control por permutación de etiquetas (200), y el GRADO de cada financiera en la red se
  reporta al lado, para que se vea qué aporta el bloque y qué no. No cambia la regla de publicación.
- Comunicación: el resultado va delante y en el lenguaje del lector (riesgo, crédito, quién carga con qué); el método va detrás,
  en anexo o en el repositorio, para quien pregunte cómo se mide. Los índices propios no van en el titular.

## ADENDA 3 (2-oct-2026, ANTES de abrir el panel subido): la cifra para comunicar
Elasticidad descriptiva, como en agosto: por ventana, pendiente de la regresión del rendimiento diario medio de cada grupo de
financieras sobre el rendimiento diario medio de la cadena (y por canal: infraestructura y software). Se reporta por periodos
(2016-2019, 2020-2023, 2024-2026) para tratamiento y control. Es descriptiva: no cambia la regla de publicación. Frase tipo:
"una caída del 10 % en la cadena va asociada a una caída de X % en los financiadores, frente a Y % en otras financieras".

## ADENDA 4 (2-oct-2026, ANTES de calcular ningún resultado): definición de la cadena
La lista nominal de las 46 de agosto no se conserva (no está en el artículo, el repositorio ni las transcripciones). Se fija una
definición NUEVA, escrita, con los mismos tamaños de bloque, y se declarará como tal (no como la de agosto):
- Semiconductores y hardware (23): NVDA AMD AVGO INTC TXN QCOM MU AMAT LRCX KLAC ADI TER SNPS CDNS ANET SMCI HPE STX WDC NTAP APH GLW TEL
- Compradores y software (11): MSFT GOOGL AMZN META ORCL NOW CRM ADBE INTU ACN IBM
- Equipo eléctrico (5, como en agosto): EMR ETN JCI PH PWR. Utilities (7, como en agosto): AES D DUK EXC NRG SO XEL
- Fuera: las 5 de historia corta de agosto (CEG GEV VST DELL IR) y DLR, EQIX (centros de datos: ambiguos entre cadena y
  financiación). Cesta neutra: los 58 valores restantes del panel de agosto (definicion_cadena_20261002.json).
- Canal infraestructura = semis + equipo + utilities (35); canal software = compradores y software (11).
- Periodos: ventanas etiquetadas por su fecha final; "2024-2026" = final desde 2024-01-01; "2016-2022" = final hasta 2022-12-31.

## ADENDA 5 (2-oct-2026, tras el análisis principal y ANTES de correr esto): comprobación de factores
Objeción a descartar: que un factor común (mercado, sector financiero, apetito por riesgo) explique la especificidad medida.
En cada ventana, los rendimientos de TODOS los valores se sustituyen por los residuos de una regresión sobre:
  A) el mercado (SPY);
  B) el mercado y un factor financiero simétrico (media equiponderada de las 42 financieras, tratamiento y control a la vez).
Con los residuos se repite exactamente el análisis principal (misma doble diferencia, mismas 200 permutaciones).
Regla: el titular se mantiene si, en A y en B, el nivel 2024-2026 y el cambio frente a 2016-2022 siguen positivos con p < 0,05.
Si cae en B, el resultado se reformula como "comparten un factor financiero", sin titular de IA.

## ADENDA 6 (2-oct-2026, ANTES de correr el bloque Omega): concreción del análisis secundario
- Código: las fórmulas del arnés público validate_omega_block.py (repositorio BiomeMakers/Omega-block) copiadas sin cambios:
  A = |corr| de rendimientos logarítmicos en 250 días con diagonal cero; s = A·1 (grado); tri = ((A·A)∘A)·1;
  E = s²·(Σs²)²/(Σs)³; exceso = (tri - E)/max(E, 1e-12). Universo como el arnés: valores con al menos 95 % de datos
  (queda fuera OWL, que cotiza desde 2020), huecos de rendimiento a cero; SPY excluido.
- Episodios de estrés de la cadena: días cuyo rendimiento a 10 días de la cesta equiponderada de las 46 cae en el peor decil
  de toda la muestra. En cada uno, el bloque se calcula sobre la ventana de 250 días que termina ese día.
- Medidas por financiera: cuota de triángulos (tri_i / media de tri), exceso triádico y, al lado, cuota de grado (s_i / media).
- Estadístico: media sobre los días de estrés de (media tratamiento - media control); permutación de etiquetas entre las
  financieras presentes (200). Se reporta además por periodo (antes de 2024 y desde 2024), de forma descriptiva.
- Lectura fijada: si la cuota de triángulos replica la de grado, el bloque no aporta aquí más que el grado y se dice así; lo
  que aporte el bloque estará, si está, en el exceso triádico.

## ADENDA 7 (2-oct-2026, ANTES de mirar los datos de estos días): ¿quién cae cuando cae la IA?
Pregunta decisiva para el artículo: en los peores días de la cadena de la IA desde 2024, ¿caen los financiadores más que las
demás financieras, descontado el mercado?
- Días: el 5 % peor de los rendimientos diarios de la cesta equiponderada de las 46 de la cadena, entre 2024-01-01 y
  2026-10-01. Comparación: el 5 % peor de 2016-2023 (¿es nuevo?) y el resto de días de 2024-2026.
- Rendimiento anormal de cada financiera en cada día: rendimiento menos beta por el del SPY, con la beta estimada en los 250
  días anteriores a ese día (sin mirar el futuro).
- Estadístico: media en esos días de (anormal medio de los 18 financiadores - anormal medio de las 24 de control), en puntos
  porcentuales por día; permutación de etiquetas (200).
- REGLA: hay artículo con fuerza si la diferencia es negativa, de al menos -0,5 puntos porcentuales por día, con p < 0,05.
  Si no, el artículo no tiene fuerza suficiente: nota en el repositorio y post en LinkedIn, sin escribir al FT.
- Descriptivo, sin decidir nada: la clasificación por empresa (anormal medio de cada financiadora en esos días) y el día de
  DeepSeek (27-ene-2025), con nombres.

## ADENDA 8 (2-oct-2026, ANTES de descargar datos): ¿quién más está en el barco?
Mismos días que la adenda 7: los 35 peores días de la cesta de las 46 de la cadena entre 2024-01-01 y 2026-10-01, y los 92
peores de 2016-2023 como comparación. Mismo rendimiento anormal (beta de 250 días previos frente al índice de su mercado).
A) VEHÍCULOS DE CRÉDITO PRIVADO COTIZADOS (BDC, EE. UU.): ARCC, OBDC, BXSL, FSK, GBDC, MAIN, HTGC, PSEC, TSLX, OCSL, GSBD, NMFC,
   CGBD, TCPC, BCSF, MFIC. Comparación: las 24 financieras de control de siempre. Índice: SPY.
   Estadístico: anormal medio de las BDC menos el de control, en pp/día; permutación de etiquetas (200).
B) MEGABANCOS JAPONESES EN TOKIO: 8306.T (MUFG), 8316.T (SMFG), 8411.T (Mizuho) frente a bancos regionales japoneses: 8331.T,
   8354.T, 7186.T, 8418.T, 8385.T, 8359.T, 8377.T, 8366.T, 8341.T, 8334.T, 7167.T, 8524.T. Índice: TOPIX (ETF 1306.T).
   Día de Tokio = primera sesión de Tokio posterior a cada peor día de la cadena (Tokio abre después del cierre de EE. UU.).
   Estadístico igual; permutación exhaustiva de los 3 tratados entre los 15 bancos.
REGLA (cada prueba por separado): pasa si la diferencia es de al menos -0,5 pp/día con p < 0,05. Lo que no pase se dice tal cual.
Descriptivo: cada BDC y cada banco por nombre; comparación con 2016-2023 (las que tengan historia; OBDC desde 2019, BXSL desde 2021).
