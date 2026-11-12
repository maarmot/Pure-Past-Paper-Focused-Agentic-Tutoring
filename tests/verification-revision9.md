# Revision 9 release verification

## Starting state

The prior chat ended at revision 8 on 12 November 2026. Re-inspection found its release commit on the local `roadmap-evidence-studio` branch with a clean index and no untracked files. The remote advertised only `main`, at the revision 7 commit. The local topic branch was one commit ahead of it. The publication checkout's *local* `main` was older (`20b6f9b`). The release used the actual advertised remote and full commit identities throughout.

| Baseline | GitHub and normal host install, revision 7 | Local release, revision 8 |
|---|---:|---:|
| Commit | `1bc3ccf735c440116bb97cc875940630f61828da` | `364188ab9a20d9e53e469b1dfef32b04c3eaf6db` |
| Git tree | `5c214d07a071603d0644de33dc4041f304786707` | `87b6c5587c768918e8a9dc8520cefccf9a1e4a24` |
| Entry SHA-256 | `52fa32d1a067dd7f0813491976604a23691316887e1f28f238c1fde09a80fe39` | `51e0f14554d22b9e07a4d6ed32e5d56a156de518d34e758298579be3e170d242` |
| Entry size, bytes / whitespace-delimited words | 5,079 / 744 | 5,197 / 756 |
| Runtime, files / bytes | 41 / 231,674 | 47 / 253,668 |
| Routed Markdown references, count / bytes | 15 / 126,984 | 16 / 136,638 |
| Entire tracked tree, files / blob bytes | 225 / 2,712,053 | 331 / 3,602,475 |

Fresh Codex `skills/list` on the intended host reported a single enabled user-scope copy and a disabled project compatibility copy. The host's existing sync command verified all 225 tracked blobs in *each* checkout at revision 7. The old compact revision 8 install was isolated. The revision 8 ZIP SHA-256 was `93183a0c9553759e86ae674d6efd9ebe53fe4f58f029c691d07587356d3a4b8c` (111,810 bytes). A live REA archive inspection recognized its ZIP format and root hash. Archive inventory supplies static evidence. The packager's member-to-Git comparison and execution from the installed files test different properties.

Fieldnotes returned HTTP 200 on the existing loopback origin. Opt-in data belongs to that origin and browser profile. All test writes used disposable browser contexts and synthetic inputs. Baseline reruns passed 76 Python tests and 17 JavaScript model tests. The revision 8 comparisons tied the older tutor on the held-out cases. [Revision 8 results](behaviour/results/2026-11-12/revision8/README.md)

## Acceptance and method

- Freeze unseen cases and criteria before changing teaching instructions. Compare each incremental change against the last retained version. Preserve rejected candidates and judge disagreements. Validate live discovery separately from explicit source-packet behavior.
- Solve the three learner sheets and their three transfer tasks independently. Recalculate from printed inputs using a separate computational approach. Include a deliberately wrong method or implementation capable of failing. Keep learner sheets free of answers. [Checks and assumptions](../assets/challenges/technical-practice/verification.md)
- Correcting a recorded attempt must preserve observations, dates and exposure while withdrawing delayed checks whose links became invalid. A newly selected invalid link must fail. The prepared prompt must distinguish the original date from the correction, carry the source category and any recorded independence veto, and exclude raw locators.
- A fresh install must select one enabled copy in the intended project, read the release skill during a real invocation, reproduce the offline exercise, and agree with the committed package. Release via ordinary fast-forward only after local checks and independent review.

## Exercising the changes

The revision 8 model failed both new tests before implementation. Redating the earlier attempt beyond one of its later checks raised a validation error and rejected the entire correction. The prepared prompt returned no provenance even though the underlying event had a source category. The revised model retains both observations, removes only invalidated links and carries provenance, correction date and any explicit independence flag into session preparation. Earlier evidence about familiarity survives a date change. A rejected fresh link leaves the original state intact.

The reference calculations cover a kink and feasibility boundaries in calculus, per-edge conservation and wraparound in a streamed digital interface, and shared projection constraints in a three-camera depth estimate. The release integrator solved the six prompts without inspecting the keys. Computational checks complement the written proofs. None of the examples has been calibrated against an instructor's exam or tried on a physical device.

[Research and later human trial](../docs/research-revision9.md) · [Fieldnotes storage and browser checks](../docs/roadmap-guide.md)

## Results on the integrated worktree

The normal runtime has 59 files and 280,893 uncompressed bytes, including all 12 new learner and examiner sheets. Its entry is 759 whitespace-delimited words (5,225 bytes). Sixteen routed Markdown references occupy 137,133 bytes. The runtime added no library requirements. The full Git tree additionally carries tests, screenshots, historical evidence and source. A Git installer copies that full tree; the ZIP contains the manifest only. Fieldnotes uses browser APIs and a static file server. Playwright and axe-core are pinned development dependencies.

| Check | Observed result |
|---|---|
| Three teaching trials | Goal-setting tied at 6/0/0 full/partial/fail per arm. The diagnostic variant changed 4/2/0 to 5/0/1. The feasibility variant tied at 6/0/0. None cleared its frozen gate. The final release tied revision 8 at 4/0/0 on three control scenarios. Two masked graders agreed on 44/44 repeated criterion ratings. See [cases, disagreements, rejected deltas and cost](behaviour/results/2026-11-12/revision9/README.md). |
| Additional release conversations | All five open scenarios passed their prespecified criteria in review of seven tutor turns, including a full-solution override, an injected demand inside a lab note, and a fresh problem from a corrected handoff. These used no model tools. [Replies and checks](behaviour/results/2026-11-12/revision9-smoke/README.md) |
| Local software | 85 top-level Python tests passed on 3.9.7 and 3.12.13. Both also passed 24 command-level checks spanning historic evidence and its negative suites, Manim model arithmetic, the CLI audit and template acceptance/rejection. The nine new exercise tests include deliberate corrupted keys. Twenty JavaScript model tests passed. |
| Correction and persistence | An independent browser reproduction found that editing just the date could strip embedded newlines from an imported source or problem ID. Saving an unchanged form could also invent a new correction date. The fixed form updates only changed fields and the model recognizes a no-op. Exported text retains original line endings and omitted optional fields. The retrieval menu recomputes eligible prior attempts when the date changes. |
| Explicit withdrawal | A pre-existing test expected an explicit negative independence flag to disappear when recorded help changed to none. The browser actually offered to *keep* that flag. An independent reviewer reproduced the resulting false transfer credit. The revised test requires the veto to persist through that edit and checks that an explicit withdrawal reopens eligible gates. A fresh browser run verified both operations. |
| Browser | Edge 157 passed at 320×740, 736×414 and 1360×930 with dark and light surroundings. The suite exercises keyboard controls, axe, isolated saves, offline reload, conflict and corrupt-data recovery, import/export and the editable prompt. Its monitored walkthrough reported zero uncaught page errors and zero off-origin requests. Human screen-reader use remains open. |
| Live host at baseline | A fresh normal CLI chat selected the enabled revision 7 installation and correctly reported that it lacked the requested bundled FPGA exercise. Exact post-install hashes and invocation are host-specific delivery receipts. |

The beginner circuit, calculus, hardware and imaging problems use stated idealizations. No student has completed the new tasks as part of this release. No inference about this learner's proficiency, retention, transfer, or the optimal intensity of the next session follows from the software and transcript counts.
