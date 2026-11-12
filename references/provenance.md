# Provenance: where this method came from

Read this when revising the skill or when someone asks what a recommendation rests on. Ordinary tutoring does not need it. It records history and sources; it is not a set of instructions, and none of the files or runtimes it names are promised to exist in the active workspace.

## Revision 8, 2026-11-12

The oral exam extends this skill's existing practice and Jane Street's single-question format. It keeps the learner's goal negotiable, asks them to defend a real decision, and treats the requested solution or pause as immediately binding. The local roadmap uses dated evidence for a particular activity and its conditions. The Jane Street decisions and MIT notice below still apply.

There is experimental reason to distinguish immediate fluency from later performance. In two prose-learning studies, immediate recall and delayed recall favored different study conditions. In four other experiments, previously tested participants did better on a one-week final test than participants who restudied, including some new inference questions. These are reasons to measure retention and transfer separately from confidence. Neither study evaluated PPP, this oral-exam format, the roadmap interface, or an engineering learner's outcomes. [Roediger and Karpicke, 2006](https://pubmed.ncbi.nlm.nih.gov/16507066/) · [Butler, 2010](https://pubmed.ncbi.nlm.nih.gov/20804289/)

## Revision 7, 2026-11-12

Jane Street's `socratic-tutor` starts an explicitly requested course by mapping subskills and diagnosing a starting level. Its questions ask the learner to predict, explain an error or apply an idea. It asks for actual output on practical tasks and uses later recall and mixed tasks to check progress. A learner can ask for the answer or carry a progress summary to a new conversation. The source for this comparison was the complete skill at commit `7c6715c`. [Jane Street skill](https://github.com/janestreet/agent_skills/blob/7c6715c29548a3b39d4a9545c698ee4fd17a7213/socratic-tutor/SKILL.md)

| Decision | Why it fits PPP | A case that could show a mistake |
|---|---|---|
| Keep PPP's past-paper loop and direct-answer override. | An existing attempt identifies the relevant step. A specific question or request for a worked solution sets the amount of help. | Give a complete solution on request. Give only the first hint when the learner wants to try. |
| Adapt focused questions and decomposition. | If two explanations of an error would call for different help, choose one prediction or boundary case that distinguishes them. For a project, trace the target back to the first uncertain prerequisite. | A correct guess with no reasoning leaves the cause open. A clear arithmetic slip needs no intake quiz. |
| Adapt practical checks and review. | Compare the learner's prediction with a trace or measured output. Offer a cold problem with a changed setup when the learner wants to revisit a topic. | A passing simulation after copying code establishes a result for that run. Delayed independent transfer requires a later response from the learner. |
| Keep PPP's dated evidence when resuming. | A short handoff can carry the next decision. Its source, assistance level and subsequent corrections determine what it supports. | A corrected claim about who performed a step must change the next task. A missing record leaves the prior performance unknown. |
| Decline fixed diagnostics, percentages, failure quotas and compulsory final assessments. | Their cost depends on the learner's goal, the evidence already available and the time left. | A learner who declines the plan, changes subject or stops should be able to do so in one turn. |

These are design decisions. Whether a focused probe helps a person retain or transfer a method remains a question for learner evaluation. PPP uses its own wording and record formats. The [upstream MIT notice](jane-street-license.txt) applies to Jane Street's material. [Original license](https://github.com/janestreet/agent_skills/blob/7c6715c29548a3b39d4a9545c698ee4fd17a7213/LICENSE.md)

## Revision 6, 2026-11-11

Revision 6 clarifies targeted essay diagnosis versus full marking, the scope and basis of estimated marks, engineering approximation decisions for a stated quantity and tolerance, and a reasoning move demonstrated across fields in either direction. Historical E05's strength-first criterion conflicts with its learner's requested weakest-point feedback. Its additional partial concerns an implied grade. E08's extra partial leaves the next action implicit. Published revision 5 already includes the later E15 wording, which is the baseline for this release.

The [revision 6 comparison](https://github.com/maarmot/Pure-Past-Paper-Focused-Agentic-Tutoring/blob/20b6f9bf06c1b962aaf7f5f99beae577ae96c30d/tests/behaviour/results/2026-11-11/revision6/README.md) retains synthetic prompts, exact replies shown to graders, criteria, keys, partials, disagreements and reproducible counts. Five development contexts per version precede three fresh comparison contexts per version. These are instruction design choices and tutor-response observations, not evidence about a human learner's transfer or retention.

The beam reference was independently derived from bending and shear strain energy. [INL's MOOSE theory](https://mooseframework.inl.gov/moose/modules/solid_mechanics/C0TimoshenkoBeam.html) supports the kinematic distinction, and [PyCBA's author documentation](https://ccaprani.github.io/pycba/notebooks/timoshenko.html#example-1-a-simply-supported-deep-beam) gives the central-force displacement components. [Roylance's MIT notes](https://ocw.mit.edu/courses/3-11-mechanics-of-materials-fall-1999/13534abb67b86d2fb8ee11a1f4f2b8c4_MIT3_11F99_bdisp.pdf), pages 6-7, derive the shear-energy factor and component deflections; the final printed ratio is inconsistent with those components. The reference uses the components and independent integration, not that ratio. The constant rectangular shear factor is an elementary model assumption.

## Revision 5, 2026-11-10

Revision 5 added a feedback wording standard and difficulty signals to tutoring, the loop's form in engineering and essay subjects, good-faith argument and source companions, delegation by job, a beat order and measured render workflow for short videos, and record fields for argument and essay work.

Every rule added in revision 5 is a design choice. The reading below informed the choices; it does not establish them, and none of it tested this skill.

### What was read, and how

The table below records the original draft's literature intake. The release review also checked Study 1's goal-choice and postfailure results in Mueller and Dweck's original paper. Among 123 fifth graders, 67% of those praised for intelligence chose a performance goal, compared with 8% of those praised for effort. The percentages describe a choice on this task. Advising a tutor to identify a sound step in a college student's work is a separate design decision. [Mueller and Dweck, 1998, pp. 36–37](https://www.columbia.edu/cu/psychology/courses/3615/Readings/Mueller_Dweck.pdf)

Kalyuga, Chandler, and Sweller report three experiments in which the relative usefulness of integrated explanatory text changed as learners became more experienced. The publisher's abstract was available for this release check. The difficulty signals in the skill are practical choices with no measured thresholds. [Levels of Expertise and Instructional Design](https://journals.sagepub.com/doi/10.1518/001872098779480587)

| Topic | Sources looked for | What was actually read | Used for |
|---|---|---|---|
| Feedback | Hattie and Timperley 2007; Kluger and DeNisi 1996; Shute 2008; Yeager and others 2014; Mueller and Dweck 1998 | A secondary summary of the first; abstract snippets of the second; nothing readable of the rest | Criticise the step, not the person; name the correct move when praising. The feedback examples and choice to prioritize consequential errors are authored guidance |
| Level of challenge | Bjork on desirable difficulties; Wood, Bruner and Ross 1976; Kalyuga on expertise reversal; Kapur on productive failure; Koedinger and Aleven 2007; Wilson and others 2019 | Encyclopedia pages and snippets | Changing support on observed performance, one thing at a time. The signal table has no measured thresholds. The "85% rule" was not adopted: as summarised, it comes from simulated learners on classification tasks, not people solving problems |
| Transfer between fields | Barnett and Ceci 2002; Gick and Holyoak 1980, 1983; Chi, Feltovich and Glaser 1981; Perkins and Salomon | Snippets and one encyclopedia page | The cautious wording in [across fields](fields.md): what is "worth prompting", and that a named bridge is not evidence. No claim about how much transfers |
| Essay marking | AQA A-level Philosophy and History specification pages | The assessment-objective pages were read; the level-descriptor wording and a mark scheme PDF were not readable | Best-fit marking against criteria, and the rule that a band needs the criteria open. One exam board is not all marking |
| Argument | Socratic method, principle of charity, Toulmin, argument mapping, Adler and Van Doren; Chi and others on self-explanation; Dunlosky and others 2013; work on fluency after watching explanations; work on agreement-seeking in language models | Encyclopedia pages for the first five; snippets for the rest | The argument loop and the source table are this skill's design. "Refuting a claim does not prove its opposite" follows a criticism reported on the Socratic method page |

### The public repository

[maarmot/Pure-Past-Paper-Focused-Agentic-Tutoring](https://github.com/maarmot/Pure-Past-Paper-Focused-Agentic-Tutoring) was read on 2026-11-10 at commit `f4e8c31`. It is this skill's published revision 4 with wording made more cautious in places, a README, and a test workflow. Revision 5 was written on top of that commit, not on the local draft it replaced.

### Caption timings of eight videos

The [caption recount](measurements/caption-recount.json) records the counts, cue times and input hashes. The [render trial data](measurements/bench-trials.json) records each retained timing condition and its individual runs.

English VTT captions and video metadata were retained for eight 3Blue1Brown videos. In the release audit, an independent parser reproduced all eight cue counts, word counts, metadata durations, and first timestamps containing a question mark. The rate divides caption words by the full video duration, including silences. The two passage columns are approximate navigation points from the earlier reader's coding of examples, formulas, and definitions.

| Video | Length | Caption words | Words/min | First cue with `?` | Case passage | Formula or definition passage |
|---|---:|---:|---:|---:|---:|---:|
| [Essence of calculus](https://www.youtube.com/watch?v=WUvTyaaNkzM) | 17:04 | 2,906 | 170.3 | 1:22 | 1:35 (circle area) | 3:32 |
| [Paradox of the derivative](https://www.youtube.com/watch?v=9vKqVkMQHKk) | 16:50 | 2,917 | 173.3 | 2:59 | 1:07 | 5:22 |
| [Fourier series](https://www.youtube.com/watch?v=r6sGWTCMz2k) | 24:47 | 4,426 | 178.6 | 5:03 | 0:05 | 6:46 |
| [Neural network](https://www.youtube.com/watch?v=aircAruvnKk) | 18:40 | 3,357 | 179.8 | 2:48 | 0:04 | 3:25 |
| [Vectors, chapter 1](https://www.youtube.com/watch?v=fNk_zzaMoSs) | 9:51 | 1,800 | 182.7 | 4:04 | 0:55 | 0:30 |
| [Central limit theorem](https://www.youtube.com/watch?v=zeJD6dqJ5lo) | 31:14 | 6,253 | 200.2 | 5:39 | 0:00 | 15:57 |
| [Differential equations](https://www.youtube.com/watch?v=p_di4Zn4wz4) | 27:16 | 4,548 | 166.8 | 3:27 | 2:13 | 3:15 |
| [Bayes theorem](https://www.youtube.com/watch?v=HZGCoVF3YvM) | 15:11 | 2,650 | 174.5 | 1:24 | 1:04 | 7:15 |

The eight topic terms first appeared in cues beginning between 3.369 and 74.202 seconds. The earliest cue containing a question mark began at 82.032 seconds. A question can start in an earlier cue and acquire its punctuation later. Seven selected case passages precede the selected formula or definition passage. In Vectors the description of an arrow comes first. The earlier reader classified endings as callbacks, invitations, or forward references. The selection and coding reflect that reader's judgement.

Use these observations to consider a sequence for a new explanation. The prediction beat and boundary case in [Manim and media](manim.md) come from the tutoring design. Screen transitions, useful holds, and learning outcomes need separate evidence.

### Render measurements

The earlier Windows benchmark used Python 3.12.13, Manim Community 0.22.1, and a 12-second scene. The table gives the retained wall times in seconds from process start to exit. The in-place version updates existing objects, caches repeated text labels to one decimal place, and stops updates during a hold. The rebuild version reconstructs marks and text each frame, displays two decimal places, and keeps updating during the hold. The comparison includes all of these differences.

| Setting | In-place trials (s) | Rebuild trials (s) |
|---|---|---|
| Cairo, 854 × 480, 15 fps, cache off | 4.92, 4.73 | 8.08, 7.93 |
| Cairo, 1920 × 1080, 30 fps, cache off | 9.82, 9.48 | 14.22, 13.74 |
| Cairo, 1920 × 1080, 60 fps, cache off | 15.46 | 24.58 |
| Cairo, 1080p30, cache enabled, cold | 9.56 | 14.36 |
| Cairo, 1080p30, cache enabled, two warm runs | 7.42, 7.35 | 11.81, 12.25 |
| OpenGL, 1080p30, cache off | 13.85, 12.98 | 17.26 |

For the in-place scene at 1080p30, a six-second section (`-n 2,2`) took 7.42 and 7.43 seconds. Rendering a final still took 2.45 and 2.43 seconds. The four benchmark reports support these trials. The separate startup, parallel-process, stream-copy, and encode-size comparisons lack corresponding trial records in those reports.

Use the trial values only for this workload. Keep parameters and visual precision matched when testing the effect of an individual change.

An earlier preview held the opening objects at 0.2 seconds, when the two candidates coincide. The opening hold now uses 0.17 seconds, where the dot and square have distinct positions. The release audit also found ten old sample pairs during the final question about a new 12 photos/s camera. The closing shot now restores the two original motion markers and names the changed camera. Moving the extra square onto the extra dot in a scratch copy still passed the pure model check. The real scene-object check rejected the fault at the reveal.

### What was not done

No narrated video was produced; the starter scene is a silent preview. No learner used any of this. The behaviour comparison in `tests/behaviour` measures a model's replies, not anyone's learning.

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
