# Is the marker within five metres?

Original generated computer-vision problem. Your goal is to decide which depth claims follow from bounded pixel measurements. Use scratch paper and a calculator. Explain why the bounds you report are attainable.

Two ideal pinhole cameras have parallel optical axes, with a horizontal baseline of 0.12 m and focal length 240 pixels. Both see the same stationary point. In the left camera's coordinates the point is at horizontal position `X` and forward depth `Z > 0`, in metres. A camera at horizontal position `b` projects it to column `u = c + 240(X − b)/Z`, where `c` is that camera's principal column. Treat the baseline, focal length and principal columns as exact. Distortion and vertical coordinates can be ignored.

| Camera | b (m) | c (px) | Reported column (px) |
| --- | ---: | ---: | ---: |
| Left | 0 | 160 | 178 |
| Right | 0.12 | 158 | 170 |

Each true image column lies within 0.5 px of its report, inclusive. Any combination of errors within these bounds is permitted. This is a deterministic error bound.

1. Eliminate the unknown horizontal position. Compute depth using the reported columns as exact, then determine the tight range of positive depths consistent with the error bound.
2. Can the rig certify that the point is at most 5 m away in forward depth? Exhibit feasible observations on both sides of this threshold if the data admit them.
3. Imagine a different match on the same rig whose reported difference of **principal-column-corrected** coordinates is 1 px. What finite lower or upper depth bound survives? Distinguish a disparity of zero from a limit of positive disparities.
