// Real-time browser test runner (Chrome DevTools protocol, Node 22+).
//   node tools/tests/run.mjs <page.html> [timeoutSeconds]
// Opens the page in headless Chrome, waits for the page to write its results into an element with id "RES",
// then prints those results plus any console errors or uncaught exceptions the page produced.
// Set CHROME to the browser path if it is not in the default macOS location.
import { spawn } from "node:child_process";
import { setTimeout as sleep } from "node:timers/promises";
import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const page = process.argv[2];
const limit = (+process.argv[3] || 60) * 1000;
const chromePath = process.env.CHROME || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const port = 9300 + Math.floor(Math.random() * 500);
const dir = mkdtempSync(join(tmpdir(), "ftf-cdp-"));
const chrome = spawn(chromePath, [
  "--headless=new", "--disable-gpu", `--remote-debugging-port=${port}`, `--user-data-dir=${dir}`,
  "--window-size=1440,900", "--no-first-run", "--no-default-browser-check", "about:blank",
], { stdio: "ignore" });
const done = code => { try { chrome.kill("SIGKILL"); } catch {} process.exit(code); };
try {
  let targets;
  for (let i = 0; i < 50; i++) {
    try { targets = await (await fetch(`http://127.0.0.1:${port}/json`)).json(); if (targets.length) break; } catch {}
    await sleep(200);
  }
  const t = targets.find(x => x.type === "page");
  const ws = new WebSocket(t.webSocketDebuggerUrl);
  await new Promise((ok, no) => { ws.onopen = ok; ws.onerror = no; });
  let id = 0; const pending = new Map(); const errors = [];
  ws.onmessage = m => {
    const d = JSON.parse(m.data);
    if (d.id && pending.has(d.id)) { pending.get(d.id)(d); pending.delete(d.id); return; }
    if (d.method === "Runtime.exceptionThrown") {
      const e = d.params.exceptionDetails; errors.push("exception: " + ((e.exception && e.exception.description) || e.text).split("\n")[0]);
    } else if (d.method === "Runtime.consoleAPICalled" && d.params.type === "error") {
      errors.push("console.error: " + d.params.args.map(a => a.value ?? a.description ?? "").join(" ").slice(0, 200));
    }
  };
  const send = (method, params = {}) => new Promise(r => { const i = ++id; pending.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
  await send("Page.enable"); await send("Runtime.enable");
  await send("Page.navigate", { url: "file://" + page });
  const t0 = Date.now(); let out = null;
  while (Date.now() - t0 < limit) {
    await sleep(400);
    const r = await send("Runtime.evaluate", { expression: "(document.getElementById('RES')||{}).textContent||''", returnByValue: true });
    const v = r.result && r.result.result && r.result.result.value;
    if (v) { out = v; break; }
  }
  console.log(out === null ? "NO RESULT (timed out)" : out);
  console.log("PAGE_ERRORS " + (errors.length ? errors.length + "\n" + errors.join("\n") : "0"));
  done(0);
} catch (e) { console.log("RUNNER ERROR " + e.message); done(1); }
