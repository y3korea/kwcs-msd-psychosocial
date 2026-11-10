"""R1 음성대조 결과변수 분석 + '모두 아니오' 응답 성향 점검 (2026-11-10). 집계만 출력."""
import os, sys; sys.path.insert(0, os.path.dirname(__file__))
import numpy as np, pandas as pd
import importlib.util
spec = importlib.util.spec_from_file_location('a', os.path.join(os.path.dirname(__file__), 'r1_03_analysis.py'))
# r1_03의 함수만 재사용하지 않고 필요한 부분을 다시 정의(전체 실행 방지)
src = open(spec.origin).read().split("print('='*78); print('T1.")[0]
exec(src)
print('='*78); print('T7. 음성대조 결과변수 (통제 범주 PR, 주 모형과 같은 보정)'); print('='*78)
rows = []
for out, lab, sub in [('pain_any','Musculoskeletal pain (any)', d), ('nc_headeye','Headache/eye strain', d),
                      ('nc_fatigue','General fatigue', d), ('nc_hearing','Hearing problem (W2-W5)', d[d.wave <= 5]),
                      ('nc_skin','Skin problem (W2-W5)', d[d.wave <= 5])]:
    s = sub[sub[out].notna()]
    b, V, n = pois(f"{out} ~ {EXPO} + C(emp4) + {ERG} + {COV}", s)
    prev = np.average(s[out], weights=s.wt_n) * 100
    rows.append([lab, n, f"{prev:.1f}", fmt(pr(b,V,'C(ctrl_cat)[T.none]')), fmt(pr(b,V,'C(ctrl_cat)[T.partial]')), fmt(pr(b,V,'dem_z'))])
T7 = pd.DataFrame(rows, columns=['outcome','n','prev %','Control none vs full','Control partial vs full','Demand per SD'])
print(T7.to_string(index=False)); T7.to_csv(os.path.join(OUT, 'T7_negative_control.csv'), index=False)

print('\n' + '='*78); print('T8. 통제 범주별 특성 (가중): "모두 아니오" 집단은 누구인가'); print('='*78)
d['n_health_yes'] = d[['pain_back','pain_upper','pain_lower','nc_headeye','nc_fatigue']].sum(axis=1)
g = {}
for c, sub in d.groupby('ctrl_cat', observed=True):
    w = sub.wt_n
    g[c] = {'n': len(sub), 'employee %': np.average((sub.emp4=='employee'), weights=w)*100,
            'age': np.average(sub.age, weights=w), 'college %': np.average(sub.edu3=='college', weights=w)*100,
            'ideas (1-5) mean': np.average(sub.ideas.fillna(sub.ideas.mean()), weights=w),
            'demand (1-7) mean': np.average(sub.demand, weights=w), 'erg_n mean': np.average(sub.erg_n, weights=w),
            'health problems reported (0-5) mean': np.average(sub.n_health_yes.fillna(0), weights=w)}
print(pd.DataFrame(g).round(2).to_string())
