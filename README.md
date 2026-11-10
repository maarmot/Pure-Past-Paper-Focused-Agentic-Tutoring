# Pure Past Paper tutoring

A portable tutoring skill for past-paper practice, visual inquiry, and study review. PPP means **Pure Past Paper**: attempt a real question, locate the first unsupported step, repair it, retry, and then try a different problem.

The skill also supports curiosity-led explanations. A learner can ask to see a mechanism, change a parameter, or request the full solution without completing a preliminary exercise.

## What is included

- **Tutoring instructions** that use the learner's actual work, preserve papers reserved for timed practice, and distinguish hints from unaided performance.
- **Visual inquiry and interactive builds**, with a complete sampling-ambiguity starter that runs in a browser.
- **A study journal, question bank, and roadmap** for recorded attempts, learner recall ratings, review dates, and evidence of understanding.
- **Verification tools** for structured records, due-review selection, caption timing, and media decoding.
- **Manim and PDF guides**, plus five LaTeX starter formats. Their runtimes are optional and are not bundled.

Start with [SKILL.md](SKILL.md). It selects the reference needed for the current request rather than loading every workflow.

## Install

The repository root is the skill folder. For a personal Codex installation, clone it into an unused skill directory:

```sh
git clone https://github.com/maarmot/Pure-Past-Paper-Focused-Agentic-Tutoring.git ~/.agents/skills/ppp-learning
```

For a project-only installation, use `.agents/skills/ppp-learning` inside that project instead. If the destination already exists, inspect and preserve its changes before replacing or updating it. Avoid two enabled installations with the same skill name.

Codex uses [agents/openai.yaml](agents/openai.yaml) for interface metadata. The skill can also be read manually by a compatible assistant, or installed in another host's supported skill location. Installing this folder does not install Python, Manim, LaTeX, or a browser, and does not grant permission to write learner records.

## Use it

Example requests:

> Use $ppp-learning to check my working. Identify the first unsupported step and give me one useful hint.

> Show me why a wheel can look as though it is turning backwards. Keep equations optional and let me investigate.

> What should I review today? Use the question bank in this project, and leave my reserved paper unopened.

> Give me the complete solution now. I do not want hints or a video.

For a standalone visual example, open [assets/interactive.template.html](assets/interactive.template.html) in a browser. It compares two fixed motions under different camera measurements and includes a check of the drawn marks. When building a lesson, copy the starter into the active project's output area and edit that copy.

## Personalize the workflow

Use the active project's instructions to establish the subject, course or textbook, allowed methods, preferred explanation style, and permitted output locations. Keep curiosity and exam practice distinct. A visual inquiry can end with a useful observation or a sharper question; it does not require an exam-style exit task.

Create a journal or question bank only where learning records are authorized. Keep dates, assistance, learner self-report, and observed work separate. A record in one workspace is not permission to read or write records in another. A specific problem or solution request takes precedence over opening the study journal.

The review intervals in [study habits](references/study-habits.md) are adjustable planning suggestions. `due` reads the dates already recorded; it does not choose an optimal schedule, create reminders, or run in the background.

## Command-line tools

The helpers require Python 3.9 or newer and use its standard library. Media probing and decoding additionally require FFmpeg and ffprobe on `PATH`. Run these commands from the repository root:

```sh
python scripts/ppp_tools.py audit
python scripts/ppp_tools.py validate-record assets/session.template.json --allow-template
python scripts/ppp_tools.py validate-record path/to/session.json
python scripts/ppp_tools.py due path/to/question-bank.json
python scripts/ppp_tools.py check-captions captions.srt --media lesson.mp4
python scripts/ppp_tools.py media-info lesson.mp4 --require-video --require-audio
```

Replace the example input paths with actual files. `--allow-template` is for checking starter files; omit it when validating real records. The validator intentionally rejects leftover starter text in a real record. See [the CLI reference](references/tools.md) for fields, exit status, and limitations.

## Verify a change

```sh
python -B -m unittest discover -s tests -p "test_*.py" -v
```

The suite covers record consistency, protected questions, due selection, captions, subprocess failures, and a real media round trip when FFmpeg is available. The browser starter also needs actual control, keyboard, layout, and theme checks; its self-check is not a substitute for those. The [behavior evaluation protocol](tests/behaviour/README.md) supplies separate tutor-response scenarios.

Passing tests establishes the properties checked. It does not establish a learner's understanding, retention, or exam performance. A valid record is not proof that its observations happened; only actual learner work supports progress claims.

## Sources and scope

[Provenance](references/provenance.md) records the method's sources and the limits of those comparisons. Source references are retained for traceability. No creator's voice, lesson assets, or complete scenes are bundled.

This repository contains instructions, templates, and local tools. It provides no background service, shared learner database, automatic memory, or measured claim of improved learning outcomes.
