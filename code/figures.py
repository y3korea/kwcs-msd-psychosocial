"""SH@W 원고 그림 1-3 (집계 CSV만 사용). JPG 500 dpi, 폭 16.5 cm."""
import os, numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter
plt.rcParams.update({'font.family': 'Arial', 'font.size': 8, 'axes.spines.top': False, 'axes.spines.right': False})
R = os.path.join(os.path.dirname(__file__), '..', 'output', 'r1')
F = os.path.join(os.path.dirname(__file__), '..', 'output', 'figures'); os.makedirs(F, exist_ok=True)
W = 16.5 / 2.54
COL = {'employee': '#1b6ca8', 'own_account': '#d1495b', 'employer': '#edae49', 'unpaid_family': '#66a182'}
LAB = {'employee': 'Employees', 'own_account': 'Own-account self-employed', 'employer': 'Employers', 'unpaid_family': 'Unpaid family workers'}

# Fig 1
dist = pd.read_csv(os.path.join(R, 'F1_ctrl_distribution.csv'), index_col=0)
trend = pd.read_csv(os.path.join(R, 'T5_nocontrol_trend.csv'), index_col=0)
fig, ax = plt.subplots(1, 2, figsize=(W, 2.9), gridspec_kw={'width_ratios': [1, 1.25]})
order = ['employee', 'own_account', 'employer', 'unpaid_family']
greys = ['#3b3b3b', '#8c8c8c', '#bdbdbd', '#e6e6e6']
left = np.zeros(4)
for k, c in zip(['0.0', '1.0', '2.0', '3.0'], greys):
    v = dist.loc[order, k].values
    ax[0].barh(range(4), v, left=left, color=c, edgecolor='white', label=f'{int(float(k))} of 3')
    for i, (l, x) in enumerate(zip(left, v)):
        if x > 9: ax[0].text(l + x / 2, i, f'{x:.0f}', ha='center', va='center', color='white' if k == '0.0' else 'black', fontsize=7)
    left += v
ax[0].set_yticks(range(4)); ax[0].set_yticklabels([LAB[o].replace(' self-employed', '\nself-employed').replace(' family', '\nfamily') for o in order])
ax[0].invert_yaxis(); ax[0].set_xlabel('Weighted % of workers'); ax[0].set_xlim(0, 100)
ax[0].legend(title='Control items answered "yes"', ncol=4, fontsize=6.5, title_fontsize=7, loc='lower center', bbox_to_anchor=(0.45, 1.0), frameon=False, handlelength=1)
ax[0].set_title('A', loc='left', fontweight='bold', x=-0.42)
years = {2: 2010, 3: 2011, 4: 2014, 5: 2017, 6: 2020, 7: 2023}
for o in order:
    ax[1].plot([years[w] for w in trend.index], trend[o], marker='o', ms=3, color=COL[o], label=LAB[o])
ax[1].axvspan(2009.5, 2012, color='#f2f2f2', zorder=0); ax[1].text(2010.75, 72, 'Paper\ninterview', ha='center', fontsize=6.5, color='#555')
ax[1].text(2018.5, 72, 'Tablet-assisted interview', ha='center', fontsize=6.5, color='#555')
ax[1].set_ylim(0, 80); ax[1].set_xticks(list(years.values())); ax[1].set_xticklabels(['2010', '2011', '2014', '2017', '2020', '2023'], rotation=45); ax[1].set_ylabel('No control on any item (weighted %)')
ax[1].legend(fontsize=6.5, frameon=False, loc='lower right'); ax[1].set_title('B', loc='left', fontweight='bold', x=-0.18)
fig.tight_layout(); fig.savefig(os.path.join(F, 'Fig1.jpg'), dpi=500, pil_kwargs={'quality': 95}); plt.close(fig)

# Fig 2
f2 = pd.read_csv(os.path.join(R, 'F2_control_count_pr.csv'))
labs = list(dict.fromkeys(f2.label))
fig, ax = plt.subplots(figsize=(W, 3.6))
mk = {2: ('s', '#9e9e9e', '2 of 3'), 1: ('D', '#5b5b5b', '1 of 3'), 0: ('o', '#c0392b', '0 of 3 (no control)')}
for i, lab in enumerate(labs):
    for j, k in enumerate([2, 1, 0]):
        r = f2[(f2.label == lab) & (f2.yes_n == k)].iloc[0]
        y = i + (j - 1) * 0.24
        ax.errorbar(r.pr, y, xerr=[[r.pr - r.lo], [r.hi - r.pr]], fmt=mk[k][0], color=mk[k][1], ms=3.5, lw=0.9, capsize=0,
                    label=mk[k][2] if i == 0 else None)
ax.axvline(1, color='k', lw=0.6, ls='--'); ax.axhline(3.5, color='#999', lw=0.5)
ax.set_xscale('log'); ax.xaxis.set_minor_formatter(NullFormatter()); ax.set_xticks([0.6, 0.7, 0.8, 0.9, 1.0, 1.25, 1.5]); ax.set_xticklabels(['0.6', '0.7', '0.8', '0.9', '1.0', '1.25', '1.5'])
ax.set_yticks(range(len(labs))); ax.set_yticklabels(labs); ax.invert_yaxis()
ax.text(1.42, 1.5, 'Musculoskeletal\noutcomes', fontsize=7, color='#555', ha='center', va='center')
ax.text(1.42, 5.5, 'Non-musculoskeletal\n(negative-control)\noutcomes', fontsize=7, color='#555', ha='center', va='center')
ax.set_xlabel('Adjusted prevalence ratio (95% CI) vs all three control items answered "yes"')
ax.legend(frameon=False, fontsize=7, loc='lower left', ncol=3, bbox_to_anchor=(0, 1.0))
fig.tight_layout(); fig.savefig(os.path.join(F, 'Fig2.jpg'), dpi=500, pil_kwargs={'quality': 95}); plt.close(fig)

# Fig 3
t = pd.read_csv(os.path.join(R, 'T11_negcontrol_by_emp.csv'))
name = {'pain_any': 'MSK pain, any site', 'nc_headeye': 'Headache/eye strain', 'nc_fatigue': 'General fatigue', 'nc_hearing': 'Hearing problem*', 'nc_skin': 'Skin problem*'}
def parse(s):
    a, b = s.split(' ('); lo, hi = b.rstrip(')').split('–'); return float(a), float(lo), float(hi)
fig, ax = plt.subplots(figsize=(W, 2.6))
outs = list(name)
for j, (g, c, m) in enumerate([('employee', COL['employee'], 'o'), ('self-employed', COL['own_account'], 's')]):
    for i, o in enumerate(outs):
        e, lo, hi = parse(t[(t.group == g) & (t.outcome == o)].iloc[0]['none vs full'])
        ax.errorbar(e, i + (j - 0.5) * 0.3, xerr=[[e - lo], [hi - e]], fmt=m, color=c, ms=3.5, lw=0.9,
                    label=('Employees' if g == 'employee' else 'Self-employed (own-account and employers)') if i == 0 else None)
ax.axvline(1, color='k', lw=0.6, ls='--'); ax.set_xscale('log'); ax.xaxis.set_minor_formatter(NullFormatter())
ax.set_xticks([0.6, 0.7, 0.8, 0.9, 1.0, 1.1]); ax.set_xticklabels(['0.6', '0.7', '0.8', '0.9', '1.0', '1.1'])
ax.set_yticks(range(len(outs))); ax.set_yticklabels([name[o] for o in outs]); ax.invert_yaxis()
ax.set_xlabel('Adjusted prevalence ratio (95% CI): no control (0 of 3) vs full control (3 of 3)')
ax.legend(frameon=False, fontsize=7, loc='lower left', ncol=2, bbox_to_anchor=(0, 1.0))
fig.tight_layout(); fig.savefig(os.path.join(F, 'Fig3.jpg'), dpi=500, pil_kwargs={'quality': 95}); plt.close(fig)
print('figures saved')
