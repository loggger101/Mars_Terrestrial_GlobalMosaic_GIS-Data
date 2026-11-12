log v3_edf.json, written 2026-11-12 05:01; 10000 block resamples, seed 60

**Test: the 14 held-out blocks' windows** (237 and 1652 polygons with pixels)

| polygons | score | base | rep | freshw | edf |
|---|---|---|---|---|---|
| 237 v2 | accuracy | 87.5 | 86.8 | 88.0 | 75.1 |
| 237 v2 | balanced accuracy | 84.7 | 85.4 | 81.5 | 56.3 |
| 237 v2 | κ | 0.843 | 0.833 | 0.848 | 0.679 |
| 237 v2 | producer's, Crater | 97.4 | 98.4 | 97.3 | 82.8 |
| 237 v2 | producer's, steep/windy hills | 86.6 | 97.7 | 53.0 | 47.8 |
| 237 v2 | producer's, lava tube | 90.5 | 95.6 | 82.8 | 3.4 |
| 237 v2 | producer's, Normal Ground | 98.6 | 98.8 | 98.5 | 98.7 |
| 237 v2 | producer's, volcanic edifice | 76.3 | 66.6 | 85.7 | 53.8 |
| 237 v2 | producer's, apron | 87.4 | 90.4 | 84.8 | 83.2 |
| 237 v2 | producer's, fluvial channel | 56.4 | 50.0 | 68.5 | 24.6 |
| 1,652 v3 | accuracy | 86.4 | 85.5 | 86.7 | 73.0 |
| 1,652 v3 | balanced accuracy | 77.5 | 74.2 | 77.7 | 54.1 |
| 1,652 v3 | κ | 0.827 | 0.815 | 0.830 | 0.648 |
| 1,652 v3 | producer's, Crater | 94.0 | 92.8 | 96.0 | 77.3 |
| 1,652 v3 | producer's, steep/windy hills | 80.6 | 92.3 | 48.1 | 43.2 |
| 1,652 v3 | producer's, lava tube | 46.7 | 27.4 | 65.5 | 0.6 |
| 1,652 v3 | producer's, Normal Ground | 97.7 | 98.0 | 97.3 | 98.2 |
| 1,652 v3 | producer's, volcanic edifice | 79.1 | 69.1 | 88.3 | 56.8 |
| 1,652 v3 | producer's, apron | 82.0 | 85.4 | 79.4 | 74.4 |
| 1,652 v3 | producer's, fluvial channel | 62.4 | 54.8 | 69.5 | 27.9 |

| polygons | difference | accuracy, 95 % by block (points) | balanced accuracy |
|---|---|---|---|
| 237 v2 | base − rep | -1.6 to +2.4 | -6.1 to +3.8 |
| 237 v2 | edf − base | -20.7 to -6.8 | -34.3 to -16.0 |
| 237 v2 | edf − freshw | -20.4 to -6.3 | -32.3 to -10.8 |
| 237 v2 | edf − rep | -20.0 to -6.8 | -34.4 to -15.9 |
| 1,652 v3 | base − rep | -0.9 to +2.4 | -3.4 to +6.9 |
| 1,652 v3 | edf − base | -20.6 to -7.4 | -29.8 to -15.8 |
| 1,652 v3 | edf − freshw | -20.2 to -7.6 | -28.8 to -13.9 |
| 1,652 v3 | edf − rep | -19.2 to -7.3 | -29.9 to -13.7 |

**Areas on the held-out blocks' windows** (share of the ground every map of the set holds; groups' shares of that ground: off_edifice_units 98.6, highland 42.6, volcanic_plains 34.8, edifice_units 1.4)

| class, % of the ground | base | rep | freshw | edf |
|---|---|---|---|---|
| Crater | 27.1 | 32.8 | 30.8 | 26.7 |
| steep/windy hills | 4.2 | 7.5 | 1.7 | 1.8 |
| lava tube | 2.5 | 3.2 | 3.0 | 0.1 |
| Normal Ground | 35.7 | 35.6 | 32.4 | 40.7 |
| volcanic edifice | 16.3 | 8.7 | 14.5 | 9.6 |
| apron | 6.2 | 7.4 | 6.8 | 16.0 |
| fluvial channel | 8.1 | 4.8 | 10.8 | 5.1 |

| volcanic edifice, % of each unit group | base | rep | freshw | edf |
|---|---|---|---|---|
| off_edifice_units | 15.4 | 7.8 | 13.5 | 8.9 |
| highland | 16.5 | 8.7 | 13.3 | 8.0 |
| volcanic_plains | 17.3 | 8.8 | 16.5 | 10.8 |
| edifice_units | 77.9 | 71.3 | 88.5 | 58.2 |

**Areas on the validation blocks' windows** (share of the ground every map of the set holds; groups' shares of that ground: off_edifice_units 99.2, highland 62.0, volcanic_plains 22.1, edifice_units 0.8)

| class, % of the ground | fresh | edfv |
|---|---|---|
| Crater | 38.4 | 34.4 |
| steep/windy hills | 0.5 | 0.6 |
| lava tube | 2.6 | 0.1 |
| Normal Ground | 23.0 | 35.4 |
| volcanic edifice | 18.0 | 9.3 |
| apron | 3.9 | 15.0 |
| fluvial channel | 13.6 | 5.2 |

| volcanic edifice, % of each unit group | fresh | edfv |
|---|---|---|
| off_edifice_units | 17.5 | 9.0 |
| highland | 16.1 | 7.3 |
| volcanic_plains | 22.7 | 12.9 |
| edifice_units | 80.9 | 55.7 |

**Validation: fresh's 14 blocks** (895 polygons with pixels)

| score | fresh | edfv |
|---|---|---|
| accuracy | 86.6 | 71.3 |
| balanced accuracy | 72.2 | 47.4 |
| κ | 0.815 | 0.601 |
| producer's, Crater | 97.1 | 68.3 |
| producer's, steep/windy hills | 18.3 | 9.4 |
| producer's, lava tube | 93.7 | 0.4 |
| producer's, Normal Ground | 85.7 | 94.4 |
| producer's, volcanic edifice | 84.1 | 57.2 |
| producer's, apron | 89.4 | 90.5 |
| producer's, fluvial channel | 37.4 | 11.7 |
edfv − fresh by block: accuracy -25.4 to -6.9, balanced accuracy -26.8 to -15.5 points

**The six Syrtis Major edifice polygons** (share of their ground each map calls each class; base 7.7 % edifice, §69.105)

| map | Crater | steep/windy hills | lava tube | Normal Ground | volcanic edifice | apron | fluvial channel |
|---|---|---|---|---|---|---|---|
| base | 46.8 | 0.5 | 0.3 | 26.2 | 6.9 | 0.0 | 19.3 |
| rep | 94.9 | 0.6 | 0.0 | 2.9 | 0.0 | 0.0 | 1.6 |
| freshw | 36.5 | 1.7 | 5.2 | 8.5 | 41.4 | 0.0 | 6.7 |
| edf | 71.8 | 0.9 | 0.0 | 18.4 | 0.0 | 0.6 | 8.3 |

**Predictions** (the log's verdicts; the numbers beside each)
- E1 NOT held: validation accuracy edfv 71.3 against fresh 86.6, 15.34 points apart (bound 3).
- E2 held: edifice off the edifice units on the validation windows, edfv 9.0 against fresh 17.5.
- E3 NOT held: accuracy edf against base, 75.1 against 87.5 on the 237 polygons and 73.0 against 86.4 on the 1,652 (12.39 and 13.38 points apart, bound 3).
- E4 NOT held: edifice off the edifice units on the held-out windows, edf 8.9 against base 15.4, rep 7.8, freshw 13.5.
- E5 NOT held: producer's accuracy of volcanic edifice on the 1,652 polygons, edf 56.8 against base 79.1 and rep 69.1 (floor 59.1).
- The rule: does not recommend edf's labels.
