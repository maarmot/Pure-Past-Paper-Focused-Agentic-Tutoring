# Where should the inspection cart park?

Original generated calculus problem. Your goal is to choose a dock from a description of the work, then defend that choice even when the demand changes. Use pencil and paper and, if wanted, a basic calculator. Give exact results and show the argument that establishes the minimum.

A cart departs from a fixed dock to inspect locations on a straight, 4 m rail. The cart returns by a separate mechanism. Only the outward distance counts. A location's coordinate is its distance from the left end. Write coordinates as their numerical values in metres.

On a typical shift the expected number of routine calls between coordinates `a` and `b` is the integral of `x dx` from `a` to `b`. For example, the first metre generates half a routine call per shift on average. An additional four calls per shift come from the station at coordinate 1. Each call requires a separate trip. Any point of the rail can serve as the dock.

1. For a dock at coordinate `s`, write the expected total outward travel per shift. Show which calls get farther away when the dock moves a little to the right.
2. Find the dock location that minimizes travel and the corresponding travel per shift. Defend the result against every feasible dock, including the station and the ends of the rail.
3. Replace the four station calls by `W ≥ 0` expected calls per shift. Find all values of `W` for which the optimal dock is exactly at the station. What happens at the threshold?
