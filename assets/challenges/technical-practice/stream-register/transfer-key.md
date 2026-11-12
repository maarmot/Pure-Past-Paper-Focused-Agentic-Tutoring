# Examiner's key · What happened between two software reads?

Let `N` be the completions after the first snapshot up to the second. The register promises `0 ≡ 6 + N (mod 8)` and `0 ≤ N ≤ 10`. Thus `N = 2` or `N = 10`. For the former, deliver a terminal beat on the first two edges and idle on the rest. For the latter, deliver one single-beat frame on every edge. Both histories leave 0 in the register.

With up to seven intervening edges, the counts 0 through 7 have distinct residues. At eight edges, zero and eight completions can each return any initial value to itself. This establishes the largest universally safe gap. At 10 MHz one period is 0.1 microseconds. Seven periods give 0.7 microseconds for edge-aligned snapshots. For ten edges the counter needs distinct representations of the eleven possible counts 0 through 10. Four bits give period 16. Three give period 8.

| Quantity | Exact result |
| --- | ---: |
| Smaller feasible count | 2 |
| Larger feasible count | 10 |
| Largest universally safe gap (edges) | 7 |
| Largest aligned gap (microseconds) | 0.7 |
| Minimum width for ten edges (bits) | 4 |

**Mark out of 4.** Give one point each for both feasible counts with realizable histories, the universally safe bound with an ambiguity witness, the timing conversion, and the minimum width with a lower-bound argument. A time guarantee on equipment would also need a defined snapshot clock relationship and elapsed-time bound.
