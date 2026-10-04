"""Spanish version of the page. Fixed text goes through ES; sentences built from data go through RULES (patterns with their
numbers). Files kept by hand carry their own Spanish columns (description_es, bet_es, measure_es, *_es fields); when a row has
no Spanish, the English is shown."""
import html as H
import re

ES = {
 "Now": "Ahora", "Positions": "Posiciones", "Your savings": "Tus ahorros",
 "History": "Historia", "Evidence": "Evidencias", "1 week": "1 semana", "1 month": "1 mes", "3 months": "3 meses", "Year to date": "En el año",
 "no data yet": "sin datos aún", "unchanged": "sin cambios",
 "Lenders' gap in AI sell-offs, last 12 months": "Brecha de los financiadores en las caídas de la IA, últimos 12 meses",
 "Inside its 2024-2026 range: the market still singles out the AI-dependent lenders.": "Dentro de su rango de 2024-2026: el mercado sigue señalando a los financiadores dependientes de la IA.",
 "Back inside its pre-2024 range: the market no longer singles out the lenders.": "De vuelta a su rango anterior a 2024: el mercado ya no señala a los financiadores.",
 "Wider than any year since 2024: the lenders are lagging more than ever.": "Más amplia que en cualquier año desde 2024: los financiadores se rezagan más que nunca.",
 "Above its usual range.": "Por encima de su rango habitual.",
 "Zones from its own history (2016-2023 and 2024-2026)": "Zonas según su propia historia (2016-2023 y 2024-2026)",
 "AI supply chain since ChatGPT": "Cadena de la IA desde ChatGPT",
 "Grey band: past booms at the same age (chart above)": "Banda gris: booms pasados a la misma edad (gráfica de historia)",
 "Signs of a turning point": "Señales de punto de giro", "Signs of a late frenzy": "Señales de frenesí tardío",
 "None of the six features is present yet.": "Todavía no aparece ninguno de los seis rasgos.",
 "All six features of a late frenzy are present.": "Aparecen los seis rasgos de un frenesí tardío.",
 "Each sign tied to a data series or a sourced event": "Cada señal ligada a una serie de datos o a un acontecimiento con fuente",
 "Oracle's largest item with OpenAI, share of its value": "Mayor partida de Oracle con OpenAI, en proporción a su valor",
 "Broadcom's largest item with Anthropic, share of its value": "Mayor partida de Broadcom con Anthropic, en proporción a su valor",
 "Over 20% of its value rests on one tenant: in the zone of the exposed companies.": "Más del 20 % de su valor depende de un solo inquilino: en la zona de las empresas expuestas.",
 "Under 10% of its value: in the zone of the companies that could absorb a failure.": "Menos del 10 % de su valor: en la zona de las empresas que podrían absorber un fallo.",
 "Between the two groups of Table 3: worth watching.": "Entre los dos grupos de la tabla 3: conviene vigilarla.",
 "Zones are this paper's reading of Table 3: the giants sit under 10%, the exposed above 20%": "Las zonas son la lectura del artículo sobre la tabla 3: los gigantes, por debajo del 10 %; los expuestos, por encima del 20 %",
 "See the full panel: eight more numbers": "Ver el panel completo: ocho cifras más",
 "Oracle against the AI chain since Jan 2025": "Oracle frente a la cadena de la IA desde enero de 2025",
 "CoreWeave against the AI chain since Jan 2025": "CoreWeave frente a la cadena de la IA desde enero de 2025",
 "SoftBank against the Tokyo market since Jan 2025": "SoftBank frente a la bolsa de Tokio desde enero de 2025",
 "Near the bottom of its 52-week range: the market keeps weighing its exposure to OpenAI.": "Cerca del suelo de su rango de 52 semanas: el mercado sigue pesando su exposición a OpenAI.",
 "Near the top of its 52-week range.": "Cerca del techo de su rango de 52 semanas.", "In the middle of its 52-week range.": "En mitad de su rango de 52 semanas.",
 "Bar: its 52-week range": "Barra: su rango de 52 semanas",
 "Lenders' link to chips and power, this year": "Vínculo de los financiadores con chips y energía, este año",
 "Above its pre-2024 range: the lenders still move with chips and power beyond the market.": "Por encima de su rango anterior a 2024: los financiadores siguen moviéndose con chips y energía más allá del mercado.",
 "Back inside its pre-2024 range: the link to chips and power has faded.": "De vuelta a su rango anterior a 2024: el vínculo con chips y energía se ha desvanecido.",
 "Blue band: its 2016-2023 range": "Banda azul: su rango de 2016-2023",
 "Capital raised for AI in 2026 so far": "Capital levantado para la IA en lo que va de 2026",
 "Grey band: all of 2025 (Barclays)": "Banda gris: todo 2025 (Barclays)",
 "10-year Treasury yield": "Bono del Tesoro a 10 años",
 "Dearer refinancing matters for a build-out financed with debt.": "Refinanciarse más caro pesa en una construcción financiada con deuda.",
 "Bar: its 20-year range (FRED)": "Barra: su rango de 20 años (FRED)",
 "What the twelve signs are, and which are present": "Cuáles son las doce señales y cuáles aparecen", "present": "presente", "absent": "ausente",
 "Everything that changed since the previous update": "Todo lo que ha cambiado desde la actualización anterior",
 "First update of the monitor.": "Primera actualización del monitor.", "The four houses": "Las cuatro casas",
 "Each house is one of the paper's four listing paths: who is on it, what they have at stake, and what the data show for it now. The signal counts are evidence, not probabilities.":
     "Cada casa es uno de los cuatro caminos de salida a bolsa del artículo: quién está en ella, qué se juega y qué dicen hoy los datos. Los recuentos de señales son evidencias, no probabilidades.",
 "Main characters": "Quién la sostiene", "Four positions on the AI listings": "Cuatro posiciones sobre las salidas a bolsa de la IA",
 "Which position do your savings hold?": "¿Qué posición tienen tus ahorros?", "Show the position my savings hold": "Mostrar la posición de mis ahorros",
 "Where the current signals point among the four positions": "Hacia dónde apuntan las señales actuales entre las cuatro posiciones", "What the data show now": "Lo que dicen hoy los datos", "No current signal.": "Ninguna señal por ahora.",
 "Strong listing": "Salida fuerte", "Weak listing": "Salida débil", "Delay": "Aplazamiento", "Market fall": "Caída del mercado",
 "Which house are your savings in?": "¿En qué casa están tus ahorros?",
 "Where past booms went from here": "Adónde fueron los booms pasados desde aquí",
 "Technology booms": "Booms tecnológicos", "Energy booms": "Booms energéticos", "Credit boom": "Boom de crédito",
 "years since the start of the frenzy": "años desde el inicio del frenesí",
 "Oil, 1979-89": "Petróleo, 1979-89", "Tech and telecoms, 1995-2003": "Tecnología y telecos, 1995-2003", "Credit, 2003-13": "Crédito, 2003-13",
 "Shale, 2010-20": "Esquisto, 2010-20", "US market, 1926-34": "Bolsa de EE. UU., 1926-34", "Utilities, 1926-34": "Eléctricas, 1926-34",
 "US railroads, 1865-75": "Ferrocarriles de EE. UU., 1865-75",
 "Past booms from the start of their frenzy, rebased to 100, in calendar years: technology (electric utilities and the US market from July 1926; software, hardware, chips and telecoms from the Netscape listing in August 1995; US railroads from the end of the Civil War in April 1865 to beyond the Panic of 1873, monthly), energy (oil from January 1979, when the Shah left Iran; shale from January 2010) and credit (banks, finance and real estate from the Federal Reserve's cut to 1% in June 2003). Blue: the AI supply chain from the launch of ChatGPT, extended every week. The start dates are conventions, not forecasts: other dates would shift the curves. Total returns except the railroads (price index). The story begins earlier, with the printing press and the British railway mania of the 1840s, for which no price series is freely available. Sources: Kenneth French Data Library; F.R. Macaulay via NBER and FRED; daily prices.":
     "Booms pasados desde el inicio de su frenesí, en base 100 y en años de calendario: tecnológicos (las eléctricas y la bolsa de EE. UU. desde julio de 1926; software, hardware, chips y telecos desde la salida a bolsa de Netscape en agosto de 1995; los ferrocarriles de EE. UU. desde el final de la guerra civil en abril de 1865 hasta después del pánico de 1873, con datos mensuales), energéticos (el petróleo desde enero de 1979, cuando el sah dejó Irán; el esquisto desde enero de 2010) y de crédito (bancos, financieras e inmobiliario desde la bajada de la Reserva Federal al 1 % en junio de 2003). En azul, la cadena de la IA desde el lanzamiento de ChatGPT, que avanza cada semana. Las fechas de inicio son convenciones, no previsiones: otras fechas desplazarían las curvas. Rentabilidad total salvo los ferrocarriles (índice de precios). La historia empieza antes, con la imprenta y la manía ferroviaria británica de la década de 1840, de las que no hay series de precios de libre acceso. Fuentes: Kenneth French Data Library; F.R. Macaulay vía NBER y FRED; precios diarios.",
 "The evidence": "Las evidencias", "The measures behind every number above, one question each.": "Las medidas que hay detrás de cada cifra, una pregunta cada una.",
 "Do the AI-dependent lenders still lag when AI falls?": "¿Siguen rezagándose los financiadores dependientes de la IA cuando cae la IA?",
 "Is it the managers or their loan books, and since when?": "¿Son las gestoras o sus préstamos, y desde cuándo?",
 "Who carries OpenAI's and Anthropic's commitments?": "¿Quién carga con los compromisos de OpenAI y de Anthropic?",
 "Who carries OpenAI's and Anthropic's commitments": "Quién carga con los compromisos de OpenAI y de Anthropic",
 "How do the exposed companies and the listed tenants trade?": "¿Cómo cotizan las empresas expuestas y los inquilinos que ya cotizan?",
 "Does the news move them?": "¿Les mueven las noticias?", "Cash, debt and supplier financing": "Caja, deuda y financiación de proveedores",
 "Rates and the supplier warning sign": "Los tipos y la señal de los proveedores", "What the filings and the record say": "Lo que dicen los documentos y el registro",
 "Who lags, since 2024": "Quién se rezaga, desde 2024", "The managers, not their loan books": "Las gestoras, no sus préstamos",
 "The listed loan vehicles (BDCs) fall in AI sell-offs in almost every year; the managers' gap moved around zero before 2024 and has stayed negative since.":
     "Los vehículos de préstamo cotizados (BDC) caen en las caídas de la IA casi todos los años; la brecha de las gestoras oscilaba alrededor de cero antes de 2024 y desde entonces se ha mantenido negativa.",
 "Year": "Año", "Lenders": "Financiadores", "BDCs": "BDC", "Since when, and through what": "Desde cuándo y por dónde",
 "The lenders' link to the AI chain beyond other financial stocks, net of the market and of the financial sector (equation 3), in hundredths of a correlation.":
     "El vínculo de los financiadores con la cadena de la IA más allá de las demás financieras, descontando el mercado y el sector financiero (ecuación 3), en centésimas de correlación.",
 "The largest documented item each listed counterparty has at stake with each tenant, as a share of its market value, updated weekly with prices. Items are different instruments and are not added.":
     "La mayor partida documentada que cada contraparte cotizada tiene en juego con cada inquilino, en proporción a su valor en bolsa, actualizada cada semana con los precios. Son instrumentos distintos y no se suman.",
 "How the three exposed companies trade": "Cómo cotizan las tres empresas expuestas",
 "Since January 2025: Oracle and CoreWeave against the rest of the chain, SoftBank against the Tokyo market (%).": "Desde enero de 2025: Oracle y CoreWeave frente al resto de la cadena, SoftBank frente a la bolsa de Tokio (%).",
 "Tenants that already have a public price": "Inquilinos que ya tienen precio público",
 "Zhipu and MiniMax in Hong Kong since January, xAI inside SpaceX since June: change against the listing price (%).": "Zhipu y MiniMax en Hong Kong desde enero, xAI dentro de SpaceX desde junio: variación frente al precio de salida (%).",
 "No price data yet for these listings.": "Aún no hay precios de estas salidas a bolsa.",
 "Does SoftBank still move with OpenAI's news?": "¿Sigue moviéndose SoftBank con las noticias de OpenAI?",
 "SoftBank against the Tokyo market on the first session after each piece of news about OpenAI, in points. The paper predicts this fades if OpenAI lists.":
     "SoftBank frente a la bolsa de Tokio en la primera sesión tras cada noticia sobre OpenAI, en puntos. El artículo predice que esto se apagará si OpenAI sale a bolsa.",
 "Date": "Fecha", "News": "Noticia", "Pts": "Ptos", "Announcement": "Anuncio", "Tenant": "Inquilino", "Measure": "Medida", "Quarter": "Trimestre",
 "Announcements against what the market does": "Los anuncios frente a lo que hace el mercado",
 "Oracle and CoreWeave against the rest of the chain over the sessions after each capability announcement (%).": "Oracle y CoreWeave frente al resto de la cadena en las sesiones posteriores a cada anuncio de capacidad (%).",
 "No capability announcement on record yet.": "Aún no hay anuncios de capacidad registrados.",
 "Cash against the story": "La caja frente al relato", "The debt side: how far it has spread": "El lado de la deuda: hasta dónde se ha repartido",
 "Suppliers financing customers": "Proveedores que financian a sus clientes",
 "The warning sign of the telecoms boom: suppliers kept lending after outside capital left ($bn).": "La señal de alarma del boom de las telecos: los proveedores siguieron prestando cuando el capital de fuera ya se había ido (miles de millones de dólares).",
 "Supplier financing": "Financiación de proveedores", "Outside capital": "Capital de fuera", "The ten-year Treasury yield": "El bono del Tesoro a diez años",
 "What the new filings say": "Lo que dicen los documentos nuevos", "Events on record": "Acontecimientos registrados",
 "No new guarantee or off-balance-sheet language in the filings scanned so far.": "Sin frases nuevas sobre garantías o compromisos fuera de balance en los documentos revisados hasta ahora.",
 "Code and definitions:": "Código y definiciones:",
 ". The positions' emblems are this site's own. This page describes public market data; it is not investment advice.":
     ". Los emblemas de las posiciones son propios de esta web. Esta página describe datos públicos de mercado; no es una recomendación de inversión.",
 "Built with the assistance of Claude (Anthropic). Anthropic is one of the companies tracked here; its figures follow the same rules and sources as the others.":
     "Hecha con la ayuda de Claude (Anthropic). Anthropic es una de las empresas que sigue esta web; sus cifras siguen las mismas reglas y fuentes que las demás.",
 "Split your savings across these doors (rough percentages; they need not add up exactly).": "Reparte tus ahorros entre estas puertas (porcentajes aproximados; no hace falta que sumen exactamente).",
 "Show which house my savings are in": "Mostrar en qué casa están mis ahorros",
 "of 6": "de 6", "No change since the previous update.": "Sin cambios desde la actualización anterior.", "Show or hide groups of past booms": "Mostrar u ocultar grupos de booms pasados", "Change over": "Variación en",
}

KIND = {"contracted": "contratado", "invested": "invertido", "leases": "arrendamientos", "guarantee cap": "tope de garantía", "loan": "préstamo", "stake": "participación"}
CHAINS = {"Software": "Software", "Chips, power": "Chips y energía", "10-year": "10 años", "Oracle": "Oracle", "CoreWeave": "CoreWeave", "SoftBank": "SoftBank"}


def _n(x):
    """Spanish decimal comma."""
    return x.replace(".", ",")


SCEN_ES = {"Strong listing": "Salida fuerte", "Weak listing": "Salida débil", "Delay": "Aplazamiento", "Market fall": "Caída del mercado"}

RULES = [
 (r"^(Strong listing|Weak listing|Delay|Market fall) · (.*)$", lambda m: f"{SCEN_ES[m[1]]} · {m[2]}"),
 (r"^([\d.]+) years after ChatGPT, the AI build-out shows (\d) of 6 signs of a late frenzy and (?:none of the signs of a turning point|(\d) of 6 signs of a turning point)\.$",
  lambda m: f"A {_n(m[1])} años de ChatGPT, la construcción de la IA muestra {m[2]} de las 6 señales de un frenesí tardío y " + ("ninguna de punto de giro." if not m[3] else f"{m[3]} de las 6 de punto de giro.")),
 (r"^Following “The Sharp End of AI Debt” \(Acedo, 2026\)\. Prices updated every weekday, filings every week; last update (.+)\.$",
  lambda m: f"Sigue las medidas de «The Sharp End of AI Debt» (Acedo, 2026). Precios actualizados cada día laborable y documentos cada semana; última actualización {m[1]}."),
 (r"^(\d+) signals?$", lambda m: f"{m[1]} señal" + ("es" if m[1] != "1" else "")),
 (r"^Who carries the risk of the AI build-out, measured every week\. Following “The Sharp End of AI Debt” \(Acedo, 2026\); prices updated every weekday, filings every week; last update (.+)\.$",
  lambda m: f"Quién carga con el riesgo de la construcción de la IA, medido cada semana. Sigue las medidas de «The Sharp End of AI Debt» (Acedo, 2026); precios cada día laborable y documentos cada semana; última actualización {m[1]}."),
 (r"^Like the four points of a compass: (.*) Bets last recorded (.+)\.$",
  lambda m: f"Como los cuatro puntos cardinales: cada posición es uno de los caminos de salida a bolsa del artículo, con quién la sostiene, qué se juega y qué dicen hoy los datos. Apuestas registradas por última vez el {m[2]}."),
 (r"^Heading: (.+?)\. (.*?)( The dotted trail shows the heading over the last (\d+) updates\.| The trail of past headings will appear as updates accumulate\.) The needle adds up the explicit signals listed in each position below; it is a count of evidence, not a probability\.$",
  lambda m: "Rumbo: " + _heading_es(m[1], m[2]) + (f" La estela punteada muestra el rumbo de las últimas {m[4]} actualizaciones." if m[4] else " La estela de los rumbos pasados irá apareciendo con las actualizaciones.")
            + " La aguja suma las señales explícitas que figuran en cada posición; es un recuento de evidencias, no una probabilidad."),
 (r"^NOT_USED_BALANCE$",
  lambda m: "Las señales se compensan: las evidencias aún no han elegido camino. La aguja suma las señales actuales; es un recuento de evidencias, no una probabilidad."),
 (r"^The needle leans towards (.+)\. The needle adds up the current signals; it is a count of evidence, not a probability\.$",
  lambda m: "La aguja se inclina hacia " + ", ".join(SCEN_ES.get(x.strip().capitalize(), x) .lower() for x in m[1].split(",")) + ". La aguja suma las señales actuales; es un recuento de evidencias, no una probabilidad."),
 (r"^peak (\d{4})$", lambda m: f"pico {m[1]}"),
 (r"^Today, ([\d.]+) years in$", lambda m: f"Hoy, a {_n(m[1])} años"),
 (r"^AI supply chain ([\d.]+)x since ChatGPT$", lambda m: f"Cadena de la IA: {_n(m[1])}x desde ChatGPT"),
 (r"^(Software|Chips, power|10-year|Oracle|CoreWeave|SoftBank|Zhipu|MiniMax|SpaceX \(with xAI\)) ([+-]?[\d.,]+%?)$",
  lambda m: f"{CHAINS.get(m[1], m[1].replace('(with xAI)', '(con xAI)'))} {_n(m[2])}"),
 (r"^([\d.]+)% \((contracted|invested|leases|guarantee cap|loan|stake)\)$", lambda m: f"{_n(m[1])} % ({KIND[m[2]]})"),
 (r"^(Above|Below) the range of past booms at ([\d.]+) years\. (.*)$",
  lambda m: f"{'Por encima' if m[1] == 'Above' else 'Por debajo'} del rango de los booms pasados a {_n(m[2])} años. " + _peak(m[3])),
 (r"^Within the range of past booms at ([\d.]+) years\. (.*)$", lambda m: f"Dentro del rango de los booms pasados a {_n(m[1])} años. " + _peak(m[2])),
 (r"^(\d) of the six features are present\.$", lambda m: f"Aparecen {m[1]} de los seis rasgos."),
 (r"^([\d.]+) times all of 2025, with the year not over\.$", lambda m: f"{_n(m[1])} veces todo 2025, sin haber terminado el año."),
 (r"^Highest since (\d{4}): dearer refinancing for a build-out financed with debt\.$", lambda m: f"El más alto desde {m[1]}: refinanciarse sale más caro en una construcción financiada con deuda."),
 (r"^In the last twelve months the lenders lagged other financial stocks by ([\d.]+) points a day when AI fell hardest, beyond any year before 2024\. (.*)$",
  lambda m: f"En los últimos doce meses, los financiadores han quedado {_n(m[1])} puntos al día por detrás del resto de las financieras cuando más cayó la IA, más que en cualquier año anterior a 2024. "
            + "Financiadores e inversores en infraestructura de IA frente al resto de las financieras, en los días en que más cae la cadena de la IA, descontando el mercado (puntos al día). Sombreado: el rango de 2016-2023 (años con al menos cinco días de caída). Los umbrales solo usan datos pasados, así que los valores anuales difieren un poco de los del artículo."),
 (r"^In the last twelve months the gap was ([+-][\d.]+) points a day, back inside the range of 2016-2023\. (.*)$",
  lambda m: f"En los últimos doce meses la brecha fue de {_n(m[1])} puntos al día, de vuelta en el rango de 2016-2023. Financiadores e inversores en infraestructura de IA frente al resto de las financieras, en los días en que más cae la cadena de la IA, descontando el mercado (puntos al día). Sombreado: el rango de 2016-2023. Los umbrales solo usan datos pasados."),
 (r"^When the AI chain falls 10%, the lenders now fall about ([\d.]+)% and other financial stocks ([\d.]+)%; in 2020-2023, ([\d.]+)% and ([\d.]+)%\.$",
  lambda m: f"Cuando la cadena de la IA cae un 10 %, los financiadores caen ahora alrededor de un {_n(m[1])} % y el resto de las financieras un {_n(m[2])} %; en 2020-2023, un {_n(m[3])} % y un {_n(m[4])} %."),
 (r"^([\d.]+)% on (\S+), ([+-]\d+) basis points in three months\. When last measured \(2 October 2026\), rising rates had not widened the lenders' gap\.$",
  lambda m: f"{_n(m[1])} % el {m[2]}, {m[3]} puntos básicos en tres meses. En la última medición (2 de octubre de 2026), la subida de tipos no había ampliado la brecha de los financiadores."),
 (r"^Sources: (.*)Data status: (.*)\. Manual files: (.*)\.$",
  lambda m: "Fuentes: precios diarios de Stooq, con Yahoo Finance de respaldo; bono a 10 años de FRED; documentos de SEC EDGAR; booms pasados de la Kenneth French Data Library; acontecimientos, apuestas y cifras del registro público que figura en el repositorio, cada uno con su fuente. "
            + f"Estado de los datos: {m[2]}. Ficheros manuales: {m[3].replace('last entry', 'última entrada').replace('(stale)', '(caducado)')}."),
 (r"^NOT_USED_(.*)(.+)$",
  lambda m: f"Cada casa es uno de los cuatro caminos de salida a bolsa del artículo: quién está en ella, qué se juega y qué dicen hoy los datos. Los recuentos de señales son evidencias, no probabilidades. Apuestas registradas por última vez el {m[2]}."),
]


HEAD_ES = {"towards a strong listing": "hacia una salida fuerte", "towards listings, but later than planned": "hacia salidas a bolsa, pero más tarde de lo previsto",
           "towards a delay": "hacia el aplazamiento", "towards a longer delay in a weakening market": "hacia un aplazamiento más largo en un mercado que se debilita",
           "towards a market fall": "hacia una caída del mercado", "towards weak listings in a falling market": "hacia salidas débiles en un mercado que cae",
           "towards a weak listing": "hacia una salida débil", "towards listings that go ahead below the private rounds": "hacia salidas que siguen adelante por debajo de las rondas privadas"}
PT_ES = {"N": "norte", "NE": "noreste", "E": "este", "SE": "sureste", "S": "sur", "SW": "suroeste", "W": "oeste", "NW": "noroeste"}


def _heading_es(head, rest):
    if head.startswith("centre"):
        return "centro. Las señales se compensan: las evidencias aún no han elegido camino."
    pt, _, reading = head.partition(", ")
    return f"{PT_ES.get(pt, pt)}, {HEAD_ES.get(reading, reading)}."


def _peak(t):
    m = re.match(r"^([\d.]+)% below its peak: past the 20% mark that defines a bear market\.$", t)
    if m:
        return f"Un {_n(m[1])} % por debajo de su máximo: más allá del 20 % que define un mercado bajista."
    m = re.match(r"^([\d.]+)% below its peak\.$", t)
    if m:
        return f"Un {_n(m[1])} % por debajo de su máximo."
    return "En su máximo." if t.strip() == "At its peak." else t


CITE = [("Table 3 of the paper", "Tabla 3 del artículo"), ("Company projection reported by the Financial Times, via", "Proyección de la empresa publicada por el Financial Times, vía"),
        ("Prospectus as reported by Reuters, via", "Folleto según Reuters, vía"), ("cited by the Bank of England FPC record of", "citado en el acta del FPC del Banco de Inglaterra del"),
        ("Bloomberg via", "Bloomberg vía"), ("Reuters via", "Reuters vía"), ("Nikkei study via", "Estudio de Nikkei vía"), ("FPC record,", "Acta del FPC,"),
        ("Nikkei study, Aug 2026", "estudio de Nikkei, ago 2026")]


def tr(text):
    t = text.strip()
    if not t:
        return text
    if t.startswith("(") and t.endswith(")"):
        u = t
        for a, b in CITE:
            u = u.replace(a, b)
        return text.replace(t, u)
    if t in ES:
        return text.replace(t, ES[t])
    for pat, f in RULES:
        m = re.match(pat, t, re.S)
        if m:
            return text.replace(t, f(m))
    return text


NUM = re.compile(r"^([+-]?)([\d,]*\d)(\.\d+)?(%|x)?$")


def localize_number(t):
    """3.88x -> 3,88x; 1,400.0 -> 1.400,0; 76.9% -> 76,9 %."""
    m = NUM.match(t.strip())
    if not m:
        return None
    sign, ints, dec, suf = m.groups()
    out = sign + ints.replace(",", ".") + (dec.replace(".", ",") if dec else "")
    return out + (" %" if suf == "%" else (suf or ""))


def translate_html(page):
    """Translate every text node and the aria-labels of a rendered English page."""
    def node(m):
        raw = m.group(1)
        num = localize_number(H.unescape(raw))
        if num is not None:
            return ">" + raw.replace(raw.strip(), num) + "<"
        if not re.search(r"[A-Za-z]{2,}", raw):
            return m.group(0)
        return ">" + H.escape(tr(H.unescape(raw)), quote=False) + "<"
    head, sep, body = page.partition("<body>")
    body = re.sub(r">([^<>]+)<", node, body)
    body = re.sub(r'aria-label="([^"]+)"', lambda m: f'aria-label="{H.escape(tr(H.unescape(m[1])))}"', body)
    return head + sep + body


def untranslated(page_es):
    """Text nodes of the Spanish page that still look English, for checking."""
    body = page_es.partition("<body>")[2]
    body = re.sub(r"<script>.*?</script>", " ", body, flags=re.S)
    out = []
    for raw in re.findall(r">([^<>]+)<", body):
        t = H.unescape(raw).strip()
        if re.search(r"\b(the|and|of|since|with|from|their|this|is|are|its)\b", t) and t not in ES.values():
            out.append(t)
    return list(dict.fromkeys(out))


CALC_ES = [
 ("US stock index fund (S&P 500)", "Fondo indexado de bolsa de EE. UU. (S&P 500)"),
 ("Large AI weight; the S&P 500 will not add OpenAI or Anthropic for at least twelve months and only with profits.", "Mucho peso de la IA; el S&P 500 no incluirá a OpenAI ni a Anthropic hasta pasados al menos doce meses y solo con beneficios."),
 ("Nasdaq-100 or technology fund", "Fondo del Nasdaq-100 o tecnológico"),
 ("Must buy new giant listings within about fifteen trading days, so it carries their first price swings.", "Tiene que comprar las grandes salidas a bolsa en unas quince sesiones, así que carga con sus primeros vaivenes."),
 ("Global stock fund", "Fondo de bolsa global"), ("Same channels as the S&P 500, diluted by other markets.", "Los mismos canales que el S&P 500, diluidos por otros mercados."),
 ("Investment-grade bond fund", "Fondo de bonos con grado de inversión"),
 ("AI groups are a leading source of new bonds and lengthen the index's duration.", "Los grupos de la IA son una de las principales fuentes de bonos nuevos y alargan la duración del índice."),
 ("Pension plan or life insurance", "Plan de pensiones o seguro de vida"),
 ("Insurers and pension managers bought data-centre bonds and hold private credit.", "Aseguradoras y gestoras de pensiones compraron bonos de centros de datos y tienen crédito privado."),
 ("Private credit fund or listed BDC", "Fondo de crédito privado o BDC cotizado"),
 ("Sensitive to AI-dependent borrowers; some funds limited redemptions this year.", "Sensible a prestatarios que dependen de la IA; algunos fondos limitaron los reembolsos este año."),
 ("Shares in Oracle, CoreWeave or SoftBank", "Acciones de Oracle, CoreWeave o SoftBank"),
 ("The three balance sheets that carry OpenAI's counterparty risk.", "Los tres balances que cargan con el riesgo de contraparte de OpenAI."),
 ("Shares in Nvidia, Microsoft, Amazon or Alphabet", "Acciones de Nvidia, Microsoft, Amazon o Alphabet"),
 ("Large exposure in money, small relative to their value.", "Mucha exposición en dinero, poca en proporción a su valor."),
 ("Pre-IPO or private AI fund", "Fondo privado o previo a la salida a bolsa de IA"),
 ("Bets directly on the listing price; hard to sell before it.", "Apuesta directamente al precio de salida; difícil de vender antes."),
 ("Deposits, cash or government bonds", "Depósitos, efectivo o deuda pública"),
 ("Outside the AI chain; government bonds tend to gain when equities fall.", "Fuera de la cadena de la IA; la deuda pública suele ganar cuando cae la bolsa."),
 ('"the strong-listing position","the weak-listing position","the delay position","the market-fall position"', '"la posición de salida fuerte","la posición de salida débil","la posición de aplazamiento","la posición de caída del mercado"'),
 ("Enter at least one percentage to see how each path would reach your savings.", "Introduce al menos un porcentaje para ver cómo llegaría cada camino a tus ahorros."),
 ("Your savings sit closest to ${S[best]}, and are most exposed to ${S[worst]}.", "Tus ahorros están más cerca de ${S[best]} y son más sensibles a ${S[worst]}."),
 ("<th>Position</th><th>Your mix</th>", "<th>Posición</th><th>Tu combinación</th>"), ('n.replace("the ","").replace(" position","")', 'n.replace("la posición de ","")'),
 ('"gains"', '"gana"'), ('"leans to gain"', '"tiende a ganar"'), ('"little affected"', '"apenas le afecta"'), ('"leans to lose"', '"tiende a perder"'), ('"loses"', '"pierde"'),
 ("How each path reaches you", "Cómo te llega cada camino"),
 ("A qualitative reading of the mechanisms documented in the paper, not a forecast of returns and not investment advice.", "Una lectura cualitativa de los mecanismos documentados en el artículo; no es una previsión de rentabilidad ni una recomendación de inversión."),
 ("'no data yet'", "'sin datos aún'"), ("'unchanged'", "'sin cambios'"), ("' vs last year'", "' frente al año pasado'"), ("toLocaleString('en-US'", "toLocaleString('es-ES'"),
]


def translate_scripts(page):
    for a, b in CALC_ES:
        page = page.replace(a, b)
    return page


# ---------------------------------------------------------------------------------------------------------------
# Spanish rewritten as Spanish (October 2026), with a fixed glossary:
#   AI build-out = inversión en infraestructura de IA / despliegue de la IA; lenders = prestamistas de la IA
#   (financiadores when investors are included); tenants = clientes de los centros de datos; frontier listing =
#   salida a bolsa de un gran laboratorio de IA; sell-off days = jornadas de mayor caída de la IA; boom = auge;
#   frenzy = frenesí; turning point = punto de inflexión; telecoms = telecomunicaciones.
# ---------------------------------------------------------------------------------------------------------------
ES.update({
 "Now": "Hoy", "Positions": "Posiciones", "Your savings": "Tus ahorros", "History": "Historia", "Evidence": "Pruebas",
 "1 week": "1 semana", "1 month": "1 mes", "3 months": "3 meses", "Year to date": "En lo que va de año",
 "no data yet": "aún sin datos", "unchanged": "sin cambios", "of 6": "de 6", "Change over": "Variación en",
 "Lenders' gap in AI sell-offs, last 12 months": "Rezago de los prestamistas en las peores jornadas de la IA, últimos 12 meses",
 "Inside its 2024-2026 range: the market still singles out the AI-dependent lenders.": "Dentro de su rango de 2024-2026: el mercado sigue castigando a los prestamistas que dependen de la IA.",
 "Back inside its pre-2024 range: the market no longer singles out the lenders.": "De vuelta a su rango anterior a 2024: el mercado ya no castiga a los prestamistas.",
 "Wider than any year since 2024: the lenders are lagging more than ever.": "Mayor que en cualquier año desde 2024: los prestamistas se quedan más atrás que nunca.",
 "Above its usual range.": "Por encima de su rango habitual.",
 "Zones from its own history (2016-2023 and 2024-2026)": "Zonas según su propia historia (2016-2023 y 2024-2026)",
 "AI supply chain since ChatGPT": "Cadena de suministro de la IA desde ChatGPT",
 "Grey band: past booms at the same age (chart above)": "En gris, los auges anteriores a la misma edad (ver la gráfica histórica)",
 "Signs of a turning point": "Señales de punto de inflexión", "Signs of a late frenzy": "Señales de frenesí avanzado",
 "None of the six features is present yet.": "Todavía no aparece ninguno de los seis rasgos.",
 "All six features of a late frenzy are present.": "Aparecen los seis rasgos de un frenesí avanzado.",
 "Each sign tied to a data series or a sourced event": "Cada señal se apoya en una serie de datos o en un hecho con fuente",
 "Oracle's largest item with OpenAI, share of its value": "Lo que Oracle tiene comprometido con OpenAI, en proporción a su valor",
 "Broadcom's largest item with Anthropic, share of its value": "Lo que Broadcom tiene comprometido con Anthropic, en proporción a su valor",
 "Over 20% of its value rests on one tenant: in the zone of the exposed companies.": "Más de una quinta parte de su valor depende de un solo cliente: está en la zona de las empresas expuestas.",
 "Under 10% of its value: in the zone of the companies that could absorb a failure.": "Menos del 10 % de su valor: está en la zona de las empresas que podrían encajar un impago.",
 "Between the two groups of Table 3: worth watching.": "Entre los dos grupos de la tabla 3: conviene vigilarla.",
 "Zones are this paper's reading of Table 3: the giants sit under 10%, the exposed above 20%": "Las zonas son la lectura que hace el artículo de su tabla 3: los gigantes quedan por debajo del 10 % y las empresas expuestas, por encima del 20 %",
 "See the full panel: eight more numbers": "Ver el panel completo: ocho indicadores más",
 "Oracle against the AI chain since Jan 2025": "Oracle frente al resto de la cadena de la IA desde enero de 2025",
 "CoreWeave against the AI chain since Jan 2025": "CoreWeave frente al resto de la cadena de la IA desde enero de 2025",
 "SoftBank against the Tokyo market since Jan 2025": "SoftBank frente a la bolsa de Tokio desde enero de 2025",
 "Near the bottom of its 52-week range: the market keeps weighing its exposure to OpenAI.": "Cerca del mínimo de las últimas 52 semanas: el mercado sigue penalizando su exposición a OpenAI.",
 "Near the top of its 52-week range.": "Cerca del máximo de las últimas 52 semanas.", "In the middle of its 52-week range.": "En la mitad de su rango de las últimas 52 semanas.",
 "Bar: its 52-week range": "La barra muestra su rango de las últimas 52 semanas",
 "Lenders' link to chips and power, this year": "Vínculo de los prestamistas con chips y energía este año",
 "Above its pre-2024 range: the lenders still move with chips and power beyond the market.": "Por encima de su rango anterior a 2024: los prestamistas siguen moviéndose con los chips y la energía más allá de lo que explica el mercado.",
 "Back inside its pre-2024 range: the link to chips and power has faded.": "De vuelta a su rango anterior a 2024: el vínculo con los chips y la energía se ha diluido.",
 "Blue band: its 2016-2023 range": "En azul, su rango de 2016-2023",
 "Capital raised for AI in 2026 so far": "Dinero captado para la IA en lo que va de 2026",
 "Grey band: all of 2025 (Barclays)": "En gris, el total de 2025 (Barclays)",
 "10-year Treasury yield": "Rentabilidad del bono estadounidense a 10 años",
 "Dearer refinancing matters for a build-out financed with debt.": "Refinanciarse sale más caro, y eso pesa en una inversión pagada con deuda.",
 "Bar: its 20-year range (FRED)": "La barra muestra su rango de los últimos 20 años (FRED)",
 "What the twelve signs are, and which are present": "Las doce señales y cuáles aparecen hoy", "present": "aparece", "absent": "no aparece",
 "Everything that changed since the previous update": "Todo lo que ha cambiado desde la última actualización",
 "First update of the monitor.": "Primera actualización de la web.", "No change since the previous update.": "Sin cambios desde la última actualización.",
 "Main characters": "Quién la sostiene", "Four positions on the AI listings": "Cuatro posiciones ante las salidas a bolsa de la IA",
 "Which position do your savings hold?": "¿En qué posición están tus ahorros?", "Show the position my savings hold": "Ver en qué posición están mis ahorros",
 "Where the current signals point among the four positions": "Hacia dónde apuntan hoy las señales entre las cuatro posiciones",
 "What the data show now": "Lo que dicen hoy los datos", "No current signal.": "Ninguna señal por ahora.",
 "Strong listing": "Salida fuerte", "Weak listing": "Salida débil", "Delay": "Aplazamiento", "Market fall": "Caída del mercado",
 "Where past booms went from here": "Adónde fueron los auges anteriores desde este punto",
 "Technology booms": "Auges tecnológicos", "Energy booms": "Auges energéticos", "Credit boom": "Auge del crédito",
 "years since the start of the frenzy": "años desde el inicio del frenesí",
 "Oil, 1979-89": "Petróleo, 1979-89", "Tech and telecoms, 1995-2003": "Tecnología y telecomunicaciones, 1995-2003", "Credit, 2003-13": "Crédito, 2003-13",
 "Shale, 2010-20": "Esquisto, 2010-20", "US market, 1926-34": "Bolsa de EE. UU., 1926-34", "Utilities, 1926-34": "Eléctricas, 1926-34",
 "US railroads, 1865-75": "Ferrocarriles de EE. UU., 1865-75",
 "Past booms from the start of their frenzy, rebased to 100, in calendar years: technology (electric utilities and the US market from July 1926; software, hardware, chips and telecoms from the Netscape listing in August 1995; US railroads from the end of the Civil War in April 1865 to beyond the Panic of 1873, monthly), energy (oil from January 1979, when the Shah left Iran; shale from January 2010) and credit (banks, finance and real estate from the Federal Reserve's cut to 1% in June 2003). Blue: the AI supply chain from the launch of ChatGPT, extended every week. The start dates are conventions, not forecasts: other dates would shift the curves. Total returns except the railroads (price index). The story begins earlier, with the printing press and the British railway mania of the 1840s, for which no price series is freely available. Sources: Kenneth French Data Library; F.R. Macaulay via NBER and FRED; daily prices.":
  "Cada curva gris es un auge anterior, contado desde el inicio de su frenesí, con base 100 y en años de calendario. Tecnológicos: las eléctricas y la bolsa de EE. UU. desde julio de 1926; el software, el hardware, los chips y las telecomunicaciones desde la salida a bolsa de Netscape, en agosto de 1995; y los ferrocarriles de EE. UU. desde el final de la guerra de Secesión, en abril de 1865, hasta después del pánico de 1873 (datos mensuales). Energéticos: el petróleo desde enero de 1979, cuando el sah abandonó Irán, y el esquisto desde enero de 2010. Crédito: bancos, financieras e inmobiliarias desde que la Reserva Federal bajó los tipos al 1 %, en junio de 2003. En azul, la cadena de suministro de la IA desde el lanzamiento de ChatGPT, que avanza cada semana. Las fechas de inicio son convenciones, no previsiones: con otras fechas, las curvas se desplazarían. Todas las series incluyen dividendos salvo la de los ferrocarriles, que es un índice de precios. La historia empieza antes, con la imprenta y con la fiebre ferroviaria británica de la década de 1840, pero de esas épocas no hay series de precios de libre acceso. Fuentes: Kenneth French Data Library; F. R. Macaulay, vía NBER y FRED; precios diarios.",
 "The evidence": "Las pruebas", "The measures behind every number above, one question each.": "Las mediciones que sostienen cada indicador, una pregunta por apartado.",
 "Do the AI-dependent lenders still lag when AI falls?": "¿Siguen quedándose atrás los prestamistas de la IA cuando la IA cae?",
 "Is it the managers or their loan books, and since when?": "¿Son las gestoras o sus carteras de préstamos, y desde cuándo?",
 "Who carries OpenAI's and Anthropic's commitments?": "¿Quién carga con los compromisos de OpenAI y Anthropic?",
 "Who carries OpenAI's and Anthropic's commitments": "Quién carga con los compromisos de OpenAI y Anthropic",
 "How do the exposed companies and the listed tenants trade?": "¿Cómo cotizan las empresas expuestas y los clientes de los centros de datos que ya cotizan?",
 "Does the news move them?": "¿Les afectan las noticias?", "Cash, debt and supplier financing": "Caja, deuda y financiación de los proveedores",
 "Rates and the supplier warning sign": "Los tipos y la señal de alarma de los proveedores", "What the filings and the record say": "Lo que dicen los documentos oficiales y el registro de hechos",
 "Who lags, since 2024": "Quién se queda atrás desde 2024", "The managers, not their loan books": "Las gestoras, no sus carteras de préstamos",
 "The listed loan vehicles (BDCs) fall in AI sell-offs in almost every year; the managers' gap moved around zero before 2024 and has stayed negative since.":
  "Los vehículos de préstamo cotizados (los BDC estadounidenses) caen en las peores jornadas de la IA casi todos los años. El rezago de las gestoras, en cambio, rondaba el cero antes de 2024 y desde entonces se mantiene negativo.",
 "Year": "Año", "Lenders": "Prestamistas", "BDCs": "BDC", "Since when, and through what": "Desde cuándo y a través de qué",
 "The lenders' link to the AI chain beyond other financial stocks, net of the market and of the financial sector (equation 3), in hundredths of a correlation.":
  "Cuánto se mueven los prestamistas con la cadena de la IA más allá de lo que lo hacen las demás financieras, descontado el efecto del mercado y del sector financiero (ecuación 3), en centésimas de correlación.",
 "The largest documented item each listed counterparty has at stake with each tenant, as a share of its market value, updated weekly with prices. Items are different instruments and are not added.":
  "El mayor compromiso documentado de cada empresa cotizada con cada cliente de los centros de datos, en proporción a su valor en bolsa y actualizado cada semana con los precios. Son instrumentos distintos y no se suman.",
 "How the three exposed companies trade": "Cómo cotizan las tres empresas expuestas",
 "Since January 2025: Oracle and CoreWeave against the rest of the chain, SoftBank against the Tokyo market (%).": "Desde enero de 2025: Oracle y CoreWeave frente al resto de la cadena, y SoftBank frente a la bolsa de Tokio (%).",
 "Tenants that already have a public price": "Laboratorios de IA que ya cotizan",
 "Zhipu and MiniMax in Hong Kong since January, xAI inside SpaceX since June: change against the listing price (%).": "Zhipu y MiniMax, en Hong Kong desde enero, y xAI, dentro de SpaceX desde junio: variación respecto al precio de salida (%).",
 "No price data yet for these listings.": "Aún no hay precios de estas salidas a bolsa.",
 "Does SoftBank still move with OpenAI's news?": "¿Sigue moviéndose SoftBank con las noticias de OpenAI?",
 "SoftBank against the Tokyo market on the first session after each piece of news about OpenAI, in points. The paper predicts this fades if OpenAI lists.":
  "SoftBank frente a la bolsa de Tokio en la primera sesión tras cada noticia sobre OpenAI, en puntos. Según el artículo, esta reacción debería apagarse si OpenAI sale a bolsa.",
 "Date": "Fecha", "News": "Noticia", "Pts": "Puntos", "Announcement": "Anuncio", "Tenant": "Empresa", "Measure": "Concepto", "Quarter": "Trimestre",
 "Announcements against what the market does": "Los anuncios frente a la reacción del mercado",
 "Oracle and CoreWeave against the rest of the chain over the sessions after each capability announcement (%).": "Oracle y CoreWeave frente al resto de la cadena en las sesiones posteriores a cada anuncio de capacidades (%).",
 "No capability announcement on record yet.": "Aún no hay anuncios de capacidades registrados.",
 "Cash against the story": "La caja frente al relato", "The debt side: how far it has spread": "La deuda: hasta dónde se ha extendido",
 "Suppliers financing customers": "Proveedores que financian a sus clientes",
 "The warning sign of the telecoms boom: suppliers kept lending after outside capital left ($bn).": "La señal de alarma del auge de las telecomunicaciones: los proveedores siguieron prestando cuando el capital externo ya se había retirado (miles de millones de dólares).",
 "Supplier financing": "Financiación de proveedores", "Outside capital": "Capital externo", "The ten-year Treasury yield": "La rentabilidad del bono estadounidense a diez años",
 "What the new filings say": "Lo que dicen los últimos documentos oficiales", "Events on record": "Hechos registrados",
 "No new guarantee or off-balance-sheet language in the filings scanned so far.": "Los documentos revisados hasta ahora no contienen frases nuevas sobre garantías ni compromisos fuera de balance.",
 "Code and definitions:": "Código y definiciones:",
 ". The positions' emblems are this site's own. This page describes public market data; it is not investment advice.":
  ". Los emblemas de las posiciones son propios de esta web. Esta página describe datos públicos de mercado y no constituye una recomendación de inversión.",
 "Built with the assistance of Claude (Anthropic). Anthropic is one of the companies tracked here; its figures follow the same rules and sources as the others.":
  "Elaborada con la ayuda de Claude, de Anthropic. Anthropic es una de las empresas que sigue esta web, y sus cifras se tratan con las mismas reglas y fuentes que las demás.",
 "Split your savings across these doors (rough percentages; they need not add up exactly).": "Reparte tus ahorros entre estas opciones (porcentajes aproximados; no hace falta que sumen exactamente 100).",
 "Show or hide groups of past booms": "Mostrar u ocultar grupos de auges anteriores",
})

SCEN_ES = {"Strong listing": "Salida fuerte", "Weak listing": "Salida débil", "Delay": "Aplazamiento", "Market fall": "Caída del mercado"}
KIND = {"contracted": "contratado", "invested": "invertido", "leases": "arrendamientos", "guarantee cap": "garantía máxima", "loan": "préstamo", "stake": "participación"}
CHAINS = {"Software": "Software", "Chips, power": "Chips y energía", "10-year": "Bono a 10 años", "Oracle": "Oracle", "CoreWeave": "CoreWeave", "SoftBank": "SoftBank"}
HEAD_ES = {"towards a strong listing": "hacia una salida fuerte", "towards listings, but later than planned": "hacia las salidas a bolsa, pero más tarde de lo previsto",
           "towards a delay": "hacia el aplazamiento", "towards a longer delay in a weakening market": "hacia un aplazamiento largo, con el mercado debilitándose",
           "towards a market fall": "hacia una caída del mercado", "towards weak listings in a falling market": "hacia salidas débiles en un mercado a la baja",
           "towards a weak listing": "hacia una salida débil", "towards listings that go ahead below the private rounds": "hacia salidas a bolsa por debajo del precio de las rondas privadas"}
MESES = {"01": "ene", "02": "feb", "03": "mar", "04": "abr", "05": "may", "06": "jun", "07": "jul", "08": "ago", "09": "sept", "10": "oct", "11": "nov", "12": "dic"}
MESES_EN = {"Jan": "ene", "Feb": "feb", "Mar": "mar", "Apr": "abr", "May": "may", "Jun": "jun", "Jul": "jul", "Aug": "ago", "Sep": "sept", "Oct": "oct", "Nov": "nov", "Dec": "dic",
            "January": "enero de", "July": "julio de", "June": "junio de", "August": "agosto de", "September": "septiembre de", "May ": "mayo de "}


def fecha(iso):
    y, m, d = iso.split("-")
    return f"{int(d)} {MESES[m]} {y}"


def _fechas(t):
    return re.sub(r"\b(\d{4})-(\d{2})-(\d{2})\b", lambda m: fecha(m.group(0)), t)


CITE = [("Table 3 of the paper", "tabla 3 del artículo"), ("Company projection reported by the Financial Times, via", "proyección de la empresa publicada por el Financial Times, vía"),
        ("Prospectus as reported by Reuters, via", "folleto según Reuters, vía"), ("cited by the Bank of England FPC record of", "citado en el acta del Comité de Política Financiera del Banco de Inglaterra del"),
        ("Bank of England FPC", "Comité de Política Financiera del Banco de Inglaterra"), ("FPC record,", "acta del Comité de Política Financiera,"),
        ("Bloomberg via", "Bloomberg, vía"), ("Reuters via", "Reuters, vía"), ("Nikkei study via", "estudio de Nikkei, vía"), ("Nikkei study,", "estudio de Nikkei,"),
        ("Company projection", "proyección de la empresa"), ("updated", "actualizado el"), ("on Polymarket prices of", "con precios de Polymarket del")]


def _cita(t):
    for a, b in CITE:
        t = t.replace(a, b)
    t = re.sub(r"\b(January|June|July|August|September)\b", lambda m: MESES_EN[m[1]], t)
    t = re.sub(r"\b(\d{1,2}) (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) (\d{4})\b", lambda m: f"{m[1]} {MESES_EN[m[2]]} {m[3]}", t)
    t = re.sub(r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) (\d{4})\b", lambda m: f"{MESES_EN[m[1]]} {m[2]}", t)
    return t


def _n(x):
    return x.replace(".", ",")


RULES = [
 (r"^(Strong listing|Weak listing|Delay|Market fall) · (.*)$", lambda m: f"{SCEN_ES[m[1]]} · {m[2]}"),
 (r"^([\d.]+) years after ChatGPT, the AI build-out shows (\d) of 6 signs of a late frenzy and (?:none of the signs of a turning point|(\d) of 6 signs of a turning point)\.$",
  lambda m: f"A {_n(m[1])} años del lanzamiento de ChatGPT, la inversión en infraestructura de IA muestra {m[2]} de las 6 señales de un frenesí avanzado y "
            + ("ninguna de un punto de inflexión." if not m[3] else f"{m[3]} de las 6 de un punto de inflexión.")),
 (r"^(\d+) signals?$", lambda m: f"{m[1]} señal" + ("es" if m[1] != "1" else "")),
 (r"^Who carries the risk of the AI build-out, measured every week\. Following “The Sharp End of AI Debt” \(Acedo, 2026\); prices updated every weekday, filings every week; last update (.+)\.$",
  lambda m: f"Quién carga con el riesgo de la inversión en infraestructura de IA, medido cada semana. Basado en «The Sharp End of AI Debt» (Acedo, 2026). Los precios se actualizan cada día laborable y los documentos oficiales, cada semana. Última actualización: {fecha(m[1]) if re.match(r'^\d{4}-\d{2}-\d{2}$', m[1]) else m[1]}."),
 (r"^Like the four points of a compass: (.*) Bets last recorded (.+)\.$",
  lambda m: f"Como los cuatro puntos cardinales: cada posición es uno de los caminos que el artículo plantea para las salidas a bolsa de la IA, con quién la sostiene, qué se juega y qué dicen hoy los datos. Últimas apuestas registradas: {fecha(m[2]) if re.match(r'^\d{4}-\d{2}-\d{2}$', m[2]) else m[2]}."),
 (r"^Heading: (.+?)\. (.*?)( The dotted trail shows the heading over the last (\d+) updates\.| The trail of past headings will appear as updates accumulate\.) The needle adds up the explicit signals listed in each position below; it is a count of evidence, not a probability\.$",
  lambda m: "Rumbo: " + _heading_es(m[1], m[2]) + (f" La línea de puntos muestra el rumbo de las últimas {m[4]} actualizaciones." if m[4] else " La estela de rumbos anteriores irá apareciendo con las próximas actualizaciones.")
            + " La aguja suma las señales que figuran en cada posición: es un recuento de pruebas, no una probabilidad."),
 (r"^peak (\d{4})$", lambda m: f"máximo de {m[1]}"),
 (r"^Today, ([\d.]+) years in$", lambda m: f"Hoy, a {_n(m[1])} años"),
 (r"^AI supply chain ([\d.]+)x since ChatGPT$", lambda m: f"Cadena de la IA: ×{_n(m[1])} desde ChatGPT"),
 (r"^(Software|Chips, power|10-year|Oracle|CoreWeave|SoftBank|Zhipu|MiniMax|SpaceX \(with xAI\)) ([+-]?[\d.,]+%?)$",
  lambda m: f"{CHAINS.get(m[1], m[1].replace('(with xAI)', '(con xAI)'))} {_n(m[2])}"),
 (r"^([\d.]+)% \((contracted|invested|leases|guarantee cap|loan|stake)\)$", lambda m: f"{_n(m[1])} % ({KIND[m[2]]})"),
 (r"^(Above|Below) the range of past booms at ([\d.]+) years\. (.*)$",
  lambda m: f"{'Por encima' if m[1] == 'Above' else 'Por debajo'} de lo que hicieron los auges anteriores a {_n(m[2])} años de su inicio. " + _peak(m[3])),
 (r"^Within the range of past booms at ([\d.]+) years\. (.*)$", lambda m: f"Dentro de lo que hicieron los auges anteriores a {_n(m[1])} años de su inicio. " + _peak(m[2])),
 (r"^(\d) of the six features are present\.$", lambda m: f"Aparecen {m[1]} de los seis rasgos."),
 (r"^([\d.]+) times all of 2025, with the year not over\.$", lambda m: f"{_n(m[1])} veces todo lo captado en 2025, y el año aún no ha terminado."),
 (r"^Highest since (\d{4}): dearer refinancing for a build-out financed with debt\.$", lambda m: f"La más alta desde {m[1]}: refinanciarse sale más caro, y eso pesa en una inversión pagada con deuda."),
 (r"^In the last twelve months the lenders lagged other financial stocks by ([\d.]+) points a day when AI fell hardest, beyond any year before 2024\. (.*)$",
  lambda m: f"En los últimos doce meses, en las peores jornadas de la IA, los prestamistas de la IA se han quedado {_n(m[1])} puntos al día por detrás del resto de las financieras, más que en cualquier año anterior a 2024. "
            + "La gráfica compara a los prestamistas e inversores en infraestructura de IA con el resto de las financieras en las jornadas de mayor caída de la IA, descontado el efecto del mercado (puntos al día). La franja sombreada es el rango de 2016-2023 (años con al menos cinco jornadas de caída). Los umbrales solo usan datos pasados, por lo que los valores anuales difieren ligeramente de los del artículo."),
 (r"^In the last twelve months the gap was ([+-][\d.]+) points a day, back inside the range of 2016-2023\. (.*)$",
  lambda m: f"En los últimos doce meses, el rezago fue de {_n(m[1])} puntos al día, de nuevo dentro del rango de 2016-2023. La gráfica compara a los prestamistas e inversores en infraestructura de IA con el resto de las financieras en las jornadas de mayor caída de la IA, descontado el efecto del mercado. La franja sombreada es el rango de 2016-2023."),
 (r"^When the AI chain falls 10%, the lenders now fall about ([\d.]+)% and other financial stocks ([\d.]+)%; in 2020-2023, ([\d.]+)% and ([\d.]+)%\.$",
  lambda m: f"Hoy, cuando la cadena de la IA cae un 10 %, los prestamistas caen alrededor de un {_n(m[1])} % y el resto de las financieras, un {_n(m[2])} %. En 2020-2023 las caídas eran del {_n(m[3])} % y del {_n(m[4])} %."),
 (r"^([\d.]+)% on (\S+), ([+-]\d+) basis points in three months\. When last measured \(2 October 2026\), rising rates had not widened the lenders' gap\.$",
  lambda m: f"{_n(m[1])} % el {fecha(m[2]) if re.match(r'^\d{4}-\d{2}-\d{2}$', m[2]) else m[2]}, {m[3]} puntos básicos en tres meses. En la última medición (2 de octubre de 2026), la subida de tipos no había agrandado el rezago de los prestamistas."),
 (r"^Sources: (.*)Data status: (.*)\. Manual files: (.*)\.$",
  lambda m: "Fuentes: precios diarios de Stooq, con Yahoo Finance como respaldo; rentabilidad del bono a 10 años de FRED; documentos oficiales de SEC EDGAR; auges anteriores de la Kenneth French Data Library; hechos, apuestas y cifras del registro público que recoge el repositorio, cada uno con su fuente. "
            + f"Estado de los datos: {m[2]}. Ficheros que se actualizan a mano: {_fechas(m[3]).replace('last entry', 'última entrada').replace('(stale)', '(desactualizado)')}."),
]


def _heading_es(head, rest):
    if head.startswith("centre"):
        return "centro. Las señales se compensan: las pruebas aún no apuntan a ningún camino."
    pt, _, reading = head.partition(", ")
    return f"{PT_ES.get(pt, pt)}, {HEAD_ES.get(reading, reading)}."


_tr_old = tr


def tr(text):
    t = text.strip()
    if t.startswith("(") and t.endswith(")"):
        return text.replace(t, _cita(t))
    out = _tr_old(text)
    return _fechas(out) if out != text or re.fullmatch(r"\s*\d{4}-\d{2}-\d{2}\s*", text) else out


CALC_ES = [(a, b) for a, b in CALC_ES if not a.startswith('"the strong-listing')] + [
 ('"the strong-listing position","the weak-listing position","the delay position","the market-fall position"',
  '"la posición de salida fuerte","la posición de salida débil","la posición de aplazamiento","la posición de caída del mercado"')]
CALC_ES = [(a, {
 "Fondo indexado de bolsa de EE. UU. (S&P 500)": "Fondo indexado de bolsa estadounidense (S&P 500)",
 "Mucho peso de la IA; el S&P 500 no incluirá a OpenAI ni a Anthropic hasta pasados al menos doce meses y solo con beneficios.": "Tiene mucho peso en IA. El S&P 500 no incluirá a OpenAI ni a Anthropic hasta que pase al menos un año desde su salida y den beneficios.",
 "Tiene que comprar las grandes salidas a bolsa en unas quince sesiones, así que carga con sus primeros vaivenes.": "Debe comprar las grandes salidas a bolsa en unas quince sesiones, así que soporta sus primeros vaivenes.",
 "Los grupos de la IA son una de las principales fuentes de bonos nuevos y alargan la duración del índice.": "Las grandes empresas de IA están entre los mayores emisores de bonos nuevos y alargan el plazo medio del índice.",
 "Aseguradoras y gestoras de pensiones compraron bonos de centros de datos y tienen crédito privado.": "Aseguradoras y gestoras de pensiones han comprado bonos de centros de datos y tienen crédito privado.",
 "Sensible a prestatarios que dependen de la IA; algunos fondos limitaron los reembolsos este año.": "Expuesto a prestatarios que dependen de la IA; algunos de estos fondos han limitado los reembolsos este año.",
 "Fondo de crédito privado o BDC cotizado": "Fondo de crédito privado o vehículo de préstamo cotizado (BDC)",
 "Los tres balances que cargan con el riesgo de contraparte de OpenAI.": "Son las tres empresas que cargan con el riesgo de que OpenAI no pague.",
 "Mucha exposición en dinero, poca en proporción a su valor.": "Mucho dinero en juego, pero poco en proporción a su tamaño.",
 "Fondo privado o previo a la salida a bolsa de IA": "Fondo de capital privado o de acciones previas a la salida a bolsa de empresas de IA",
 "Apuesta directamente al precio de salida; difícil de vender antes.": "Apuesta directamente por el precio de salida y es difícil de vender antes.",
 "Fuera de la cadena de la IA; la deuda pública suele ganar cuando cae la bolsa.": "Queda fuera de la cadena de la IA; la deuda pública suele revalorizarse cuando cae la bolsa.",
 "Introduce al menos un porcentaje para ver cómo llegaría cada camino a tus ahorros.": "Introduce al menos un porcentaje para ver cómo afectaría cada camino a tus ahorros.",
 "Tus ahorros están más cerca de ${S[best]} y son más sensibles a ${S[worst]}.": "Tus ahorros están más cerca de ${S[best]} y son más vulnerables a ${S[worst]}.",
 '"tiende a ganar"': '"tiende a ganar"', '"apenas le afecta"': '"apenas le afecta"',
 "Cómo te llega cada camino": "Cómo te afecta cada camino",
 "Una lectura cualitativa de los mecanismos documentados en el artículo; no es una previsión de rentabilidad ni una recomendación de inversión.": "Es una lectura cualitativa de los mecanismos que documenta el artículo; no es una previsión de rentabilidad ni una recomendación de inversión.",
 "'sin datos aún'": "'aún sin datos'",
}.get(b, b)) for a, b in CALC_ES]
