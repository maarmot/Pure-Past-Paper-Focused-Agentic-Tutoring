# Study habits across sessions

Use this when the learner wants a routine: picking up where they left off, knowing what to review today, keeping a mistake log, or working toward a goal over weeks. A one-off question needs none of it.

These habits adapt ideas from DeepTutor, an open-source self-study system, to a skill that has no server, database, or background process. What was taken, what was changed, and what was left out is recorded in [provenance](provenance.md). Everything here is a plain file in the learner's project that any session can read.

Create these files only where the project authorizes learning records, and say which file you wrote. If the learner declines logging, keep the routine in the conversation and stop there.

## Three files

| File | Holds | Start from |
|---|---|---|
| Study journal | The mission, a handoff from each session, and confirmed learning records | [Journal template](../assets/study-journal.template.md) |
| Question bank | Every problem the learner has met: exposure, attempts, their own recall rating, next review date | [Bank template](../assets/question-bank.template.json) |
| Roadmap | The knowledge-point map and which evidence each point has | [Roadmap template](../assets/roadmap.template.md) and [roadmaps](roadmaps.md) |

The journal is for a person to read; the bank is for the tool to check; the roadmap changes slowly. Do not merge them.

## Open a session

1. Read the journal's mission and its most recent handoff. Treat the handoff as dated evidence about then, not proof of ability now.
2. List what is due: `python scripts/ppp_tools.py due <bank.json>` (see [tools](tools.md)).
3. Offer the learner a choice in one or two lines: the due reviews, the handoff's next step, or whatever they came with. Their choice wins. Due items are suggestions.

If there is no journal yet and the learner wants a routine, ask for the mission in their words (what they want to be able to do, by when, under what conditions) and create the journal with only that.

## Review a due item

Ask the question cold: no hint, no look at the previous attempt. This asks the learner to retrieve an answer rather than recognize a shown solution. Check the actual response before deciding what it supports.

After they respond, show the worked solution if they want it, then ask how it felt in their words and record their rating:

| Rating | The learner means | Suggested next look |
|---|---|---|
| again | Could not do it or needed the solution | 1 day |
| hard | Got there with real effort or a hint | 3 days |
| good | Solved it unaided, some effort | Roughly double the previous gap, starting at 7 days |
| easy | Immediate and unaided | Roughly triple the previous gap, starting at 14 days |

The rating is the learner's self-report, kept separate from the observed outcome and assistance. Where they disagree (rated easy, answered incorrectly), record both and let the outcome set the date. The intervals are a simple expanding schedule chosen for convenience, not an optimized algorithm; spacing reviews is well supported, these particular numbers are not. Adjust them to the exam date and the learner's week, and write the date they agree to.

Writing `next_review` schedules nothing. It is read the next time someone runs `due`. Create a reminder only if the learner asks and a supported scheduling tool exists.

After a correct, unaided review, the better next task is often a transfer problem on the same concept rather than the same question again. Add it to the bank as a new item.

## Keep the bank honest

- Add a problem when the learner first meets it. Exposure moves one way: unseen, exposed, attempted, worked. Once a solution has been shown, the item is worked for good, and a later correct answer may be memory.
- Record each attempt with its date, outcome, and the assistance given.
- Mark a paper reserved for a timed attempt as `protected`. The validator rejects a protected item that has been exposed, attempted, or scheduled, and `due` never lists one. Clear the flag only when the learner sits the paper.
- Run `validate-record` after editing. It checks consistency, not truth.

## Find weak areas

Look across the bank for a concept whose recent attempts are incorrect, assisted, or rated again or hard. Name the pattern as an observation ("three of four chain-rule items needed a hint") and propose one diagnostic problem. A weak area is a hypothesis about the work, not a label for the learner, and two items are not a trend.

## Gate mastery by kind of evidence

A single successful problem does not settle a knowledge point. Use these four kinds of evidence as a provisional review checklist, rather than certification of durable mastery:

1. **Explain** - states why the method works and the condition it needs, without the solution open.
2. **Solve unaided** - a correct solution with no assistance, from observed work.
3. **Transfer** - an unaided solution to a problem with a changed setup, representation, or method choice.
4. **Delayed retrieval** - any of the above again after a gap of days, not in the same sitting.

Leave a gate empty until the learner's own work fills it. Agent-written answers, recognition of a shown solution, and same-session repeats fill none of them. A point with three gates filled is "three of four", not "nearly mastered".

## Close a session

Write the handoff while the session is fresh: what was worked on, what the learner actually did, what stayed unresolved, and the one next step. Then update the bank's attempts and review dates, and move any gate the session's evidence supports. Add a line to the journal's confirmed records only for something the learner demonstrated; keep hopes and plans in the handoff.

Keep the close short. If the learner is leaving, a three-line handoff written now is worth more than a full review that never gets written.
