#!/usr/bin/env python3.10
# ══════════════════════════════════════════════════════════════════
# Figure 3 (v2) — Forest plot of adjusted prevalence ratios (aPR)
# Modified-Poisson regression, JDC-S exposures × 4 MSD outcomes.
#
# Standalone, publication-grade reproduction of the submitted
# Figure_3_Forest_plot.pdf with two fixes:
#   1. Estimate column formatted to exactly 2 decimals
#      ('0.98 (0.98–0.99)'), matching Table 2 of the manuscript.
#   2. x-axis explicitly log-scaled with fixed ticks labelled
#      0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3.
# Everything else (palette, 4 stacked panels a–d, filled/open
# markers by significance, grey text for non-significant rows,
# dashed null line, Model A/B separator, 'aPR (95% CI)' header,
# bottom footnote) is preserved exactly.
#
# Run:  /Users/y3korea/miniforge3/bin/python3.10 fig3_forest_v2.py
# ══════════════════════════════════════════════════════════════════
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import NullLocator

# ── Paths ──────────────────────────────────────────────────────────
DATA_CSV = ('/Users/y3korea/Library/CloudStorage/GoogleDrive-y3korea@gmail.com/'
            '내 드라이브/완석_구글자료/연구자료/20260313_kosha/Code_kosha/1_code/'
            'output/analysis_output/run_20260524_0444/table_regression.csv')
OUT_DIR = ('/Users/y3korea/Library/CloudStorage/GoogleDrive-y3korea@gmail.com/'
           '내 드라이브/완석_구글자료/연구자료/20260313_kosha/Code_kosha/1_code/'
           'paper/2_BMC_submission2_final/output')
OUT_PDF = os.path.join(OUT_DIR, 'fig_forest_v2.pdf')
OUT_PNG = os.path.join(OUT_DIR, 'fig_forest_v2.png')

# ── Style constants (extracted from the submitted Figure 3 PDF) ────
BLUE      = '#0072B2'   # markers, CI lines, caps
DARK_TXT  = '#222222'   # row labels + significant estimate text
GREY_TXT  = '#888888'   # non-significant estimate text
NULL_COL  = '#555555'   # dashed null line
SEP_COL   = '#CCCCCC'   # Model A / Model B separator
GRID_COL  = '#B0B0B0'   # vertical gridlines
FOOT_COL  = '#444444'   # footnote

FS_ROWLAB = 8.6
FS_EST    = 8.0
FS_TITLE  = 10.5
FS_HEADER = 8.2
FS_TICK   = 10.0
FS_XLABEL = 9.5
FS_FOOT   = 8.2

# ── Data ───────────────────────────────────────────────────────────
df = pd.read_csv(DATA_CSV)

# Panel definitions: (panel title, Outcome value in CSV)
PANELS = [
    ('(a) Any MSD',        'Any MSD'),
    ('(b) Back pain',      'Back pain'),
    ('(c) Upper-limb MSD', 'Upper limb'),
    ('(d) Lower-limb MSD', 'Lower limb'),
]
# Row definitions (top→bottom): display label, Model, Exposure in CSV
ROWS = [
    ('Psychological demand',  'A (Continuous)', 'Psy demand (per unit increase)'),
    ('Low decision autonomy', 'A (Continuous)', 'Low autonomy (per unit increase)'),
    ('Low social support',    'A (Continuous)', 'Low support (per unit increase)'),
    ('Job strain',            'B (Composite)',  'Job strain'),
    ('Iso-strain',            'B (Composite)',  'Iso-strain'),
]
Y_SEP = 2.4          # separator between Model A (rows 0-2) and Model B (rows 3-4)
YLIM = (4.6, -0.6)   # inverted: row 0 on top

XTICKS = [0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3]
XTICKLABELS = ['0.7', '0.8', '0.9', '1.0', '1.1', '1.2', '1.3']

FOOTNOTE = ('Filled marker = p < 0.05; open marker = p ≥ 0.05. '
            'Dashed line = null (PR = 1.0). '
            'Single pooled cross-sectional analysis (modified-Poisson regression); '
            'not a meta-analysis.')


def get_row(outcome, model, exposure):
    m = df[(df['Outcome'] == outcome) & (df['Model'] == model)
           & (df['Exposure'] == exposure)]
    assert len(m) == 1, f'expected 1 row for {outcome}/{model}/{exposure}, got {len(m)}'
    return m.iloc[0]


# ── Figure ─────────────────────────────────────────────────────────
# Geometry replicated from the submitted PDF (724 × 702 pt page):
# columns 175 / 85 / 240 pt with 6.7 pt gaps; panels 126.7 pt tall
# with 38 pt vertical gaps.
fig = plt.figure(figsize=(724.0 / 72.0, 701.7 / 72.0))
gs = fig.add_gridspec(
    4, 3, width_ratios=[175, 85, 240],
    left=113.6 / 724.0, right=627.0 / 724.0,
    top=1 - 27.54 / 701.7, bottom=1 - 648.47 / 701.7,
    wspace=0.04, hspace=0.30)

for p, (title, outcome) in enumerate(PANELS):
    rows = [get_row(outcome, model, exp) for (_, model, exp) in ROWS]

    # — Column 1: row labels —
    ax_lab = fig.add_subplot(gs[p, 0])
    ax_lab.set_xlim(0, 1)
    ax_lab.set_ylim(*YLIM)
    for sp in ax_lab.spines.values():
        sp.set_visible(False)
    ax_lab.set_xticks([]); ax_lab.set_yticks([])
    for j, (label, _, _) in enumerate(ROWS):
        ax_lab.text(0.0, j, label, fontsize=FS_ROWLAB, color=DARK_TXT,
                    ha='left', va='center')
    ax_lab.axhline(Y_SEP, color=SEP_COL, linewidth=0.6)
    ax_lab.set_title(title, loc='left', fontsize=FS_TITLE,
                     fontweight='bold', color='black', pad=11)

    # — Column 2: aPR (95% CI) estimate text —
    ax_est = fig.add_subplot(gs[p, 1])
    ax_est.set_xlim(0, 1)
    ax_est.set_ylim(*YLIM)
    for sp in ax_est.spines.values():
        sp.set_visible(False)
    ax_est.set_xticks([]); ax_est.set_yticks([])
    for j, r in enumerate(rows):
        sig = r['p'] < 0.05
        # FIX 1: exactly 2 decimals, en-dash between CI bounds
        txt = f"{r['PR']:.2f} ({r['CI_lo']:.2f}–{r['CI_hi']:.2f})"
        ax_est.text(0.04, j, txt, fontsize=FS_EST,
                    color=DARK_TXT if sig else GREY_TXT,
                    ha='left', va='center')
    if p == 0:
        ax_est.text(0.44, -0.6, 'aPR (95% CI)', fontsize=FS_HEADER,
                    fontweight='bold', color='black',
                    ha='center', va='center')

    # — Column 3: forest plot —
    ax = fig.add_subplot(gs[p, 2])
    # FIX 2: explicit log scale, fixed ticks labelled 0.7 … 1.3
    ax.set_xscale('log')
    ax.set_xlim(0.7, 1.3)
    ax.set_xticks(XTICKS)
    ax.set_xticklabels(XTICKLABELS if p == 3 else [], fontsize=FS_TICK)
    ax.xaxis.set_minor_locator(NullLocator())
    ax.set_ylim(*YLIM)
    ax.set_yticks([])
    for side in ('top', 'left', 'right'):
        ax.spines[side].set_visible(False)
    ax.spines['bottom'].set_linewidth(0.8)
    ax.tick_params(axis='x', which='major', length=3.5, width=0.8,
                   color='black', direction='out')
    ax.set_axisbelow(True)
    ax.grid(axis='x', which='major', color=GRID_COL, linewidth=0.8)

    ax.axvline(1.0, color=NULL_COL, linestyle='--', linewidth=1.0, zorder=2)
    ax.axhline(Y_SEP, color=SEP_COL, linewidth=0.6, zorder=1)

    for j, r in enumerate(rows):
        sig = r['p'] < 0.05
        pr, lo, hi = float(r['PR']), float(r['CI_lo']), float(r['CI_hi'])
        # CI line + caps (caps 1.2 pt, as in the submitted figure)
        ax.errorbar(pr, j, xerr=[[pr - lo], [hi - pr]], fmt='none',
                    ecolor=BLUE, elinewidth=1.4,
                    capsize=3.5, capthick=1.2, zorder=3)
        # marker on top: filled if p < 0.05, open otherwise
        ax.plot(pr, j, 'o', markersize=5.8,
                markerfacecolor=BLUE if sig else 'white',
                markeredgecolor=BLUE, markeredgewidth=1.3, zorder=4)

    if p == 3:
        ax.set_xlabel('Adjusted prevalence ratio (95% CI), log scale',
                      fontsize=FS_XLABEL, color='black')

# — Footnote (figure bottom-left) —
fig.text(7.2 / 724.0, 1 - 686.3 / 701.7, FOOTNOTE,
         fontsize=FS_FOOT, color=FOOT_COL, ha='left', va='top')

os.makedirs(OUT_DIR, exist_ok=True)
fig.savefig(OUT_PDF, bbox_inches='tight')
fig.savefig(OUT_PNG, dpi=300, bbox_inches='tight')
plt.close(fig)
print(f'Saved: {OUT_PDF}')
print(f'Saved: {OUT_PNG}')
