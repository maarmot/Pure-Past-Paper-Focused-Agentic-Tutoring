# Remediation follow-up

Read the [release report](../README.md) for results and the primary comparison. This round keeps the original criteria and replies intact. The source owner saw the first-round findings before editing the hint and correction guidance. Four new synthetic prompts and the [scoring plan](protocol.json) were frozen before that edit. Their [freeze hashes](freeze.json) and independent per-case permuted [version keys](key.json) can be checked locally. The initial candidate was not run on the new four-case set.

The baseline and final skill each received two fresh contexts for the four transfer cases. Two more final-skill contexts replayed all twelve original cases. The final development control used one fresh context. The generation wrapper, neutral read-only directory, host-default CLI and six preloaded source paths match the initial round. Six fresh grader contexts evaluated development, three replay groups, and two independent readings of the same complete masked transfer packet. The same concealed labels were used for both transfer graders; the key was not supplied to either. See [packets](packets), [complete replies](replies), [grade reasons](grades), [token and wall-time measurements](metrics), and the release [decoded summary](../summary.json).

| Fresh tutor run | Wall seconds | Input / output tokens |
|---|---:|---:|
| Baseline transfer 1 | 12.35 | 28,761 / 256 |
| Baseline transfer 2 | 15.80 | 28,761 / 339 |
| Final transfer 1 | 14.23 | 29,165 / 359 |
| Final transfer 2 | 17.99 | 29,165 / 452 |
| Final exposed replay 1 | 36.39 | 29,612 / 1,153 |
| Final exposed replay 2 | 37.70 | 29,612 / 1,276 |
| Final development | 6.96 | 29,034 / 117 |

Each count includes the host context and lab packet. Cash cost, controlled seeds and exact backend model ID were unavailable. The measurements do not estimate ordinary tutoring-turn latency.

From this directory `python -B check_followup.py` recomputes grades and differences against the unchanged original grades. To resample, keep fresh evaluation copies in the parent and child directory structure, preserving the completed primary replies and key in the parent. Use `python compare.py build REPO REVISION SPLIT ARM PACKET` for the baseline transfer and each final split, then the parent `run_context.py` to collect the seven replies (baseline-t1/t2 and final-t1/t2/h1/h2/d1) in this directory's replies folder. In a new copy without an existing follow-up key or grades, `python compare.py mask` constructs six masked packets. Run `python compare.py grade JOB NEUTRAL_DIR` for transfer, second, replay1, replay2, replay3 and development. Save both grades before unmasking the paired results. The same four gates cannot stay held out against changes made in response to these published results.
