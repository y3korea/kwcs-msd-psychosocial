"""R1 분석자료 재구성 (2026-11-10). 코드북·조사표(2~7차) 대조 결과를 반영한다.

이전 파이프라인(0_extract / 1_preprocess)과 달라진 점
 1. 요구(demand): hazard_psy1('동료가 아닌 사람을 직접 상대함', 고객 응대)이 아니라
    winten2_1(매우 빠른 속도), winten2_2(엄격한 마감시간) 사용 -- JDC 요구의 표준 문항.
 2. 빈도 척도 코드 7('절대 노출 안 됨/전혀 없음')은 유효 응답(가장 낮은 노출)으로 유지.
    8=모름, 9=거절만 결측. (이전에는 7을 결측 처리해 비노출자가 대거 탈락)
 3. 동료지지 7('해당 없음', 동료 없음)은 결측이 아니라 별도 범주. 상사지지는 자영업자에게
    구조적으로 해당이 없으므로 주 모형에서 쓰지 않는다.
 4. 통제(control): '예' 개수 0-3을 사전 정의 범주로 사용(백분위 절단 사용 안 함).
 5. emp_type: 1=고용원 없는 자영업자, 2=고용원 있는 자영업자(고용주), 3=임금근로자,
    4=무급가족종사자 (조사표 확인). 5(기타, 3차 위주)는 제외.
출력: output/r1/kwcs_r1.parquet  (KWCS 파생 원자료 -- 외부 업로드 금지)
"""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
import numpy as np, pandas as pd
from r1_00_load import load_all

OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'output', 'r1')
os.makedirs(OUT, exist_ok=True)
df = load_all()
N0 = len(df)
flow = [('pooled raw (W2-W7)', N0)]

def valid(s, lo, hi):
    return s.where((s >= lo) & (s <= hi))

# outcomes: 1=있다, 2=없다
for k, v in {'pain_back':'heal_prob1','pain_upper':'heal_prob2','pain_lower':'heal_prob3'}.items():
    df[k] = valid(df[v], 1, 2).map({1:1.0, 2:0.0})
df['pain_any'] = df[['pain_back','pain_upper','pain_lower']].max(axis=1, skipna=False)
# 음성대조(근골격계 외 건강문제)
for k, v in {'nc_headeye':'heal_prob4','nc_fatigue':'heal_prob6','nc_hearing':'heal_prob8','nc_skin':'heal_prob9'}.items():
    df[k] = valid(df[v], 1, 2).map({1:1.0, 2:0.0}) if v in df else np.nan

# demand: 1=근무시간 내내 ... 7=전혀 없음  -> 높을수록 요구 큼 (1..7)
for i, v in [(1,'winten2_1'),(2,'winten2_2')]:
    df[f'dem{i}'] = 8 - valid(df[v], 1, 7)
df['demand'] = df[['dem1','dem2']].mean(axis=1, skipna=False)
# 사전 정의: 두 문항 모두 '근무시간의 절반 이상'(코드 1-4 -> dem>=4)
df['hi_dem'] = np.where(df[['dem1','dem2']].notna().all(axis=1),
                        ((df.dem1 >= 4) & (df.dem2 >= 4)).astype(float), np.nan)

# control: 1=그렇다, 2=아니다
for i in (1,2,3):
    df[f'ctl{i}'] = valid(df[f'decla{i}'], 1, 2).map({1:1.0, 2:0.0})
df['ctrl_n'] = df[['ctl1','ctl2','ctl3']].sum(axis=1, min_count=3)
df['ctrl_cat'] = pd.cut(df.ctrl_n, [-0.5, 0.5, 2.5, 3.5], labels=['none','partial','full'])
df['no_ctrl'] = np.where(df.ctrl_n.notna(), (df.ctrl_n == 0).astype(float), np.nan)
# skill discretion proxy: wsituation9 '업무에 내 생각을 적용할 수 있다' 1=항상..5=전혀
df['ideas'] = 6 - valid(df['wsituation9'], 1, 5)   # 높을수록 재량 큼

# colleague support: 1 항상 2 대부분 3 가끔 4 별로 5 전혀 7 해당없음
ws = df['wsituation1']
df['sup_cat'] = np.select([ws.isin([1,2]), ws.isin([3,4,5]), ws.eq(7)], ['high','low','none_colleague'], default=None)

# ergonomic: 1 내내 ... 4 절반 5 1/4 6 거의 노출 안됨 7 절대 노출 안됨 ; high = 절반 이상
for k, v in {'erg_post':'hazard_erg1','erg_heavy':'hazard_erg3','erg_stand':'hazard_erg4','erg_rep':'hazard_erg6'}.items():
    s = valid(df[v], 1, 7)
    df[k] = np.where(s.notna(), (s <= 4).astype(float), np.nan)
df['erg_n'] = df[['erg_post','erg_heavy','erg_stand','erg_rep']].sum(axis=1, min_count=4)

# employment status
df['emp4'] = df.emp_type.map({1:'own_account', 2:'employer', 3:'employee', 4:'unpaid_family'})
df['selfemp'] = df.emp_type.map({1:1.0, 2:1.0, 3:0.0})   # 주 비교: 자영업(1+2) vs 임금근로(3)

# covariates
df['female'] = df.sex.map({1:0.0, 2:1.0})
df['age_c'] = (df.age - 50) / 10
df['age_c2'] = df.age_c ** 2
df['edu3'] = pd.cut(valid(df.edu, 1, 7), [0, 3, 4, 7], labels=['le_middle','high','college'])
h = df.wtime_week.where(df.wtime_week < 168)
df['hours_cat'] = np.select([h.isna(), h > 52], ['missing', 'gt52'], default='le52')
df['ind'] = df['ind'].fillna(-1).astype(int)
df['wt_n'] = df.wt / df.groupby('wave').wt.transform('mean')   # 차수 내 평균 1로 정규화

keep = df.emp4.notna()
flow.append(('valid employment status (excl. other/NA)', int(keep.sum())))
core = ['pain_any','pain_back','pain_upper','pain_lower','ctrl_n','demand','sup_cat',
        'erg_n','female','age','edu3']
m = keep.copy()
for c in core:
    m &= df[c].notna()
    flow.append((f'+ non-missing {c}', int(m.sum())))
ana = df.loc[m].copy()
print('\n'.join(f'{a:45s} {b:>8,} ({b/N0*100:5.1f}%)' for a, b in flow))
print('final analytic N =', len(ana), f'({len(ana)/N0*100:.1f}% of pooled raw)')
print('by wave:', ana.wave.value_counts().sort_index().to_dict())
ana['strata'] = ana['stratification'] if 'stratification' in ana else np.nan
cols = ['strata','nc_headeye','nc_fatigue','nc_hearing','nc_skin','wave','year','wt','wt_n','pain_any','pain_back','pain_upper','pain_lower','dem1','dem2','demand','hi_dem',
        'ctl1','ctl2','ctl3','ctrl_n','ctrl_cat','no_ctrl','ideas','sup_cat','erg_post','erg_heavy','erg_stand',
        'erg_rep','erg_n','emp4','selfemp','female','age','age_c','age_c2','edu3','hours_cat','ind']
ana[cols].to_parquet(os.path.join(OUT, 'kwcs_r1.parquet'), index=False)
pd.DataFrame(flow, columns=['step','n']).to_csv(os.path.join(OUT, 'flow.csv'), index=False)
print('saved')
