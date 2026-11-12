# Examiner's key · A different contract for the rail

From a dock at `s` metres, the slowest possible leftward trip ends at 0 and takes `s/2` seconds. The slowest rightward trip ends at 4 and takes `4 − s` seconds. Hence `T(s) = max(s/2, 4 − s)`. Intermediate points on either side take less time than the corresponding endpoint.

On an unrestricted rail, the decreasing rightward time meets the increasing leftward time at `s = 8/3` m. The worst time decreases up to this point and increases after it. On the left legal interval the best legal point is therefore 2, with worst time 2 s. On the right interval it is 3.5, with worst time 7/4 s. Comparing these two values proves the unique legal optimum.

| Quantity | Exact result |
| --- | ---: |
| Unrestricted dock (m) | 8/3 |
| Legal dock (m) | 7/2 |
| Worst time at legal dock (s) | 7/4 |

The nearest legal point to 8/3 is 2 (distance 2/3 m), while 3.5 is 5/6 m away. A metre of dock displacement increases the worst time twice as quickly on the left branch as on the right. The farther legal alternative wins.

**Mark out of 4.** Award one each for the endpoint-time model, unrestricted balance, comparison across both intervals, and rejection of the nearest-point rule with evidence. Credit a table or diagram that establishes the monotonicity and comparison.
