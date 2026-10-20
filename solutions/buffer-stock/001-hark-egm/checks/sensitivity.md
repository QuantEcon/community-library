# Sensitivity of the HARK baseline

HARK baseline: seven positive values per shock plus zero transitory income (56 joint outcomes), 960 asset points, asset grid top 20. The tables compare consumption on the common grid, target wealth and the MPC at the target. Target differences retain their sign.

## 1. HARK baseline against the independent EGM solver (same 56 joint shock outcomes, 12,000 knots to a = 50)

| m | HARK | EGM | difference |
| --- | --- | --- | --- |
| 0.25 | 0.2324218 | 0.2324229 | -1.1e-06 |
| 0.5 | 0.4606692 | 0.4606713 | -2.1e-06 |
| 0.75 | 0.6758563 | 0.6758586 | -2.3e-06 |
| 1 | 0.8527854 | 0.8527869 | -1.5e-06 |
| 1.25 | 0.9647240 | 0.9647253 | -1.3e-06 |
| 1.5 | 1.0346454 | 1.0346467 | -1.3e-06 |
| 2 | 1.1273869 | 1.1273883 | -1.4e-06 |
| 2.5 | 1.1939523 | 1.1939536 | -1.2e-06 |
| 3 | 1.2484674 | 1.2484688 | -1.4e-06 |
| 4 | 1.3401163 | 1.3401183 | -2.0e-06 |
| 5 | 1.4194961 | 1.4194982 | -2.1e-06 |
| 6 | 1.4918864 | 1.4918893 | -3.0e-06 |
| 8 | 1.6241387 | 1.6241428 | -4.1e-06 |
| 10 | 1.7460689 | 1.7460737 | -4.8e-06 |
| 15 | 2.0262320 | 2.0262378 | -5.9e-06 |
| 20 | 2.2867095 | 2.2865815 | +1.3e-04 |

Target: HARK 1.391031, EGM 1.391027, difference +4.2e-06.

## 2. HARK's own grid settings (56 joint shock outcomes throughout)

| Setting | Maximum absolute consumption difference from baseline | Maximum absolute consumption difference from EGM | Target difference from baseline | MPC at target, step 1e-4 | MPC at target, interpolant slope | MPCmin of solution object |
| --- | --- | --- | --- | --- | --- | --- |
| baseline | 0.0e+00 | 1.3e-04 | +0.0e+00 | 0.26937 | 0.26897 | 0.04043 |
| 480 asset points | 2.5e-05 | 1.0e-04 | +1.8e-05 | 0.26921 | 0.26921 | 0.04043 |
| 1920 asset points | 6.5e-06 | 1.3e-04 | -2.9e-06 | 0.26942 | 0.26942 | 0.04043 |
| grid top 40 | 1.4e-04 | 1.4e-05 | +7.6e-07 | 0.26900 | 0.26900 | 0.03968 |
| grid top 80 | 1.4e-04 | 1.5e-05 | +2.0e-06 | 0.27001 | 0.27001 | 0.03939 |
| 1920 points, top 40 | 1.3e-04 | 3.0e-06 | -2.7e-06 | 0.26948 | 0.26948 | 0.03968 |

## 3. Shock discretisation, HARK (960 points, top 20)

| positive values per shock | maximum absolute consumption difference from baseline | target difference from baseline | target |
| --- | --- | --- | --- |
| 3 | 3.5e-02 | -2.1e-02 | 1.369696 |
| 5 | 9.4e-03 | -6.0e-03 | 1.385078 |
| 7 | 0.0e+00 | +0.0e+00 | 1.391031 |
| 11 | 7.4e-03 | +4.9e-03 | 1.395910 |
| 21 | 1.3e-02 | +8.4e-03 | 1.399414 |

## 4. Shock discretisation, independent EGM (3,000 knots to a = 50, its own equiprobable atoms)

| positive values per shock | maximum absolute consumption difference from baseline | target difference from baseline | target |
| --- | --- | --- | --- |
| 3 | 3.5e-02 | -2.1e-02 | 1.369693 |
| 5 | 9.4e-03 | -6.0e-03 | 1.385074 |
| 7 | 0.0e+00 | +0.0e+00 | 1.391029 |
| 11 | 7.4e-03 | +4.9e-03 | 1.395907 |
| 21 | 1.3e-02 | +8.4e-03 | 1.399411 |

## 5. The MPC at the target: finite-difference step

| solution | step 1e-4 | step 1e-3 | step 1e-2 | interpolant slope |
| --- | --- | --- | --- | --- |
| HARK, baseline | 0.26937 | 0.26952 | 0.26956 | 0.26897 |
| HARK, 1920 asset points | 0.26942 | 0.26958 | 0.26956 | 0.26942 |
| HARK, 1920 points, top 40 | 0.26948 | 0.26957 | 0.26955 | 0.26948 |
| EGM, 12,000 knots | 0.26949 | — | 0.26956 | — |
