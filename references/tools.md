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

A protected item must be `unseen`, with no attempts and no review date. The validator cannot tell whether a rating was really the learner's or whether a review date is wise.

## Visual evidence schema, version 1

Use `kind: "visual-evidence"`, `schema_version: 1`, `source` with verified title/creator/HTTP(S) URL, timezone-aware `captured_at`, `visual_status: "complete"` or `"incomplete"`, `frames`, and string arrays `observations`, `transcript_claims`, `interpretations`.

Each frame has a contained relative `file`, finite nonnegative `timestamp_seconds`, `visible_timestamp` text, and Boolean `inspected`. The path must exist beneath the record directory. Complete records need nonempty frames all marked inspected. Empty-frame records must remain incomplete. A string containing a timestamp or a checkmark is not evidence that a frame was actually viewed.

Optional `motion_claim` has `basis: "ordered-frames"` or `"playback"`, plus an `evidence` description. Ordered frames need at least two inspected frames at strictly increasing times. The validator cannot verify a playback assertion, image authenticity, or that different files actually show different frames. Keep the evidence trail and inspect it.

JSON duplicate keys, NaN/infinity, numbers disguised as booleans, malformed types, and escaping file paths are rejected. Accepted capture/end-point timestamps use `YYYY-MM-DDTHH:MM:SS`, optional fractional seconds, and `Z` or a numeric timezone offset.
