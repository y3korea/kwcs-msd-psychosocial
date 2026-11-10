#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Figure 4 (v2) — Autonomy x Ergonomic interaction, BMC Public Health submission.

Panel (a): MSD prevalence by decision autonomy x ergonomic exposure quadrant
           (unweighted prevalence, 95% normal-approximation binomial CI).
Panel (b): Industry-stratified adjusted PR for low decision autonomy
           (top-5 KSIC sectors), forest plot on log scale with text columns.

v2 change vs. submitted Figure_4_Interaction.pdf (ONLY fix):
  - Panel (b) estimate column uses 2 decimals '0.81 (0.76-0.85)'
    instead of 3 decimals '0.810 (0.760-0.850)', matching Table S1.
  - Everything else (palette, layout, fonts, labels) preserved exactly.

Data sources (no model re-fitting; panel (b) reads the frozen results table):
  - input/analytic_sample.csv                      -> panel (a) prevalences
  - output/analysis_output/run_20260524_0444/
        table_interaction_industry.csv             -> panel (b) aPRs

Run: /Users/y3korea/miniforge3/bin/python3.10 fig4_interaction_v2.py
"""

import os

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import numpy as np
import pandas as pd

# ────────────────────────────────────────────────────────────────
# Paths
# ────────────────────────────────────────────────────────────────
BASE = ('/Users/y3korea/Library/CloudStorage/GoogleDrive-y3korea@gmail.com/'
        '내 드라이브/완석_구글자료/연구자료/20260313_kosha/Code_kosha/1_code')
ANALYTIC_CSV = os.path.join(BASE, 'paper/2_BMC_submission2_final/input/analytic_sample.csv')
INDUSTRY_CSV = os.path.join(BASE, 'output/analysis_output/run_20260524_0444/'
                                  'table_interaction_industry.csv')
OUT_DIR = os.path.join(BASE, 'paper/2_BMC_submission2_final/output')
OUT_PDF = os.path.join(OUT_DIR, 'fig_interaction_v2.pdf')
OUT_PNG = os.path.join(OUT_DIR, 'fig_interaction_v2.png')

# ────────────────────────────────────────────────────────────────
# Panel (a) data — quadrant prevalences from analytic sample
# ────────────────────────────────────────────────────────────────
df = pd.read_csv(ANALYTIC_CSV)
dfa = df.dropna(subset=['autonomy', 'support', 'lo_auto', 'lo_sup',
                        'edu_hi', 'poor_wlb']).copy()

dfa['erg_any_hi'] = ((dfa['erg_posture_hi'] == 1) | (dfa['erg_heavy_hi'] == 1) |
                     (dfa['erg_stand_hi'] == 1) | (dfa['erg_repeat_hi'] == 1)).astype(float)
dfa['lo_auto_binary'] = (dfa['lo_auto'] == 1).astype(float)

# (label, lo_auto_binary value, erg_any_hi value)
quadrants = [
    ('High auto / Low erg', 0, 0),   # Reference
    ('High auto / High erg', 0, 1),
    ('Low auto / Low erg', 1, 0),
    ('Low auto / High erg', 1, 1),
]

quad_stats = {}
for label, auto_val, erg_val in quadrants:
    sub = dfa[(dfa['lo_auto_binary'] == auto_val) & (dfa['erg_any_hi'] == erg_val)]
    n = len(sub)
    p = sub['msd_any'].mean()
    ci = 1.96 * np.sqrt(p * (1 - p) / n)          # normal-approx binomial CI
    quad_stats[(auto_val, erg_val)] = {'n': n, 'rate': p * 100, 'ci': ci * 100}

# Verify against the published numbers (submitted Figure 4 / manuscript text)
EXPECTED = {(0, 0): (11050, 30.0), (0, 1): (29806, 51.9),
            (1, 0): (11455, 21.9), (1, 1): (30977, 43.4)}
for key, (exp_n, exp_rate) in EXPECTED.items():
    got = quad_stats[key]
    assert got['n'] == exp_n, f'quadrant {key}: n={got["n"]} != expected {exp_n}'
    assert round(got['rate'], 1) == exp_rate, \
        f'quadrant {key}: rate={got["rate"]:.2f} != expected {exp_rate}'

# ────────────────────────────────────────────────────────────────
# Panel (b) data — frozen industry-stratified results table
# ────────────────────────────────────────────────────────────────
KSIC_NAMES = {
    3:  'Manufacturing',
    6:  'Construction',
    7:  'Wholesale/retail trade',
    9:  'Accommodation/food services',
    17: 'Health/social work',
}
df_ind = pd.read_csv(INDUSTRY_CSV)
df_ind_sorted = df_ind.sort_values('Autonomy_PR').reset_index(drop=True)

assert list(df_ind_sorted['Autonomy_PR']) == [0.81, 0.83, 0.85, 0.89, 0.91], \
    f'unexpected PR order: {list(df_ind_sorted["Autonomy_PR"])}'
assert int(df_ind_sorted.loc[0, 'Industry']) == 17, 'Health/social work must be first'

# ────────────────────────────────────────────────────────────────
# Figure — geometry replicated from submitted Figure_4_Interaction.pdf
# (all coordinates below in PDF points of the tight-cropped page)
# ────────────────────────────────────────────────────────────────
plt.rcParams['font.family'] = 'DejaVu Sans'

PAGE_W, PAGE_H = 954.27, 388.47                 # pt
FIG_W, FIG_H = PAGE_W / 72.0, PAGE_H / 72.0

AX_TOP, AX_BOT = 27.6, 326.9                    # pt from page top
AX_Y0 = (PAGE_H - AX_BOT) / PAGE_H              # axes bottom (fig fraction)
AX_HF = (AX_BOT - AX_TOP) / PAGE_H              # axes height (fig fraction)


def ax_rect(x0_pt, w_pt):
    return [x0_pt / PAGE_W, AX_Y0, w_pt / PAGE_W, AX_HF]


fig = plt.figure(figsize=(FIG_W, FIG_H))
ax_a   = fig.add_axes(ax_rect(46.3, 200.0))     # (a) grouped bars
ax_lab = fig.add_axes(ax_rect(262.3, 162.5))    # (b) industry-label column
ax_apr = fig.add_axes(ax_rect(440.9, 93.7))     # (b) aPR text column
ax_f   = fig.add_axes(ax_rect(550.7, 187.5))    # (b) forest plot

C_BLUE, C_ORANGE = '#56B4E9', '#E69F00'         # Okabe-Ito colorblind-safe
C_FOREST = '#0072B2'

# ── Panel (a): grouped bars ─────────────────────────────────────
x = np.arange(2)                                # 0 = High autonomy, 1 = Low autonomy
width = 0.38
lo_erg = [quad_stats[(0, 0)], quad_stats[(1, 0)]]   # blue: low ergonomic exposure
hi_erg = [quad_stats[(0, 1)], quad_stats[(1, 1)]]   # orange: high ergonomic exposure

ax_a.grid(axis='y', alpha=0.15)
ax_a.set_axisbelow(True)

for xc_arr, stats, color in [(x - width / 2, lo_erg, C_BLUE),
                             (x + width / 2, hi_erg, C_ORANGE)]:
    rates = [s['rate'] for s in stats]
    cis = [s['ci'] for s in stats]
    ax_a.bar(xc_arr, rates, width, color=color, edgecolor='#333333',
             linewidth=1.0, zorder=2)
    ax_a.errorbar(xc_arr, rates, yerr=cis, fmt='none', ecolor='#333333',
                  elinewidth=1.0, capsize=3, capthick=1.0, zorder=3)
    for xc, s in zip(xc_arr, stats):
        pct_y = s['rate'] + s['ci'] + 0.84
        ax_a.text(xc, pct_y, f"{s['rate']:.1f}%", ha='center', va='bottom',
                  fontsize=8.5, fontweight='bold')
        ax_a.text(xc, 1.5, f"n={s['n']:,}", rotation=90, ha='center',
                  va='bottom', fontsize=6.4, color='#333333')

# 'Ref' tag above the reference (High autonomy / Low ergonomic) bar
s_ref = quad_stats[(0, 0)]
ax_a.text(x[0] - width / 2, s_ref['rate'] + s_ref['ci'] + 0.84 + 1.41, 'Ref',
          ha='center', va='bottom', fontsize=7.5, color='#333333')

ax_a.set_ylim(0, 62)
ax_a.set_yticks(np.arange(0, 61, 10))
ax_a.set_xticks(x)
ax_a.set_xticklabels(['High autonomy', 'Low autonomy'], fontsize=9.5)
ax_a.tick_params(axis='y', labelsize=10)
ax_a.set_ylabel('MSD prevalence (%)', fontsize=10)
ax_a.set_title('(a) MSD prevalence by decision autonomy and ergonomic exposure',
               fontsize=10.5, fontweight='bold', loc='left', pad=6)
ax_a.spines['top'].set_visible(False)
ax_a.spines['right'].set_visible(False)

legend_a = ax_a.legend(
    handles=[mpatches.Patch(facecolor=C_BLUE, edgecolor='#333333', linewidth=1.0,
                            label='Low ergonomic exposure'),
             mpatches.Patch(facecolor=C_ORANGE, edgecolor='#333333', linewidth=1.0,
                            label='High ergonomic exposure')],
    loc='upper left', bbox_to_anchor=(-0.196, -0.134), ncol=2,
    fontsize=8.2, framealpha=0.8, edgecolor='#cccccc')
legend_a.get_frame().set_linewidth(1.0)

# ── Panel (b): text columns + forest plot ───────────────────────
N_ROWS = len(df_ind_sorted)
y_rows = [N_ROWS - 1 - i for i in range(N_ROWS)]    # top -> bottom: 4,3,2,1,0
YLIM = (-0.6, 4.7)
HEADER_YF = 0.9448                                   # header baseline (axes fraction)

for ax in (ax_lab, ax_apr):
    ax.set_xlim(0, 1)
    ax.set_ylim(*YLIM)
    ax.axis('off')

# Industry-label column (left-aligned, two lines per row)
ax_lab.text(0, HEADER_YF, 'Industry (n)', transform=ax_lab.transAxes,
            ha='left', va='baseline', fontsize=8.6, fontweight='bold')
for i, row in df_ind_sorted.iterrows():
    name = KSIC_NAMES.get(int(row['Industry']), f"KSIC {int(row['Industry'])}")
    ax_lab.text(0, y_rows[i], f"{name}\n(n = {int(row['N']):,})",
                ha='left', va='center', fontsize=8.2, color='#222222',
                linespacing=1.1)

# aPR text column (right-aligned) — v2 FIX: 2 decimals, matching Table S1
ax_apr.text(1, HEADER_YF, 'aPR (95% CI)', transform=ax_apr.transAxes,
            ha='right', va='baseline', fontsize=8.4, fontweight='bold')
for i, row in df_ind_sorted.iterrows():
    est = f"{row['Autonomy_PR']:.2f} ({row['CI_lo']:.2f}–{row['CI_hi']:.2f})"
    ax_apr.text(1, y_rows[i], est, ha='right', va='center', fontsize=8.2,
                color='#000000')

# Forest plot (log-scale x)
ax_f.set_xscale('log')
ax_f.grid(axis='x', alpha=0.15)
ax_f.set_axisbelow(True)
ax_f.axvline(x=1.0, color='#555555', linestyle='--', linewidth=1.0, zorder=1)
for i, row in df_ind_sorted.iterrows():
    pr, lo, hi = row['Autonomy_PR'], row['CI_lo'], row['CI_hi']
    ax_f.errorbar(pr, y_rows[i], xerr=[[pr - lo], [hi - pr]], fmt='o',
                  color=C_FOREST, ecolor=C_FOREST, elinewidth=1.5,
                  capsize=3.5, capthick=1.2, markersize=6.5, zorder=3)

ax_f.set_xlim(0.7, 1.1)
ax_f.set_ylim(*YLIM)
ax_f.set_xticks([0.7, 0.8, 0.9, 1.0, 1.1])
ax_f.set_xticklabels(['0.7', '0.8', '0.9', '1', '1.1'], fontsize=10)
ax_f.minorticks_off()
ax_f.set_yticks([])
ax_f.set_xlabel('aPR for low decision autonomy (95% CI), log scale', fontsize=9.2)
ax_f.set_title('(b) Low decision autonomy → MSD by industry (top-5 KSIC sectors)',
               fontsize=10.5, fontweight='bold', loc='left', pad=12)
for side in ('top', 'right', 'left'):
    ax_f.spines[side].set_visible(False)

legend_f = ax_f.legend(
    handles=[mlines.Line2D([], [], color='#555555', linestyle='--',
                           linewidth=1.0, label='Null (PR = 1.0)')],
    loc='lower right', fontsize=8.0, framealpha=0.8, edgecolor='#cccccc')
legend_f.get_frame().set_linewidth(1.0)

# ────────────────────────────────────────────────────────────────
# Save
# ────────────────────────────────────────────────────────────────
os.makedirs(OUT_DIR, exist_ok=True)
fig.savefig(OUT_PDF, bbox_inches='tight')
fig.savefig(OUT_PNG, dpi=300, bbox_inches='tight')
plt.close(fig)

print('Saved:')
print(' ', OUT_PDF)
print(' ', OUT_PNG)
for key, (exp_n, exp_rate) in EXPECTED.items():
    got = quad_stats[key]
    print(f'  quadrant lo_auto={key[0]} erg_hi={key[1]}: '
          f'n={got["n"]:,} rate={got["rate"]:.1f}% (expected {exp_rate}%)')
print('  panel (b) PRs:', list(df_ind_sorted['Autonomy_PR']))
