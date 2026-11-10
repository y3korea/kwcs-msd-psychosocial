"""R1 사후 분석 (2026-11-10): 응답 형식 비교. 5점 척도 통제 문항(wsituation9, '업무에 내 생각을 적용할 수 있다')과
예/아니오 3문항(decla1-3) 통제 범주를 같은 모형에 넣어 비교. 이전 KWCS 연구(Lee 2021, 5점 척도 통제)와의 차이를 점검하기 위해 추가."""
import os
src = open(os.path.join(os.path.dirname(__file__), 'r1_03_analysis.py')).read().split("print('='*78); print('T1.")[0]
exec(src)
d2 = d[d.ideas.notna()].copy()
d2['low_ideas'] = (d2.ideas <= 2).astype(float)   # 거의/전혀 적용 못함 (원 코드 4-5)
base = f"C(sup_cat) + dem_z + C(emp4) + {ERG} + {COV}"
lab = {'pain_any': 'Any musculoskeletal pain', 'nc_headeye': 'Headache/eye strain', 'nc_fatigue': 'General fatigue',
       'nc_hearing': 'Hearing problem*', 'nc_skin': 'Skin problem*'}
rows = []
for out in lab:
    s = d2[d2[out].notna()]
    b, V, n = pois(f"{out} ~ low_ideas + {base}", s)
    b2, V2, _ = pois(f"{out} ~ low_ideas + C(ctrl_cat) + {base}", s)
    rows.append([lab[out], f'{n:,}', fmt(pr(b, V, 'low_ideas')), fmt(pr(b2, V2, 'low_ideas')),
                 fmt(pr(b2, V2, 'C(ctrl_cat)[T.none]')), fmt(pr(b2, V2, 'C(ctrl_cat)[T.partial]'))])
T = pd.DataFrame(rows, columns=['Outcome', 'n', 'Low own-ideas item, alone', 'Low own-ideas item, joint model',
                                'Yes/no control: none vs full, joint model', 'Yes/no control: partial vs full, joint model'])
print(T.to_string(index=False)); T.to_csv(os.path.join(OUT, 'T13_format_comparison.csv'), index=False)
w = np.average(d2.low_ideas, weights=d2.wt_n) * 100
x = d2.groupby('ctrl_cat', observed=True).apply(lambda s: np.average(s.low_ideas, weights=s.wt_n) * 100, include_groups=False).round(1)
print(f'low own-ideas weighted %: {w:.1f}; by yes/no control category (weighted %):', x.to_dict())
pd.Series({'low_ideas_pct': round(w, 1), **{f'low_ideas_pct_{k}': v for k, v in x.items()}}).to_csv(os.path.join(OUT, 'T13b_format_xtab.csv'))
