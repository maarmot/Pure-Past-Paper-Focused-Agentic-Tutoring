# Manim and media production

Read this when a lesson needs animation, interaction, or media verification. Inspect the active workspace's actual environment before choosing commands. This skill does not bundle Manim, a Python environment, speech credentials, or the example lesson sources. Missing Manim must not block ordinary tutoring or a useful static explanation.

## Before rendering

For inquiry, first read [visual inquiry](visual-inquiry.md) and use [its storyboard](../assets/inquiry-storyboard.template.md). For exam repair use [the practice storyboard](../assets/storyboard.template.md). Define the observable puzzle, learner action, fixed reference, and meaningful variable before planning equations. Include source, assumptions, domain, units, a counterexample, and an independent check. Keep optional formal detail separate from the initial view.

A Manim video is a guided explanation. It cannot respond to a new question or support free parameter manipulation by itself. Choose an interactive companion when the learner must compare cases or test a conjecture. Plan branches around the misconception or question that changes the explanation, not a menu of cosmetic variants. Do not write narration that reveals the answer during the supposed question beat.

Prefer the active project's compatible dependencies and verify any needed setup. ManimGL source may inform a principle but cannot simply be executed as Manim Community code. Run `audit` from [the CLI guide](tools.md) first: if Manim is absent, say so and offer [an interactive page](interactive.md) or a static explanation rather than installing anything unasked.

## Reusable implementation patterns

- Keep mathematical state in a small pure function with explicit domain checks. Rendering objects read that state; they do not silently clamp invalid inputs into valid answers.
- Use one `ValueTracker` per independent changing parameter. Derive all dependent coordinates and readouts from it. A single state prevents disagreement among diagram, graph, and displayed values, but reference tests must use an independent derivation.
- Use `always_redraw` when geometry must be rebuilt. Use an updater when moving or changing an existing object is sufficient. Never typeset an entire equation every frame just to change one number.
- Keep labels tied to the objects they describe and reserve space for captions. Use color plus variable names, line styles, or shape. Check signs and root bars after scaling.
- Keep an unchanging diagram visible while explaining its equation. Explain a mathematical transformation; do not let a visual morph stand in for a derivation.
- Keep speech generation separate from rendering. Cache by text, voice, and rate. Write asset paths relative to the lesson directory; resolve at load time. Reuse a valid cache when relocating a project.
- Anchor important visual actions to verified speech word timings. A missing phrase must fail before final delivery. Do not silently replace it with the current frame time.

Authoritative API guidance: [Manim updater utilities](https://docs.manim.community/en/stable/reference/manim.animation.updaters.mobject_update_utils.html). The case study these patterns came from, with its reproduction commands, is in [provenance](provenance.md).

## Preview and profile intentionally

Use low resolution first while preserving the planned frame rate when timing matters. Render preview files into a distinct media directory. Do not overwrite accepted exports to test a change. Typeset all expressions before a long render.

For any lesson, source and timing records must refer to the same render.

Measure total wall time around the command. Record renderer, resolution, fps, cache state, dependency versions, hardware, and output quality settings. Compare before and after under the same conditions; use repeated runs if noise matters. For a known CPU bottleneck, use Python `cProfile` and inspect cumulative time. Report process memory only when an actual measurement tool collected it, and state whether child processes are included. See [Manim's profiling guide](https://docs.manim.community/en/stable/contributing/performance.html).

Optimize the measured cost: repeated typesetting, excessive object reconstruction, unnecessary high-resolution previews, or invalidated audio caches. Do not promise speedups from stylistic refactoring. Keep math, text size, timing, and geometry acceptance criteria unchanged while comparing.

## Verify in separate layers

1. Math: independently derive answers, units, signs, theorem conditions, and boundaries. Test a plausible wrong setup and verify the test rejects it.
2. Rendered state: compare actual plotted vertices and readouts with the reference at representative parameters, including changes during motion. A sampled sweep is not a global proof.
3. Pixels: open setup, transition, equation, invalid-case, and conclusion frames. Inspect clipping, overlap, symbols, contrast, and correspondence. Observe actual playback before claiming smoothness or pacing; sparse ordered stills can show a change without establishing how that change feels in time.
4. Media: fully decode the final video, inspect stream metadata, and check caption ranges with the CLI. These checks cannot hear pronunciation or see synchronization.
5. Perception: listen to final narration and view captions during playback. Check missing words, awkward mathematical phrasing, captions over labels, and a clean ending. Mark unlistened audio explicitly.
6. Interaction, if delivered: exercise keyboard controls, play/pause, reset, reveal, and reduced motion. Record actual dimensions at widths 320, 736, and a desktop width, in light and dark surroundings. Include heights and browser conditions.

Use independent references, boundary checks, and controlled faults for each new topic; do not copy another lesson's assertions. Test the final displayed object as well as intermediate updaters, because tests on the updaters can pass while the last frame shows the wrong thing. Tie every consequential visible claim to a coordinate, invariant, or independently inspected relationship. Physics additionally needs explicit modeling assumptions and independent unit/conservation or trusted-reference checks.

Image generation can supply original non-quantitative imagery when it helps. Use controlled drawing code for exact plots, equations, and vector directions. Record the actual image model/version exposed by the tool; do not invent one.
