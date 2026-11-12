# What happened between two software reads?

Original generated hardware–software transfer problem. Reason on paper or use a small script. A repaired FPGA counter increments exactly once per delivered frame and wraps modulo 8. It starts at an arbitrary value. Software takes coherent, non-destructive snapshots. Between two snapshots there are exactly 10 potentially incrementing clock edges, with at most one completion per edge. A beat can be a complete frame. The snapshots read 6 and then 0. There is no reset.

1. List every possible number of completed frames in the interval and give a feasible event pattern for each.
2. What is the largest integer number of intervening edges that guarantees unambiguous reconstruction for **every** pair of possible snapshot readings? Justify the boundary with a counterexample.
3. At 10 MHz, convert that universal bound to time for edge-aligned reads. If exactly 10 edges between reads are required, what minimum counter width suffices?
