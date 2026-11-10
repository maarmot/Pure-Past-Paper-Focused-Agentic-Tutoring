# Five PDF purposes

Choose the document's job before drafting. These are editable starter templates, not completed course notes or permission to bring material into an exam. Replace their fields using the actual course instructions and current problem sources.

| Purpose and source template | Include | Omit | Verify |
|---|---|---|---|
| [Exam/reference sheet](../assets/latex/reference-sheet.tex) | Conditions beside formulas, defined symbols, decision cues, compact error reminders | Long exposition, unconfirmed topics, unauthorized worked examples | Allowed content, page limit, page size, minimum readable size, every formula and domain |
| [Topic overview](../assets/latex/topic-overview.tex) | Target capability, prerequisite links, concept relationships, one worked connection, retrieval prompt | Encyclopedic coverage or disconnected formula lists | Consistent notation, complete assumptions, relation between picture and algebra |
| [Exploratory research brief](../assets/latex/research-brief.tex) | Question, scope, primary evidence, disagreements, claim confidence, discriminating next test | Unsupported conclusions or a bibliography without claim links | Exact sources, dates/versions, units and comparability, contradictory evidence |
| [Curiosity-driven concept review](../assets/latex/concept-review.tex) | Motivating question, useful model, thought experiment, prediction, failure of an analogy | Forced exam framing, invented applicability, unexplained jargon | Assumptions, boundary case, what is exact versus an analogy |
| [Practice set/mock exam](../assets/latex/practice-set.tex) | Scope, source labels, time/marks if known or explicitly estimated, space to work, separate answer key | Answers on question pages, protected fresh questions, invented institutional provenance | Solvability, independent answer derivation, wording, allocated marks/time, source permissions |

The shared style is [ppp-common.tex](../assets/latex/ppp-common.tex). Keep it beside each template. The templates use ordinary LaTeX with `amsmath`, `amssymb`, `geometry`, `xcolor`, and `hyperref`; no shell escape is needed.

## Author and verify

1. Record the purpose, audience, course/textbook edition, permitted coverage, and requested page limit. Unknown exam permissions remain unknown; label a study reference as such.
2. Write the mathematical content and independent expected answers first. Keep questions, hints if any, and solutions in different files. A generated question must say so on its question page.
3. Draw exact figures using TikZ, PGFPlots, Matplotlib, or Manim. Match axes, units, constraints, and values to the derivation. Use labels as well as colors.
4. Compile with the available supported compiler. Use the LaTeX compile skill if present, or `tectonic --outdir <build> <file.tex>` / `latexmk -pdf -interaction=nonstopmode -halt-on-error <file.tex>` after verifying those tools. Keep packages isolated where feasible; don't assume an install on another machine.
5. Inspect compiler diagnostics for missing references, missing symbols, and overfull boxes. Open every rendered page image, checking clipping, formulas, spacing, figure labels, and page numbering. Text extraction is a separate check, not visual inspection.
6. Recompile and inspect changed pages after fixing a defect. Check question and solution outputs independently for spoilers and matching identifiers.

For reproducibility retain the `.tex` sources, figures, compiler/version, command, logs, generated PDFs, page images, and verification record. If a compiler is unavailable, deliver the source and say it is uncompiled. If pages were not opened, say visual QA remains unrun. Never call a template an exam-approved sheet.
