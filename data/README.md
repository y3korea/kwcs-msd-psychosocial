# Data

This directory should contain the Korean Working Conditions Survey (KWCS) raw data files.

## How to obtain the data

1. Visit the KOSHA data portal: https://oshri.kosha.or.kr
2. Navigate to the KWCS (Korean Working Conditions Survey) section
3. Download waves 2-7 (2010-2023)
4. Place the files in subdirectories as follows:

```
data/
├── 2차_근로환경/[CSV]2nd_KWCS_kor/
│   └── ★원시자료_2차 근로환경조사_제공용_220207.csv
├── 3차_근로환경/[CSV]3rd_KWCS_kor/
│   └── ★원시자료_3차 근로환경조사_제공용_22207.csv
├── 4차_근로환경/[CSV]4th_KWCS_kor/
│   └── ★원시자료_4차 근로환경조사_제공용_220126.csv
├── 5차_근로환경/[CSV]5th_KWCS_kor/
│   └── ★원시자료_5차 근로환경조사_제공용_22207.csv
├── 6차_근로환경/[CSV]6th_KWCS_kor/
│   └── ★원시자료_6차 근로환경조사_제공용_220210.csv
└── 7차_근로환경/[CSV] 7th KWCS_kor/
    └── [데이터] 2023년 제7차 근로환경조사.dat
```

## Notes

- Wave 1 (2006) is excluded because lower limb MSD and work intensity items were unavailable.
- Wave 7 (2023) uses tab-separated `.dat` format; waves 2-6 use CSV with UTF-8-BOM encoding.
- Data use is subject to KOSHA's terms and conditions.
