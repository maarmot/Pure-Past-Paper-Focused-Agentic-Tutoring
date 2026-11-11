# Manim and media production

Use this guide for animation and media verification. Inspect the active workspace's environment. The skill includes one editable starter scene. Manim Community, a speech service, and the historical benchmark scenes have separate dependencies. A static diagram can answer many questions on its own.

## Before rendering

For inquiry, first read [visual inquiry](visual-inquiry.md) and use [its storyboard](../assets/inquiry-storyboard.template.md). For exam repair use [the practice storyboard](../assets/storyboard.template.md). Define the observable puzzle, learner action, fixed reference, and meaningful variable before planning equations. Include source, assumptions, domain, units, a counterexample, and an independent check. Keep optional formal detail separate from the initial view.

A Manim video is a guided explanation. It cannot respond to a new question or support free parameter manipulation by itself. Choose an interactive companion when the learner must compare cases or test a conjecture. Plan branches around the misconception or question that changes the explanation, not a menu of cosmetic variants. Do not write narration that reveals the answer during the supposed question beat.

Prefer the active project's compatible dependencies and verify any needed setup. ManimGL source may inform a principle but cannot simply be executed as Manim Community code. Run `audit` from [the CLI guide](tools.md) first: if Manim is absent, say so and offer [an interactive page](interactive.md) or a static explanation rather than installing anything unasked.

## Order the beats of a short tutorial

For a 3 to 8 minute video that builds intuition, start from this order. It is a default, not a ladder. If the learner asks for the formal statement first, lead with it. For a clip under about two minutes, merge beats 6 and 7. For an exam-repair video use the order in [the practice storyboard](../assets/storyboard.template.md) instead: question, first wrong step, repair, transfer.

| Beat | On screen | Narration does | Check |
|---|---|---|---|
| 1 Object and aim | The concrete case, already moving | Names the topic and says, in one sentence, the question this video settles | No formula yet; the opening frame shows what the question is about |
| 2 Case | One reference state, one condition varied | Says what changes and what stays fixed | Values match the independent derivation |
| 3 Predict | A held frame with the question as a caption | Asks one question, says to pause, does not answer | The answer is in no narration, caption, or frame; the hold is long enough to read the caption twice |
| 4 Reveal and name | The outcome, then names attached to visible parts | Introduces each symbol as a name for something already seen | Every symbol points at an object |
| 5 Formal statement | The formula beside the unchanged diagram | States conditions, units, and domain | Matches the cited source, or the independent derivation when the problem is generated |
| 6 Limit | A case where the picture misleads | Says what the picture does not prove | The counterexample is checked |
| 7 Return | The opening case again | Gives one task to try away from the video | No list recap |

A viewer who already solves this kind of problem needs beat 2 only as a single reference state, and beat 3 is optional. A video cannot hear an answer, so beat 3 is an invitation; the chat reply that delivers the video must still show something on the first turn.

[The starter scene](../assets/manim/lesson_beats.py) is a silent, seven-section example. Copy it and [the scene check](../assets/manim/check_scene.py) into the project. `python lesson_beats.py --check` tests the sampling model with Python's standard library. With Manim available, `python check_scene.py` constructs the scene and checks the marker positions selected for all seven holds. Adapt both checks when changing the lesson.

Eight videos informed the ordering. All eight caption tracks named the topic within 75 seconds. The earlier reading placed a concrete example before its selected formula or definition in seven. Those judgements depend on the example and formula chosen. Prediction and a counterexample come from the tutoring design. Choose holds for the current explanation, and write original narration and scenes. [Caption evidence](provenance.md)

Do not aim at a words-per-minute figure. Compute the actual pace from the script's word count and the measured audio duration, record each beat's share of the running time beside the plan, and adjust after watching.

## Reusable implementation patterns

- Keep mathematical state in a small pure function with explicit domain checks. Rendering objects read that state; they do not silently clamp invalid inputs into valid answers.
- Use one `ValueTracker` per independent parameter. Derive dependent coordinates and readouts from it. Verify the actual plotted marks and labels against an independent derivation. A shared state can still be displayed incorrectly.
- Use `always_redraw` when geometry must be rebuilt. Use an updater when moving or changing an existing object is sufficient. Never typeset an entire equation every frame just to change one number.
- Keep labels tied to the objects they describe and reserve space for captions. Use color plus variable names, line styles, or shape. Check signs and root bars after scaling.
- Keep an unchanging diagram visible while explaining its equation. Explain a mathematical transformation; do not let a visual morph stand in for a derivation.
- For a narrated lesson, draft the script and storyboard together, obtain the audio in the authorized environment, then measure its phrase landmarks before timing final motion. Keep a speech cache keyed by text, voice, and rate. Resolve its asset paths relative to the lesson directory.
- Anchor important visual actions to verified speech word timings. A missing phrase must fail before final delivery. Do not silently replace it with the current frame time.

Authoritative API guidance: [Manim updater utilities](https://docs.manim.community/en/stable/reference/manim.animation.updaters.mobject_update_utils.html). The case study these patterns came from, with its reproduction commands, is in [provenance](provenance.md).

## Preview and profile intentionally

Use a low-cost render for the question being checked. The commands below target Manim Community 0.22.1. Check the installed version with `manim --version` and confirm the available options in `manim render --help` and `manim cache clear --help`.

| Question | Command | What it gives |
|---|---|---|
| Is the model right? | `python lesson_beats.py --check` | Model against hand-derived values; no Manim needed |
| Does the layout fit at final size? | `manim render -s -qh scene.py Scene` | The last frame only. For another beat, render to it with `-n` |
| Does the motion read, and does timing fit? | `manim render -ql --fps 30 --save_sections scene.py Scene` | 480p at the final frame rate, one file per section with durations. Plain `-ql` is 15 fps |
| One part only | `manim render -ql --fps 30 -n 4,6 scene.py Scene` | Animations 4 to 6 |
| Final | `manim render -qh --fps 30 scene.py Scene` | 1080p. `-qh` alone is 60 fps |
| Try an H.264 quality setting (0.22 or later) | add `--video-codec libx264 --encoder-option crf=18` | Compare the resulting size and visible detail with the current encode |
| Stale cache (0.22 or later) | `manim cache clear scene.py Scene` | Removes cached segments for that scene |

Render previews into a distinct media directory. Do not overwrite accepted exports to test a change. A `-ql` or silent render is a preview and must be reported as one. Mark finished parts with `self.next_section(skip_animations=True)` while iterating and remove every skip before the final render.

`python scripts/ppp_tools.py render-timing scene.py Scene` times the still, preview, and final renders of a scene with the cache off and reports wall time for each. Use it to get a baseline before changing anything and again after.

Two versions of the same 12-second example were timed on one Windows machine with Manim Community 0.22.1. The versions differ in object rebuilding, text precision, repeated label caching, and updater handling during holds. Each comparison measures their combined effect. The benchmarks also tested resolution, frame rate, cache, and renderer. [Recorded timings and run counts](provenance.md)

| Change | Observed |
|---|---|
| In-place version, 480p15, 1080p30, 1080p60 | 4.73 s, 9.48 s, 15.46 s. Resolution and frame count both change. |
| Per-frame rebuild version at the same three settings | 7.93 s, 13.74 s, 24.58 s. The 60 fps values are single trials. |
| Unchanged in-place scene with the cache enabled | 9.56 s cold, then 7.42 and 7.35 s warm |
| One 6-second animation with `-n` | 7.4 s |
| Last frame only with `-s` | 2.43 s wall time |
| `--renderer=opengl` | Slower here: 13.0 s against 9.5 s |

Check the model, inspect a still, then preview the motion. If a measured bottleneck warrants it, try cached labels, suspend unneeded updates during a hold, or render independent beats in separate processes with separate output directories. Compare output quality and timing under matched settings. Keep a continuous scene when object continuity across beats matters.

When a lesson is split into scenes, join the finished files without re-encoding, then run `media-info` and `check-captions` on the joined file. The joined file is the render the timing record and captions must refer to.

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
