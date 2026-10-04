# PRE-REGISTRO: ¿se suman o se multiplican el choque de tipos y el de la IA en los mismos financiadores? (2-oct-2026, ANTES de descargar)

Motivo: el Banco de Inglaterra (FPC, 25-sep-2026) advierte de que han aumentado las probabilidades de que varias vulnerabilidades
se materialicen a la vez (deuda pública en máximos desde 2008, deuda de la IA). Literatura revisada: el choque de tipos sobre la IA
está documentado como episodio (18-ago-2026) y el canal deuda de la IA -> tipos (Fed de Dallas, Vanguard); las medidas de riesgo
sistémico conjunto (CoVaR, SRISK, MES) existen; no se ha encontrado una medición de la INTERACCIÓN tipos x IA sobre los financiadores
con grupo de control. Aportación: aplicación, no método.

Datos: panel_capa_financiera_20261002.csv (154 valores EE. UU.) y la serie diaria del bono a 10 años de EE. UU. (^TNX), con el de
30 años (^TYX) como comprobación. Grupos y cadena: los del artículo (18 financiadores, 24 otras financieras, 46 de la cadena).

PASO 1, la interacción (decide):
  Brecha diaria G_t = media de AR de los 18 financiadores - media de AR de las 24 otras financieras (AR de la ecuación 1, beta a
  250 días previos frente a SPY).
  Choque IA: AI_t = -(rendimiento equiponderado de la cadena - rendimiento de SPY), positivo cuando la IA cae más que el mercado.
  Choque de tipos: R_t = variación diaria del rendimiento a 10 años en puntos básicos, positivo cuando suben los tipos.
  Regresión: G_t = a + b1 AI_t + b2 R_t + b3 AI_t R_t, por periodo: 2024-01-02 a 2026-09-30 (principal) y 2016-2023 (comparación,
  incluye 2022). Inferencia: 2.000 reasignaciones aleatorias de las 42 financieras en grupos de 18 y 24, reestimando b3.
  REGLA: "los dos golpes se multiplican" si en 2024-2026 b3 < 0 con p < 0,05 Y el término conjunto, evaluado en los percentiles 90
  de AI_t y de R_t a la vez, vale al menos -0,20 puntos porcentuales al día. Si no, se dice que se suman (o que no hay interacción).
  Descriptivo: la brecha media en los días con los dos choques en su decil superior a la vez, y lo mismo para Oracle frente a la cadena.

PASO 2, el bloque Omega frente al MES en días de choque conjunto (comprobación de producto, expectativa baja declarada):
  Mismo protocolo que el arnés público validate_omega_block.py (ventanas de 250 días, paso 21, cinco pliegues por activo, base
  estándar con MES, placebo gaussiano de la misma anchura, bootstrap por bloques), cambiando SOLO el objetivo: en lugar del
  rendimiento medio en el 5 % peor de días de mercado del año siguiente, el rendimiento medio en los días del año siguiente con
  choque conjunto (AI_t en su quintil superior y R_t en su quintil superior del año). Ventanas con menos de 8 días conjuntos se excluyen.
  El código copia las fórmulas del arnés sin tocarlas; el único cambio es el objetivo, y se declara.
  REGLA: la del arnés (mejora de R2 con IC que excluye cero y por encima del techo del placebo). Expectativa declarada: baja (la
  respuesta a la Fed como perturbación no mejoró el MES en septiembre, y el bloque no anticipó a los prestamistas de la IA).

ENMIENDA 1 (2-oct-2026, ANTES de ver la serie real de tipos): la prueba en seco con una serie de tipos INVENTADA dio PASS en el
paso 2, porque el objetivo así definido se reduce en la práctica a los días malos de la IA, que el bloque ya atribuye. Un PASS con
la serie real no probaría nada sobre los tipos. Control añadido: el mismo cálculo repetido con la serie de tipos barajada al azar en
el tiempo (3 barajados con semillas fijas 1, 2, 3). REGLA DEL PASO 2 corregida: PASS del arnés con los tipos reales Y su mejora media
mayor que la de los tres barajados Y su límite inferior del intervalo por encima de la media de los barajados. El paso 1 no cambia
(su inferencia ya compara contra grupos al azar y la interacción aísla la coincidencia).
