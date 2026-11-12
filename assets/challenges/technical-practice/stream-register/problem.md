# Why does the host count extra frames?

Original generated FPGA and firmware debugging problem. Your goal is to account for individual transfers under backpressure, repair a register, and explain a software-visible discrepancy. Pencil and paper, a calculator or a small local simulator are allowed. Keep data and its end-of-frame flag together.

One rising-edge clock drives a source, a **one-entry** register, a sink and a hardware completion counter read by software. All signals below describe the values just before each edge. A beat transfers when its interface's valid and ready are both 1. The source offers its next beat as soon as the previous beat is accepted and holds an unaccepted beat stable. A full register drives output valid and its stored beat. An empty register has no output beat, even if an input is arriving. A full register can accept a replacement on the edge that the sink accepts its current beat.

Starting just before edge 1, the register is empty and the counter is zero. The source has the five beats below, followed by idle. A star means that beat ends a frame. The counter is wide enough to avoid wrap in this trace.

```text
Source order: A B* C* D E*
Edge:         1 2 3 4 5 6 7 8 9
Sink ready:   0 1 0 0 1 1 0 1 1
```

1. Trace the intended register. At each edge give the accepted input, delivered output, stored beat after the edge, and **cumulative delivered frames**. Use a dash for no beat.
2. A proposed implementation uses these synchronous updates. Both conditions see pre-edge state. If both assign to the same register, the last executed assignment wins. Find the first edge where storage disagrees with your intended trace. Write replacement pseudocode and an ordering or conservation property that would expose losing an accepted beat.

```text
in_ready = empty OR sink_ready
push = source_valid AND in_ready
pop  = full AND sink_ready

if push: stored <= offered; full <= 1
if pop:  full <= 0
```

3. Independently, assume storage works as intended. A proposed counter increments on every edge with `full AND stored.last`. Predict the count that software would read after edge 9, identify when it first diverges, and repair its update. Can a single output beat that is held through a long stall make the faulty count grow without another delivery?
