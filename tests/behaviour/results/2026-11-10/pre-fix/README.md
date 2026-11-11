# Recovered comparison of tutor replies

The files in `cases/` contain the synthetic learner message, scenario-specific rubric, anonymized reply texts, word counts, grader's criterion-level judgments and reasons, and the subsequently decoded version and sample key. The comparison covers **the original revision 5 draft before release fixes** and revision 4 (`f4e8c31`). Scores describe those specific tutor replies to hypothetical learners.

| Original grades recovered | PASS | PARTIAL | FAIL |
|---|---:|---:|---:|
| Revision 4 | 146 | 32 | 2 |
| Pre-fix revision 5 | 159 | 17 | 4 |

There are 14 graded first-turn scenarios, two tutor replies per version per scenario, and 180 rubric decisions per version. Several criteria apply to the same reply. The 180 decisions cannot be treated as independent observations. The counts include the original evaluators' judgments, including their use of approximate length limits.

The largest difference in the essay-plan case E05 was 14 passes for the draft versus nine passes and five partial ratings for revision 4. On E07, both draft argument replies exceeded the length criterion and ended with multiple questions, earning two failures. On E11, one 657-word production reply failed the length criterion. On E04, one draft reply rechecked only the failing binary-search input. Detailed examples, including E03's reversibility qualification and its unsupported prediction about marks, are in the case files. Four scenarios had worse rubric profiles for the draft (E03, E04, E07, E11), seven had better profiles (E01, E02, E05, E08, E10, E13, E15), and three had identical counts (E06, E09, E12). Here “better” means at least as many passes, no more failures, and a strict change on at least one of those two counts.

## How the transcripts were paired

The workflow generated two samples for each of two versions and permuted their four positions before grading. The raw tutor result carries a version, sample and journal event; the blind grader supplies only W, X, Y or Z. For each grader, reconstruction uses tutor results completed before that grading request and the workflow's fixed position permutation. Where the workflow later completed another grade for the same scenario (E01), only the latest complete grade and the four new tutor calls that followed the previous grade were used. Every selected cell had exactly one candidate result in its batch.

For example, E04's W was the draft's second sample. Its result was recorded at event 46, grading started at event 158, and the grade returned at 173. A later reply with the same tutor label arrived at event 242. Pairing that later reply with the earlier grade would misattribute the evidence. The per-case `lineage` and `key` preserve the relevant event line numbers without private paths or worker identities. The tutor was prompted with a synthetic read-only project; the actions claimed outside the reply were not supplied to the grader and are excluded from these transcript files.

The original workflow produced no completed grades for E14, T1, T2, or T3. The journal had all four E14 first replies and all 12 first replies for the two-turn cases, but no completed second replies. No grade for those four scenarios is included in the totals above. A subsequent completion or regrade requires a separately labeled cohort. No final post-fix behavior claim follows from these historical grades.

## Rubric limitations

E02's specified 2.4-ohm Thevenin result assumes the 6-ohm resistor remains inside the measured two-terminal network. If the 6-ohm resistor is the external load that is disconnected, the Thevenin resistance of the remaining source network is 4 ohms. T3 has the same ambiguity. The original criterion and grades are preserved for inspection; an answer explaining the two interpretations is mathematically sound. A span-to-depth ratio in the beam scenarios is a screening estimate; adequacy also depends on material, loading, and allowable approximation error.

The original grader was blind to version labels. One grader handled each available scenario, and tutors and graders came from a related model family. The original record does not establish blindness to clues within response style or independent human scoring. This comparison measures neither student learning nor host skill-selection rates.

Run `python -B check_results.py` in this folder to reproduce the counts and check the four reply slots, sample keys, rubric coverage and reported tallies. `coverage.json` contains per-scenario counts and missingness.
