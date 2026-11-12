// Start the documented localhost server first. PLAYWRIGHT_PATH and BROWSER_PATH are optional.
const assert = require("node:assert/strict");
const fs = require("node:fs/promises");
const path = require("node:path");
const { createRequire } = require("node:module");
const devRequire = createRequire(
  path.join(__dirname, "browser", "package.json"),
);
const { chromium } = process.env.PLAYWRIGHT_PATH
  ? require(process.env.PLAYWRIGHT_PATH)
  : devRequire("playwright");
const axeSource = devRequire("axe-core").source;
const url = process.env.ROADMAP_URL || "http://127.0.0.1:4173/";
const output = process.env.ROADMAP_EVIDENCE &&
  path.resolve(__dirname, "..", process.env.ROADMAP_EVIDENCE);
const button = (p, name) => p.getByRole("button", { name, exact: true });
const click = (p, name) => button(p, name).click();
const input = (p, label) => p.getByLabel(label, { exact: true });
const chooseFile = (p, obj) =>
  input(p, "Import a roadmap backup or one PPP evidence event").setInputFiles({
    name: "fixture.json",
    mimeType: "application/json",
    buffer: Buffer.from(JSON.stringify(obj)),
  });
async function artifact(page, name) {
  if (output)
    await page.screenshot({
      path: path.join(output, name),
      fullPage: true,
      animations: "disabled",
    });
}
async function checkImportedCorrections(browser, backup) {
  const page = await browser.newPage();
  const original = {
    skill_id: "aliasing", attempt_id: "first", date: "2020-05-02",
    problem_id: "Scope trace\r\npart A", provenance: "source-adapted",
    source: "Manual, ch. 1\r\nTable 2", evidence: "Compared edges.\r\nRechecked.",
    outcome: "partial", assistance: "hint", response_basis: "reasoned",
    attribution: "observed-work", transfer: false,
  };
  const later = {
    ...original, attempt_id: "later", problem_id: "Later trace", date: "2020-05-04",
    retrieval_from: "first",
  };
  const absent = {
    ...original, attempt_id: "absent", problem_id: "Skipped", date: "2020-05-01",
    outcome: "not-attempted",
  };
  const another = {
    ...original, attempt_id: "another", problem_id: "Another trace", date: "2020-05-06",
    corrected_on: "2020-05-07", outcome: "correct", activity: "solve",
    transfer: true, independent_success: false,
  };
  try {
    await page.goto(url);
    await click(page, "My data");
    await chooseFile(page, { ...backup, evidence: [original, later, absent, another] });
    await click(page, "Replace roadmap");
    const edit = (text) => click(page.locator(".row").filter({ hasText: text }), "Correct");
    const dateField = input(page, "Date");
    const sources = input(page, "Delayed check of earlier attempt");
    const listed = () => sources.locator("option").evaluateAll((options) => options.map((item) => item.value));

    await edit("Another trace");
    await click(page, "Apply correction");
    await edit("Later trace");
    const initially = await listed();
    await dateField.fill("2020-05-02");
    const sameDay = await listed();
    await dateField.fill("2020-05-07");
    const afterBoth = await listed();
    await sources.selectOption("another");
    await input(page, "Source or locator").fill("Revised manual\nAppendix A");
    await input(page, "What remains uncertain?").fill("Timing of the last edge");
    await click(page, "Apply correction");
    await edit("Scope trace");
    await dateField.fill("2020-05-03");
    await input(page, "Help used").selectOption("prompt");
    await click(page, "Apply correction");
    await click(page, "My data");
    const gotDownload = page.waitForEvent("download");
    await click(page, "Export roadmap");
    const saved = JSON.parse(await fs.readFile(await (await gotDownload).path(), "utf8"));
    const [corrected, changedLink, unchangedAbsent, unchangedOther] = saved.evidence;
    const { corrected_on, ...rest } = corrected;
    assert.match(corrected_on, /^\d{4}-\d{2}-\d{2}$/);
    assert.deepEqual(
      { corrected: rest, initially, sameDay, afterBoth },
      {
        corrected: { ...original, date: "2020-05-03", assistance: "prompt" },
        initially: ["", "first"], sameDay: [""], afterBoth: ["", "first", "another"],
      },
    );
    assert.equal(changedLink.date, "2020-05-07");
    assert.equal(changedLink.retrieval_from, "another");
    assert.equal(changedLink.source, "Revised manual\nAppendix A");
    assert.equal(changedLink.uncertainty, "Timing of the last edge");
    assert.deepEqual(unchangedAbsent, absent);
    assert.deepEqual(unchangedOther, another);
    await click(page, "Close dialog");
    await edit("Another trace");
    await input(page, "Help used").selectOption("none");
    assert.equal(await input(page, "Legacy independence flag").inputValue(), "keep");
    await click(page, "Apply correction");
    await click(page, "Prepare a session");
    const prompt = await input(page, "Editable prompt").inputValue();
    const evidence = JSON.parse(prompt.slice(prompt.indexOf("\n\n{") + 2));
    assert.equal(evidence.observations.find(item => item.problem === "Another trace").independent_success, false);
    assert.equal(evidence.gates.solve, false);
    assert.equal(evidence.gates.transfer, false);
  } finally {
    await page.close();
  }
}
async function run() {
  if (output) await fs.mkdir(output, { recursive: true });
  const browser = await chromium.launch({
    headless: true,
    executablePath: process.env.BROWSER_PATH || undefined,
  });
  const issues = [],
    foreign = [],
    conditions = [];
  const context = await browser.newContext({
    viewport: { width: 1360, height: 930 },
    permissions: ["clipboard-read", "clipboard-write"],
  });
  const page = await context.newPage();
  page.setDefaultTimeout(6000);
  page.on("pageerror", (e) => issues.push(e.message));
  context.on("request", (r) => {
    const target = new URL(r.url());
    if (
      ["https:", "http:", "ws:", "wss:"].includes(target.protocol) &&
      target.origin !== new URL(url).origin
    )
      foreign.push(target.origin);
  });
  try {
    await page.goto(url);
    await page.getByRole("heading", { name: "Signals & sampling" }).waitFor();
    assert.equal(await page.locator("#state-label").innerText(), "Untested");
    assert.equal(await page.evaluate(() => localStorage.length), 0);
    await artifact(page, "desktop.png");
    async function audit() {
      await page.evaluate(axeSource);
      const results = await page.evaluate(() =>
        axe.run(document, {
          runOnly: {
            type: "tag",
            values: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"],
          },
        }),
      );
      assert.deepEqual(
        results.violations.map((v) => [v.id, v.nodes.map((n) => n.target)]),
        [],
      );
    }
    await audit();
    const initial = await page.locator(".node").allTextContents();
    assert.equal(initial.length, 6);
    const links = await page
      .locator("#world path[data-prerequisite]")
      .evaluateAll((paths) => {
        const nodes = [...document.querySelectorAll("#world .node")];
        const checks = paths.map((edge) => {
          const length = edge.getTotalLength(),
            first = edge.getPointAtLength(0),
            last = edge.getPointAtLength(length);
          const from = nodes.find(
            (n) => n.dataset.skill === edge.dataset.prerequisite,
          );
          const to = nodes.find(
            (n) => n.dataset.skill === edge.dataset.dependent,
          );
          if (
            Math.abs(first.x - (from.offsetLeft + from.offsetWidth)) > 1 ||
            Math.abs(last.x - to.offsetLeft) > 1 ||
            Math.abs(first.y - (from.offsetTop + from.offsetHeight / 2)) > 1 ||
            Math.abs(last.y - (to.offsetTop + to.offsetHeight / 2)) > 1
          )
            throw Error("Disconnected edge");
          for (let d = 0; d < length; d += 3) {
            const point = edge.getPointAtLength(d);
            if (
              nodes.some(
                (n) =>
                  n !== from &&
                  n !== to &&
                  point.x > n.offsetLeft &&
                  point.x < n.offsetLeft + n.offsetWidth &&
                  point.y > n.offsetTop &&
                  point.y < n.offsetTop + n.offsetHeight,
              )
            )
              throw Error("Edge crosses unrelated node");
          }
          return edge.dataset.prerequisite + ">" + edge.dataset.dependent;
        });
        return checks.sort();
      });
    assert.deepEqual(
      links,
      [
        "sample-clock>samples",
        "periodicity>boundary",
        "samples>aliasing",
        "periodicity>aliasing",
        "aliasing>design",
        "boundary>design",
      ].sort(),
    );
    for (const node of await page.locator(".node").all()) {
      await node.focus();
      await node.press("Enter");
      assert.equal(
        await page.locator("#skill-title").innerText(),
        await node.innerText(),
      );
    }
    await click(page, "List");
    const list = await page.locator(".list-row strong").allTextContents();
    assert.deepEqual(list, initial);
    await page
      .locator(".list-row")
      .filter({ hasText: "Aliasing" })
      .first()
      .click();
    assert.equal(await page.locator("#skill-title").innerText(), "Aliasing");
    await click(page, "Graph");
    const transform = () =>
      page.locator("#world").evaluate((el) => el.style.transform);
    const start = await transform();
    await click(page, "Zoom in");
    assert.notEqual(await transform(), start);
    await click(page, "Recenter");
    assert.equal(await transform(), start);
    await page.locator("#canvas").press("ArrowRight");
    assert.notEqual(await transform(), start);
    await click(page, "Recenter");
    const frame = await page.locator("#canvas").boundingBox();
    await page.mouse.move(frame.x + 5, frame.y + 5);
    await page.mouse.down();
    await page.mouse.move(frame.x + 50, frame.y + 35);
    await page.mouse.up();
    assert.notEqual(await transform(), start);
    await click(page, "Set study goal");
    await input(page, "What do you want to be able to do?").fill(
      "Distinguish two candidate wheel speeds.",
    );
    await input(page, "Permitted aids").fill("Pencil only");
    await input(page, "Preferred challenge intensity").fill("Hard");
    await click(page, "Apply goal");
    assert.equal(await page.evaluate(() => localStorage.length), 0);
    await click(page, "Record attempt");
    await input(page, "Problem or activity ID").fill("wheel-A");
    await input(page, "What did you actually do?").fill(
      "Needed a hint to identify the phase difference.",
    );
    await input(page, "Material").selectOption("generated");
    await input(page, "Outcome").selectOption("partial");
    await input(page, "Activity").selectOption("solve");
    await input(page, "Help used").selectOption("hint");
    await click(page.getByRole("dialog"), "Record attempt");
    assert.equal(
      await page.locator("#state-label").innerText(),
      "With assistance",
    );
    await click(page, "Prepare a session");
    const prompt = input(page, "Editable prompt");
    for (const mode of ["exam", "explore", "prepare", "grill"]) {
      await input(page, "Mode").selectOption(mode);
      const text = await prompt.inputValue();
      for (const expected of [
        "Pencil only",
        "wheel-A",
        "hint",
        "Hard",
        "periodicity",
      ])
        assert.ok(text.includes(expected), expected);
    }
    await prompt.fill("Edited by learner");
    await input(page, "Mode").selectOption("exam");
    assert.equal(await prompt.inputValue(), "Edited by learner");
    await click(page, "Copy prompt");
    assert.equal(
      await page.evaluate(() => navigator.clipboard.readText()),
      "Edited by learner",
    );
    await page.keyboard.press("Escape");
    assert.equal(
      await page
        .locator("#prepare")
        .evaluate((el) => el === document.activeElement),
      true,
    );
    await click(page, "My data");
    await click(page, "Save on this device");
    await click(page, "Close dialog");
    await page.reload();
    await page.getByText("Saved on this device", { exact: true }).waitFor();
    assert.equal(
      await page.locator("#state-label").innerText(),
      "With assistance",
    );
    await click(page, "Correct");
    await input(page, "Outcome").selectOption("correct");
    await input(page, "Help used").selectOption("none");
    await input(page, "Evidence source").selectOption("observed-work");
    await input(page, "Response basis").selectOption("reasoned");
    await input(page, "What did you actually do?").fill(
      "Wrote the phase difference for every integer frame.",
    );
    await click(page, "Apply correction");
    await page.getByRole("dialog").waitFor({ state: "hidden" });
    await click(page, "Prepare a session");
    const prepared = await input(page, "Editable prompt").inputValue();
    const handoff = JSON.parse(prepared.slice(prepared.indexOf("\n\n{") + 2));
    assert.equal(handoff.observations[0].provenance, "generated");
    assert.match(handoff.observations[0].corrected_on, /^\d{4}-\d{2}-\d{2}$/);
    assert.equal(handoff.observations[0].assistance, "none");
    await page.keyboard.press("Escape");
    assert.equal(
      await page.locator("#state-label").innerText(),
      "Solved unaided",
    );
    await click(page, "Edit review date or open question");
    await input(page, "Optional review date").fill("2020-02-29");
    await input(page, "Open question").fill(
      "Would a scalar projection suffice?",
    );
    await click(page, "Apply review plan");
    await page.getByText(/review date has arrived/).waitFor();
    await click(page, "My data");
    const dl = page.waitForEvent("download");
    await click(page, "Export roadmap");
    const download = await dl;
    const backup = JSON.parse(await fs.readFile(await download.path(), "utf8"));
    assert.equal(backup.evidence.length, 1);
    await checkImportedCorrections(browser, backup);
    const wrong = structuredClone(backup);
    wrong.skills[0].prerequisites = [wrong.skills[0].id];
    await chooseFile(page, wrong);
    await page
      .getByRole("dialog")
      .getByRole("alert")
      .filter({ hasText: /cycle/i })
      .waitFor();
    assert.equal(
      await page.locator("#state-label").innerText(),
      "Solved unaided",
    );
    await chooseFile(page, {
      kind: "roadmap-evidence",
      schema_version: 1,
      event: backup.evidence[0],
    });
    await page
      .getByRole("dialog")
      .getByRole("alert")
      .filter({ hasText: /already recorded/i })
      .waitFor();
    await click(page, "Close dialog");
    await click(page, "Delete");
    await click(page, "Delete attempt");
    await page.getByRole("dialog").waitFor({ state: "hidden" });
    assert.equal(await page.locator("#state-label").innerText(), "Untested");
    assert.equal(
      await page
        .locator("#add")
        .evaluate((el) => el === document.activeElement),
      true,
      "Return focus after deleting its opener",
    );
    await click(page, "My data");
    // Two reads finish out of order. Only the file still named in the picker may be applied.
    await page.evaluate(() => {
      const read = File.prototype.text;
      File.prototype.text = async function () {
        const data = await read.call(this);
        if (data.includes("Slow backup"))
          await new Promise((resolve) => {
            window.releaseOldRead = resolve;
          });
        return data;
      };
    });
    await chooseFile(page, { ...backup, topic: "Slow backup" });
    await page.waitForFunction(() => !!window.releaseOldRead);
    await chooseFile(page, backup);
    await button(page, "Replace roadmap").waitFor();
    await page.evaluate(() => window.releaseOldRead());
    assert.equal(await button(page, "Replace roadmap").count(), 1);
    await click(page, "Replace roadmap");
    await page.getByRole("dialog").waitFor({ state: "hidden" });
    assert.equal(
      await page.locator("#state-label").innerText(),
      "Solved unaided",
    );
    const event = structuredClone(backup.evidence[0]);
    event.attempt_id = "separate-observation";
    event.problem_id = "wheel-B";
    event.outcome = "incorrect";
    await click(page, "My data");
    await chooseFile(page, {
      kind: "roadmap-evidence",
      schema_version: 1,
      event,
    });
    await click(page, "Add imported event");
    await page.getByRole("dialog").waitFor({ state: "hidden" });
    assert.equal(
      await page.locator("#state-label").innerText(),
      "Mixed evidence",
    );
    await page.evaluate(() => navigator.serviceWorker.ready);
    await page.waitForFunction(() => !!navigator.serviceWorker.controller);
    await context.setOffline(true);
    await page.reload();
    await page
      .getByText("Offline · local workspace", { exact: true })
      .waitFor();
    assert.equal(
      await page.locator("#state-label").innerText(),
      "Mixed evidence",
    );
    await context.setOffline(false);
    const second = await context.newPage();
    await second.goto(url);
    await click(second, "Edit study goal");
    await input(second, "What do you want to be able to do?").fill(
      "A distinct goal from another tab",
    );
    await click(second, "Apply goal");
    await page.getByText(/changed in another tab/).waitFor();
    assert.equal(
      await page.locator("#goal-line").innerText(),
      backup.goal.capability,
    );
    await second.close();
    await click(page, "My data");
    await click(page, "Reload saved copy");
    await page
      .getByText("A distinct goal from another tab", { exact: true })
      .waitFor();
    await click(page, "My data");
    await click(page, "Erase local roadmap");
    await click(page, "Erase and start fresh");
    await page.getByRole("dialog").waitFor({ state: "hidden" });
    assert.equal(await page.evaluate(() => localStorage.length), 0);
    await page.reload();
    assert.equal(await page.locator("#state-label").innerText(), "Untested");
    for (const theme of ["dark", "light"])
      for (const width of [320, 736, 1360]) {
        const height = width === 320 ? 740 : width === 736 ? 414 : 930;
        await page.setViewportSize({ width, height });
        await page.emulateMedia({
          colorScheme: theme,
          reducedMotion: "reduce",
        });
        await page.reload();
        await page.getByRole("heading", { name: "Aliasing" }).waitFor();
        assert.equal(
          await page.evaluate(
            () => document.documentElement.scrollWidth <= innerWidth,
          ),
          true,
          "horizontal overflow " + width,
        );
        const ax = await page.locator("body").ariaSnapshot();
        for (const label of [
          "Skill map",
          "Aliasing",
          "Signals & sampling",
          "Prepare a session",
          "Evidence notebook",
        ])
          assert.ok(ax.includes(label), label);
        if (width === 320) {
          assert.equal(
            await button(page, "List").getAttribute("aria-pressed"),
            "true",
          );
          if (theme === "light") {
            await artifact(page, "mobile.png");
            await audit();
          }
        }
        if (width === 1360)
          assert.equal(
            await button(page, "Graph").getAttribute("aria-pressed"),
            "true",
          );
        await click(page, "Prepare a session");
        const dialogAX = await page.getByRole("dialog").ariaSnapshot();
        assert.ok(dialogAX.includes("Editable prompt"));
        assert.ok(dialogAX.includes('combobox "Mode"'));
        if (width === 1360 && theme === "light") await audit();
        await page.keyboard.press("Escape");
        conditions.push({ width, height, theme });
      }
    await page.setViewportSize({ width: 320, height: 740 });
    await page.reload();
    await click(page, "My data");
    const wide = {
      ...backup,
      field: "F".repeat(240),
      topic: "T".repeat(240),
      skills: [
        {
          id: "constructor",
          title: "Q".repeat(240),
          description: "D".repeat(240),
          prerequisites: [],
          challenge: "C".repeat(240),
        },
      ],
      evidence: [],
    };
    await chooseFile(page, wide);
    await click(page, "Replace roadmap");
    await page.getByRole("dialog").waitFor({ state: "hidden" });
    assert.equal(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
      true,
      "custom long labels " +
        JSON.stringify(
          await page.evaluate(() =>
            [...document.querySelectorAll("body *")]
              .filter((e) => e.getBoundingClientRect().right > innerWidth + 1)
              .slice(0, 12)
              .map((e) => [e.id, e.className, e.tagName]),
          ),
        ),
    );
    assert.ok(
      !(await page.locator("#skill-icon path").getAttribute("d")).includes(
        "function",
      ),
    );
    const chain = {
      ...wide,
      skills: Array.from({ length: 40 }, (_, i) => ({
        id: "n" + i,
        title: "Skill " + i,
        description: "Description",
        challenge: "Challenge",
        prerequisites: i ? ["n" + (i - 1)] : [],
      })),
    };
    await click(page, "My data");
    await chooseFile(page, chain);
    await click(page, "Replace roadmap");
    await page.getByRole("dialog").waitFor({ state: "hidden" });
    await click(page, "Graph");
    await click(page, "Recenter");
    const chosen = await page.locator(".node[aria-pressed=true]").boundingBox(),
      canvas = await page.locator("#canvas").boundingBox();
    assert.ok(
      chosen.x >= canvas.x &&
        chosen.x + chosen.width <= canvas.x + canvas.width,
      "recenter shows selected skill",
    );
    // Invalid saved bytes survive launch and ordinary edits. A fresh tab can recover them.
    await page.evaluate(() =>
      localStorage.setItem("ppp-fieldnotes-roadmap:v1", "{damaged"),
    );
    await page.reload();
    await page.getByText(/saved copy could not be opened/).waitFor();
    await click(page, "Set study goal");
    await input(page, "What do you want to be able to do?").fill(
      "Recover my work",
    );
    await click(page, "Apply goal");
    assert.equal(
      await page.evaluate(() =>
        localStorage.getItem("ppp-fieldnotes-roadmap:v1"),
      ),
      "{damaged",
    );
    await click(page, "My data");
    await chooseFile(page, backup);
    await click(page, "Replace roadmap");
    await page.getByRole("dialog").waitFor({ state: "hidden" });
    await click(page, "My data");
    await click(page, "Save this copy over stored data");
    await click(page, "Replace stored copy with this tab");
    await page.getByRole("dialog").waitFor({ state: "hidden" });
    await page.reload();
    await page.getByText("Saved on this device", { exact: true }).waitFor();
    assert.equal(
      await page.locator("#goal-line").innerText(),
      backup.goal.capability,
    );
    // Clean context, simulated write failure: verify the in-memory edit is available for export.
    const blocked = await browser.newContext();
    const bp = await blocked.newPage();
    await bp.addInitScript(() => {
      Storage.prototype.setItem = () => {
        throw Error("storage full");
      };
    });
    await bp.goto(url);
    await click(bp, "Set study goal");
    await input(bp, "What do you want to be able to do?").fill(
      "Keep my unsaved work",
    );
    await click(bp, "Apply goal");
    await click(bp, "My data");
    await click(bp, "Save on this device");
    await click(bp, "Close dialog");
    await bp.getByText(/edit is available in this tab only/).waitFor();
    assert.equal(
      await bp.locator("#goal-line").innerText(),
      "Keep my unsaved work",
    );
    await blocked.close();
    const noModule = await browser.newContext({ serviceWorkers: "block" });
    const broken = await noModule.newPage();
    await broken.route("**/model.mjs", (route) => route.abort());
    await broken.goto(url);
    await broken
      .getByRole("heading", { name: "Roadmap unavailable" })
      .waitFor();
    await noModule.close();
    assert.deepEqual(issues, []);
    assert.deepEqual(foreign, []);
    const report = {
      browser: await browser.version(),
      conditions,
      uncaughtPageErrors: issues,
      foreignRequests: foreign,
      completed: true,
    };
    if (output)
      await fs.writeFile(
        path.join(output, "browser-result.json"),
        JSON.stringify(report, null, 2) + "\n",
      );
    console.log(JSON.stringify(report));
  } finally {
    await browser.close();
  }
}
run().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
