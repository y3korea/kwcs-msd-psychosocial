"""표 1-2와 보충표 S1-S6 마크다운 생성 (결과 CSV에서 직접 생성; 수기 전사 없음)."""
import os, pandas as pd
R = os.path.join(os.path.dirname(__file__), '..', 'output', 'r1')
M = os.path.join(os.path.dirname(__file__), '..', 'output', 'tables'); os.makedirs(M, exist_ok=True)
rd = lambda f, **k: pd.read_csv(os.path.join(R, f), **k)

def md(df):
    cols = list(df.columns)
    out = ['| ' + ' | '.join(map(str, cols)) + ' |', '|' + '|'.join([':--'] + ['--:'] * (len(cols) - 1)) + '|']
    for _, r in df.iterrows(): out.append('| ' + ' | '.join(str(x) for x in r.values) + ' |')
    return '\n'.join(out)

# ---------- Table 1
t1 = rd('T1_by_employment.csv', index_col=0)
lab = {'n': 'n (unweighted)', 'female %': 'Women, %', 'age mean': 'Age, mean (years)', 'pain any %': 'Any musculoskeletal pain, %',
       'back %': '  Back pain, %', 'upper %': '  Upper-limb pain, %', 'lower %': '  Lower-limb pain, %',
       'no control (0/3) %': 'No control (0 of 3 items), %', 'full control (3/3) %': 'Full control (3 of 3 items), %',
       'high demand %': 'High demand*, %', 'low colleague support %': 'Low colleague support, %', 'no colleagues %': 'No colleagues, %',
       '>=2 ergonomic exposures %': '≥2 ergonomic exposures†, %'}
t1 = t1.loc[list(lab)]
t1.index = [lab[i] for i in t1.index]
t1 = t1.rename(columns={'All': 'All', 'employee': 'Employees', 'own_account': 'Own-account self-employed', 'employer': 'Employers', 'unpaid_family': 'Unpaid family workers'})
t1 = t1.map(lambda x: f'{x:,.1f}')
t1.loc['n (unweighted)'] = [f'{int(float(v.replace(",", ""))):,}' for v in t1.loc['n (unweighted)']]
t1 = t1.reset_index().rename(columns={'index': 'Characteristic'})
T1 = ('**Table 1.** Characteristics of the study population by employment status, Korean Working Conditions Survey 2010–2023 '
      '(weighted percentages and means)\n\n' + md(t1) +
      '\n\n*Working at very high speed and to tight deadlines, each for at least half of working time. '
      '†Tiring or painful postures, moving heavy loads, standing, or repetitive hand/arm movements for at least half of working time.\n')

# ---------- Table 2
t2 = rd('T2_main.csv')
ex = ['Control: partial vs full', 'Control: none vs full', 'Demand (per SD)', 'Colleague support: low vs high', 'No colleagues vs high support']
exl = {'Control: partial vs full': 'Job control: partial (1–2 of 3) vs full (3 of 3)', 'Control: none vs full': 'Job control: none (0 of 3) vs full (3 of 3)',
       'Demand (per SD)': 'Psychological demand, per SD', 'Colleague support: low vs high': 'Colleague support: low vs high',
       'No colleagues vs high support': 'Colleague support: no colleagues vs high'}
oc = {'pain_any': 'Any site', 'pain_back': 'Back', 'pain_upper': 'Upper limb', 'pain_lower': 'Lower limb'}
w = t2.pivot(index='exposure', columns='outcome', values='PR (95% CI)').loc[ex, list(oc)]
w.index = [exl[i] for i in w.index]; w.columns = [oc[c] for c in w.columns]
w = w.reset_index().rename(columns={'index': 'Exposure'})
T2 = ('**Table 2.** Adjusted prevalence ratios (95% CI) for 12-month musculoskeletal pain (n=252,798)\n\n' + md(w) +
      '\n\nModified Poisson regression with robust variance and survey weights; all exposures entered together and adjusted for age, age², sex, '
      'education, industry, weekly working hours, survey wave, employment status, and four ergonomic exposures.\n')
open(os.path.join(M, 'tables.md'), 'w').write('# Tables\n\n' + T1 + '\n\n\\newpage\n\n' + T2)

# ---------- Supplementary
S = ['# Supplementary material\n',
     '**Table S1.** Survey items and coding (identical wording and response codes in the 2nd–7th waves, verified against each questionnaire)\n',
     md(pd.DataFrame([
        ['Back / upper-limb / lower-limb pain (heal_prob1–3)', 'Problem in past 12 months: yes/no', '1=yes; 2=no; 8, 9 missing'],
        ['Headache/eye strain (heal_prob4); overall fatigue (heal_prob6)', 'Same block, all waves', 'As above'],
        ['Hearing (heal_prob8); skin (heal_prob9)', 'Same block, 2010–2017 only', 'As above'],
        ['Job control (decla1–3)', 'Able to choose or change task order / methods / speed or rate of work: yes/no', 'Number of "yes" (0–3); full=3, partial=1–2, none=0'],
        ['Demand (winten2_1, winten2_2)', 'Working at very high speed; to tight deadlines: 1=all of the time … 7=never', 'Reversed (8−x), mean of 2 items, standardized; 8, 9 missing'],
        ['Colleague support (wsituation1)', '1=always … 5=never; 7=not applicable', '1–2 high; 3–5 low; 7 no colleagues'],
        ['Skill discretion (wsituation9)', 'Able to apply own ideas: 1=always … 5=never', 'Reversed, standardized (sensitivity only)'],
        ['Ergonomic exposures (hazard_erg1, 3, 4, 6)', '1=all of the time … 6=almost never, 7=never', 'Exposed if codes 1–4 (≥ half of time); 7 valid; 8, 9 missing'],
        ['Employment status (emp_type)', '1 own-account; 2 employer; 3 employee; 4 unpaid family', 'Code 5 (other) excluded'],
        ['Weekly working hours (wtime_week)', 'Hours', '>52 h; values ≥168 or missing as separate category'],
     ], columns=['Variable (KWCS name)', 'Item / response scale', 'Analytic coding'])), '\n\n\\newpage\n']
fl = rd('flow.csv')
fl = fl[~fl.step.isin(['+ non-missing pain_back', '+ non-missing pain_upper', '+ non-missing pain_lower', '+ non-missing female', '+ non-missing age'])]
fl['%'] = (fl.n / fl.n.iloc[0] * 100).round(1)
fl['n'] = fl.n.map('{:,}'.format)
fl['step'] = fl.step.map({'pooled raw (W2-W7)': 'All respondents, 2nd–7th waves', 'valid employment status (excl. other/NA)': 'Valid employment status (excluding "other")',
    '+ non-missing pain_any': 'and valid answers to all three pain items', '+ non-missing ctrl_n': 'and all three job-control items',
    '+ non-missing demand': 'and both demand items', '+ non-missing sup_cat': 'and colleague support (including "not applicable")',
    '+ non-missing erg_n': 'and all four ergonomic items', '+ non-missing edu3': 'and education (analytic sample)'})
t3_lab = {'employee': 'Employees', 'self-employed': 'Self-employed'}
S += ['**Table S2.** Sample flow (2nd–7th waves pooled)\n', md(fl.rename(columns={'step': 'Step'})), '\n\n\\newpage\n']
t3 = rd('T3_stratified.csv')[['group', 'exposure', 'PR (95% CI)', 'n']]
t3['group'] = t3.group.map(t3_lab); t3['n'] = t3.n.map('{:,}'.format)
t3 = t3.rename(columns={'group': 'Group', 'exposure': 'Exposure'})
S += ['**Table S3.** Associations with any musculoskeletal pain stratified by employment status, and interaction tests\n', md(t3),
      '\n\nInteraction (ratio of PRs, self-employed vs employees): partial control 0.96 (0.93–0.99), p=0.010; no control 1.01 (0.99–1.04), p=0.298; '
      'demand 0.95 (0.94–0.96), p<0.001; joint Wald test for control × employment χ²(2)=11.50, p=0.003. '
      'RERI for no control × self-employment 0.033 (0.010–0.055). Self-employed = own-account workers and employers.\n\n\\newpage\n']
t4 = rd('T4_sensitivity.csv')
t4['n'] = t4.n.map('{:,}'.format)
t4['analysis'] = t4.analysis.str.replace('Wave 2', '2010').str.replace('Wave 3', '2011').str.replace('Wave 4', '2014').str.replace('Wave 5', '2017').str.replace('Wave 6', '2020').str.replace('Wave 7', '2023')
S += ['**Table S4.** Sensitivity analyses for any musculoskeletal pain (PR, 95% CI)\n', md(t4),
      '\n\n2023 only, variance clustered on 55 sampling strata: no control 0.86 (0.81–0.91), partial control 1.09 (1.00–1.19), demand 1.06 (1.03–1.09) '
      '(robust variance: 0.86 [0.84–0.89], 1.09 [1.05–1.13], 1.06 [1.05–1.08]).\n\n\\newpage\n']
f2 = rd('F2_control_count_pr.csv')
f2['PR (95% CI)'] = f2.apply(lambda r: f'{r.pr:.2f} ({r.lo:.2f}–{r.hi:.2f})', axis=1)
w5 = f2.pivot(index='label', columns='yes_n', values='PR (95% CI)')[[2, 1, 0]].loc[list(dict.fromkeys(f2.label))]
w5.columns = ['2 of 3 "yes"', '1 of 3 "yes"', '0 of 3 "yes"']
S += ['**Table S5.** Prevalence ratios by number of control items answered "yes" (reference: 3 of 3), and by individual item\n',
      md(w5.reset_index().rename(columns={'label': 'Outcome'})),
      '\n\n*2010–2017 only. Individual items entered together (answer "no" vs "yes"), any musculoskeletal pain: task order 0.96 (0.94–0.98); '
      'work methods 1.00 (0.98–1.03); speed or rate 0.91 (0.89–0.93). Weighted distribution of "yes" answers: 0 of 3, 49.4%; 1 of 3, 8.1%; 2 of 3, 8.3%; 3 of 3, 34.2%.\n\n\\newpage\n']
t7 = rd('T7_negative_control.csv'); t7['n'] = t7.n.map('{:,}'.format)
t11 = rd('T11_negcontrol_by_emp.csv'); t11['n'] = t11.n.map('{:,}'.format)
S += ['**Table S6.** Negative-control outcomes: all workers and by employment status\n', md(t7), '\n\n', md(t11),
      '\n\nCharacteristics by control category (weighted means; full / partial / none): ergonomic exposures 1.48 / 1.43 / 1.43; demand (1–7) 2.71 / 2.97 / 2.72; '
      'health problems reported (0–5) 1.27 / 1.25 / 1.00; employees 65.1% / 78.5% / 81.2%.\n\n\\newpage\n']
t6 = rd('T6_trends.csv'); t6['wave'] = t6.wave.map({2: 2010, 3: 2011, 4: 2014, 5: 2017, 6: 2020, 7: 2023})
t5 = rd('T5_nocontrol_trend.csv'); t5['wave'] = t5.wave.map({2: 2010, 3: 2011, 4: 2014, 5: 2017, 6: 2020, 7: 2023})
S += ['**Table S7.** Weighted prevalence (%) by survey wave\n',
      md(t6.rename(columns={'wave': 'Year', 'pain_any': 'Any MSK pain', 'no_ctrl': 'No control', 'hi_dem': 'High demand', 'low_sup': 'Low colleague support'})),
      '\n\nNo control (0 of 3) by employment status (weighted %):\n\n',
      md(t5.rename(columns={'wave': 'Year', 'employee': 'Employees', 'own_account': 'Own-account', 'employer': 'Employers', 'unpaid_family': 'Unpaid family'})),
      '\n\nInterview mode: paper questionnaires in 2010–2011; tablet computer-assisted personal interviewing from 2014 (survey quality and fieldwork reports).\n']
open(os.path.join(M, 'supplementary.md'), 'w').write('\n'.join(S))
print('tables written')
