# Use the local roadmap

From the repository root, run the following command and open [Fieldnotes](http://127.0.0.1:4173/) in a modern browser. Keep the command running while using the site. Ctrl+C stops the server. Python serves only the static `roadmap` directory on the loopback interface. The compact tutor ZIP is a separate deliverable.

```sh
python -m http.server 4173 --bind 127.0.0.1 --directory roadmap
```

## From a goal to an observation

1. Choose **Set study goal**. For example, you might want to distinguish two candidate motions from a camera trace using only a pencil. The graph starts without a goal or any learner observations. You can explore before picking one.
2. Select **Aliasing**. Its prerequisites are discrete sequences and periodicity. The figure above the map shows two different cosine signals that coincide at each marked sampling instant. A unit circle's horizontal coordinate follows a cosine. The challenges also consider what is gained by measuring its vertical coordinate.
3. Use **Prepare a session** to choose **Grill me**, **Generate a hard exam**, **Explore why**, or **Prepare my next session**. Read and edit the local template, copy it, and paste it into a chat with PPP when ready. Receiving a challenge creates no evidence. An edited prompt stays inside that dialog until you copy or close it.
4. Choose **Record attempt** for a real observation. Identify the problem, source, work, help and result. A learner report and an inspected solution carry different attribution. **Evidence by capability** shows which conclusions the observations can support. When outcomes conflict, try a short diagnostic.
5. To plan a later check, use **Edit review date or open question**. The date appears in the notebook. To revisit a study decision, use **Correct** or **Delete** on the observation. If a date or outcome correction invalidates an existing delayed-check link, both observations remain and the recommendation updates. Prepare a new prompt to send the corrected evidence to a tutor.
6. Choose **My data → Save on this device** if you want refresh persistence. The browser holds the roadmap in local storage for its exact origin. Reopen the same hostname and port with the same profile. Private browsing, clearing site data, using another computer, or changing ports can make a stored copy unavailable. Keep a JSON export for longer-term continuity.

The graph supports dragging its background, arrow-key panning when focused, zoom buttons, Ctrl/Command–wheel zoom and **Recenter**. The list exposes the same skills and prerequisite names. Narrow screens start in list view. Selected work is available in either view. Native dialogs accept Tab, Shift+Tab and Escape.

[Desktop screenshot](roadmap-preview/desktop.png) · [Mobile screenshot](roadmap-preview/mobile.png)

## Data and recovery

- **Export roadmap** downloads the graph, goals, evidence, questions and review dates. Import previews the topic and counts before replacing the current roadmap. The app rejects an invalid snapshot as a whole. The file limit is 2 MiB.
- **Export PPP session** downloads one selected observation in the existing session format. Use the Python bridge to bring one authorized session event into a graph. Existing Markdown roadmaps remain independently authored documents. Use the format guide for exact fields, conflict resolution and migration. [Exchange guide](../roadmap/FORMAT.md)
- After a successful first online load, a service worker caches the application shell. The browser tests exercise a later offline reload. The first visit still requires a functioning local server. Offline status describes browser connectivity. The application has no model backend.
- If another tab changes the stored copy or a write fails, your current work stays in memory. Export it before closing. **Recover original file** preserves bytes from unreadable storage. You can then reload the other copy or explicitly replace it with the displayed one. Browser storage errors can prevent local saves. A downloaded snapshot remains usable on another origin or browser.
- **Erase local roadmap** clears this application's learner-data key at the current origin. Downloaded backups, source sessions and tutor chats have their own deletion controls. Keep personal files outside public source control. The app's service worker caches public UI files only.
- To use a different curriculum, export a snapshot, define the new skills and prerequisite IDs in that format, and import the validated file. Remap evidence only when its source actually supports the new skill. The shipped curriculum covers one field.

## Repeat the checks

The site has no npm runtime dependency. For the development checks, use a current Node with `node:test` and the pinned development dependencies in `tests/browser`. Install them once, then run the tests with the local server above running in another terminal.

```sh
node --test tests/roadmap-model.test.mjs
python -B -m unittest discover -s tests -p "test_*.py"
npm ci --prefix tests/browser
node tests/browser/node_modules/playwright/cli.js install chromium
npm test --prefix tests/browser
```

Set `BROWSER_PATH` if testing an installed Chromium-family executable. Set `ROADMAP_EVIDENCE` to a new directory to save synthetic screenshots and a browser report. The original release evidence covers Edge, automated accessibility-tree and axe checks and keyboard interaction. A person using a screen reader should separately try setting a goal, finding a prerequisite, editing a saved attempt and restoring a backup. Record misannounced controls, missing context, unexpected focus movement and task completion.

## Real learner evaluation

Agree on one goal and permitted aids first. Use a short unassisted baseline on a new problem and score reasoning, assumptions and verification separately. Try a grill session and record the first unsupported step and exact assistance. Reserve a different problem for an unaided session on a later day (for instance, three to seven days later if the learner agrees). Freeze the two keys and partial-credit rules beforehand, mark the delayed work without seeing which tutoring condition preceded it, and retain the solution and elapsed time. For a comparison, alternate comparable topics or counterbalance different forms across learners. One person's successful retry can inform that person's next lesson. A causal claim about this release requires a design that controls topic difficulty, ordering, prior exposure and extra study.

[Design and acceptance criteria](roadmap-design.md) · [Behavioral comparisons](../tests/behaviour/results/2026-11-12/revision8/README.md)
