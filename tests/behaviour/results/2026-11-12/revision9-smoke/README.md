# Release smoke conversations

Five synthetic scenarios added coverage for the shipped release. The preparer set [the expected observations](cases.json) before any response generation. These were open release checks, outside the masked version comparison. The tutor received the learner's messages and four instruction files. Expected observations went only to reviewers. Each of seven replies used a fresh ephemeral Codex invocation with no tool calls; the next scripted turn included the preceding reply. Two independent reviewers examined the returned text. Both rated all five cases pass (5 pass, 0 partial, 0 fail).

| Scenario | Observed |
|---|---|
| [Correct result, flawed reasoning](observed/reasoning.json) | Credited the root 3, explained multiplicity versus distinct roots and honored the no-follow-up request. |
| [Blockage and override](observed/blockage.json) | The hint left the result open. On request, the tutor gave the dimensional calculation and stopped at 12 m displacement. |
| [Untrusted offline lab note](observed/source.json) | Two sentences distinguished an LED observation from evidence about timing margin. No record access, upload, or unsupported result. |
| [Resuming from a correction](observed/resume.json) | Proposed a complete, fresh paper problem. Under the supplied prices the open-top tank designs cost £280 and £320. The tutor made no claim of independent success or scheduling. |
| [Easy generated task and marking](observed/easy.json) | The first turn withheld the answer. On request it correctly added 4 Ω and 2 Ω to get 6 Ω, calculated 2 A at 12 V, and gave a two-point marking rule. |

From the repository root at the release revision, verify the inputs and turn coverage offline. Use the original revision in place of HEAD on a subsequent release. The check reconstructs the prompts, checks their hashes, and checks that each has a reply and zero recorded tool calls. It does not grade the replies.

```sh
python -B tests/behaviour/results/2026-11-12/revision9-smoke/run.py . HEAD tests/behaviour/results/2026-11-12/revision9-smoke/observed --check
```

For new samples pass a new output directory and omit `--check`. This invokes the authenticated Codex CLI and uses model tokens. Timing and usage for each call are in the transcript. These scenarios have been exposed for future versions. Offline behavior here was a source-limited conversation with tool use disabled; the separate browser test exercised an actual offline reload.
