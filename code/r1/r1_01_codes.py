"""차수별 응답 코드 분포(집계)."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
import pandas as pd
from r1_00_load import load_all, ITEMS
df = load_all()
print("N by wave:", df.wave.value_counts().sort_index().to_dict(), "total", len(df))
for v in ITEMS+['sex']:
    if v in ('wtime_week',):
        print(f"\n{v}: describe by wave"); print(df.groupby('wave')[v].describe(percentiles=[.5,.99]).round(1).to_string()); 
        print(" >=168 counts:", df[df[v]>=168].groupby('wave').size().to_dict()); continue
    t = pd.crosstab(df[v].fillna(-1).astype(int), df.wave)
    print(f"\n{v}"); print(t.to_string())
print("\nage describe:"); print(df.groupby('wave')['age'].describe().round(1).to_string())
print("\nind unique by wave:", df.groupby('wave')['ind'].nunique().to_dict())
print("wt missing by wave:", df.groupby('wave')['wt'].apply(lambda s:s.isna().sum()).to_dict())
