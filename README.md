# kwcs-msd-psychosocial

Analysis code for:

**Lack of job control and musculoskeletal pain among Korean workers: a non-specific inverse association identified with negative-control outcomes in six waves of the Korean Working Conditions Survey**

Heo S, Choi T, Choi W. (manuscript under review)

## Overview

Pooled cross-sectional analysis of the 2nd–7th waves (2010–2023) of the Korean Working Conditions Survey (KWCS; n=252,798 of 260,996 respondents). The code

- re-derives job demand, control, and support, ergonomic exposures, and 12-month musculoskeletal pain from the raw KWCS files, with item wording and response codes checked against each wave's questionnaire;
- estimates prevalence ratios by weighted modified Poisson regression with robust variance;
- tests heterogeneity by employment status (employees vs self-employed; multiplicative and additive scales);
- uses non-musculoskeletal health problems (headache/eye strain, fatigue, hearing, skin) as negative-control outcomes;
- runs sensitivity analyses (control count and single items, unweighted, alternative adjustment sets, wave- and age-stratified estimates, stratum-clustered variance for 2023).

## Data

KWCS microdata are available from the Occupational Safety and Health Research Institute, Korea Occupational Safety and Health Agency: https://oshri.kosha.or.kr. Raw data are **not** included in this repository. Place the downloaded wave folders under `data/` (see `data/README.md`), or set the environment variable `KWCS_DATA_DIR` to the folder that contains them.

## Running the analysis

```bash
pip install -r requirements.txt
python code/r1/r1_01_codes.py        # response-code distributions by wave (aggregate)
python code/r1/r1_02_build.py        # analytic dataset -> output/r1/kwcs_r1.parquet (not tracked)
python code/r1/r1_03_analysis.py     # main models, stratified/interaction, sensitivity, trends
python code/r1/r1_04_negcontrol.py   # negative-control outcomes
python code/r1/r1_05_extra.py        # control count, single items, 2023 stratum-clustered variance
python code/r1/r1_06_figdata.py      # figure inputs
python code/figures.py               # figures -> output/figures/
python code/make_tables.py           # tables -> output/tables/
```

All scripts print aggregate results only; no individual-level records are written to the console. Python 3.12 (numpy 2.3, pandas 2.3, patsy 1.0, scipy 1.17, matplotlib 3.11, pyarrow).

## Key coding decisions

| Construct | KWCS items | Coding |
|---|---|---|
| Job control | decla1–3 (choose/change task order, methods, speed or rate; yes/no) | number of "yes" (0–3): full 3, partial 1–2, none 0 |
| Psychological demand | winten2_1, winten2_2 (very high speed; tight deadlines; 7-point frequency) | reversed, mean, standardized |
| Colleague support | wsituation1 (1 always … 5 never; 7 not applicable) | high 1–2, low 3–5, no colleagues 7 |
| Ergonomic exposures | hazard_erg1, 3, 4, 6 (7 = never is a valid answer) | exposed if at least half of working time |
| Outcomes | heal_prob1–3 (back, upper limb, lower limb) | 12-month pain yes/no |
| Negative controls | heal_prob4, heal_prob6 (all waves); heal_prob8, heal_prob9 (2010–2017) | yes/no |

## Archive

`archive/2026-07_bmc_version/` keeps the code of an earlier, unpublished version of this analysis for transparency. It is superseded: that pipeline (i) used `hazard_psy1` (dealing directly with people who are not colleagues) as "psychological demand", (ii) set the valid response "never" (code 7) of frequency items to missing, and (iii) treated "not applicable" supervisor support as missing, which together excluded about two-thirds of respondents. Do not use it.

## License

MIT License. See [LICENSE](LICENSE).

## Funding

Regional Innovation System & Education (RISE) Program, Gyeongbuk RISE Center, Ministry of Education and Gyeongsangbuk-do, Republic of Korea (2026 RISE-15-102).
