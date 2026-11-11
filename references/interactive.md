# Interactive builds

Use this when the learner should change something and see the consequence: compare cases, test a conjecture, or find where an intuition breaks. It needs only a browser, so it is the route that works when Manim or LaTeX is not installed. Read [visual inquiry](visual-inquiry.md) first to choose what the page is for.

## Start from the worked starter

Copy [the interactive starter](../assets/interactive.template.html) into the active project and edit the copy. It is a complete example (two motions that fit the same samples) so each pattern can be seen running. Never edit or render into the skill's own `assets` folder.

Keep its five parts in this order:

1. **A pure model.** Functions from parameters to values, with no DOM access. Reject invalid input with an error; do not clamp it into a plausible answer.
2. **One state object** and a frozen starting state. Every control writes to it; reset restores the starting state exactly.
3. **A render function that reads only the state and the model.** This reduces inconsistent calculations, but the drawn marks, labels, and interpretation still need independent checks.
4. **Expected values derived by hand,** written into the page as literals, from a derivation that does not call the model.
5. **A self-check that reads the drawn marks,** not just the model's return values. A correct formula cannot rescue a marker drawn in the wrong place.

The supplied starter is one file with no network requests, build step, or external framework. It can be opened from disk in a compatible browser. Future browser compatibility has not been established.

## Design the controls

Name each control by its effect in the situation ("Camera rate"), not by the variable. Say on the page what stays fixed. A control must never quietly change the thing being measured: in the starter, the two candidate frequencies are constants that no control touches, because letting the fast frequency follow the camera rate would make the samples agree at every setting and answer a different question.

Order the page the way a reply is ordered: the reference state and the question first, then the control that matters, then a case where the picture fails, with the derivation and check values in a closed layer at the end.

Offer one meaningful change at a time. Separate changing the system, changing the instrument, changing a model assumption, and changing only the view. Put the prediction prompt above the controls and keep the reveal off at the start; the reveal is a checkbox the learner can turn back off. Put the algebra in a closed disclosure the learner opens when they want it.

State the interpretation in a sentence that updates with the state, and bound the claim in that sentence ("separates these two candidates, and only these two").

## Check before handing it over

Open the page and run the self-check; `window.__selfCheck.ok` must be true and every line must read `pass`. Then, in the actual page:

- Move each control to both ends and to a case from the expected-value list. Compare the drawn result with the hand derivation.
- Reset, and confirm every control and the reveal return to the documented start.
- Operate everything with the keyboard alone and confirm the focus ring is visible.
- Check a narrow width near 320 px and a desktop width for clipping and sideways scrolling, in light and dark schemes.
- Break one thing in a scratch copy (for example, tie a fixed quantity to a control) and confirm the self-check fails. A check that cannot fail tells you nothing.

Report which of these you ran and which you did not. The page being correct says nothing about the learner; only their own prediction or explanation does.

## Hand it over without a toll

Build the page when the learner asks to see the idea; do not wait for a prediction before building. The prediction prompt belongs on the page, above the controls, with the reveal off, so the learner can answer it, ignore it, or go straight to the controls. In the same reply, give a few lines or a small table that show the effect immediately, in case they cannot open the file yet.

A page is a working artifact, not a learner record. Save it where the project keeps its outputs. If the project's instructions limit where you may write, use the permitted location and say where it went; a restriction on records is a reason to choose the folder carefully, not a reason to withhold the page.

Colors need a second cue: the starter pairs each color with a marker shape and a line style. Any motion should respect `prefers-reduced-motion`; the starter has no autoplay, which is the simplest way to comply. For published or shared pages, follow the host's own rules for scripts and storage.
