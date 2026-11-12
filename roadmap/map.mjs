const ns = "http://www.w3.org/2000/svg";
function svg(tag, attrs) {
  const el = document.createElementNS(ns, tag);
  for (const [name, value] of Object.entries(attrs))
    el.setAttribute(name, value);
  return el;
}
const glyphs = {
  "sample-clock": "M2 15H6V5H11V15H16V5H21V15H27",
  periodicity: "M3 16C3 5 15 1 21 8M21 3V8H16M25 6C25 16 14 21 7 13M7 18V13H12",
  samples: "M3 17V12M9 17V4M15 17V7M21 17V15M27 17V11",
  boundary:
    "M2 10Q14 -2 27 10Q14 22 2 10ZM17 10A3 3 0 1 1 11 10A3 3 0 1 1 17 10",
  aliasing: "M1 11Q5 1 9 11T17 11T25 11M1 11Q13 2 25 11",
  design: "M3 17L14 4L26 17ZM10 13H18M14 4V1",
};
export function icon(id) {
  const el = svg("svg", {
    viewBox: "0 0 30 21",
    class: "mini-icon",
    "aria-hidden": "true",
  });
  el.append(
    svg("path", {
      d: Object.hasOwn(glyphs, id) ? glyphs[id] : "M3 16L12 6L24 12",
      fill: "none",
      stroke: "currentColor",
      "stroke-width": 1.8,
      "stroke-linecap": "round",
      "stroke-linejoin": "round",
    }),
  );
  return el;
}
export function drawSignal(canvas) {
  for (let i = 0; i <= 4; i++)
    canvas.append(
      svg("path", {
        d: "M " + (10 + 100 * i) + " 5v108",
        stroke: "#487062",
        "stroke-width": 0.7,
      }),
    );
  for (const y of [15, 59, 103])
    canvas.append(
      svg("path", {
        d: "M 10 " + y + "h400",
        stroke: "#487062",
        "stroke-width": 0.6,
      }),
    );
  const y = (t, f) => 59 - 42 * Math.cos(2 * Math.PI * f * t);
  for (const [f, color, width] of [
    [11, "#f1af82", 1.6],
    [1, "#e6f5aa", 2.5],
  ]) {
    const points = Array.from(
      { length: 401 },
      (_, i) => 10 + i + "," + y(i / 1000, f).toFixed(2),
    );
    canvas.append(
      svg("polyline", {
        points: points.join(" "),
        stroke: color,
        fill: "none",
        "stroke-width": width,
      }),
    );
  }
  for (let n = 0; n <= 4; n++)
    canvas.append(
      svg("circle", {
        cx: 10 + 100 * n,
        cy: y(n / 10, 1),
        r: 4,
        fill: "#f8faea",
        stroke: "#173e34",
        "stroke-width": 1.4,
      }),
    );
}
export function setupMap({ choose }) {
  const $ = (id) => document.getElementById(id);
  const frame = $("canvas"),
    world = $("world"),
    list = $("map-list");
  let selection,
    items = [],
    positions = new Map(),
    size = { w: 1, h: 1 },
    fit = 1,
    zoom = 1,
    x = 0,
    y = 0,
    drag = null;
  let graph = !matchMedia("(max-width:530px)").matches;
  frame.tabIndex = 0;
  frame.setAttribute(
    "aria-label",
    "Prerequisite graph. Use arrow keys to pan, or Tab to choose a skill.",
  );
  function paint() {
    world.style.transform =
      "translate(" + x + "px," + y + "px) scale(" + zoom + ")";
    $("zoom-level").value = Math.round(zoom * 100) + "%";
  }
  function recenter() {
    if (!graph || !frame.clientWidth) return;
    fit = Math.min(
      1.22,
      (frame.clientWidth - 24) / size.w,
      (frame.clientHeight - 22) / size.h,
    );
    zoom = Math.max(0.75, fit);
    const node = positions.get(selection);
    const centerX = fit < zoom && node ? node.x + 151 / 2 : size.w / 2;
    const centerY = fit < zoom && node ? node.y + 82 / 2 : size.h / 2;
    x = frame.clientWidth / 2 - centerX * zoom;
    y = frame.clientHeight / 2 - centerY * zoom;
    paint();
  }
  function enlarge(r, cx = frame.clientWidth / 2, cy = frame.clientHeight / 2) {
    const z = Math.max(0.35, Math.min(2.6, zoom * r)),
      ratio = z / zoom;
    x = cx - (cx - x) * ratio;
    y = cy - (cy - y) * ratio;
    zoom = z;
    paint();
  }
  function view(value) {
    graph = value;
    frame.hidden = !graph;
    list.hidden = graph;
    document.querySelector(".map-foot").hidden = !graph;
    $("graph-view").setAttribute("aria-pressed", String(graph));
    $("list-view").setAttribute("aria-pressed", String(!graph));
    if (graph) recenter();
  }
  function select(id) {
    selection = id;
    for (const btn of [
      ...world.querySelectorAll("button"),
      ...list.querySelectorAll("button"),
    ])
      btn.setAttribute("aria-pressed", String(btn.dataset.skill === id));
  }
  function render(skills, id, status) {
    items = skills;
    world.replaceChildren();
    list.replaceChildren();
    positions = new Map();
    const levels = new Map(),
      layers = [];
    // Input has already passed DAG validation. Work iteratively for deep imports.
    let pending = items.slice();
    while (pending.length) {
      const unresolved = [];
      for (const item of pending) {
        if (!item.prerequisites.every((p) => levels.has(p))) {
          unresolved.push(item);
          continue;
        }
        const l = item.prerequisites.reduce(
          (m, p) => Math.max(m, 1 + levels.get(p)),
          0,
        );
        levels.set(item.id, l);
        (layers[l] ??= []).push(item);
      }
      if (unresolved.length === pending.length)
        throw Error("Cannot arrange these prerequisites.");
      pending = unresolved;
    }
    const cellX = 182,
      cellY = 105,
      w = 151,
      h = 82;
    size = {
      w: Math.max(1, layers.length) * cellX - 31,
      h: Math.max(1, ...layers.map((a) => a.length)) * cellY - 23,
    };
    world.style.width = size.w + "px";
    world.style.height = size.h + "px";
    layers.forEach((layer, l) =>
      layer.forEach((s, n) =>
        positions.set(s.id, {
          x: l * cellX,
          y: (size.h - ((layer.length - 1) * cellY + h)) / 2 + n * cellY,
        }),
      ),
    );
    const lines = svg("svg", {
      width: size.w,
      height: size.h,
      "aria-hidden": "true",
    });
    world.append(lines);
    for (const s of items) {
      const to = positions.get(s.id);
      for (const p of s.prerequisites) {
        const from = positions.get(p),
          x1 = from.x + w,
          y1 = from.y + h / 2,
          x2 = to.x,
          y2 = to.y + h / 2,
          mid = (x1 + x2) / 2;
        // Adjacent cards use the gap. Long edges travel through a lane above their row.
        const long = x2 - x1 > cellX,
          lane = from.y > to.y ? size.h + 15 : -15;
        const d = long
          ? "M " +
            x1 +
            " " +
            y1 +
            "h9V" +
            lane +
            "H" +
            (x2 - 10) +
            "V" +
            y2 +
            "H" +
            x2
          : "M " +
            x1 +
            " " +
            y1 +
            " C " +
            mid +
            " " +
            y1 +
            " " +
            mid +
            " " +
            y2 +
            " " +
            x2 +
            " " +
            y2;
        lines.append(
          svg("path", {
            d,
            "data-prerequisite": p,
            "data-dependent": s.id,
            fill: "none",
            stroke: "#738d73",
            "stroke-width": 1.65,
          }),
        );
        lines.append(
          svg("path", {
            d: "M " + (x2 - 6) + " " + (y2 - 3) + "l5 3-5 3",
            fill: "none",
            stroke: "#738d73",
            "stroke-width": 1.65,
          }),
        );
      }
      const btn = document.createElement("button");
      btn.className = "node";
      btn.dataset.skill = s.id;
      btn.style.left = to.x + "px";
      btn.style.top = to.y + "px";
      const name = document.createElement("span");
      name.textContent = s.title;
      btn.append(icon(s.id), name);
      btn.setAttribute("aria-label", s.title);
      btn.onclick = () => choose(s.id);
      btn.onfocus = () => {
        const b = btn.getBoundingClientRect(),
          f = frame.getBoundingClientRect();
        if (
          b.left < f.left ||
          b.right > f.right ||
          b.top < f.top ||
          b.bottom > f.bottom
        ) {
          x = frame.clientWidth / 2 - (to.x + w / 2) * zoom;
          y = frame.clientHeight / 2 - (to.y + h / 2) * zoom;
          paint();
        }
      };
      world.append(btn);
      const row = document.createElement("button");
      row.className = "list-row";
      row.dataset.skill = s.id;
      const title = document.createElement("strong");
      title.textContent = s.title;
      const desc = document.createElement("small");
      desc.textContent =
        status(s.id) +
        " · " +
        (s.prerequisites.length
          ? "Requires " +
            s.prerequisites
              .map((k) => items.find((n) => n.id === k).title)
              .join(", ")
          : "No prerequisites");
      row.append(title, desc);
      row.onclick = () => choose(s.id);
      list.append(row);
    }
    select(id);
    view(graph);
  }
  frame.onpointerdown = (e) => {
    if (e.target.closest("button") || e.button !== 0) return;
    drag = { id: e.pointerId, x: e.clientX, y: e.clientY, left: x, top: y };
    frame.setPointerCapture(e.pointerId);
  };
  frame.onpointermove = (e) => {
    if (drag?.id === e.pointerId) {
      x = drag.left + e.clientX - drag.x;
      y = drag.top + e.clientY - drag.y;
      paint();
    }
  };
  frame.onlostpointercapture = () => {
    drag = null;
  };
  frame.onpointerup = () => {
    drag = null;
  };
  frame.onwheel = (e) => {
    if (!e.ctrlKey && !e.metaKey) return;
    e.preventDefault();
    const rect = frame.getBoundingClientRect();
    enlarge(
      e.deltaY < 0 ? 1.12 : 1 / 1.12,
      e.clientX - rect.left,
      e.clientY - rect.top,
    );
  };
  frame.onkeydown = (e) => {
    const moves = {
      ArrowLeft: [36, 0],
      ArrowRight: [-36, 0],
      ArrowUp: [0, 36],
      ArrowDown: [0, -36],
    };
    if (moves[e.key]) {
      e.preventDefault();
      x += moves[e.key][0];
      y += moves[e.key][1];
      paint();
    }
  };
  $("zoom-in").onclick = () => enlarge(1.2);
  $("zoom-out").onclick = () => enlarge(1 / 1.2);
  $("fit").onclick = recenter;
  $("graph-view").onclick = () => view(true);
  $("list-view").onclick = () => view(false);
  new ResizeObserver(recenter).observe(frame);
  return { render, select };
}
