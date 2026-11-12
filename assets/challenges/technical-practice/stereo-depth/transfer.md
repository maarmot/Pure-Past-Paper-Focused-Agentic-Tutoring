# Reconcile three views of one marker

Original generated transfer problem. Use pencil and paper or a small script. Three parallel pinhole cameras view one stationary point. The focal length is 240 px. The camera positions along a straight baseline are 0, 0.12 and 0.24 m. The report from each camera has already had its principal column subtracted.

| Camera position (m) | Reported corrected column (px) |
| ---: | ---: |
| 0 | 18 |
| 0.12 | 12 |
| 0.24 | 7.8 |

Each true corrected column is within 0.5 px of its own report, inclusive. Calibration is exact. All three observations must be projections of **one** point with positive finite depth.

1. Find the tight depth interval and show how a real point could produce each endpoint.
2. An engineer checks the first and second views as one pair, then the first and third as another, and intersects the resulting depth intervals. Does this produce the tight joint answer? Show why.
3. Suppose the third report changes to 8.2 px while the first two stay the same. Is there any compatible depth? Explain how you decided.
