# Examiner's verification plan

These criteria were set after writing the six learner prompts and before writing or evaluating their keys. All three examples are original generated practice. They have no instructor-endorsed timing or course alignment. Open the transfer prompt after an attempt at the main problem. Its key can remain closed until requested.

| Exercise | Expected result from the stated model | Independent way to reject a wrong key |
| --- | --- | --- |
| Rail | One-way distance is the demand-weighted absolute displacement in metres per shift. The fixed station can be optimal at a corner. | Integrate the original distance model directly by exact quadratic quadrature on each side, and compare demand on either side. Doubling all travel preserves the best dock and fails the shift total. |
| Rail transfer | Worst travel to an endpoint governs on each connected component of the allowed set. | Compare arrival times directly on a rational grid including each legal endpoint and the unrestricted balance point. A distance-to-nearest-legal-point rule must fail on this input. The written monotonicity argument establishes globality. |
| Register | Accepted input minus delivered output equals stored occupancy on each edge. Delivered tags constitute an ordered prefix of accepted tags. | Simulate with a one-element queue and compare every printed trace cell. Check the last-write-wins implementation and the valid-only counter against the same stimuli. |
| Register transfer | Counts between snapshots must be feasible over the available edges and agree modulo the counter period. | Enumerate bounded counts and all starting residues. Show the first ambiguous universal gap and check the time and width conversion. |
| Stereo | Every reported depth obeys both projection equations and the positive-depth condition. An interval containing arbitrarily small positive disparity permits arbitrarily large finite depth. | Build the intersection of the measurement bands in horizontal-position/depth coordinates via their line intersections, using exact rational arithmetic. Project endpoint witnesses back to the column intervals. |
| Stereo transfer | One scene point must satisfy all three image measurements simultaneously. A conflicting report can make the joint set empty. | Enumerate feasible vertices of the three-view bands and compare to the printed bounds and the two-pair shortcut. Verify the changed report has no feasible vertex in this bounded case. |

Reproduce from the repository root:

```sh
python -m unittest discover -s tests -p test_technical_practice.py -v
```

Each key contains a short table of the assessed results. Tests read those values, the printed prompts and the register trace. The band and queue calculations do not call a solver used to write a key. Exact comparison is appropriate for these deliberately idealized data. The tests cannot grade a proof in prose, verify an FPGA board, or measure a learner's retention.

## Observed results

The initial run of the eight content checks failed with missing answer files before the keys were written. The same eight checks passed on the printed keys. A subsequent mutation check kept the three source files intact while substituting incorrect answers in memory. All three substitutions triggered assertion failures in the original checks:

| Fault inserted | Check that rejected it |
| --- | --- |
| Double only the reported rail travel, preserving the right dock location | Direct integration of one-way weighted distance |
| Clear the register on a simultaneous send and receive at edge 2 | FIFO reference compared with the printed post-edge state |
| Substitute the loose two-pair stereo lower bound for the joint bound | Feasible vertices from all three projection bands |

The nine-test suite passed with the mutation check included. A second solver independently worked from the six prompts before seeing the keys and agreed on the main and transfer results. These are checks of solvability and answer accuracy. There were no learner attempts in this evaluation.
