import { initialRoadmap } from "./curriculum.mjs";
import { setupMap, icon, drawSignal } from "./map.mjs";
import {
  validateRoadmap,
  parseRoadmap,
  parseEvidence,
  recordAttempt,
  correctAttempt,
  deleteAttempt,
  skillState,
  buildPrompt,
  exportSession,
  localDay,
} from "./model.mjs";

const $ = (id) => document.getElementById(id);
const key = "ppp-fieldnotes-roadmap:v1";
let state,
  selected,
  saved = null,
  persistent = false,
  conflict = false;
let modalsFrom = null,
  dirty = false;
window.addEventListener("beforeunload", (e) => {
  if (dirty) {
    e.preventDefault();
    e.returnValue = "";
  }
});
const say = (text) => {
  $("announce").textContent = text;
};
const setText = (id, text) => {
  $(id).textContent = text;
};
function banner(text) {
  setText("alert", text);
  $("alert").hidden = !text;
}
function elt(tag, text, cls) {
  const el = document.createElement(tag);
  if (text !== undefined) el.textContent = text;
  if (cls) el.className = cls;
  return el;
}
function button(text, action, cls = "btn") {
  const b = elt("button", text, cls);
  b.type = "button";
  b.onclick = action;
  return b;
}
const map = setupMap({ choose });
function choose(id) {
  selected = id;
  map.select(id);
  detail();
  say("Selected " + state.skills.find((s) => s.id === id).title);
  if (matchMedia("(max-width:760px)").matches) $("skill-title").focus();
}
function dialog(title) {
  const d = $("dialog");
  if (!d.open) modalsFrom = document.activeElement;
  setText("dialog-title", title);
  const body = $("dialog-body");
  body.replaceChildren();
  if (!d.open) d.showModal();
  d.scrollTop = 0;
  return body;
}
function close() {
  if ($("dialog").open) $("dialog").close();
}
$("close").onclick = close;
$("dialog").onclose = () => {
  (modalsFrom?.isConnected ? modalsFrom : $("add")).focus();
};
function errorBox(body) {
  const el = elt("p", "", "problem");
  el.setAttribute("role", "alert");
  body.append(el);
  return el;
}
function field(parent, label, name, value, options = {}) {
  const wrap = elt("div", undefined, "field"),
    caption = elt("label", label);
  caption.htmlFor = "entry-" + name;
  wrap.append(caption);
  const input = elt(
    options.choices ? "select" : options.rows ? "textarea" : "input",
  );
  input.name = name;
  input.id = caption.htmlFor;
  if (options.choices) {
    for (const [v, t] of options.choices) {
      const o = elt("option", t);
      o.value = v;
      input.append(o);
    }
  } else if (options.rows) input.rows = options.rows;
  else input.type = options.type || "text";
  if (options.required) input.required = true;
  if (options.max) input.maxLength = options.max;
  input.value = value ?? "";
  wrap.append(input);
  parent.append(wrap);
  return input;
}
function download(value, name) {
  const url = URL.createObjectURL(
    new Blob(
      [
        typeof value === "string"
          ? value
          : JSON.stringify(value, null, 2) + "\n",
      ],
      { type: "application/json" },
    ),
  );
  const a = elt("a");
  a.href = url;
  a.download = name;
  document.body.append(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
function localStatus() {
  setText(
    "save-state",
    persistent
      ? "Saved on this device"
      : conflict
        ? "Unsaved copy"
        : "Session only",
  );
}
function load() {
  state = validateRoadmap(initialRoadmap());
  try {
    saved = localStorage.getItem(key);
    if (saved !== null) {
      state = parseRoadmap(saved);
      persistent = true;
    }
  } catch {
    conflict = true;
    banner(
      "The saved copy could not be opened. My data lets you recover the original or import a backup.",
    );
  }
  selected =
    state.skills.find((s) => s.id === "aliasing")?.id || state.skills[0].id;
}
async function locked(action) {
  if (navigator.locks) return navigator.locks.request(key, action);
  return action();
}
async function change(next, saveNow = false) {
  validateRoadmap(next);
  const shouldSave = persistent || saveNow;
  if (shouldSave) {
    try {
      await locked(() => {
        const current = localStorage.getItem(key);
        if (conflict || current !== saved)
          throw Error(
            "Another copy exists. Export this session, then reload the saved copy.",
          );
        const raw = JSON.stringify(next);
        localStorage.setItem(key, raw);
        saved = raw;
        persistent = true;
      });
    } catch (e) {
      persistent = false;
      conflict = true;
      banner(
        "This edit is available in this tab only. Export it in My data before closing. " +
          (e.message?.startsWith("Another copy")
            ? e.message
            : "Browser storage is unavailable or full."),
      );
    }
  }
  dirty = !persistent;
  state = next;
  if (!state.skills.some((s) => s.id === selected))
    selected = state.skills[0].id;
  render();
}
window.addEventListener("storage", (e) => {
  if (e.key !== key && e.key !== null) return;
  if (e.newValue === saved && e.key === key) return;
  persistent = false;
  conflict = true;
  localStatus();
  banner(
    "Saved data changed in another tab. Export any edits, then open My data to reload the saved copy.",
  );
});
function render() {
  localStatus();
  setText("topic", state.topic);
  setText("field", state.field);
  setText(
    "goal-line",
    state.goal.capability ||
      "Choose what you want to explain, solve, or test independently.",
  );
  setText("goal", state.goal.capability ? "Edit study goal" : "Set study goal");
  $("plate").hidden = state.topic !== initialRoadmap().topic;
  setText(
    "map-meta",
    state.skills.length +
      " skills · " +
      state.skills.reduce((n, s) => n + s.prerequisites.length, 0) +
      " prerequisite links",
  );
  map.render(state.skills, selected, (id) => skillState(state, id).label);
  detail();
}
function detail() {
  const s = state.skills.find((i) => i.id === selected),
    info = skillState(state, selected);
  setText("skill-title", s.title);
  setText("description", s.description);
  setText("state-label", info.label);
  $("skill-icon").replaceChildren(icon(selected));
  $("prereqs").replaceChildren();
  for (const p of info.prerequisites)
    $("prereqs").append(button(p.title, () => choose(p.id), "prereq"));
  if (!info.prerequisites.length)
    setText("prereqs", "No prerequisites in this map.");
  setText("recommend", info.recommendation);
  setText("challenge", s.challenge);
  $("challenge").hidden = info.events.length > 0;
  const n = info.events.length;
  setText(
    "ledger-meta",
    s.title +
      " · " +
      n +
      (n === 1 ? " observation" : " observations") +
      (s.review_date ? " · Review " + s.review_date : ""),
  );
  const events = $("events");
  events.replaceChildren();
  if (info.stale || info.reviewDue)
    events.append(
      elt(
        "p",
        info.reviewDue
          ? "The review date has arrived. Check retrieval on a fresh task."
          : "Earlier work may need a fresh check.",
        "note",
      ),
    );
  if (s.open_question)
    events.append(elt("p", "Open question · " + s.open_question, "note"));
  if (!n)
    events.append(
      elt(
        "p",
        "No recorded attempt for this skill. Add the work you did and the help you used.",
        "empty",
      ),
    );
  for (const e of info.events) {
    const row = elt("div", undefined, "row");
    row.append(
      elt("small", e.date + " · " + e.problem_id),
      elt("p", e.evidence),
      elt(
        "small",
        e.outcome + " · help: " + e.assistance + " · " + e.attribution,
      ),
    );
    const details = elt("details");
    details.append(elt("summary", "Source and conditions"));
    for (const [label, value] of [
      ["Activity", e.activity || "unspecified"],
      ["Response", e.response_basis],
      ["Prior exposure", e.previously_seen ? "Previously seen" : null],
      ["Material", e.provenance],
      ["Source", e.source],
      ["Confidence", e.confidence || "unknown"],
      ["Transfer", e.transfer ? "changed problem" : "not identified"],
      ["Delayed check of", e.retrieval_from],
      ["Source session", e.session_ref],
    ]) {
      if (value) details.append(elt("p", label + " · " + value, "note"));
    }
    row.append(details);
    if (e.uncertainty)
      row.append(elt("p", "Uncertainty · " + e.uncertainty, "note"));
    if (e.corrected_on)
      row.append(elt("small", " · corrected " + e.corrected_on));
    const actions = elt("div", undefined, "group");
    actions.append(
      button("Correct", () => attempt(e), "text-action"),
      button(
        "Export PPP session",
        () => download(exportSession(state, e.attempt_id), "ppp-session.json"),
        "text-action",
      ),
      button("Delete", () => removeEvent(e), "text-action danger"),
    );
    row.append(actions);
    events.append(row);
  }
  const support = elt("details"),
    summary = elt("summary", "Evidence by capability");
  support.append(summary);
  for (const [key, label] of [
    ["explain", "Explanation"],
    ["solve", "Unaided solving"],
    ["transfer", "Transfer"],
    ["delayed", "Delayed retrieval"],
  ])
    support.append(
      elt(
        "div",
        label +
          " · " +
          (info.gates[key] ? "Supported by recorded work" : "Untested"),
        "note",
      ),
    );
  events.append(
    support,
    button("Edit review date or open question", review, "text-action"),
  );
}
function submit(form, label, handler) {
  const err = errorBox(form),
    b = elt("button", label, "primary");
  b.type = "submit";
  form.append(b);
  form.onsubmit = async (e) => {
    e.preventDefault();
    b.disabled = true;
    try {
      await handler(Object.fromEntries(new FormData(form)));
    } catch (x) {
      err.textContent = x.message;
    } finally {
      b.disabled = false;
    }
  };
}
function goal() {
  const body = dialog("Study goal"),
    form = elt("form");
  body.append(form);
  field(
    form,
    "What do you want to be able to do?",
    "capability",
    state.goal.capability,
    { rows: 2, required: true },
  );
  for (const [name, label] of [
    ["context", "Why or where will you use it?"],
    ["success", "What would count as success?"],
    ["aids", "Permitted aids"],
    ["timebox", "Available time"],
    ["intensity", "Preferred challenge intensity"],
    ["deadline", "Deadline (optional)"],
  ])
    field(
      form,
      label,
      name,
      state.goal[name],
      name === "deadline" ? { type: "date" } : {},
    );
  form.append(
    elt(
      "p",
      persistent
        ? "Edits are saved in this browser."
        : "Your goal stays in this tab until you choose Save on this device in My data.",
      "note",
    ),
  );
  submit(form, "Apply goal", async (data) => {
    await change({ ...state, goal: { ...state.goal, ...data } });
    close();
    say("Goal updated");
  });
}
function review() {
  const body = dialog("Review plan"),
    form = elt("form"),
    s = state.skills.find((n) => n.id === selected);
  body.append(form);
  field(form, "Open question", "open_question", s.open_question, { rows: 2 });
  field(form, "Optional review date", "review_date", s.review_date, {
    type: "date",
  });
  form.append(
    elt(
      "p",
      "A date appears in this notebook. It does not schedule a reminder.",
      "note",
    ),
  );
  submit(form, "Apply review plan", async (values) => {
    await change({
      ...state,
      skills: state.skills.map((i) => (i === s ? { ...i, ...values } : i)),
    });
    close();
    say("Review plan updated");
  });
}
const opts = (...vs) => vs.map((v) => [v, v.replaceAll("-", " ")]);
function attempt(previous) {
  const editing = !!previous,
    body = dialog(editing ? "Correct attempt" : "Record attempt"),
    form = elt("form");
  body.append(form);
  const e = previous || {
    date: localDay(),
    attribution: "learner-statement",
    activity: "unspecified",
    assistance: "unknown",
    response_basis: "unknown",
    provenance: "",
    outcome: "",
    confidence: "unknown",
  };
  field(form, "Problem or activity ID", "problem_id", e.problem_id, {
    required: true,
  });
  const observation = field(
    form,
    "What did you actually do?",
    "evidence",
    e.evidence,
    { rows: 2, required: e.outcome !== "not-attempted" },
  );
  const grid = elt("div", undefined, "form-grid");
  form.append(grid);
  field(grid, "Date", "date", e.date, { type: "date", required: true });
  const outcome = field(grid, "Outcome", "outcome", e.outcome, {
    required: true,
    choices: [
      ["", "Choose an outcome"],
      ...opts("not-attempted", "incorrect", "partial", "correct"),
    ],
  });
  outcome.onchange = () => {
    observation.required = outcome.value !== "not-attempted";
  };
  field(grid, "Help used", "assistance", e.assistance, {
    choices: opts(
      "unknown",
      "none",
      "prompt",
      "hint",
      "partial",
      "full-solution",
      "ai-assisted",
    ),
  });
  field(grid, "Evidence source", "attribution", e.attribution, {
    choices: [
      ["learner-statement", "Learner report"],
      ["observed-work", "Observed work"],
      ["agent-inference", "Tutor inference"],
    ],
  });
  field(grid, "Activity", "activity", e.activity || "unspecified", {
    choices: opts("solve", "explain", "unspecified"),
  });
  field(grid, "Response basis", "response_basis", e.response_basis, {
    choices: opts("unknown", "reasoned", "recognition", "guess"),
  });
  field(grid, "Material", "provenance", e.provenance, {
    required: true,
    choices: [
      ["", "Choose the source type"],
      ...opts("generated", "past-paper", "source-adapted"),
    ],
  });
  field(grid, "Source or locator", "source", e.source);
  field(
    grid,
    "New transfer problem?",
    "transfer",
    String(e.transfer ?? false),
    {
      choices: [
        ["false", "No"],
        ["true", "Yes, a changed problem"],
      ],
    },
  );
  field(
    grid,
    "Confidence (optional)",
    "confidence",
    e.confidence || "unknown",
    { choices: opts("unknown", "low", "medium", "high") },
  );
  field(
    form,
    "Prior exposure outside this notebook",
    "prior_familiarity",
    e.previously_seen ? "seen" : "keep",
    {
      choices: [
        ["keep", "Use recorded evidence"],
        ["seen", "I had already seen this problem or its solution"],
        ...(e.previously_seen
          ? [["correct", "Correct a mistaken prior-exposure marker"]]
          : []),
      ],
    },
  );
  const earlier = state.evidence.filter(
    (x) => x.skill_id === selected && x.attempt_id !== e.attempt_id,
  );
  field(
    form,
    "Delayed check of earlier attempt",
    "retrieval_from",
    e.retrieval_from,
    {
      choices: [
        ["", "None"],
        ...earlier.map((x) => [x.attempt_id, x.date + " · " + x.problem_id]),
      ],
    },
  );
  field(form, "What remains uncertain?", "uncertainty", e.uncertainty, {
    rows: 2,
  });
  let withdraw;
  if (editing && typeof e.independent_success === "boolean") {
    withdraw = field(form, "Legacy independence flag", "legacy", "keep", {
      choices: [
        ["keep", "Keep prior flag (" + e.independent_success + ")"],
        ["withdraw", "Withdraw disputed flag"],
      ],
    });
  }
  submit(
    form,
    editing ? "Apply correction" : "Record attempt",
    async (values) => {
      delete values.legacy;
      const event = {
        ...values,
        source: values.source || null,
        transfer: values.transfer === "true",
        retrieval_from: values.retrieval_from || null,
      };
      if (values.prior_familiarity !== "keep")
        event.previously_seen = values.prior_familiarity === "seen";
      delete event.prior_familiarity;
      if (withdraw?.value === "withdraw") event.independent_success = null;
      const next = editing
        ? correctAttempt(state, e.attempt_id, event)
        : recordAttempt(state, {
            ...event,
            attempt_id: crypto.randomUUID(),
            skill_id: selected,
          });
      await change(next);
      close();
      say(editing ? "Attempt corrected" : "Attempt recorded");
    },
  );
}
function removeEvent(e) {
  const body = dialog("Delete attempt?");
  body.append(
    elt("p", e.date + " · " + e.problem_id),
    elt(
      "p",
      "This removes the observation from this roadmap. Copies previously exported are separate.",
      "note",
    ),
  );
  const err = errorBox(body);
  body.append(
    button(
      "Delete attempt",
      async () => {
        try {
          await change(deleteAttempt(state, e.attempt_id));
          close();
          say("Attempt deleted");
        } catch (x) {
          err.textContent = x.message;
        }
      },
      "btn danger",
    ),
  );
}
function prepare() {
  const body = dialog("Prepare a session");
  body.append(
    elt(
      "p",
      "Choose a tutoring mode, edit the prompt, then copy it into a chat with PPP.",
      "note",
    ),
  );
  const mode = field(body, "Mode", "mode", "grill", {
    choices: [
      ["grill", "Grill me"],
      ["exam", "Generate a hard exam"],
      ["explore", "Explore why"],
      ["prepare", "Prepare my next session"],
    ],
  });
  const text = field(
    body,
    "Editable prompt",
    "prompt",
    buildPrompt(state, selected, "grill"),
    { rows: 12 },
  );
  let built = text.value;
  const regen = () => {
    built = buildPrompt(state, selected, mode.value);
    text.value = built;
  };
  const controls = elt("div", undefined, "group");
  body.append(controls);
  const update = button("Replace edited prompt", () => {
    regen();
    update.hidden = true;
  });
  update.hidden = true;
  mode.onchange = () => {
    if (text.value !== built) {
      update.hidden = false;
    } else regen();
  };
  const status = elt("p", "", "note");
  status.setAttribute("role", "status");
  controls.append(
    button(
      "Copy prompt",
      async () => {
        try {
          await navigator.clipboard.writeText(text.value);
          status.textContent = "Copied.";
        } catch {
          text.focus();
          text.select();
          status.textContent =
            "Text selected. Use the copy command on your device.";
        }
      },
      "primary",
    ),
    update,
  );
  body.append(
    status,
    elt("small", "Generated from a local template. No model request is sent."),
  );
}
function dataMenu() {
  const body = dialog("My data");
  body.append(
    elt(
      "p",
      persistent
        ? "This browser stores your roadmap at this local address."
        : "Your changes live in this tab. Save on this device to reopen them after refresh.",
      "note",
    ),
  );
  const top = elt("div", undefined, "group");
  body.append(top);
  if (!persistent && !conflict)
    top.append(
      button(
        "Save on this device",
        async () => {
          await change(state, true);
          dataMenu();
        },
        "primary",
      ),
    );
  top.append(
    button("Export roadmap", () => download(state, "ppp-roadmap.json")),
  );
  if (conflict) {
    top.append(
      button("Recover original file", () => {
        try {
          const raw = localStorage.getItem(key);
          if (raw !== null) download(raw, "ppp-roadmap-recovery.json");
          else say("No stored copy found.");
        } catch {
          say("Browser storage unavailable.");
        }
      }),
      button("Reload saved copy", () => {
        dirty = false;
        location.reload();
      }),
      button("Save this copy over stored data", resolveConflict),
      button("Clear this tab only", clearTab),
    );
  }
  body.append(elt("hr"));
  const file = field(
    body,
    "Import a roadmap backup or one PPP evidence event",
    "file",
    null,
    { type: "file" },
  );
  file.accept = ".json,application/json";
  const err = errorBox(body),
    preview = elt("div");
  body.append(preview);
  let importVersion = 0;
  file.onchange = async () => {
    const version = ++importVersion;
    const current = () =>
      version === importVersion && file.isConnected && $("dialog").open;
    preview.replaceChildren();
    err.textContent = "";
    const f = file.files[0];
    if (!f) return;
    try {
      if (f.size > 2 * 1024 * 1024)
        throw Error("Choose a JSON file of at most 2 MiB.");
      const raw = (await f.text()).replace(/^\uFEFF/, "");
      if (!current()) return;
      let candidate;
      try {
        candidate = JSON.parse(raw);
      } catch {
        throw Error("Invalid JSON. The current roadmap was kept.");
      }
      const event =
        candidate?.kind === "roadmap-evidence" ? parseEvidence(raw) : null;
      const next = event ? recordAttempt(state, event) : parseRoadmap(raw);
      preview.append(
        elt(
          "p",
          event
            ? "Add one evidence event to this roadmap?"
            : "Replace this roadmap with “" +
                next.topic +
                "” (" +
                next.skills.length +
                " skills, " +
                next.evidence.length +
                " attempts)? Export your current copy first if you need it.",
          "note",
        ),
      );
      preview.append(
        button(
          event ? "Add imported event" : "Replace roadmap",
          async () => {
            if (!current()) return;
            try {
              await change(next);
              close();
              say("Import complete");
            } catch (x) {
              err.textContent = x.message;
            }
          },
          "primary",
        ),
      );
    } catch (x) {
      if (current()) err.textContent = x.message;
    }
  };
  body.append(elt("hr"), button("Erase local roadmap", erase, "btn danger"));
}
function resetTab() {
  state = initialRoadmap();
  selected = "aliasing";
  dirty = false;
  persistent = false;
  render();
  close();
}
function clearTab() {
  const body = dialog("Clear this tab only?");
  body.append(
    elt(
      "p",
      "This discards all unsaved observations in this tab. A stored copy may still exist at this browser address.",
    ),
  );
  body.append(
    button(
      "Clear this tab",
      () => {
        resetTab();
        banner(
          "This tab was cleared. Open My data to inspect or erase the browser copy.",
        );
      },
      "btn danger",
    ),
  );
}
function resolveConflict() {
  const body = dialog("Replace stored copy?"),
    err = errorBox(body);
  let expected;
  try {
    expected = localStorage.getItem(key);
  } catch {
    err.textContent =
      "Browser storage is unavailable. Export this roadmap or clear this tab from My data.";
    return;
  }
  body.append(
    elt(
      "p",
      "Save the roadmap currently displayed in this tab. This replaces the copy already at this browser address. Recover it first if you need it.",
    ),
  );
  if (expected !== null)
    body.append(
      button("Download stored copy", () =>
        download(expected, "ppp-roadmap-recovery.json"),
      ),
    );
  body.append(
    button(
      "Replace stored copy with this tab",
      async () => {
        try {
          await locked(() => {
            if (localStorage.getItem(key) !== expected)
              throw Error(
                "Storage changed again. Reopen My data to review it.",
              );
            const raw = JSON.stringify(state);
            localStorage.setItem(key, raw);
            saved = raw;
          });
          persistent = true;
          conflict = false;
          dirty = false;
          banner("");
          localStatus();
          close();
          say("Roadmap saved on this device");
        } catch (x) {
          err.textContent =
            x.name === "QuotaExceededError"
              ? "Storage is full. Export your roadmap from My data."
              : x.message;
        }
      },
      "primary",
    ),
  );
}
function erase() {
  const body = dialog("Erase local roadmap?");
  body.append(
    elt(
      "p",
      "This clears this tab and the saved roadmap for this browser address. Keep an export if you want to restore it.",
    ),
  );
  const err = errorBox(body);
  let observed;
  try {
    observed = localStorage.getItem(key);
  } catch {
    err.textContent =
      "Browser storage is unavailable. You can still discard the unsaved work in this tab.";
    body.append(button("Clear this tab only", clearTab));
    return;
  }
  body.append(
    button("Export first", () => download(state, "ppp-roadmap.json")),
    button(
      "Erase and start fresh",
      async () => {
        try {
          await locked(() => {
            if (localStorage.getItem(key) !== observed)
              throw Error(
                "The saved copy changed. Reopen My data to review it.",
              );
            localStorage.removeItem(key);
          });
          saved = null;
          conflict = false;
          persistent = false;
          dirty = false;
          banner("");
          state = initialRoadmap();
          selected = "aliasing";
          render();
          close();
          say("Local roadmap erased");
        } catch (x) {
          err.textContent = x.message;
        }
      },
      "btn danger",
    ),
  );
}
$("goal").onclick = goal;
$("add").onclick = () => attempt();
$("prepare").onclick = prepare;
$("data").onclick = dataMenu;
function network() {
  setText(
    "net",
    navigator.onLine ? "Local workspace" : "Offline · local workspace",
  );
}
addEventListener("online", network);
addEventListener("offline", network);
load();
drawSignal($("signal"));
render();
network();
if ("serviceWorker" in navigator)
  navigator.serviceWorker.register("./sw.js").catch(() => {
    setText("net", "Local workspace · offline reload unavailable");
  });
