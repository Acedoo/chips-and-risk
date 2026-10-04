"""Two extra pages in both languages: the weekly archive and the method. Plain HTML with the site's look."""
import datetime
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCH = ROOT / "data" / "archive.json"
esc = lambda s: html.escape(str(s))

CSS = """:root{--ink:#14213D;--muted:#5B6B80;--rule:#E3E8EF;--panel:#F4F7FB;--calm:#2563EB}*{box-sizing:border-box}
body{margin:0;color:var(--ink);font:16px/1.65 'Instrument Sans',system-ui,-apple-system,sans-serif;-webkit-font-smoothing:antialiased}
main{max-width:46rem;margin:0 auto;padding:1.2rem 1.25rem 4rem}
.nav{display:flex;gap:1.1rem;align-items:center;padding:.7rem 0;border-bottom:1px solid var(--rule);overflow-x:auto;white-space:nowrap}
.nav a{color:var(--ink);text-decoration:none;font-size:.88rem}.nav .brand{font-weight:700;margin-right:auto}
.nav .lng{font-weight:600;border:1px solid var(--rule);border-radius:999px;padding:.1rem .55rem}
h1{font-family:'Newsreader',Georgia,serif;font-weight:400;font-size:2rem;line-height:1.2;margin:1.6rem 0 .4rem}
h2{font-size:1.15rem;margin:2rem 0 .4rem}p,li{color:#33415C}a{color:var(--calm)}
.issue{border-top:1px solid var(--rule);padding:1rem 0}.issue h3{margin:0;font-size:1rem}.issue .d{color:var(--muted);font-size:.85rem}
.issue ul{margin:.4rem 0 0;padding-left:1.1rem;font-size:.92rem}.lead{font-size:1.05rem}
footer{margin-top:3rem;padding-top:1rem;border-top:1px solid var(--rule);font-size:.85rem;color:var(--muted)}"""

T = {
 "en": {"home": "Dashboard", "method": "Method", "archive": "Archive", "brand": "Chips and Risk",
        "arch_title": "Weekly archive", "arch_lead": "One entry per week: the sentence of the week, where the needle pointed and what changed. Each entry is kept as it was published.",
        "issue": "Issue", "heading": "Heading", "changes": "What changed", "none": "No archived weeks yet.",
        "foot": "Chips and Risk measures who carries the risk of the AI build-out. It describes public market data; it is not investment advice."},
 "es": {"home": "Panel", "method": "Método", "archive": "Archivo", "brand": "Chips and Risk",
        "arch_title": "Archivo semanal", "arch_lead": "Una entrada por semana: la frase de la semana, hacia dónde apuntaba la aguja y qué cambió. Cada entrada se conserva tal como se publicó.",
        "issue": "Número", "heading": "Rumbo", "changes": "Qué cambió", "none": "Todavía no hay semanas archivadas.",
        "foot": "Chips and Risk mide quién carga con el riesgo de la inversión en infraestructura de IA. Describe datos públicos de mercado y no constituye una recomendación de inversión."}}

METHOD = {
"en": """<h1>Method</h1>
<p class="lead">Chips and Risk is not a bubble meter. It does not ask whether AI is overvalued, but who would carry the loss if the financing of the build-out broke down. Every number on the dashboard is measured or published, and the page says where it comes from.</p>
<h2>What is measured</h2>
<p>The lenders' gap compares eighteen listed lenders to and investors in AI infrastructure with twenty-four other financial stocks on the days when a basket of forty-six AI supply-chain companies falls hardest, net of the market. The exposure table divides the largest documented commitment of each listed counterparty of OpenAI and Anthropic by its market value, updated with prices. The past booms come from the Kenneth French Data Library and from Macaulay's railroad index. The filings come from SEC EDGAR, the yields from FRED, the prices from Stooq and Yahoo Finance.</p>
<h2>What is our reading</h2>
<p>Three things are judgment, and the dashboard says so: which features count as signs of a late frenzy or of a turning point (following Carlota Perez), which signal points to which of the four listing positions, and the two exposure zones (under 10% of value a company could absorb a failure, above 20% it is exposed), read from the gap in Table 3 of the paper. The savings calculator is a qualitative reading of the mechanisms in the paper.</p>
<h2>Why there is no single risk score</h2>
<p>Many AI dashboards add their indicators into one score from 0 to 100. This one does not. A composite score is only credible if it can be checked against what happened afterwards, and there is no record yet to check it against. The needle of the compass only adds up explicit signals, each with its rule and source. When enough weekly history has accumulated, any number that turns out to have led the changes of heading can be added to it, with its weight justified by that record.</p>
<h2>What it does not do</h2>
<p>It does not forecast. The past booms are aligned at the start of their frenzy by convention; another start date would shift the curves. The signal counts are evidence, not probabilities.</p>
<h2>Sources and code</h2>
<p>The paper behind the measures is <em>The Sharp End of AI Debt</em> (Acedo, 2026). Code, data, dated pre-registrations and the full rules are in the repository: <a href="https://github.com/Acedoo/chips-and-risk">github.com/Acedoo/chips-and-risk</a>. Built with the assistance of Claude (Anthropic); Anthropic is one of the companies tracked, and its figures follow the same rules as the others.</p>""",
"es": """<h1>Método</h1>
<p class="lead">Chips and Risk no es un medidor de burbuja. No pregunta si la IA está sobrevalorada, sino quién cargaría con las pérdidas si la financiación de su infraestructura se rompiera. Cada cifra del panel está medida o publicada, y la página dice de dónde sale.</p>
<h2>Qué se mide</h2>
<p>El rezago de los prestamistas compara a dieciocho prestamistas e inversores cotizados en infraestructura de IA con otras veinticuatro financieras, en las jornadas en que más cae una cesta de cuarenta y seis empresas de la cadena de suministro de la IA, descontado el efecto del mercado. La tabla de exposición divide el mayor compromiso documentado de cada empresa cotizada que trabaja con OpenAI y Anthropic entre su valor en bolsa, actualizado con los precios. Los auges anteriores salen de la Kenneth French Data Library y del índice ferroviario de Macaulay. Los documentos oficiales proceden de SEC EDGAR; la rentabilidad del bono, de FRED; y los precios, de Stooq y Yahoo Finance.</p>
<h2>Qué es lectura nuestra</h2>
<p>Hay tres cosas que son criterio propio, y el panel lo indica: qué rasgos cuentan como señales de frenesí avanzado o de punto de inflexión (siguiendo a Carlota Pérez), qué señal apunta a cada una de las cuatro posiciones ante las salidas a bolsa, y las dos zonas de exposición (por debajo del 10 % de su valor una empresa podría encajar un impago; por encima del 20 %, está expuesta), tomadas del salto que muestra la tabla 3 del artículo. La calculadora de ahorros es una lectura cualitativa de los mecanismos que describe el artículo.</p>
<h2>Por qué no hay una puntuación única</h2>
<p>Muchos paneles sobre la IA suman sus indicadores en una sola nota de 0 a 100. Este no. Un índice compuesto solo es creíble si se puede contrastar con lo que pasó después, y todavía no hay historia con la que contrastarlo. La aguja de la brújula solo suma señales explícitas, cada una con su regla y su fuente. Cuando se haya acumulado suficiente historia semanal, cualquier cifra que demuestre haberse adelantado a los cambios de rumbo podrá incorporarse, con un peso justificado por esos datos.</p>
<h2>Lo que no hace</h2>
<p>No hace previsiones. Los auges anteriores se alinean por convención en el inicio de su frenesí, y con otra fecha de inicio las curvas se desplazarían. Los recuentos de señales son pruebas, no probabilidades.</p>
<h2>Fuentes y código</h2>
<p>Las mediciones proceden del artículo <em>The Sharp End of AI Debt</em> (Acedo, 2026). El código, los datos, los pre-registros fechados y todas las reglas están en el repositorio: <a href="https://github.com/Acedoo/chips-and-risk">github.com/Acedoo/chips-and-risk</a>. Elaborada con la ayuda de Claude, de Anthropic; Anthropic es una de las empresas que sigue esta web, y sus cifras se tratan con las mismas reglas que las demás.</p>"""}


def shell(lang, title, body, home, other_lang_href):
    t = T[lang]
    other = "ES" if lang == "en" else "EN"
    return f"""<!DOCTYPE html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} · Chips and Risk</title>
<link href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400&family=Instrument+Sans:wght@400;600;700&display=swap" rel="stylesheet">
<style>{CSS}</style></head><body><main>
<nav class="nav"><a class="brand" href="{home}">{t['brand']}</a><a href="{home}">{t['home']}</a><a href="{home}method/">{t['method']}</a><a href="{home}archive/">{t['archive']}</a>
<a class="lng" href="{other_lang_href}" hreflang="{other.lower()}" lang="{other.lower()}">{other}</a></nav>
{body}
<footer><p>{t['foot']}</p></footer></main></body></html>"""


def update_archive(ind):
    """One entry per ISO week; runs within the same week refresh that week's entry."""
    arch = json.loads(ARCH.read_text()) if ARCH.exists() else []
    d = datetime.date.fromisoformat(ind["updated"])
    wk = f"{d.isocalendar()[0]}-W{d.isocalendar()[1]:02d}"
    nd = ind["needle"]
    entry = {"week": wk, "date": ind["updated"], "headline_en": ind["headline"], "headline_es": ind["headline_es"],
             "point": nd["point"], "reading": nd["reading"], "changes_en": ind["changes"], "changes_es": ind["changes_es"]}
    arch = [a for a in arch if a["week"] != wk] + [entry]
    arch.sort(key=lambda a: a["week"])
    for i, a in enumerate(arch, 1):
        a["issue"] = i
    ARCH.write_text(json.dumps(arch, indent=1, ensure_ascii=False))
    return arch


def build(arch, docs):
    from monitor import i18n
    for lang in ("en", "es"):
        t = T[lang]
        base = docs if lang == "en" else docs / "es"
        home = "../"
        items = []
        for a in reversed(arch):
            date = a["date"] if lang == "en" else i18n.fecha(a["date"])
            if lang == "en":
                head = "centre, the signals balance out" if a["point"] == "centre" else f"{a['point']}, {a['reading']}"
            else:
                head = i18n._heading_es(a["point"] if a["point"] == "centre" else f"{a['point']}, {a['reading']}", "").rstrip(".")
            ch = "".join(f"<li>{esc(c)}</li>" for c in (a["changes_en"] if lang == "en" else a["changes_es"]))
            items.append(f'<div class="issue"><h3>{t["issue"]} {a["issue"]}</h3><p class="d">{esc(date)}</p><p>{esc(a["headline_" + lang])}</p>'
                         f'<p>{t["heading"]}: {esc(head)}</p><p class="d">{t["changes"]}</p><ul>{ch}</ul></div>')
        body = f'<h1>{t["arch_title"]}</h1><p class="lead">{t["arch_lead"]}</p>' + ("".join(items) or f"<p>{t['none']}</p>")
        other = "../es/archive/" if lang == "en" else "../../archive/"
        (base / "archive").mkdir(parents=True, exist_ok=True)
        (base / "archive" / "index.html").write_text(shell(lang, t["arch_title"], body, home, other), encoding="utf-8")
        other = "../es/method/" if lang == "en" else "../../method/"
        (base / "method").mkdir(parents=True, exist_ok=True)
        (base / "method" / "index.html").write_text(shell(lang, t["method"], METHOD[lang], home, other), encoding="utf-8")
