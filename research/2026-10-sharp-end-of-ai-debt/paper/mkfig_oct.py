"""Figuras de la nota de octubre, con el estilo del artículo de agosto (SSRN 7307362)."""
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
NAVY, CRIM, GREEN, GREY, LIGHT = '#1f4e79', '#c8102e', '#1b7a4a', '#9aa5b1', '#c9d1dc'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9, 'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.edgecolor': '#555555', 'axes.titleweight': 'bold', 'figure.dpi': 200})
def guarda(fig, nombre):
    fig.savefig(nombre, bbox_inches='tight', facecolor='white'); plt.close(fig)
def barras(ax, labels, vals, since, fmt='{:+.2f}'):
    cols = [CRIM if s else GREY for s in since]
    ax.bar(range(len(vals)), vals, color=cols, width=0.62)
    ax.axhline(0, color='#555555', lw=0.8)
    for i, v in enumerate(vals):
        ax.text(i, v + (0.02 if v >= 0 else -0.02) * (max(map(abs, vals)) / 0.7), fmt.format(round(v, 1) if fmt == '{:+.1f}' and abs(v) < 0.05 else v).replace('-0.0', '0.0').replace('+0.0', '0.0') if abs(v) < 0.05 else fmt.format(v), ha='center',
                va='bottom' if v >= 0 else 'top', fontsize=8, color='#222222')
    ax.set_xticks(range(len(vals))); ax.set_xticklabels(labels)
# Figura 1: brecha por año en las caídas bruscas
b = pd.read_csv('../brecha_por_anio.csv')
fig, ax = plt.subplots(figsize=(7.2, 3.3))
barras(ax, [str(y) if y < 2026 else '2026*' for y in b.year], list(b.gap), [y >= 2024 for y in b.year])
ax.set_ylabel('Lenders minus other financials\n(points a day, beyond market beta)')
ax.set_title("The lenders' lag in AI sell-offs jumped in 2024", fontsize=11, pad=10)
ax.set_ylim(min(b.gap) - 0.15, max(b.gap) + 0.15)
fig.text(0.01, -0.02, '* 2026: January to September', fontsize=7.5, color='#666666')
guarda(fig, 'fig1_brecha_anual.png')
# Figura 2: clasificación de prestamistas
r = json.load(open('../quien_cae_resultados.json'))['ranking_pp']
nombres = {'OWL': 'Blue Owl', 'MFG': 'Mizuho (NY)', 'SMFG': 'Sumitomo Mitsui (NY)', 'ARES': 'Ares', 'CG': 'Carlyle', 'MUFG': 'MUFG (NY)',
           'GS': 'Goldman Sachs', 'APO': 'Apollo', 'JPM': 'JPMorgan', 'MS': 'Morgan Stanley', 'C': 'Citigroup', 'BLK': 'BlackRock',
           'BX': 'Blackstone', 'BAC': 'Bank of America', 'KKR': 'KKR', 'BN': 'Brookfield', 'PRU': 'Prudential', 'MET': 'MetLife'}
filas = [(nombres[k], v) for k, v in r.items() if k in nombres]
fig, ax = plt.subplots(figsize=(7.2, 4.6))
ys = list(range(len(filas)))[::-1]
ax.barh(ys, [v for _, v in filas], color=[CRIM if v < -0.3 else GREY for _, v in filas], height=0.66)
ax.set_yticks(ys); ax.set_yticklabels([n for n, _ in filas])
for y, (_, v) in zip(ys, filas):
    ax.text(v + (0.012 if v >= 0 else -0.012), y, f'{v:+.2f}', va='center', ha='left' if v >= 0 else 'right', fontsize=7.5)
ax.axvline(0, color='#555555', lw=0.8)
for x, lab, yy in ((0.42, 'Other financial stocks (+0.42)', len(filas) - 0.2), (0.22, 'Without insurers and exchanges (+0.22)', len(filas) - 1.6)):
    ax.axvline(x, color=NAVY, lw=0.9, ls='--'); ax.text(x + 0.01, yy, lab, fontsize=7.5, color=NAVY, va='top')
ax.set_xlabel('Average return beyond market beta in the 35 sharpest AI sell-offs since 2024 (percentage points)')
ax.set_xlim(-0.75, 0.75)
ax.set_title('Blue Owl lagged the most; Blackstone and KKR did not', fontsize=11, pad=10)
guarda(fig, 'fig2_prestamistas.png')
# Figura 3: especificidad de correlación, neta de mercado y sector
v3 = [-0.04, -0.20, -0.18, 0.32, 0.20, -0.12, 0.16, 0.97, 1.41, 3.11, 1.27]
anios = [str(y) for y in range(2016, 2026)] + ['2026*']
fig, ax = plt.subplots(figsize=(7.2, 2.7))
barras(ax, anios, v3, [a >= '2024' for a in anios], fmt='{:+.1f}')
ax.set_ylabel('Extra correlation x100')
ax.set_ylim(-0.6, 3.6)
ax.set_title('A link specific to the AI chain appears in 2023-2024', fontsize=11, pad=10)
fig.text(0.01, -0.02, 'Lenders minus other financial stocks, net of the market and the financial sector. * 2026: January to September', fontsize=7.5, color='#666666')
guarda(fig, 'fig3_correlacion.png')
# Figura 4: canales
c = json.load(open('../canales_residuos_B_resultados.json'))['por_anio']
yrs = sorted(int(k) for k in c['infra'].keys())
fig, ax = plt.subplots(figsize=(7.2, 2.6))
ax.plot(yrs, [c['soft'][str(y)] * 100 for y in yrs], color=CRIM, lw=2, marker='o', ms=3.5, label='Software and buyers')
ax.plot(yrs, [c['infra'][str(y)] * 100 for y in yrs], color=NAVY, lw=2, marker='o', ms=3.5, label='Chips, hardware and power')
ax.axhline(0, color='#555555', lw=0.8)
ax.set_xticks(yrs); ax.set_xticklabels([str(y) if y < 2026 else '2026*' for y in yrs])
ax.set_ylabel('Extra correlation x100'); ax.legend(frameon=False, loc='upper left')
ax.set_title('Software first; chips and power since 2024', fontsize=11, pad=10)
guarda(fig, 'fig4_canales.png')
# Figura 5: telecos frente a IA (industrias)
f = json.load(open('../analisis_french_resultados.json'))
tel = f['telecos_residuos_mercado']['por_anio']; ai = f['calibracion_residuos_mercado']['por_anio']
fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 2.6), sharey=True)
ty = sorted(int(k) for k in tel); ay = sorted(int(k) for k in ai)
a1.axvspan(1999.5, 2002.5, color=LIGHT, alpha=0.6, lw=0); a1.text(2001, 13.8, 'Crash', ha='center', fontsize=7.5, color='#555555')
a1.plot(ty, [tel[str(y)] * 100 for y in ty], color=NAVY, lw=2, marker='o', ms=3.5)
a2.plot(ay, [ai[str(y)] * 100 for y in ay], color=CRIM, lw=2, marker='o', ms=3.5)
for a, t in ((a1, 'Telecoms boom, 1993-2004'), (a2, 'AI build-out, 2015-2026')):
    a.axhline(0, color='#555555', lw=0.8); a.set_title(t, fontsize=9, fontweight='bold')
a1.set_ylabel('Extra correlation x100')
a1.set_xticks([1993, 1996, 1999, 2002]); a2.set_xticks([2015, 2018, 2021, 2024])
fig.suptitle('In the telecoms boom the tie formed early and outlasted the crash', fontsize=11, fontweight='bold', y=1.04)
guarda(fig, 'fig5_telecos.png')
print('figuras hechas')
