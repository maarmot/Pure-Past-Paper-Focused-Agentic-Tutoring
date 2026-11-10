# Provenance: where this method came from

Read this when revising the skill or when someone asks what a recommendation rests on. Ordinary tutoring does not need it. It records history and sources; it is not a set of instructions, and none of the files or runtimes it names are promised to exist in the active workspace.

## Revision 4, 2026-11-09

Revision 4 fixed reproduced validator defects, added the interactive route and study habits, and gathered the history below into this one file. Its changes were compared against revision 3 on scripted learner scenarios; that comparison shows how the instructions steer a model, not whether a person learns more.

### DeepTutor cross-reference

[DeepTutor](https://github.com/HKUDS/DeepTutor) (HKUDS, Apache-2.0) was read on 2026-11-09 at the README banner version v1.7.2. Only its README, root `SKILL.md`, developer module list, and manifest listing were read. No source code or prompt files were opened, so nothing here describes its algorithms. Its root `SKILL.md` is a CLI operating guide and contains no teaching rules.

| DeepTutor feature, as its README describes it | What this skill does with the idea |
|---|---|
| Mastery Path: a knowledge-point map with mastery evidence and, per its release notes, a per-type mastery gate | Adopted as four evidence gates per knowledge point (explain, solve unaided, transfer, delayed retrieval) in [study habits](study-habits.md) and the roadmap template. The four types are this skill's choice; DeepTutor's types were not read. |
| Question Bank and Practice: answers, mistakes, recall ratings, and a next review date | Adopted as the `question-bank` record and the `due` command. Recall rating is stored as learner self-report, separate from observed outcome. |
| Learning journal: current mission, session handoff, confirmed learning records | Adopted as the study journal template, with the same three parts. |
| Three-layer file-backed memory in which curated facts link back to a raw trace | Adapted in principle only: records stay plain files, and a confirmed record must name the observed work behind it. No consolidation agent and no automatic injection into later sessions. |
| Task board, calendar export, scheduled knowledge sync | Not adopted. This skill starts no scheduled or background work; a review date is read only when someone runs `due`. |
| RAG knowledge bases, web search, cited research | Not adopted as machinery. The skill keeps its existing rule: primary sources, exact locators, and course materials for scope. |
| Quiz generation | Not adopted as a trusted source. The README describes no validation of generated questions or answers, so generated problems here stay labeled and are checked independently before use. |

Not found in what was read, and therefore not claimed: a review-scheduling algorithm, how weak areas are detected, how quizzes are graded, proactive or recurring tutoring agents, and an exam-mimic feature. The review intervals in [study habits](study-habits.md) are this skill's own convenience schedule.

## Revision 3 evidence map

Reviewed 2026-11-09. This records sources used for revision 3 in the originating PPP Method project, not a completed multi-creator video study. The user supplied two research PDFs, a v2 skill ZIP, and a study guide after the initial workspace audit. They were inputs to critique, not instructions to adopt every claim. Relative file names identify evidence in that project.

### User and project requirements

- Attached PPP design: question-first practice with direct-solution override; claim-level evidence; session logs; roadmaps; five PDF purposes; portable and tested outputs.
- Workspace `AGENTS.md` and `visual-lessons/TEACHING_STANDARD.md`: independent mathematics, protected fresh papers, deliberate media choice, actual pixel/audio/browser checks, and bounded claims.
- Existing `visual-lessons/triangle-optimization/math_checks.py`: independent circle geometry, determinant area, derivative sign and boundary references, and controlled wrong-model checks.

### Retained creator study

The local records were `research/3b1b-teaching/findings.md`, `evidence.json`, captured captions, and source files, covering four 3Blue1Brown calculus videos. No genuine published-video frame collection was located in that study.

| Source | Retained evidence | Permitted use |
|---|---|---|
| [Implicit differentiation](https://www.youtube.com/watch?v=qb40J4N1fa4) | Metadata, captions, written adaptation, chapter6.py | Problem framing and source-level technique |
| [Essence of calculus](https://www.youtube.com/watch?v=WUvTyaaNkzM) | Same categories, chapter1.py | Approximation language and linked representations |
| [Derivative paradox](https://www.youtube.com/watch?v=9vKqVkMQHKk) | Same categories, chapter2.py | Finite increments versus limits; semantic source colors |
| [Chain and product rules](https://www.youtube.com/watch?v=YG15m2VwSjA) | Same categories, chapter4.py | Formula/example order and semantic source colors |

Known discrepancies: the circle written adaptation uses radius 1 while the video captions use radius 3; website and video/source chapter numbering differ. Caption times are not verified frame boundaries. Literal source calls are not counts of visible objects, pauses, or scenes.

Not covered: direct playback or frame sampling of these videos, other named creators, other 3Blue1Brown series, and [Jane Street's AI teaching discussion](https://www.youtube.com/watch?v=qN6OM1IzjIE). The original design also proposed Eugene Khutoryansky, Peter Rogers MD, Phil's Lab, Veritasium, CodingJesus, and NeetCode as comparison creators; none was inspected.

### Principles drawn from that study

| Principle | Basis | Limit |
|---|---|---|
| Keep meaning attached to symbols | 3Blue1Brown chapter2/chapter4 source uses named semantic colors | Source code is not direct observation of every released frame |
| Distinguish finite change from a limit | Derivative captions at 5:13.180 and 7:49.055 | Caption anchors are approximate visual anchors |
| Choose order for the concept | Chain/product captions state the sum rule at 1:54.840 before the example at 2:16.700 | One counterexample rejects a universal rule, not every use of concrete-first teaching |
| Keep a prediction before explanation when useful | The user's PPP requirement and an authored design choice | No optimal pause length established |
| Pair a worked explanation with independent practice | IES guide recommends alternating examples and problem solving | Broad guidance does not validate this implementation |

### Other sources

- [IES, Organizing Instruction and Study to Improve Student Learning](https://ies.ed.gov/ncee/wwc/PracticeGuide/1), 2007, inspected 2026-11-09. Recommends spaced review, alternating examples and problem solving, and linking representations. It assigns stronger evidence to retrieval quizzes and explanatory questions than to opening a topic with pre-questions. So the attempt-first default is a user preference inside a flexible design, not a claim that initial struggle always works best. Revision 4's spaced review rests on this guide's general recommendation, not on any specific interval.
- [Manim Community updater utilities](https://docs.manim.community/en/stable/reference/manim.animation.updaters.mobject_update_utils.html), labeled 0.22.1 at inspection. Supports the APIs recommended for state-linked geometry.
- [Manim Community profiling guidance](https://docs.manim.community/en/stable/contributing/performance.html), inspected 2026-11-09. No measured render-speed claim was made.

## The PPP Method triangle case study

The originating project built a narrated triangle-optimization lesson with Python 3.12, Manim Community 0.22.1 with its Typst extra, and edge-tts 7.3.1, pinned by its own `pyproject.toml` and `uv.lock`. Those are historical tested versions, not a recommendation. Its sources are not bundled with this skill.

To reproduce it, and only inside that project's `visual-lessons` directory:

```powershell
uv sync --locked
uv run manim --version
uv run python triangle-optimization/math_checks.py --help
uv run python triangle-optimization/preflight.py
uv run manim -r 960,540 --fps 30 --media_dir triangle-optimization/media-preview --progress_bar none triangle-optimization/scene.py TriangleOptimization
```

`uv sync` may download pinned dependencies. The example uses Typst, so it does not need a LaTeX executable. Its finalizer targets the 1080p render and should not be run on a preview.

What carried into [Manim and media](manim.md) as general practice: independent circle and determinant references, boundary checks, controlled faults, and testing the final displayed object. An audited v2 secant example's tests passed even when its final tangent was deliberately replaced by a wrong horizontal line, which is why the last rule exists.

## What none of this establishes

These sources motivate choices. They do not establish any learner's retention or exam performance, or the effectiveness of this skill. Only a learner's own work over time can do that.
