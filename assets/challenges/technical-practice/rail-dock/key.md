# Examiner's key · Where should the inspection cart park?

## Worked solution

Use numerical coordinates in metres. For one call at `x`, the outward travel is `|x − s|` m. For a small rightward change in the dock, calls already to its left get farther away, and calls still to its right get closer. A call exactly at the dock gets farther away in either direction. The routine density is numerically `x` calls per metre per shift. Keep the four station calls as a separate point load.

For `0 ≤ s ≤ 4`, the expected travel in m/shift is

```text
D(s) = ∫₀ˢ (s − x)x dx + ∫ₛ⁴ (x − s)x dx + 4|s − 1|
     = s³/3 − 8s + 64/3 + 4|s − 1|.
```

For `0 < s < 1`, the derivative is `s² − 12`, which is negative throughout. For `1 < s < 4`, it is `s² − 4`, negative below 2 and positive above 2. The cost is continuous at the station. It therefore falls from 0 to 2, then rises to 4. Substitution in the original travel function gives 12 m/shift at the unique minimum. Dividing the cost by a positive constant would preserve that location, but any reported travel must be put back on the original scale.

| Quantity | Exact result |
| --- | ---: |
| Best dock (m) | 2 |
| Least travel (m/shift) | 12 |
| Travel at 0 m (m/shift) | 76/3 |
| Travel at 1 m (m/shift) | 41/3 |
| Travel at 4 m (m/shift) | 68/3 |
| Smallest station load (calls/shift) | 7 |

For a station load of `W`, the derivative immediately to the left of 1 is `−7 − W`, and immediately to the right it is `−7 + W`. Below 1 cost decreases for all allowed `W`. To the right the derivative `s² − 8 + W` is strictly increasing. Thus the unique minimum occurs at 1 precisely when `W ≥ 7`. At equality the right derivative is zero at 1 and strictly positive everywhere to its right. The optimum remains unique. A separate check counts routine calls left and right of 1. Those demands are 0.5 and 7.5 calls per shift. Moving right saves travel for the extra seven calls on that side until the station load offsets the advantage.

## Graduated hints

Give one hint in response to the learner's actual work. If they request the full solution, give it.

1. **If the setup assigns negative travel**, ask how far a cart at 2 travels to a call at 0.5. Where does the sign of the expression for distance change?
2. **If routine calls look uniformly spread**, ask how many routine calls lie in the first and last metre. Write the travel for a narrow interval as distance per call times expected calls there.
3. **If the derivative gives a candidate but no proof**, mark 0, 1 and 4 on a number line. Write one derivative on each side of the station and check its sign over each interval.
4. **If the threshold is missing**, compare slopes just left and right of 1 with `W` still symbolic. At equality, check what happens immediately beyond the station.

## Oral follow-ups

| Ask one at a time | Expected reasoning and next probe |
| --- | --- |
| If two proposed solutions use outward distance and round-trip distance, which of their results can agree? | Multiplying all costs by two leaves the optimizer fixed. Ask which units and number the client requested. |
| Why does setting a single derivative to zero miss a valid dock? | The station's concentrated demand causes a corner. Ask what the two one-sided slopes mean for actual travel. |
| At the threshold, can several nearby docks tie? | The right slope is zero only at 1 and becomes positive immediately. If the learner claims a flat segment, ask for the slope at any larger legal point. |

## Partial credit

| Evidence | Points |
| --- | ---: |
| Captures the domain and one-way distance, weights by routine demand, and handles the station separately (1 each) | 3 |
| Splits the routine integral correctly and evaluates it at the original scale (1 each) | 2 |
| Finds the minimizing dock, substantiates globality across both branches and ends, and reports the correct travel with units (1 each) | 3 |
| Uses directional slopes or demand imbalance for the threshold and resolves equality/uniqueness (1 each) | 2 |

Total 10. An exact balance-of-demand argument earns the same reasoning credit without differentiating the expanded polynomial. Mark a scale error once and credit valid downstream optimization of the consistently scaled objective.

## Interpreting an attempt

A correct location alongside a doubled cost supports locating an optimizer and leaves the physical objective unresolved. A proof that considers only one branch leaves the global claim open even with the right number. Record what the learner did before any hint. If they independently construct the model and prove globality, use the separate contract problem to see whether they can choose a different objective. A later fresh setup gives evidence on retention.
