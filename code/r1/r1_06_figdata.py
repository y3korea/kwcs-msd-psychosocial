"""그림용 집계 (2026-11-10): 통제 '예' 개수별 PR (8개 결과), 종사상지위별 개수 분포."""
import os
src = open(os.path.join(os.path.dirname(__file__), 'r1_03_analysis.py')).read().split("print('='*78); print('T1.")[0]
exec(src)
d['ctrl_f'] = pd.Categorical(d.ctrl_n.astype(int), [3, 2, 1, 0])
rhs = f"C(ctrl_f) + dem_z + C(sup_cat) + C(emp4) + {ERG} + {COV}"
outs = [('pain_any','MSK pain, any site'),('pain_back','Back pain'),('pain_upper','Upper-limb pain'),('pain_lower','Lower-limb pain'),
        ('nc_headeye','Headache/eye strain'),('nc_fatigue','General fatigue'),('nc_hearing','Hearing problem*'),('nc_skin','Skin problem*')]
rows = []
for o, lab in outs:
    s = d[d[o].notna()]
    b, V, n = pois(f"{o} ~ {rhs}", s)
    for k in [2, 1, 0]:
        e, lo, hi, p = pr(b, V, f'C(ctrl_f)[T.{k}]'); rows.append([o, lab, k, e, lo, hi, n])
pd.DataFrame(rows, columns=['outcome','label','yes_n','pr','lo','hi','n']).to_csv(os.path.join(OUT, 'F2_control_count_pr.csv'), index=False)
dist = d.groupby(['emp4','ctrl_n'], observed=True).wt_n.sum().unstack()
dist = (dist.T / dist.sum(axis=1)).T * 100
dist.round(2).to_csv(os.path.join(OUT, 'F1_ctrl_distribution.csv')); print(dist.round(1).to_string())
print(pd.read_csv(os.path.join(OUT, 'F2_control_count_pr.csv')).round(2).to_string())
