#!/usr/bin/env python3.10
# ══════════════════════════════════════════════════════════════
# Figure 2 (v2) — Temporal trends, KWCS 2010–2023 (two panels A/B)
# BMC Public Health submission — standalone, publication-grade.
#
# Adapted from 2_analysis.ipynb Cell 2 ("(A) 시간 추세 분석").
# Preserves the original palette / markers / layout EXACTLY.
# v2 fixes (ONLY these):
#   1. Legend labels spelled out: 'Hi demand'  -> 'High demand'
#                                 'Lo autonomy'-> 'Low autonomy'
#                                 'Lo support' -> 'Low support'
#   2. Panel titles as per submission text:
#        '(A) MSD prevalence trends, KWCS 2010–2023'
#        '(B) Psychosocial risk-factor trends, KWCS 2010–2023'
#
# Data  : output/analysis_output/run_20260524_0444/table_trend.csv
# Output: paper/2_BMC_submission2_final/output/fig_trends_v2.{pdf,png}
# Interpreter: /Users/y3korea/miniforge3/bin/python3.10
# ══════════════════════════════════════════════════════════════
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

BASE = os.path.expanduser(
    '~/Library/CloudStorage/GoogleDrive-y3korea@gmail.com/'
    '내 드라이브/완석_구글자료/연구자료/20260313_kosha/Code_kosha/1_code')
CSV_IN  = os.path.join(BASE, 'output', 'analysis_output',
                       'run_20260524_0444', 'table_trend.csv')
OUT_DIR = os.path.join(BASE, 'paper', '2_BMC_submission2_final', 'output')
os.makedirs(OUT_DIR, exist_ok=True)

df_trend = pd.read_csv(CSV_IN)
df_trend = df_trend.sort_values('year').reset_index(drop=True)

outcomes  = ['msd_any', 'msd_back_b', 'msd_upper_b', 'msd_lower_b']
exposures = ['psy_demand_hi', 'lo_auto', 'lo_sup', 'job_strain', 'iso_strain']

# ── Sanity: all needed columns present ──
for v in outcomes + exposures:
    assert f'{v}_prev' in df_trend.columns, f'missing column: {v}_prev'

# ── Spot-checks against the source CSV (submission QC) ──
def _val(var, year):
    return float(df_trend.loc[df_trend['year'] == year, f'{var}_prev'].iloc[0])

assert round(_val('lo_auto', 2010), 1) == 34.3, _val('lo_auto', 2010)
assert round(_val('lo_auto', 2023), 1) == 64.4, _val('lo_auto', 2023)
assert round(_val('msd_any', 2010), 1) == 49.1, _val('msd_any', 2010)
assert round(_val('msd_any', 2017), 1) == 31.4, _val('msd_any', 2017)

# ── 추세 그림 (legend 외부 배치, 데이터 겹침 방지) — original layout ──
fig, axes = plt.subplots(1, 2, figsize=(14, 5.2))

# Desaturated professional palette (identical to original)
PAL_OUT = ['#1F4E79', '#8B2E2E', '#4A6B53', '#A06A28']            # navy/crimson/forest/ochre
PAL_PSY = ['#1F4E79', '#8B2E2E', '#4A6B53', '#A06A28', '#5F5278']

# Panel A — MSD trends
ax = axes[0]
for v, label, c in zip(outcomes,
                       ['Any MSD', 'Back', 'Upper limb', 'Lower limb'],
                       PAL_OUT):
    ax.plot(df_trend['year'], df_trend[f'{v}_prev'], 'o-', label=label,
            color=c, linewidth=1.8, markersize=6)
ax.set_xlabel('Year', fontsize=10)
ax.set_ylabel('Weighted prevalence (%)', fontsize=10)
ax.set_title('(A) MSD prevalence trends, KWCS 2010–2023',
             fontsize=11, fontweight='bold')
ax.grid(alpha=0.25, linestyle=':')
# Legend: outside bottom, 4-column horizontal — never overlaps data
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.14), ncol=4,
          fontsize=9, framealpha=0.95, edgecolor='#888', borderpad=0.5)

# Panel B — psychosocial risk-factor trends
ax = axes[1]
for v, label, c in zip(exposures,
                       ['High demand', 'Low autonomy', 'Low support',
                        'Job strain', 'Iso-strain'],
                       PAL_PSY):
    ax.plot(df_trend['year'], df_trend[f'{v}_prev'], 's--', label=label,
            color=c, linewidth=1.8, markersize=6)
ax.set_xlabel('Year', fontsize=10)
ax.set_ylabel('Weighted prevalence (%)', fontsize=10)
ax.set_title('(B) Psychosocial risk-factor trends, KWCS 2010–2023',
             fontsize=11, fontweight='bold')
ax.grid(alpha=0.25, linestyle=':')
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.14), ncol=5,
          fontsize=9, framealpha=0.95, edgecolor='#888', borderpad=0.5)

plt.subplots_adjust(left=0.06, right=0.98, top=0.92, bottom=0.20, wspace=0.20)

pdf_path = os.path.join(OUT_DIR, 'fig_trends_v2.pdf')
png_path = os.path.join(OUT_DIR, 'fig_trends_v2.png')
fig.savefig(pdf_path, bbox_inches='tight')
fig.savefig(png_path, dpi=300, bbox_inches='tight')
plt.close(fig)

print(f'Saved: {pdf_path}')
print(f'Saved: {png_path}')
print('Spot-checks passed: lo_auto 2010=34.3, 2023=64.4; msd_any 2010=49.1, 2017=31.4')
