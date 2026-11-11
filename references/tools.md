# Local verification tools

Run commands from the `ppp-learning` folder, or give absolute script and input paths. The CLI needs Python 3.9 or newer. It uses the standard library; media checks additionally need FFmpeg and ffprobe on PATH. No command installs software or calls a network service.

```powershell
python scripts/ppp_tools.py audit --output capability-audit.json
python scripts/ppp_tools.py validate-record path/to/session.json
python scripts/ppp_tools.py validate-record assets/session.template.json --allow-template
python scripts/ppp_tools.py due path/to/question-bank.json --on 2026-11-09
python scripts/ppp_tools.py check-captions path/to/captions.srt --media path/to/lesson.mp4
python scripts/ppp_tools.py check-captions path/to/captions.srt --duration 285.3
python scripts/ppp_tools.py media-info path/to/lesson.mp4 --require-video --require-audio --timeout 60
python scripts/ppp_tools.py render-timing path/to/scene.py SceneName --manim "uv run manim"
python -B -m unittest discover -s tests -p "test_*.py" -v
```

Replace example paths with the actual files. `--media` probes the duration with ffprobe; `--duration` takes a number you measured another way. Give exactly one. Use the project interpreter to audit its environment; another Python executable may have different installed packages. `audit` reports metadata and PATH discovery only. A bundled compiler can exist outside PATH, so check the host's supported runtime before declaring it unavailable.

## Exit status and scope

Validation, caption, and media commands return 0 when their applicable checks pass, 1 on rejection or unavailable required runtime. Argument parsing errors use the standard argparse status 2. Audit returns 0 on successful discovery even when a tool is absent; inspect its findings.

- `validate-record` reports `structurally-valid`, not verified truth. It cannot inspect image pixels, authenticate a source, establish actual observation, or measure learning. A record that still contains starter text (a `template_notice`, or a value beginning `Template:`, `Template only`, `Replace with the`, `Replace with verified`, or `Replace before logging`) is rejected so a template cannot be saved as a real record; `--allow-template` checks the shape of a starter file anyway. A session dated more than one day ahead is rejected.
- `check-captions` checks complete SRT syntax, numbering, positive spans, nonoverlap, nonempty text, and media bounds. It allows at most 0.05 seconds past the duration for frame rounding, tolerates extra blank lines between cues and cue settings after the end time, and reports a WebVTT file as the wrong format rather than as broken cues. It does not assess speech alignment, reading speed, or placement.
- `media-info` probes streams and decodes the entire file with FFmpeg. `--timeout` bounds each subprocess separately. Require audio/video explicitly for a finished narrated video; omit those requirements for intentional silent or audio-only artifacts. Presence of an audio stream does not prove intelligible or non-silent narration. Listening remains required.
- `due` validates a question bank, then lists unprotected items whose `next_review` is on or before the day given (today by default), oldest first. It returns 0 whenever the bank is valid, including when nothing is due, and 1 for an invalid bank. It reads the file and schedules nothing.
- Output is written as UTF-8 whatever the console code page, so a non-ASCII filename or source title cannot replace a finding with an encoding error.
- `render-timing` times a final-sized PNG, a 480p MP4 preview and a 1080p MP4 of the requested scene with caching off. Pass an executable path (including spaces) or a launcher such as `--manim "uv run manim"`. Within a launcher string, quote arguments containing spaces using the platform's quoting convention. Each command runs without a shell. A timeout terminates the Windows job or POSIX process group containing the launcher and renderer. The time includes process startup and cleanup.
- By default the CLI removes its temporary media. With `--keep DIR` it reports a fresh `kept_directory` beneath DIR for the attempt, including partial outputs if rendering fails. An attempt-specific copy of the current directory's Manim configuration routes Manim's output and caches into that directory, selects the requested input and renders its full animation range. Appearance and renderer settings carry through. The CLI clears the configured output filename so the generated names identify the scene Manim selected. Each successful run must exit zero and produce a nonempty final file named for the requested class under its own media directory. Partial movies and section clips do not count. The JSON reports the relative artifact path, command, return code, timeout status and wall time. Inspect and decode the files separately to verify their content.
- `audit --output` is the only CLI mode that writes a report itself. Other modes print JSON; redirect it if a retained report is needed. It does not write into the media being checked.

## Session schema, version 1

Use `kind: "session"`, `schema_version: 1`, ISO `date` (not in the future), nonempty `topic`, nonempty `goals` array, `events` array, nonempty `next_step`, and `duration`.

Duration is one of:

```json
{"seconds": null, "basis": "unknown"}
```

```json
{"seconds": 2700, "basis": "user-estimate"}
```

```json
{"seconds": 600, "basis": "measured", "start": "2026-11-09T14:00:00-05:00", "end": "2026-11-09T14:10:00-05:00"}
```

Measured endpoints must be timezone-aware and match elapsed seconds. These are schema examples, not a record of the user's learning session.

Each event requires:

| Field | Allowed values or meaning |
|---|---|
| `problem_id` | Nonempty local identifier |
| `provenance` | `past-paper`, `generated`, `source-adapted` |
| `source` | Source locator required for past-paper or adapted; may be null for generated |
| `assistance` | `none`, `prompt`, `hint`, `partial`, `full-solution` |
| `outcome` | `not-attempted`, `incorrect`, `partial`, `correct` |
| `evidence` | The actual response or an accurate description of what was observed; nonempty unless `outcome` is `not-attempted` |
| `attribution` | `learner-statement`, `observed-work`, `agent-inference` |
| `transfer` | Boolean; label only a genuinely different task as transfer |
| `independent_success` | Optional Boolean; true requires correct, unaided, observed work |

An optional `inquiry` object holds `question`, `prediction`, `observation`, and `open_question`. Each is the learner's own words as a nonempty string, or null when they gave none; never fill one with a tutor's or agent's answer. A transfer task that was shown and not attempted is valid (`outcome: "not-attempted"`, `transfer: true`) and stands for a pending check.

An optional `position` object records an argument ([argument and sources](argument.md)). `question`, `first_claim`, `first_reason`, `revised_claim`, `what_moved`, and `open_question` are the learner's own words or null; a revised claim needs a first claim. `tutor_position` is the tutor's stated position or null. `source_basis` is `supplied-text`, `opened-source`, `learner-account`, or `none`. Start from [the argument template](../assets/argument-session.template.json). Quote no passage from a source in a record.

Record problem exposure, concepts, and diagnostic hypotheses as additional descriptive fields when useful. The validator permits extra fields but does not evaluate their meaning. It does not infer freshness, transfer quality, or mastery from the optional success flag. Read the actual work and prior exposure before making those claims.

## Question bank schema, version 1

Use `kind: "question-bank"`, `schema_version: 1`, and an `items` array. Start from [the bank template](../assets/question-bank.template.json) and see [study habits](study-habits.md) for how it is used.

| Field | Allowed values or meaning |
|---|---|
| `problem_id` | Nonempty identifier, unique within the bank |
| `provenance`, `source` | As for a session event |
| `concepts` | Array of nonempty strings; may be empty |
| `exposure` | `unseen`, `exposed`, `attempted`, `worked`; an item with attempts is `attempted` or `worked` |
| `protected` | Boolean; true reserves a paper for a fresh timed attempt |
| `attempts` | Array in date order; each has `date`, `outcome` (`incorrect`, `partial`, `correct`), `assistance`, and `recall` |
| `recall` | The learner's own rating `again`, `hard`, `good`, `easy`, or null when not asked |
| `next_review` | `YYYY-MM-DD` not before the latest attempt, or null |

Two optional attempt fields serve essay subjects and cross-subject work ([across fields](fields.md)). `band` holds a nonempty `estimate`, a nonempty `descriptor_source` naming the marking criteria, and an optional short `quoted` descriptor. Validation checks that the locator is present. Verify the actual criteria before estimating a band.

For a first essay submission, identify an assessable target in the criteria, such as weighing a particular objection. Use `correct`, `partial`, or `incorrect` for the observed extent to which the paragraph demonstrates that target. Keep the overall band estimate in `band`. If a fair target has yet to be established, record qualitative feedback in the authorized journal and defer the bank outcome. An actual submission counts as attempted. On a retry, the agreed repair can serve as the assessable target. The optional `bridge` records the learner's words naming a move they have used before. It supplies context for a later transfer check.

A protected item must be `unseen`, with no attempts and no review date. The validator cannot tell whether a rating was really the learner's or whether a review date is wise.

## Visual evidence schema, version 1

Use `kind: "visual-evidence"`, `schema_version: 1`, `source` with verified title/creator/HTTP(S) URL, timezone-aware `captured_at`, `visual_status: "complete"` or `"incomplete"`, `frames`, and string arrays `observations`, `transcript_claims`, `interpretations`.

Each frame has a contained relative `file`, finite nonnegative `timestamp_seconds`, `visible_timestamp` text, and Boolean `inspected`. The path must exist beneath the record directory. Complete records need nonempty frames all marked inspected. Empty-frame records must remain incomplete. A string containing a timestamp or a checkmark is not evidence that a frame was actually viewed.

Optional `motion_claim` has `basis: "ordered-frames"` or `"playback"`, plus an `evidence` description. Ordered frames need at least two inspected frames at strictly increasing times. The validator cannot verify a playback assertion, image authenticity, or that different files actually show different frames. Keep the evidence trail and inspect it.

JSON duplicate keys, NaN/infinity, numbers disguised as booleans, malformed types, and escaping file paths are rejected. Accepted capture/end-point timestamps use `YYYY-MM-DDTHH:MM:SS`, optional fractional seconds, and `Z` or a numeric timezone offset.
