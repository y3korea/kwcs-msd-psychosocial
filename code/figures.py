"""SH@W 원고 그림 1-4 (집계 CSV만 사용). 그림 1 = 가설 검정 개념도(수치는 결과 CSV에서 읽음). JPG 500 dpi, 폭 16.5 cm."""
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


# Fig 1: concept diagram (hypothesis-testing logic)
from matplotlib.patches import FancyBboxPatch
t3 = pd.read_csv(os.path.join(R, 'T3_stratified.csv')).set_index(['group', 'exposure'])['PR (95% CI)']
t7 = pd.read_csv(os.path.join(R, 'T7_negative_control.csv')).set_index('outcome')['Control none vs full']
t2 = pd.read_csv(os.path.join(R, 'T2_main.csv')).set_index(['outcome', 'exposure'])['PR (95% CI)']
t13 = pd.read_csv(os.path.join(R, 'T13_format_comparison.csv')).set_index('Outcome')
pr_ = lambda x: x.split(' ')[0]
none_all = pr_(t2[('pain_any', 'Control: none vs full')])
emp, se = pr_(t3[('employee', 'Control: none vs full')]), pr_(t3[('self-employed', 'Control: none vs full')])
skin, hear = pr_(t7['Skin problem (W2-W5)']), pr_(t7['Hearing problem (W2-W5)'])
head, fat = pr_(t7['Headache/eye strain']), pr_(t7['General fatigue'])
ideas = pr_(t13.loc['Any musculoskeletal pain', 'Low own-ideas item, joint model'])
fig = plt.figure(figsize=(W, 3.6)); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 100); ax.set_ylim(0, 60); ax.axis('off')
def box(x, y, w, h, txt, fc, ec='#555', fs=6.8, bold=False, tc='black'):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.3,rounding_size=1.2', fc=fc, ec=ec, lw=0.7))
    ax.text(x + w / 2, y + h / 2, txt, ha='center', va='center', fontsize=fs, fontweight='bold' if bold else 'normal', color=tc, wrap=True)
box(14, 51, 72, 7, f'Observation: workers answering "no" to all three yes/no job-control items\nreport less musculoskeletal pain than those answering "yes" to all three (PR {none_all})', '#f4f4f4', bold=False, fs=7.2)
for x, t in [(1, 'Candidate explanation'), (27, 'What it predicts'), (54, 'What we observed'), (84, 'Verdict')]:
    ax.text(x + (7.5 if x == 84 else 13 if x == 54 else 11), 46.5, t, ha='center', fontsize=7.3, fontweight='bold', color='#333')
rows = [
 ('A. Self-employment\n(high-control, high-pain\nworkers)', 'Inverse association confined\nto, or stronger in, the\nself-employed',
  f'Same in employees (PR {emp})\nand self-employed (PR {se})', 'Not supported', '#e8e8e8', '#7f7f7f'),
 ('B. True protective effect\nof having no control', 'Lower prevalence of\nmusculoskeletal pain only',
  f'Also fewer skin ({skin}), hearing ({hear}),\nheadache/eye ({head}), fatigue ({fat})\nproblems', 'Not supported', '#e8e8e8', '#7f7f7f'),
 ('C. Response pattern\nin self-reports', 'Non-specific across outcomes;\ndirection depends on\nquestion format',
  f'All outcomes lower; 84% identical\nanswers; 5-point control item shows\nmore pain (PR {ideas})', 'Consistent', '#d6e9f5', '#1b6ca8'),
]
for i, (a, b, c, v, fc, vc) in enumerate(rows):
    y = 31 - i * 14.5
    box(1, y, 22, 11, a, '#ffffff'); box(27, y, 22, 11, b, '#ffffff'); box(54, y, 26, 11, c, '#ffffff')
    box(84, y + 2.5, 15, 6, v, fc, ec=vc, bold=True, tc=vc if v == 'Consistent' else '#555', fs=7)
    for x0, x1 in [(23.6, 26.4), (49.6, 53.4), (80.6, 83.4)]:
        ax.annotate('', xy=(x1, y + 5.5), xytext=(x0, y + 5.5), arrowprops=dict(arrowstyle='-|>', lw=0.7, color='#777'))
fig.savefig(os.path.join(F, 'Fig1.jpg'), dpi=500, pil_kwargs={'quality': 95}); plt.close(fig)

# Fig 2
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
fig.tight_layout(); fig.savefig(os.path.join(F, 'Fig2.jpg'), dpi=500, pil_kwargs={'quality': 95}); plt.close(fig)

# Fig 3
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
fig.tight_layout(); fig.savefig(os.path.join(F, 'Fig3.jpg'), dpi=500, pil_kwargs={'quality': 95}); plt.close(fig)

# Fig 4
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
fig.tight_layout(); fig.savefig(os.path.join(F, 'Fig4.jpg'), dpi=500, pil_kwargs={'quality': 95}); plt.close(fig)
print('figures saved')
