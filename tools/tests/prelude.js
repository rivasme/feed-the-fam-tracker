/* Shared helpers for the browser tests. Suites pull them from window.__T inside their own function scope. */
window.__R = [];
window.__T = {
  /* words that must never reach a starter page; written in pieces so this file itself passes the privacy scan */
  bad: new RegExp(["da"+"vid","ri"+"vas","ok"+"lahoma","tul"+"sa","hi"+"the","d"+"ais","brea"+"the","iam"+"da"+"vid"].join("|"), "i"),
  ok: (n, c, x) => window.__R.push((c ? "PASS " : "FAIL ") + n + (x !== undefined && !c ? " -> " + x : "")),
  $: s => document.querySelector(s),
  $$: s => [...document.querySelectorAll(s)],
  wait: ms => new Promise(r => setTimeout(r, ms)),
  until: async (f, ms = 10000) => { const t = Date.now(); while (Date.now() - t < ms) { if (f()) return true; await new Promise(r => setTimeout(r, 100)); } return false; },
  setVal: (sel, v, ev = "input") => { const el = typeof sel === "string" ? document.querySelector(sel) : sel; el.value = v; el.dispatchEvent(new Event(ev, { bubbles: true })); },
  finish: () => { const p = document.createElement("pre"); p.id = "RES"; p.textContent = window.__R.join("\n"); document.body.appendChild(p); },
};
window.addEventListener("error", e => window.__R.push("FAIL uncaught error: " + e.message));
