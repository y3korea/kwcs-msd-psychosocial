"""R1 재분석 공통: KWCS 2-7차 원자료를 코드북 기준으로 다시 읽는다 (2026-11-10).
개인 단위 행은 절대 출력하지 않는다. 집계만 출력.
"""
import os, numpy as np, pandas as pd
# KWCS 원자료 폴더: 환경변수 KWCS_DATA_DIR로 지정. 없으면 프로젝트 기본 위치(코드 기준 상대경로)를 쓴다.
_DEFAULT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data')
DATA = os.path.normpath(os.environ.get('KWCS_DATA_DIR', _DEFAULT))
RAW = {
 2:('2차_근로환경/[CSV]2nd_KWCS_kor/★원시자료_2차 근로환경조사_제공용_220207.csv',2010),
 3:('3차_근로환경/[CSV]3rd_KWCS_kor/★원시자료_3차 근로환경조사_제공용_22207.csv',2011),
 4:('4차_근로환경/[CSV]4th_KWCS_kor/★원시자료_4차 근로환경조사_제공용_220126.csv',2014),
 5:('5차_근로환경/[CSV]5th_KWCS_kor/★원시자료_5차 근로환경조사_제공용_22207.csv',2017),
 6:('6차_근로환경/[CSV]6th_KWCS_kor/★원시자료_6차 근로환경조사_제공용_220210.csv',2020),
 7:('7차_근로환경/[CSV] 7th KWCS_kor/[데이터] 2023년 제7차 근로환경조사.dat',2023)}
ITEMS = ['heal_prob1','heal_prob2','heal_prob3','winten2_1','winten2_2','decla1','decla2','decla3',
         'wsituation1','wsituation2','wsituation9','hazard_erg1','hazard_erg3','hazard_erg4','hazard_erg6',
         'hazard_psy1','emp_type','edu','wtime_week']
# 음성대조 결과변수: 4=두통·눈의 피로, 6=전신피로 (전 차수), 8=청력, 9=피부 (2-5차에서만 같은 문항)
OPTIONAL = {w: ['heal_prob4','heal_prob6'] + (['heal_prob8','heal_prob9'] if w <= 5 else []) for w in range(2, 8)}
OPTIONAL[7] = OPTIONAL[7] + ['stratification']
DEMO = {2:{'TSEX':'sex','AGE':'age','IND':'ind','wt':'wt'},
        3:{'TSEX':'sex','TAGE':'age','IND':'ind','wt':'wt'},
        4:{'TSEX':'sex','TAGE':'age','IND':'ind','wt':'wt'},
        5:{'TSEX':'sex','TAGE':'age','IND':'ind','wt':'wt'},
        6:{'TSEX':'sex','AGE':'age','IND':'ind','wt':'wt'},
        7:{'gender':'sex','age':'age','ind':'ind','wt3':'wt'}}
def load_wave(w):
    f, yr = RAW[w]
    kw = dict(low_memory=False)
    if w == 7: kw.update(sep='\t', encoding='utf-8', encoding_errors='replace')
    else: kw['encoding'] = 'utf-8-sig'
    hdr = pd.read_csv(os.path.join(DATA, f), nrows=0, **{k: v for k, v in kw.items() if k != 'low_memory'}).columns
    extra = [c for c in OPTIONAL.get(w, []) if c in hdr]
    kw['usecols'] = ITEMS + list(DEMO[w]) + extra
    d = pd.read_csv(os.path.join(DATA, f), **kw).rename(columns=DEMO[w])
    for c in d.columns: d[c] = pd.to_numeric(d[c], errors='coerce')
    d['wave'], d['year'] = w, yr
    return d
def load_all():
    return pd.concat([load_wave(w) for w in RAW], ignore_index=True)
