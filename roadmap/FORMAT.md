# Roadmap exchange v1

A roadmap snapshot contains a goal, a prerequisite graph and observations. The browser can open or export a complete snapshot. PPP also exchanges one observation at a time with its existing v1 session files. Files exchanged this way are copies. A correction in one location cannot change a downloaded file, another browser profile or a private source session.

## Use existing records

1. Choose an authorized private session and the **one observed event** you want to carry into the roadmap. Check its original date, source, actual help and identity. Identify the destination skill from the roadmap. The browser opens a file chosen by the user. It never scans a project directory.
2. In the skill checkout or installation, run the bridge with a new output path in your private directory. Event numbering starts at 1. The example uses illustrative paths and IDs.

   ```sh
   python scripts/export_roadmap_event.py private/session.json --event 1 --skill aliasing --output private/one-observation.json
   ```

   If an older event has no `attempt_id`, supply a stable `--id` after checking which attempt the record describes. Reuse that ID for a retry of the **export**. Give a new learner attempt its own ID. An optional `--session-ref` adds a source label you choose. The bridge never inserts the input pathname. It keeps the selected event's original `source` locator, which may itself contain private information. Inspect the output before sharing it. The bridge checks the entire session with the existing PPP validator, selects the one event and writes complete bytes to a new destination. Other events, goals, tutor notes and timing stay in the source.
3. Open **My data**, choose the evidence file and confirm the addition. The target skill must exist. When the event names an earlier attempt for a delayed check, import the earlier event first. A duplicate or conflicting attempt ID stops the addition. Use **Correct** for an established correction after identifying the authoritative record. The correction date is distinct from the event date.
4. To take an event back to PPP, choose **Export PPP session** on its row. The export has one event, the original event day and unknown duration. It labels the goal and next step as current roadmap context at export time. Check it with `python scripts/ppp_tools.py validate-record private/ppp-session.json`. Keep this derivative separate from a multi-event source session. Use the full roadmap export for a backup of all nodes, goals and evidence.

The Markdown roadmap remains the authored plan for scope, references, protected papers and checkpoints. To add graph structure, choose stable IDs for selected Markdown rows and enter their actual dependencies in an exported snapshot. Review cross-references before importing. A checked box in Markdown, a resource visit, a journal narrative, a question-bank row or a reminder date creates no event. Carry dated observations through the bridge or record a described attempt explicitly. Keep an opaque attempt ID with any derived claim in an authorized Markdown file. Existing Markdown and banks are never rewritten automatically.

On a correction or deletion, identify the authoritative session and each derived copy the learner authorized you to maintain. Update those files explicitly. In the browser, **Delete** removes one attempt and clears later links to it. Other observations survive. The view recomputes evidence using the remaining records. **Erase local roadmap** clears the current roadmap and its saved entry for this browser address. Exports, private source sessions, clipboard contents, chat history and other devices have their own lifecycles.

## Snapshot and envelope

The snapshot has `kind: "roadmap"`, integer `schema_version: 1`, `field` and `topic` strings, one `goal` object, a nonempty `skills` array and an `evidence` array. The installed skill can read or edit an explicitly authorized export as plain JSON. Use a private working copy and run the validator before replacing any saved copy.

| Object | Fields |
| --- | --- |
| Goal | `capability`, `context`, `aids`, `timebox`, `intensity` and `success` are strings. Empty text preserves an unknown. Optional `deadline` is a calendar date. |
| Skill | `id`, `title`, `description`, `challenge`, and `prerequisites` containing skill IDs. Optional `open_question` and `review_date`. Skill IDs begin with an ASCII letter or digit. Remaining characters may also include periods, hyphens, colons and underscores. |
| Evidence | `attempt_id`, `skill_id`, `date`, `problem_id` and one PPP observation's `provenance`, `source`, `assistance`, `outcome`, `evidence`, `attribution`, `response_basis` and boolean `transfer`. Preserve the stable problem ID for the same problem throughout the map. Keep an existing `independent_success` flag when present. |
| Evidence details | Optional `activity` is `solve`, `explain` or `unspecified`. Optional `confidence` is `low`, `medium`, `high` or `unknown`. Optional `uncertainty` is explanatory text. Optional `session_ref` is a user-selected source label. `corrected_on` stores the correction day. `retrieval_from` names a prior attempted observation on the same skill. Boolean `previously_seen` records known exposure to this exact problem before the selected observation. |
| Single-event envelope | `{"kind":"roadmap-evidence","schema_version":1,"event":{...}}`. This imports one observation into the existing map. A full snapshot replaces the map after validation and confirmation. |

`source` may be null for generated work. Past-paper and source-adapted work require a locator. Dates use valid `YYYY-MM-DD` values. Optional skill or goal dates may be empty or null. Attempt dates cannot be in the future according to the device's local date. Unknown assistance stays `unknown`. The source validator accepts some older independent-success declarations with a missing response basis. Import preserves that declaration, sets the basis to `unknown` and leaves the evidence gates open.

The browser rejects unsupported schemas or fields, malformed JSON, repeated JSON keys, duplicate IDs, invalid dates, dangling prerequisites, dependency cycles, unknown skill links and broken retrieval references. It accepts up to 200 skills, 5,000 events and a 2 MiB pretty-printed UTF-8 backup, including its final newline. Skill IDs have a 96-character limit and attempt IDs a 240-character limit. The current version has no automatic transform for an unknown future schema. Preserve the original file. Migrate through an explicit converter for that version when one exists. The established migration today is the opt-in bridge from a v1 PPP **session event** into a v1 roadmap. Legacy text or an unknown activity never supplies a missing evidence gate.

Validate a snapshot locally with the same model the browser uses. This example prints only a success message for a valid file.

```sh
node --input-type=module -e "import {readFileSync} from 'node:fs'; import {parseRoadmap} from './roadmap/model.mjs'; parseRoadmap(readFileSync(process.argv[1], 'utf8')); console.log('Valid roadmap')" private/roadmap.json
```

## What the labels mean

An evidence gate requires an explicit activity, a correct outcome, unaided observed work and a reasoned response. An explicit negative independence flag withholds the gate. A report, agent inference, guess, recognition, assistance, an unspecified legacy activity or an unattempted item leaves the gate open. Confidence and review dates never strengthen an evidence claim. The validator can check these declarations for consistency. It cannot verify a person's identity, causal learning, actual aid use or whether their account is accurate.

Explanation describes a reasoned explanation. An unaided solution fills the solve gate. An unaided **solution** to a changed, previously unseen problem can also fill the transfer gate. Reusing an already recorded problem ID across the map marks the later item as familiar, including after a shown solution. A repeated problem cannot supply a fresh explanation, solve or transfer gate. Equal-day entries use their archive order to determine prior exposure. Choose separate problem IDs for genuinely different questions. Work encountered outside this local history needs accurate attribution and response-basis fields from the learner or tutor.

The bridge checks earlier problem IDs in the chosen source session before projecting one event. The browser keeps a familiarity flag on a surviving retry when the earlier event is removed, renamed or redated. This retains no deleted text, date, locator or ID. An explicit correction can withdraw `previously_seen` if the work was genuinely unseen and the remaining history agrees. An entire snapshot preserves the entered observation fields. A **single-event PPP export** of a familiar problem sets `independent_success` and `transfer` to false so readers of plain v1 session records cannot mistake it for a fresh achievement. If a familiar response qualifies as an explicitly linked cold check, the export adds `roadmap.retrieval_eligible: true`. The bridge checks the outcome, basis, help, attribution and extension before restoring that narrow eligibility. The destination still needs the linked earlier event. An original explicit negative independence claim does not gain this exception.

A delayed check needs an earlier attempted event in this skill, a later calendar day, a specific linked attempt and unaided observed reasoning on the new check. Link it only when the learner actually retrieved the work cold. A later date alone cannot fill the gate. A familiar task may support delayed retrieval without demonstrating novel transfer. After a correction, an old independence claim is withdrawn when the corrected observations contradict it. The model also accepts an explicit withdrawal of a disputed flag via `correctAttempt(..., {independent_success: null})`. Snapshot editors can remove that optional field after resolving the dispute.

The view preserves past evidence and shows mixed outcomes when a partial or incorrect response coexists with a contemporaneous or older supported result. The next action then calls for a diagnostic. A gap of more than 30 days since the last attempt displays a dated-evidence cue. That threshold is a display convention, with no measured forgetting rate behind it. A review date marks a planning choice and creates no reminder. An untested skill can suggest checking a prerequisite or starting directly.

The prompt builder reads this one goal, the selected skill, prerequisite statuses and at most three of its newest observations. It omits raw source locators, session references and observations on unrelated nodes. Imported strings remain quoted data. The user can inspect and edit the result before copying it to a chat. Treat sensitive problem names and observation text accordingly.
