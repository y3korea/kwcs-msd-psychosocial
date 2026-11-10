"""R1 주 분석 (2026-11-10). 집계 결과만 출력.
수정 포아송(로그 링크) + 샌드위치 분산. 가중치: 차수 내 정규화한 KWCS 가중치(pweight 방식).
"""
import os, sys, numpy as np, pandas as pd, patsy
from scipy import stats
OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'output', 'r1')
d = pd.read_parquet(os.path.join(OUT, 'kwcs_r1.parquet'))
d['ctrl_cat'] = pd.Categorical(d.ctrl_cat, ['full','partial','none'])
d['sup_cat'] = pd.Categorical(d.sup_cat, ['high','low','none_colleague'])
d['emp4'] = pd.Categorical(d.emp4, ['employee','own_account','employer','unpaid_family'])
d['dem_z'] = (d.demand - d.demand.mean()) / d.demand.std()
d['ideas_z'] = (d.ideas - d.ideas.mean()) / d.ideas.std()
R = []   # 결과 수집

def pois(formula, data, w='wt_n'):
    y, X = patsy.dmatrices(formula, data, return_type='dataframe', NA_action='drop')
    wt = data.loc[y.index, w].values if w else np.ones(len(y))
    yv, Xv = y.values.ravel(), X.values
    b = np.zeros(Xv.shape[1]); b[0] = np.log(np.average(yv, weights=wt))
    for _ in range(50):
        mu = np.exp(Xv @ b)
        g = Xv.T @ (wt * (yv - mu))
        H = (Xv * (wt * mu)[:, None]).T @ Xv
        step = np.linalg.solve(H, g); b += step
        if np.max(np.abs(step)) < 1e-9: break
    mu = np.exp(Xv @ b)
    Hinv = np.linalg.inv((Xv * (wt * mu)[:, None]).T @ Xv)
    S = Xv * (wt * (yv - mu))[:, None]
    V = Hinv @ (S.T @ S) @ Hinv * len(yv) / (len(yv) - Xv.shape[1])
    return pd.Series(b, X.columns), pd.DataFrame(V, X.columns, X.columns), len(yv)

def pr(b, V, term):
    se = np.sqrt(V.loc[term, term]); e = b[term]
    p = 2 * stats.norm.sf(abs(e / se))
    return np.exp(e), np.exp(e - 1.96*se), np.exp(e + 1.96*se), p

def fmt(t): return f"{t[0]:.2f} ({t[1]:.2f}–{t[2]:.2f})"
def fp(p): return '<0.001' if p < 0.001 else f'{p:.3f}'

COV = "age_c + age_c2 + female + C(edu3) + C(ind) + C(hours_cat) + C(wave)"
ERG = "erg_post + erg_heavy + erg_stand + erg_rep"
EXPO = "C(ctrl_cat) + dem_z + C(sup_cat)"
TERMS = {'Control: partial vs full':'C(ctrl_cat)[T.partial]', 'Control: none vs full':'C(ctrl_cat)[T.none]',
         'Demand (per SD)':'dem_z', 'Colleague support: low vs high':'C(sup_cat)[T.low]',
         'No colleagues vs high support':'C(sup_cat)[T.none_colleague]'}

def wpct(s, w):
    m = s.notna(); return np.average(s[m], weights=w[m]) * 100

print('='*78); print('T1. 종사상지위별 특성 (가중 %, 평균)'); print('='*78)
rows = {}
for g, sub in [('All', d)] + [(k, v) for k, v in d.groupby('emp4', observed=True)]:
    w = sub.wt_n
    rows[g] = {'n': len(sub), 'female %': wpct(sub.female, w), 'age mean': np.average(sub.age, weights=w),
        'pain any %': wpct(sub.pain_any, w), 'back %': wpct(sub.pain_back, w), 'upper %': wpct(sub.pain_upper, w),
        'lower %': wpct(sub.pain_lower, w), 'no control (0/3) %': wpct(sub.no_ctrl, w),
        'full control (3/3) %': wpct((sub.ctrl_n == 3).astype(float), w),
        'high demand %': wpct(sub.hi_dem, w),
        'low colleague support %': wpct((sub.sup_cat == 'low').astype(float), w),
        'no colleagues %': wpct((sub.sup_cat == 'none_colleague').astype(float), w),
        '>=2 ergonomic exposures %': wpct((sub.erg_n >= 2).astype(float), w)}
T1 = pd.DataFrame(rows).round(1); print(T1.to_string()); T1.to_csv(os.path.join(OUT, 'T1_by_employment.csv'))

print('\n' + '='*78); print('T2. 주 모형: 전체 근로자 (PR, 95% CI) -- 노출 3개 동시 투입, 종사상지위·인간공학 보정'); print('='*78)
T2 = []
for out in ['pain_any','pain_back','pain_upper','pain_lower']:
    b, V, n = pois(f"{out} ~ {EXPO} + C(emp4) + {ERG} + {COV}", d)
    for lab, t in TERMS.items():
        r = pr(b, V, t); T2.append([out, lab, fmt(r), fp(r[3]), n])
T2 = pd.DataFrame(T2, columns=['outcome','exposure','PR (95% CI)','p','n']); print(T2.to_string(index=False))
T2.to_csv(os.path.join(OUT, 'T2_main.csv'), index=False)

print('\n' + '='*78); print('T3. 임금근로자 vs 자영업자(고용원 유무 합산) 층화 + 상호작용 (any pain)'); print('='*78)
T3 = []
for g, sub in [('employee', d[d.selfemp == 0]), ('self-employed', d[d.selfemp == 1])]:
    b, V, n = pois(f"pain_any ~ {EXPO} + {ERG} + {COV}", sub)
    for lab, t in TERMS.items():
        if g == 'self-employed' and t == 'C(sup_cat)[T.none_colleague]' or True:
            try: r = pr(b, V, t); T3.append([g, lab, fmt(r), fp(r[3]), n])
            except KeyError: pass
T3 = pd.DataFrame(T3, columns=['group','exposure','PR (95% CI)','p','n']); print(T3.to_string(index=False))
T3.to_csv(os.path.join(OUT, 'T3_stratified.csv'), index=False)
de = d[d.selfemp.notna()].copy()
b, V, n = pois(f"pain_any ~ C(ctrl_cat)*selfemp + dem_z*selfemp + C(sup_cat) + {ERG} + {COV}", de)
it = [t for t in b.index if ':selfemp' in t]
print('\n상호작용 (ratio of PRs, self-employed vs employee):')
for t in it: print(f"  {t:35s} {fmt(pr(b, V, t))}  p={fp(pr(b, V, t)[3])}")
ci = [t for t in it if 'ctrl_cat' in t]
bb = b[ci].values; VV = V.loc[ci, ci].values
chi = float(bb @ np.linalg.solve(VV, bb)); print(f"  control x employment joint Wald chi2({len(ci)}) = {chi:.2f}, p = {fp(stats.chi2.sf(chi, len(ci)))}")
# RERI: no control (0/3) x self-employed, 기준 = full/partial control 임금근로자
de['nc'] = de.no_ctrl
b, V, n = pois(f"pain_any ~ nc*selfemp + dem_z + C(sup_cat) + {ERG} + {COV}", de)
t1, t2, t3 = 'nc', 'selfemp', 'nc:selfemp'
e1, e2, e3 = b[t1], b[t2], b[t3]
reri = np.exp(e1+e2+e3) - np.exp(e1) - np.exp(e2) + 1
gr = np.array([np.exp(e1+e2+e3)-np.exp(e1), np.exp(e1+e2+e3)-np.exp(e2), np.exp(e1+e2+e3)])
Vs = V.loc[[t1,t2,t3],[t1,t2,t3]].values; se = np.sqrt(gr @ Vs @ gr)
print(f"  RERI (no control x self-employed) = {reri:.3f} ({reri-1.96*se:.3f} to {reri+1.96*se:.3f})")

print('\n' + '='*78); print('T4. 민감도 분석 (any pain; 통제 none vs full, partial vs full, 요구 per SD)'); print('='*78)
def row(lab, data, f, w='wt_n'):
    b, V, n = pois(f, data, w)
    return [lab, n, fmt(pr(b,V,'C(ctrl_cat)[T.none]')), fmt(pr(b,V,'C(ctrl_cat)[T.partial]')), fmt(pr(b,V,'dem_z'))]
base = f"pain_any ~ {EXPO} + C(emp4) + {ERG} + {COV}"
T4 = [row('Primary (weighted)', d, base),
      row('Unweighted', d, base, None),
      row('No ergonomic adjustment', d, f"pain_any ~ {EXPO} + C(emp4) + {COV}"),
      row('No employment-status/industry adj.', d, f"pain_any ~ {EXPO} + {ERG} + age_c + age_c2 + female + C(edu3) + C(hours_cat) + C(wave)"),
      row('Excluding 2017 wave', d[d.wave != 5], base),
      row('Employees only, + skill discretion', d[d.selfemp == 0], f"pain_any ~ {EXPO} + ideas_z + {ERG} + {COV}"),
      row('Age 15-39', d[d.age < 40], base), row('Age 40-54', d[(d.age >= 40) & (d.age < 55)], base), row('Age 55+', d[d.age >= 55], base)]
for w in sorted(d.wave.unique()):
    T4.append(row(f'Wave {w}', d[d.wave == w], base.replace(' + C(wave)', '')))
T4 = pd.DataFrame(T4, columns=['analysis','n','Control none vs full','Control partial vs full','Demand per SD'])
print(T4.to_string(index=False)); T4.to_csv(os.path.join(OUT, 'T4_sensitivity.csv'), index=False)

print('\n' + '='*78); print('T5. 문항별 "아니오"(통제 불가) 가중 % : 차수 x 종사상지위'); print('='*78)
for it_ in ['ctl1','ctl2','ctl3']:
    t = d.assign(no=1 - d[it_]).groupby(['wave','emp4'], observed=True).apply(lambda s: wpct(s.no, s.wt_n)).unstack().round(1)
    print(it_); print(t.to_string())
t = d.groupby(['wave','emp4'], observed=True).apply(lambda s: wpct(s.no_ctrl, s.wt_n)).unstack().round(1)
print('no control (0/3)'); print(t.to_string()); t.to_csv(os.path.join(OUT, 'T5_nocontrol_trend.csv'))
t = d.groupby('wave').apply(lambda s: pd.Series({'pain_any': wpct(s.pain_any, s.wt_n), 'no_ctrl': wpct(s.no_ctrl, s.wt_n),
      'hi_dem': wpct(s.hi_dem, s.wt_n), 'low_sup': wpct((s.sup_cat=='low').astype(float), s.wt_n)})).round(1)
print('\n가중 유병률 추세'); print(t.to_string()); t.to_csv(os.path.join(OUT, 'T6_trends.csv'))
