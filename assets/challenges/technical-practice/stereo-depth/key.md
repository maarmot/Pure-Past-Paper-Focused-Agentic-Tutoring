# Examiner's key · Is the marker within five metres?

## Worked solution

Let `l = u_L − 160` and `r = u_R − 158` in pixels. The projection equations give `l = 240X/Z` and `r = 240(X − 0.12)/Z`. Subtracting eliminates the unknown sideways position. Thus `d = l − r = 28.8/Z`; the numerator has units px·m. Every finite point in front of these cameras has `d > 0`.

At the reported centers, `l = 18`, `r = 12`, `d = 6` px and `Z = 4.8` m. Under the error box the corrected readings can range independently over [17.5, 18.5] and [11.5, 12.5] px. The differences fill the entire interval [5, 7] px. Since taking a positive reciprocal reverses the endpoints, the consistent depths fill [144/35, 144/25] m, about [4.1143, 5.76] m.

A near witness uses true raw columns (178.5, 169.5). They have corrected difference 7 and imply `Z = 144/35` m, `X = 111/350` m. A far witness uses (177.5, 170.5), giving corrected difference 5, `Z = 144/25` m and `X = 21/50` m. Both satisfy the specified inclusive error bound, so the data cannot certify a depth at most 5 m.

If the corrected report differs by 1 px, true differences span [0, 2] before imposing the physical constraint. Finite positive depths require `0 < d ≤ 2`. Every depth from 14.4 m upward is possible. There is no finite maximum. As `d` approaches zero through positive values, consistent depths grow without bound.

| Quantity | Exact result |
| --- | ---: |
| Nominal depth (m) | 4.8 |
| Minimum depth (m) | 144/35 |
| Maximum depth (m) | 144/25 |
| Near witness X (m) | 111/350 |
| Far witness X (m) | 21/50 |
| Minimum depth for 1 px report (m) | 14.4 |

These are deterministic bounds for exact calibration, known correspondence and ideal pinhole projection. In horizontal stereo the principal columns can differ. [OpenCV camera calibration and stereo rectification](https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html)

## Graduated hints

1. **If the answer uses the raw eight-pixel difference**, point to each camera's principal column. Where is zero horizontal angle for that camera?
2. **If the interval is only half a pixel wide on either side of the difference**, try opposite error signs in the two columns. Are those allowed together?
3. **If the near and far bounds are reversed**, plug one smaller positive difference and one larger difference into the projection relationship.
4. **If zero disparity is treated as a finite depth**, return to `dZ = 28.8` and test progressively smaller positive `d`. Which bound survives?

## Oral follow-ups

| Ask one at a time | Expected reasoning and next probe |
| --- | --- |
| Why does a difference remove the unknown X? | Each corrected projection contains the same term 240X/Z. Ask what would change if the point moved between exposures. |
| Which measurements put the point farthest away? | Smallest positive corrected difference. Ask the learner to produce corresponding raw columns that still fit the error bars. |
| How confident are we that the point is closer than 5 m? | These assumptions admit both outcomes and give no probabilities. Ask which additional measurement or error model would help answer a probabilistic question. |

## Partial credit

| Evidence | Points |
| --- | ---: |
| Centers both columns, eliminates X and obtains the nominal depth with units (1 each) | 3 |
| Combines both errors, inverts the positive interval and gives tight endpoints (1 each) | 3 |
| Constructs admissible near/far observations and uses them to decide the five-metre claim (1 each) | 2 |
| Computes the new finite lower bound and justifies unbounded depth with positivity (1 each) | 2 |

Total 10. Correct limiting reasoning can earn credit after an earlier arithmetic error. A correct nominal range estimate alone does not establish a guaranteed threshold decision.

## Interpreting an attempt

A successful independent solution gives evidence that the learner can eliminate a nuisance variable and propagate bounded errors in this rig. If a hint supplied the centered coordinates, record that assistance separately. Use the transfer case to check whether they preserve correlations across three cameras. Real correspondence errors, uncertain calibration, vertical misalignment and field performance require other evidence.
