# Examiner's key · Reconcile three views of one marker

Write the true corrected columns as `a, a − d, a − 2d`. Equal camera spacing makes the step identical, and `d = 28.8/Z > 0`. In pixels the three constraints are

```text
17.5 ≤ a      ≤ 18.5
11.5 ≤ a − d  ≤ 12.5
 7.3 ≤ a − 2d ≤  8.3
```

The first pair demands `5 ≤ d ≤ 7`. The last pair demands `3.2 ≤ d ≤ 5.2`. The outside pair demands `4.6 ≤ d ≤ 5.6` after dividing their difference by two. All three together restrict `d` to [5, 5.2]. To show this is tight, construct two scenes:

| Step d (px) | True corrected columns (px) | Z (m) | X (m) |
| ---: | --- | ---: | ---: |
| 5 | 17.5, 12.5, 7.5 | 144/25 | 21/50 |
| 5.2 | 17.7, 12.5, 7.3 | 72/13 | 531/1300 |

Here `Z = 28.8/d` and `X = aZ/240`. Intermediate steps can be realized by interpolating between the rows' **image columns**; their differences still have equal spacing and all columns remain within their closed error intervals. Thus every depth between 72/13 and 144/25 m is possible.

Using only the first pair and the outside pair yields `5 ≤ d ≤ 5.6`. At `d = 5.6` the outside pair would need `a = 18.5`, giving a middle column of 12.9 px outside its allowed range. Computing two independent ranges had allowed a different left column for each pair.

If the last report is 8.2 instead of 7.8, the last two cameras have true difference at most `12.5 − 7.7 = 4.8` px. The first two require at least 5 px. They cannot be successive equally spaced projections of any point in the model.

| Quantity | Exact result |
| --- | ---: |
| Minimum joint depth (m) | 72/13 |
| Maximum joint depth (m) | 144/25 |
| Near witness X (m) | 531/1300 |
| Far witness X (m) | 21/50 |
| Two-pair lower bound (m) | 36/7 |
| Two-pair upper bound (m) | 144/25 |

**Mark out of 5.** Award 1 each for the shared-scene model, tight joint range, feasible endpoints with an argument covering intermediate values, showing where pairwise intersection goes wrong, and the incompatible changed report. An equivalent feasible-region proof earns full credit.
