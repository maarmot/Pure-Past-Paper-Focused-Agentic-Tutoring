# Delegation by job

Read this before splitting work among workers. A worker is any separate context the host provides: a subagent, a parallel task, or a fresh session. These are jobs, not registered agent names, and they read the same in any host.

Most of what this skill does is conversation and needs no worker. A hint, a diagnosis, a requested solution, a critique of an essay or argument, and reading alongside the learner are all answered directly. A requested solution or hint is never held back for a checker.

## Rules for every job

- The learner's turn is never delegated. Reading an attempt, choosing the help, and speaking to the learner stay with the main agent.
- No worker writes, guesses, or simulates a learner's attempt, prediction, or answer, and nothing a worker produces is evidence about the learner.
- The main agent writes the specification and the expected results before any build starts, including one case that would expose a tempting wrong model. A builder and a checker who share a wrong specification will agree with each other.
- Give an independent solver the question, assumptions, and units so they can derive a reference. Give an artifact reviewer the built output and its requirements. Compare their observations with the reference after each has reported.
- Each worker gets a bounded question, the files it may read, its own files or directory to write, and a named deliverable. No two writers share a file.
- Only the main agent writes the journal, question bank, session records, and roadmap, and only where the project authorizes them.
- Name the off-limits paths in every brief: reserved papers and their solutions above all. Where the host cannot restrict a worker's access, "not given" only means "not briefed"; say so in the verification record.
- A finder returns a location and a short locating phrase. The main agent opens the source before citing it. A reader of a book or transcript returns paraphrase with locations, not extracts.
- Ask each worker to mark every claim as read, run, or recalled.
- Decide the stop condition before starting. Choose a repair or recheck when an observed defect warrants it. Identify unresolved defects explicitly in the delivery.
- The main agent settles disagreements against a source or a run, never by counting votes. Agreement among workers that share a model is weak evidence.

If the host has no workers, derive the expected results first, before building, then build and compare, and say that independent review was lost.

## Jobs

| Job | Workers | Order | Each is not given | Stop when |
|---|---|---|---|---|
| Past-paper sourcing | Finder; verifier | Finders in parallel by source; verifier after | Verifier: the finder's verdict that a question is genuine or in scope. It gets the document, the location, and the scope source | Each question has an exact source and a scope match, or is labelled unverified or generated |
| Interactive page | Builder; value checker; reviewer who operates the page | Builder and value checker in parallel; reviewer after | Value checker: the page code. Reviewer: the list of expected values | Drawn values match the independent values; controls, keyboard, and reset are exercised or listed as not run |
| Narrated video | Scene builder; value checker; reviewer who watches the result | Draft beats and independent values, record or measure narration, align final motion and captions to speech, then review the joined export | Value checker: the scene code. Reviewer: the script; it reports what it sees and hears and the main agent compares | Stills, decode, and caption checks pass; a listen-through is done or recorded as not done |
| Study PDF | Compiler; solution checker; page inspector | Checker alongside compiler; inspector after | Checker: the solutions file | Every page inspected; each answer matches an independent derivation or is flagged |
| Reading or video companion, prepared ahead | Optional source reader who lists claims with locations | Before the session only | Source reader: the learner's notes and answers | Each listed claim has a location the main agent spot-checked |
| Multi-week roadmap | Scope researchers; the main agent drafts | Researchers in parallel by source | Researchers: the learner's records | Each checkpoint cites a scope source and shows its evidence state, including untested |

Many workers cannot hear audio or see motion. A check a worker could not perform stays "not run"; it does not become "passed" because nobody objected.

## Reporting

Put the delegation details in the verification record. In the reply to the learner, one line is enough: what was checked independently, and what was not.

No measurement shows that delegating improves anything this skill produces. These are working rules, chosen to keep a check independent of the thing it checks.
