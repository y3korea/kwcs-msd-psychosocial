"""R1 추가 분석 (원고용, 2026-11-10): 통제 0-3 단계, 문항별, 음성대조 x 종사상지위, 7차 층 군집 분산. 집계만 출력."""
import os, sys
src = open(os.path.join(os.path.dirname(__file__), 'r1_03_analysis.py')).read().split("print('='*78); print('T1.")[0]
exec(src)
import numpy as np, pandas as pd
base_rhs = f"C(sup_cat) + dem_z + C(emp4) + {ERG} + {COV}"
print('T9. 통제 "예" 개수 0/1/2/3 (기준 3), any pain')
d['ctrl_f'] = pd.Categorical(d.ctrl_n.astype(int), [3, 2, 1, 0])
rows = []
for out in ['pain_any','nc_skin','nc_fatigue']:
    s = d[d[out].notna()]
    b, V, n = pois(f"{out} ~ C(ctrl_f) + {base_rhs}", s)
    for k in [2, 1, 0]:
        rows.append([out, f'{k} of 3 vs 3 of 3', fmt(pr(b, V, f'C(ctrl_f)[T.{k}]')), n])
w = d.groupby('ctrl_n').apply(lambda s: pd.Series({'n': len(s), 'weighted %': np.average(np.ones(len(s)), weights=s.wt_n)}), include_groups=False)
T9 = pd.DataFrame(rows, columns=['outcome','contrast','PR (95% CI)','n']); print(T9.to_string(index=False))
print('distribution of ctrl_n (weighted %):', (d.groupby('ctrl_n').wt_n.sum() / d.wt_n.sum() * 100).round(1).to_dict())
T9.to_csv(os.path.join(OUT, 'T9_control_count.csv'), index=False)

print('\nT10. 문항별 "아니오" vs "예" (세 문항 동시 투입), any pain')
b, V, n = pois(f"pain_any ~ I(1-ctl1) + I(1-ctl2) + I(1-ctl3) + {base_rhs}", d)
for t in ['I(1 - ctl1)','I(1 - ctl2)','I(1 - ctl3)']: print(' ', t, fmt(pr(b, V, t)))

print('\nT11. 음성대조 x 종사상지위 (통제 전혀 없음 vs 완전)')
rows = []
for g, sub in [('employee', d[d.selfemp == 0]), ('self-employed', d[d.selfemp == 1])]:
    for out in ['pain_any','nc_headeye','nc_fatigue','nc_hearing','nc_skin']:
        s = sub[sub[out].notna()]
        b, V, n = pois(f"{out} ~ {EXPO} + {ERG} + {COV}", s)
        r = pr(b, V, 'C(ctrl_cat)[T.none]'); rows.append([g, out, n, fmt(r)])
T11 = pd.DataFrame(rows, columns=['group','outcome','n','none vs full']); print(T11.to_string(index=False))
T11.to_csv(os.path.join(OUT, 'T11_negcontrol_by_emp.csv'), index=False)

print('\nT12. 2023(7차) 단독: 강건 분산 vs 층(stratification) 군집 분산')
s7 = d[d.wave == 7].copy()
print('strata non-missing:', s7.strata.notna().sum(), 'unique strata:', s7.strata.nunique())
f = f"pain_any ~ {EXPO} + C(emp4) + {ERG} + " + COV.replace(' + C(wave)', '')
y, X = patsy.dmatrices(f, s7, return_type='dataframe')
wt = s7.loc[y.index, 'wt_n'].values; yv = y.values.ravel(); Xv = X.values
b0, V0, n = pois(f, s7)
mu = np.exp(Xv @ b0.values)
Hinv = np.linalg.inv((Xv * (wt * mu)[:, None]).T @ Xv)
U = pd.DataFrame(Xv * (wt * (yv - mu))[:, None]).groupby(s7.loc[y.index, 'strata'].values).sum().values
G = U.shape[0]
Vc = Hinv @ (U.T @ U) @ Hinv * G / (G - 1)
Vc = pd.DataFrame(Vc, X.columns, X.columns)
for t in ['C(ctrl_cat)[T.none]','C(ctrl_cat)[T.partial]','dem_z']:
    print(f"  {t:25s} robust {fmt(pr(b0, V0, t))}   strata-clustered (G={G}) {fmt(pr(b0, Vc, t))}")
