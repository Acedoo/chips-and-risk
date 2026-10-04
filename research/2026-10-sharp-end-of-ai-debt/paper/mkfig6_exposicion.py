# Figura 6: lo que cada contraparte cotizada tiene en juego con OpenAI o Anthropic, en % de su propio valor en bolsa.
# Cifras de la tabla 3 (fuentes en tabla_absorcion_openai_20261002.csv); se muestra la mayor partida de cada empresa,
# porque las partidas son instrumentos distintos y no se suman.
import matplotlib.pyplot as plt
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9, 'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.edgecolor': '#555555', 'axes.titleweight': 'bold', 'figure.dpi': 200})
CRIM, GREY, SLATE = '#8b1a1a', '#9a9a9a', '#3d5a80'
filas = [('Oracle', 'OpenAI', 77, 'contracted'), ('CoreWeave', 'OpenAI', 51, 'contracted'), ('SoftBank', 'OpenAI', 25, 'invested'),
         ('Microsoft', 'OpenAI', 6.6, 'contracted'), ('Amazon', 'OpenAI', 5.1, 'contracted'), ('Nvidia', 'OpenAI', 1.9, 'guarantee cap'),
         ('Broadcom', 'Anthropic', 9.8, 'leases'), ('Amazon', 'Anthropic', 4.1, 'contracted'), ('Alphabet', 'Anthropic', 2.7, 'contracted'),
         ('Microsoft', 'Anthropic', 0.8, 'contracted')]
fig, ax = plt.subplots(figsize=(7.2, 4.2))
ys = list(range(len(filas)))[::-1]
cols = [CRIM if v > 20 else (SLATE if t == 'Anthropic' else GREY) for _, t, v, _ in filas]
ax.barh(ys, [v for _, _, v, _ in filas], color=cols, height=0.66)
for y, (emp, t, v, k) in zip(ys, filas):
    ax.text(v + 1, y, f'{v:g}%  ({k})', va='center', fontsize=7.5, color='#222222')
ax.set_yticks(ys); ax.set_yticklabels([f'{e}  [{t}]' for e, t, _, _ in filas], fontsize=8)
ax.axhline(3.5, color='#bbbbbb', lw=0.8, ls='--')
ax.set_xlim(0, 100); ax.set_xlabel('largest single item at stake, % of the company\'s market value')
ax.set_title('Three balance sheets carry OpenAI; the giants could absorb either tenant', fontsize=10.5, pad=10)
fig.savefig('fig6_exposicion.png', bbox_inches='tight', facecolor='white'); plt.close(fig)
print('fig6 ok')
