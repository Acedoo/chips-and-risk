# Chips and Risk

Who carries the risk of the AI build-out, measured every week. In English and Spanish.

A web page that updates itself every week and follows, with public data, the measures proposed in
*The Sharp End of AI Debt: market evidence on where the off-balance-sheet risk of the AI build-out sits, 2016-2026*
(Alberto Acedo, Biome Makers Inc., October 2026). It does not forecast when, or whether, anything breaks; it shows which of
the paper's paths the financing of AI is taking.

## What the page shows (dashboard)

At the top, past booms in three groups that can be switched on and off (only the technology booms are shown when the page opens): technology (electric utilities and the US market
from July 1926; software, hardware, chips and telecoms from the Netscape listing in August 1995; US railroads from April 1865,
monthly, read from `data/M11005USM293NNBR.csv`, saved once from FRED because FRED does not answer requests from GitHub), energy (oil from January 1979; shale from January 2010) and credit (banks,
finance and real estate from June 2003), rebased to 100 at the start of their frenzy and plotted in calendar years,
from the Kenneth French Data Library (`config/history.json`). In blue, the AI supply chain from the launch of ChatGPT, extended
every week up to today. The alignment is a convention, not a forecast. Below: eight headline numbers with their change since
the last update; the twelve signs; the four positions (one per listing path of the paper, placed at the four points of a compass with a needle that adds up
the explicit signals (any angle; eight named headings; a dotted trail of the last twelve headings, kept in
`data/kpi_history.json`), who holds each one described only by documented positions, and the signals that point to each, in
`config/houses.json`); the
savings calculator; and the detailed evidence.

## The dashboard numbers

Twelve numbers, each with a reference scale and a reading that changes with the zone it falls in (`monitor/kpis.py`). Range
bars for most, gauges for the two sign counters (0 to 6). Every zone comes from something measured or published, and the page
says where: the lenders' gap and the chips-and-power link against their own 2016-2023 and 2024-2026 history; the AI chain
against past booms at the same age, with the conventional 20% fall from the peak as a bear market; Oracle, CoreWeave and
SoftBank against their own 52-week range; the 10-year yield against its 20-year range; the capital raised against all of
2025; and the share of value at stake with zones that are this paper's reading of Table 3 (giants under 10%, exposed above
20%), declared as such. Changes over one week (default), one month, three months and the year to date, coloured by whether
they move towards more strain (coral) or less (blue). Price-based numbers have their own history; the others build theirs
from weekly snapshots in `data/kpi_history.json`.

## Earlier layout notes

At the top, the path of a technological revolution as described by Carlota Perez (installation, frenzy, turning point,
deployment), with the earlier turning points marked. The dot is placed by counting twelve explicit signs, six of a late frenzy
and six of a turning point, each tied to a data series or to a sourced event (`config/signs.json`). It moves when a sign
appears or disappears; it is a reading of signs, not a forecast.

Then: what changed since the previous update; the four listing paths of the paper, with the number of current signals that
point to each (a count of evidence, not a probability) and the documented bets on each (`bets.csv`); a calculator that shows
which path a mix of savings is most sensitive to and through which door each path reaches it (qualitative, not a forecast of
returns and not investment advice); and the indicators below.

## What it tracks

1. The lenders' gap in AI sell-offs: lenders to and investors in AI infrastructure against other financial stocks on the days
   the AI supply chain falls hardest, net of the market (equation 2 of the paper), by year and over the last twelve months.
2. The three balance sheets most exposed to OpenAI: Oracle and CoreWeave against the rest of the chain, SoftBank against the Tokyo market.
3. SoftBank's reaction to news about OpenAI (the paper's first prediction: it should fade if OpenAI lists).
4. Supplier financing against outside capital, the warning sign of the telecoms boom.
5. New guarantee and off-balance-sheet language in the SEC filings of thirteen companies in the chain.
6. Listings, rating changes and guarantees, and the 10-year Treasury yield.
7. Managers against loan vehicles: the listed private-credit funds (BDCs) against other financial stocks in the same sell-offs.
8. Since when and through what: the AI-specific link of the lenders net of the market and of the financial sector
   (equation 3), separately for software and for chips, equipment and power.
9. Who carries OpenAI's and Anthropic's commitments: the largest documented item of each counterparty as a share of its market
   value, updated weekly by scaling the 1 October 2026 values with prices (`config/exposures.json`).
10. Cash against the story (`tenants.csv`) and the debt side (`debt.csv`): reported figures, each with its source.
11. Tenants with a public price (Zhipu and MiniMax in Hong Kong, SpaceX with xAI) against their listing price, and the
    exposed companies after each capability announcement (events of type `capability`).

All quantities use only information available on the day they refer to (betas over the previous 250 sessions, sell-off
thresholds over the previous 500), so yearly values differ slightly from the paper, which uses fixed periods.

## What the needle is and is not

The compass has two axes. Across: the timing of OpenAI's listing (right, a delay; left, a listing). Up and down: market
conditions (up, favourable; down, adverse). The four positions of the paper sit in the corners: strong listing (lists,
favourable), weak listing (lists, adverse), delay (delays, favourable: private money keeps paying and the risk stays with
Oracle, CoreWeave and SoftBank) and market fall (delays because the market falls). Twelve explicit signals, each with its
rule in `config/signs.json`, move the needle one step each along their axis, with the same weight in both directions; each
axis is normalised to [-1, 1]. Anthropic, which has filed to list, is shown as a separate marker on the timing axis rather
than mixed into OpenAI's needle. The dashboard numbers do not move the needle beyond these explicit signals: weighting them
into one direction would make a composite index that cannot yet be checked against outcomes. A dotted trail shows the needle
at each of the last twelve updates.

## Two languages

Every run writes the page in English (`docs/index.html`) and in Spanish (`docs/es/index.html`), with an EN / ES switch in the
navigation bar. The Spanish is written as Spanish, with a fixed glossary kept at the end of `monitor/i18n.py` (build-out, lenders, tenants, sell-off days, boom, frenzy, turning point); dates and citations follow Spanish usage; sentences built from data have templates in both languages;
numbers use the Spanish decimal comma on the Spanish page. Files kept by hand carry Spanish columns (`description_es` in
`events.csv`, `bet_es` in `bets.csv`, `measure_es` in `debt.csv` and `tenants.csv`, and `*_es` fields in `config/houses.json`
and `config/signs.json`). When a row has no Spanish text, the Spanish page shows the English one.

## Sharing, archive and method

Every run draws a share card (`docs/share.png` and `docs/es/share.png`, 1200x630) with the sentence of the week and the
compass, linked from the page's Open Graph tags so that LinkedIn, X and messaging apps show it as the preview. Each ISO week
gets one numbered entry in the weekly archive (`data/archive.json`, published at `archive/` and `es/archive/`); runs within the
same week refresh that week's entry. The method page (`method/`, `es/method/`) explains what is measured, what is reading and
why there is no single risk score. On phones, the navigation and the period selector scroll sideways, the numbers stack in one
column, and wide charts and tables scroll inside their own frame.

## Week against week

Each run keeps a snapshot of the headline numbers, their zones, the state of the twelve signs and the compass heading in
`data/kpi_history.json`. The page shows a table "This week against the last" (each number a week ago and now, the change,
zone changes, signs switched on or off, the heading then and now, and the events of the week); each archive entry keeps that
table; and the full Monday run opens a GitHub issue with the same digest (`data/weekly_digest.md`), which arrives as an email
to anyone watching the repository's issues. The headline panel shows the four numbers with most movement first; the sign
counters come last, since the sentence of the week and the list of signs already state them.

## Automations and alerts

GitHub Actions runs the monitor every weekday after the US close (prices, yield and every number that comes from them) and
in full every Monday (with the SEC scan). After each run it writes `data/alerts.json` and, if there is any alert, opens a
GitHub issue, so the repository owner gets an email. Alerts cover: price series or sources that failed or fell back to cached
data; manual files gone stale (`bets.csv` after 60 days, `debt.csv` after 60, `tenants.csv` after 90, `events.csv` after 45);
and any headline number that changed zone (for example, a turning-point sign appearing, or the lenders' gap leaving its
range). A failed run opens an issue too. The sentence at the top of the page is built with fixed rules from the data, not by
a language model.

## How it updates

GitHub Actions runs `python -m monitor.run` every Monday (and on demand from the Actions tab). Prices come from Stooq, with
Yahoo Finance as fallback; the 10-year yield from FRED; filings from SEC EDGAR. A source that fails keeps its last good data,
and the page reports the status of every source. Isolated bad prints in the price data are removed and counted.
Raw prices are not stored in the repository, only the derived indicators.

## Adding an event

Events that no free database records (a listing and its price, a rating change, a new loan from a supplier to a tenant) go in
`events.csv`, editable directly on GitHub. Columns: `date` (YYYY-MM-DD), `type` (`openai_news`, `ipo`, `rating`, `guarantee`,
`supplier_financing`, `outside_capital`, `capability`, `openai_private_round`, `ipo_weak`, `rating_junk`, `default` or `other`), `company`, `description`, `amount_usd_bn` (optional) and `source`
(a link or a citation) and, optionally, `description_es`. Every event needs a source. The page picks it up on the next run. Two event types feed the
turning-point signs directly: `ipo_weak` (a frontier listing priced below its last private round) and `rating_junk`
(a key counterparty cut to speculative grade). Bets go in `bets.csv` (`date`, `who`, `scenario`: `strong`, `weak`,
`delay` or `fall`, `bet`, `source`), also with a source each.

## Licence

Code under the MIT licence. The page describes public market data and is not investment advice. Contact: acedo@biomemakers.com
