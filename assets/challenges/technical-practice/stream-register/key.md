# Examiner's key · Why does the host count extra frames?

## Worked solution

Read left to right across each edge. First decide whether the old head is delivered. The source can occupy a free slot or replace a delivered head. Update storage after identifying both transfers. A star travels with its data.

| Edge | Accepted input | Delivered output | Stored after | Delivered frames so far |
| ---: | --- | --- | --- | ---: |
| 1 | A | - | A | 0 |
| 2 | B* | A | B* | 0 |
| 3 | - | - | B* | 0 |
| 4 | - | - | B* | 0 |
| 5 | C* | B* | C* | 1 |
| 6 | D | C* | D | 2 |
| 7 | - | - | D | 2 |
| 8 | E* | D | E* | 2 |
| 9 | - | E* | - | 3 |

At edge 2 the source sends B* as the sink takes A. The proposed last assignment clears `full`, so B* will not be available to the sink after that edge. Its data bits might remain in storage, but the valid bit has discarded it. Use one enable condition for replacing storage and an explicit occupancy update:

```text
push = source_valid AND ((NOT full) OR sink_ready)
pop  = full AND sink_ready
at each rising edge:
    if push:
        stored <= offered         # payload and last together
    full <= push OR (full AND NOT pop)
    if pop AND stored.last:       # pre-edge head
        completed <= completed + 1
```

The unspecified data and counter updates hold their previous values. Initialize `full` and `completed` as specified in the exercise. A direct invariant after each edge is that the sequence of accepted beats equals the sequence of delivered beats followed by the register's zero or one resident beat. A count-only check misses substitutions or reorderings. A stalled valid head must retain both payload and end flag.

The faulty counter, analyzed with **correct** storage, counts B* on edges 3, 4 and 5, C* on 6, and E* on 9. Edge 3 is already one count too high. A continuously stalled terminal beat increments the faulty counter on every valid cycle. A physical finite-width counter eventually wraps.

| Quantity | Exact result |
| --- | ---: |
| First storage error (edge) | 2 |
| First counter error (edge) | 3 |
| Faulty final count (frames) | 5 |

The exercise models one synchronous elastic register. The handshake and payload-stability rules also appear in Arm's streaming interface specification, §2.2.1. [Arm AMBA 4 AXI4-Stream Protocol Specification](https://documentation-service.arm.com/static/642583d7314e245d086bc8c9)

## Graduated hints

1. **If an empty register immediately forwards A**, draw the slot before and after edge 1. Which item could the sink see before the edge?
2. **If edge 2 is drawn as a bubble**, separately name the old head and the offered replacement. Can both interfaces transfer at the same edge?
3. **If a flag counts repeatedly**, circle every edge when the head ends a frame. Cross out those where the sink declines the beat.
4. **If the register loses B***, form a truth table with columns `push`, `pop`, and next occupancy. Specify the case with both true before simplifying.

## Oral follow-ups

| Ask one at a time | Expected reasoning and next probe |
| --- | --- |
| Why can the source already be showing C* while B* is on the output? | Each interface has its own transfer. Ask which edge retires B* from the output. |
| Could the count be right if a payload were corrupted? | Yes. Ask for a stronger property that covers order, data and last flags. |
| If the sink never accepts another beat, does the corrected counter still advance? | No. Progress depends on sink readiness. Ask what remains stable during the stall. |

## Partial credit

| Evidence | Points |
| --- | ---: |
| Gives the intended acceptance and delivery sequence, stable stalls, and per-edge cumulative count (1 each) | 3 |
| Identifies edge 2 and explains the overwritten occupancy assignment (1 each) | 2 |
| Correct replacement, stall/empty behavior and ordered conservation property (1 each) | 3 |
| Predicts the faulty final count and first divergence, then gates completion on delivery of a terminal beat and explains long stalls (1 each group) | 2 |

Total 10. Credit equivalent queue or clock-enable implementations that meet the stated same-edge replacement behavior. Classify a one-edge display shift separately from repeated counting.

## Interpreting an attempt

A correct table can establish event tracking on this trace. A proposed repair plus the ordering invariant gives evidence about reasoning across traces. If the learner only traced after a hint about pre-edge state, ask for a different stall pattern before counting the skill as independent. This paper model does not exercise synthesis, clock-domain crossings, timing closure, a real driver or a board.
