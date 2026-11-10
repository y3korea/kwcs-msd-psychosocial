# Superseded code (July 2026 version)

Kept for transparency only. This version contained three coding errors that were corrected in `code/r1/`:

1. "Psychological demand" was taken from `hazard_psy1`, which measures dealing directly with people who are not colleagues (customers, patients, etc.), not work pace or deadlines. The corrected code uses `winten2_1` and `winten2_2`.
2. Code 7 ("never") of the 7-point frequency items was treated as missing, excluding workers with no exposure.
3. "Not applicable" (code 7) for supervisor support was treated as missing, excluding most self-employed workers.
