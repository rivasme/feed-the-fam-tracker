/* Suite 1: a brand-new user. Zero roles, the tour opens by itself, Claude access is added later with a stub. */
(async () => {
  const { ok, $, $$, wait, until, setVal, finish, bad } = window.__T;
  try {
    await until(() => $("#onb").open, 4000);
    $("[data-v=list]").click();
    ok("zero roles: Listings shows a helpful empty state, not an error", allRoles().length === 0 && /No roles yet/.test($("#plist").textContent) && !!$("#plist [data-emptyadd]") && !!$("#plist [data-sheet=hp]"));
    $("#plist [data-emptyadd]").click(); ok("empty-state button opens Add a role", $("#dlg").open); $("#a-cancel").click();
    ok("empty state offers Crawl for roles first", !!$("#plist [data-emptycrawl]") && $("#sub").textContent === "No roles yet.");
    $("#plist [data-emptycrawl]").click(); ok("empty-state Crawl button opens the Crawl dialog", $("#crawl").open); $("#crx").click();
    $("[data-v=overview]").click();
    ok("tour opens on its own the first time", $("#onb").open);
    ok("tour says it never fills out or submits applications", /never fills out or submits an application for you\. You still apply yourself/.test($("#onb-body").textContent));
    ok("no personal data in the starter (no preset name)", !bad.test(document.body.innerHTML.replace(/<script[\s\S]*?<\/script>/g, "")));

    // --- step 2: name + résumé, no Claude access yet: must degrade gracefully ---
    $("#onb-next").click();
    ok("step 2 shows name and résumé fields", !!$("#o-first") && !!$("#o-resume") && !!$("#o-file"));
    setVal("#o-first", "maria");
    setVal("#o-resume", "Maria Lopez\nSenior Data Analyst, Northwind Labs, 2022-2026. Built weekly Tableau dashboards for finance.");
    $("#onb-next").click();
    await until(() => onb.parse && (onb.parse.err || onb.step === 2), 4000);
    ok("without Claude access the tour explains and does not lose the text", onb.step === 1 && onb.parse && onb.parse.err && /Claude access/.test(onb.parse.msg) && /Maria Lopez/.test($("#o-resume").value), JSON.stringify(onb.parse));
    $("#onb-next").click();
    await until(() => onb.step === 2, 3000);
    ok("Continue anyway moves on and the raw text is kept", onb.step === 2 && /Maria Lopez/.test(onb.a.resume) && !onb.a.resumeData);
    // --- step 3: what you want ---
    setVal("#o-titles", "Data Analyst, BI Analyst");
    $$(".chipbtn").find(b => b.dataset.v === "Hybrid or remote").click();
    setVal("#o-city", "Austin, TX");
    setVal("#o-min", "90"); setVal("#o-target", "110");
    setVal("#o-start", "2026-10-01", "input");
    setVal("#o-avoid", "no crypto");
    $("#onb-next").click();
    ok("step 4 shows three prompts that use this repo's files", onb.step === 3 && $$(".onb-pr").length === 3 && /profile\/strengths\.template\.md/.test($$(".onb-pr pre")[0].textContent) && /tools\/merge_crawl\.py/.test($$(".onb-pr pre")[1].textContent) && /grading\/grade_v2\.py/.test($$(".onb-pr pre")[2].textContent));
    ok("profile prompt writes profile.json and uses the example CSV rule", /profile\/profile\.json/.test($$(".onb-pr pre")[0].textContent) && /tracker\.example\.csv/.test($$(".onb-pr pre")[0].textContent));
    ok("crawl prompt carries the person's criteria and the never-applies rule", /Hybrid or remote \(Austin, TX\)/.test($$(".onb-pr pre")[1].textContent) && /never fills out or submits an application/.test($$(".onb-pr pre")[1].textContent));
    $("#onb-next").click();
    ok("last step summarises what was saved", onb.step === 4 && /Maria/.test($("#onb-body h2").textContent) && /\$90K min/.test($("#onb-body").textContent));
    $("#onb-next").click();
    ok("finishing saves the profile and closes the tour", !$("#onb").open && lsGet("jt-onb-done") === "1" && JSON.parse(lsGet("jt-onb")).first === "maria");
    // --- profile-driven values ---
    ok("first name flows to the pep talks", firstName() === "Maria");
    showPep(); ok("pep talk is signed with the first name", /Maria/.test($("#pepn").textContent) && /Maria/.test($("#pep-msg").textContent)); $("#pep").close();
    const rb = v2rubric();
    ok("rubric uses the person's pay floor and location", /\$90K/.test(rb) && /Austin, TX/.test(rb) && /\$110K/.test(rb), rb.slice(0, 200));
    ok("rubric has no leftover personal values", !/140K|160K/.test(rb) && !bad.test(rb));
    ok("rubric lists target roles and the avoid list", /Data Analyst; BI Analyst/.test(rb) && /no crypto/.test(rb));
    ok("search start date comes from the tour", SS === "2026-10-01");
    $("[data-v=overview]").click();
    ok("timeline says when the search started", /Search timeline, started Oct 1/.test($("#tl").textContent));
    ok("assistant rules use the facts, not anyone else's", /job seeker/.test(chatRules()) && !bad.test(chatRules()) && /No résumé|Résumé text/.test(chatRules()));
    ok("assistant suggestion chip uses the first target role", /Data Analyst role/.test(CHIPS[4]));

    // --- résumé: not yet sectioned, then read with a stub of Claude's sample() ---
    $("[data-v=res]").click();
    ok("Resume tab explains it has the text but needs Claude to read it", /haven't read it into sections/.test($("#resbody").textContent) && !!$("#resbody [data-rs=reparse]"));
    openTailor(allRoles()[0] ? allRoles()[0].id : "none"); // no roles yet: nothing opens
    const R = { name: "Maria Lopez", headline: "Data Analyst · SQL, Tableau", contact: "Austin, TX · maria@example.com", summary: "Data analyst with six years of SQL and Tableau experience.", exp: [{ title: "Senior Data Analyst · Northwind Labs", dates: "2022 – 2026", sub: "", bullets: ["Built weekly dashboards in Tableau for finance.", "Cut report time with SQL automation."] }, { title: "Data Analyst · Fieldnote", dates: "2019 – 2022", sub: "", bullets: ["Maintained the reporting database."] }], skills: [{ label: "Tools", items: ["SQL", "Tableau", "Python"] }], cert: "BS Statistics, 2019" };
    window.claude = { use: async n => n === "sample" ? (async () => ({ text: "```json\n" + JSON.stringify(R) + "\n```" })) : null };
    $("#resbody [data-rs=reparse]").click();
    await until(() => RESUME.exp.length === 2, 4000);
    ok("Re-read my résumé sections it (stubbed Claude)", RESUME.exp.length === 2 && RESUME.exp[0].id === "j1" && RESUME.name === "Maria Lopez");
    ok("Resume tab shows the structured résumé", /Senior Data Analyst/.test($("#resbody").textContent) && !!$("#resbody [data-rs=pdf]"));
    ok("facts now come from the résumé", FACTS.some(f => /Northwind Labs/.test(f)) && FACTS.some(f => /Search terms: minimum base \$90K/.test(f)));
    ok("résumé file names use the person's name", resumeFile() === "Maria_Lopez_Resume");
    const tp = (() => { addRoleForTest(); return tailorPrompt(allRoles()[0], ""); })();
    ok("tailor prompt names the person and the real job ids", /Tailor Maria's résumé/.test(tp) && /"id":"j1"/.test(tp) && /"id":"j2"/.test(tp) && !bad.test(tp) && !/pci/i.test(tp));
    function addRoleForTest() { state.custom.push({ id: "c-test", co: "Test Co", title: "Analyst", url: "", pay: "", level: "", fit: "", tier: 9, src: "manual" }); }
    const cl = clPrompt(allRoles()[0]);
    ok("cover letter prompt signs with the résumé name", /Sign off "Maria Lopez"/.test(cl) && /Hybrid or remote, Austin, TX/.test(cl) && !bad.test(cl));
    state.custom.length = 0;

    // --- add a role: Link, Paste, Manual (all show Not Rated) ---
    $("[data-v=list]").click(); $("#add").click();
    ok("Add a role opens on Link", $("[data-at=link]").getAttribute("aria-selected") === "true");
    setVal("#a-url", "https://example.com/jobs/1"); $("#addform").requestSubmit();
    ok("link role is added as Not Rated with a Claude Code prompt that uses the example CSV", state.custom.length === 1 && /Not Rated/.test($("#plist").textContent) && /tracker\.example\.csv/.test($("#addprompt").textContent) && /never|Do not apply/.test($("#addprompt").textContent));
    $("#a-done").click();
    $("#add").click(); $("[data-at=paste]").click(); setVal("#a-jd", "Senior Analyst\nAcme Corp is hiring.\nMust know SQL."); $("#addform").requestSubmit();
    ok("paste role is added", state.custom.length === 2 && /Must know SQL/.test($("#addprompt").textContent)); $("#a-done").click();
    $("#add").click(); $("[data-at=manual]").click(); setVal("#a-co", "Beta Inc"); setVal("#a-ti", "BI Lead"); setVal("#a-jd", "Lead BI."); $("#addform").requestSubmit();
    ok("manual role is added", state.custom.length === 3 && state.custom[2].co === "Beta Inc"); $("#a-done").click();
    ok("all three show up in Listings, none graded", $$("#plist .pc").length === 3 && $$("#plist .pc").every(c => /Not Rated/.test(c.textContent)));
    ok("detail says Claude Code evaluates them", /Waiting for Claude Code|Not Rated/.test($("#list").textContent));

    // --- Build ideas manager (no built-in ideas in the starter) ---
    $("[data-sheet=bd]").click();
    ok("Build ideas starts with no built-ins", BUILDS.length === 0 && !/Starter concept builds/.test($("#bdbody").textContent) && /Idea 0/.test($("#bdbody .bhead .tags").textContent));
    $("[data-badd]").click(); setVal("[data-bf=title]", "Dashboard case study"); setVal("[data-bf=summary]", "Rebuild a public dashboard."); setVal("[data-bf=status]", "Building", "change"); $("[data-bact=save]").click();
    ok("own idea saves", ownIdeas().length === 1 && ownIdeas()[0].status === "Building");
    const sel = $("select[data-bst=own]"); sel.value = "Done"; sel.dispatchEvent(new Event("change", { bubbles: true }));
    ok("status changes", ownIdeas()[0].status === "Done" && /Done 1/.test($("#bdbody .bhead .tags").textContent));
    $("[data-bedit]").click(); setVal("[data-bf=title]", "Dashboard case study v2"); $("[data-bact=save]").click();
    ok("edit keeps one record", ownIdeas().length === 1 && /v2/.test(ownIdeas()[0].title));
    $("[data-bdel]").click(); $("[data-bdel]").click();
    ok("delete needs two clicks and removes it", ownIdeas().length === 0); $("#shclose").click();

    // --- empty states ---
    $("[data-v=str]").click();
    ok("Strengths & Gaps shows an honest empty state with a prompt", /Nothing to show yet/.test($("#insbody").textContent) && /market-fit-analysis\.md/.test(marketPrompt()) && !!$("#insbody [data-hcopy-market]"));
    ok("market prompt names the profile.json keys the build reads", /"axes"/.test(marketPrompt()) && /"strengths"/.test(marketPrompt()) && /"gaps"/.test(marketPrompt()));
    $("[data-sheet=cl]").click();
    ok("Crawl log shows an empty state and the crawl prompt", /No crawls logged yet/.test($("#clbody").textContent) && /logs\/crawl-log\.json/.test($("#clbody").textContent + taskById("crawl").prompt));
    ok("crawl prompt has the person's criteria and never applies", /Austin, TX/.test(taskById("crawl").prompt) && /never fills out or submits an application/.test(taskById("crawl").prompt) && /tracker\.example\.csv/.test(taskById("crawl").prompt));
    $("#shclose").click();
    $("[data-sheet=qc]").click();
    ok("Quick copy starts from the profile (salary, location)", /\$110,000 base/.test($("#snipbody").textContent) && /remotely or hybrid from Austin, TX/.test($("#snipbody").textContent));
    $("[data-sx=add]").click(); $("[data-sx=save]").click();
    ok("snippet form validates", /name and some text/.test($("#snipbody").textContent));
    setVal("[data-sf=label]", "Portfolio"); setVal("[data-sf=text]", "https://example.com/me"); $("[data-sx=save]").click();
    ok("own snippet is added under Yours", /Yours/.test($("#snipbody").textContent) && /Portfolio/.test($("#snipbody").textContent));
    const mine = $$("#snipbody .sn").find(n => /Portfolio/.test(n.textContent)); mine.querySelector("[data-a=edit]").click();
    ok("custom snippet offers Delete", /Delete/.test(mine.textContent)); mine.querySelector("[data-a=reset]").click();
    ok("delete removes it", !/Portfolio/.test($("#snipbody").textContent)); $("#shclose").click();
    $("[data-sheet=hp]").click();
    ok("Help says it never fills out or submits applications", /never fills out or submits an application for you/.test($("#hpbody").textContent) && !/~\/job-search/.test($("#hpbody").textContent));
    ok("Help has the Claude Code guide link", !!$("#hpbody [data-ccg]")); $("#shclose").click();

    // --- global top bar and the Crawl dialog ---
    {
      const views = { overview: "Overview", list: "Listings", str: "Strengths & Gaps", res: "Resume", chat: "Assistant" };
      ok("top bar title follows the page", Object.entries(views).every(([v, t]) => ($("[data-v=" + v + "]").click(), $("#tbt").textContent === t)));
      $("[data-v=overview]").click();
      ok("top bar holds search, Add a role, Crawl and the menu", !!$("#topbar #q") && !!$("#topbar #add") && !!$("#topbar #crawlbtn") && !!$("#topbar #tbmore") && !$("#tab-list #q") && !$("#tab-list #add"));
      ok("a build with no crawl log says it has not crawled yet", /Not crawled yet/.test($("#tblast").textContent) && $("#tblast").dataset.stale === "0");
      ok("Crawl opens and closes from every page", Object.keys(views).every(v => { $("[data-v=" + v + "]").click(); $("#crawlbtn").click(); const o = $("#crawl").open; $("#crx").click(); return o && !$("#crawl").open; }));
      $("[data-v=overview]").click(); $("#add").click(); ok("Add a role opens from Overview", $("#dlg").open); $("#a-cancel").click();
      $("#crawlbtn").click();
      const P = () => $("#cq-pre").textContent;
      ok("default prompt covers job boards, Gmail and Slack, read-only", /Job boards/.test(P()) && /Gmail \(read-only connector\)/.test(P()) && /Slack \(read-only connector\)/.test(P()) && /never send, reply, forward, label, delete, react or post/.test(P()) && /never fills out or submits an application/.test(P()));
      ok("prompt carries the profile criteria and no personal data", /Austin, TX/.test(P()) && !bad.test(P()));
      ok("with no crawl logged the window is 30 days", /in the last 30 days/.test(P()) && $("#cq-w-since").textContent === "Last 30 days");
      $("#crawl [data-src=gmail]").click();
      ok("unchecking Gmail takes it out of the prompt", !/Gmail \(read-only/.test(P()) && /Slack \(read-only/.test(P()));
      $("#crawl [data-win='24h']").click();
      ok("the time window changes the prompt", /in the last 24 hours/.test(P()) && $("#crawl [data-win='24h']").getAttribute("aria-checked") === "true");
      setVal("#cq-slack", "#jobs, #leads"); setVal("#cq-other", "Google Drive");
      ok("Slack channels and other connectors reach the prompt", /these channels \(#jobs, #leads\)/.test(P()) && /Google Drive/.test(P()) && /Lane: other/.test(P()));
      ok("choices are remembered for next time", (() => { try { const o = JSON.parse(localStorage.getItem("jt-crawl-opts")); return o.win === "24h" && o.gmail === false && o.slackCh === "#jobs, #leads"; } catch (e) { return false; } })());
      $("#crawl [data-src=boards]").click(); $("#crawl [data-src=slack]").click(); setVal("#cq-other", "");
      ok("with nothing chosen the prompt is empty and Copy is disabled", $("#cq-copy").disabled && /Pick at least one/.test(P()));
      $("#crawl [data-src=boards]").click();
      ok("job boards alone gives the same text as the Help crawl prompt", !$("#cq-copy").disabled && crawlPrompt({ when: "since [DATE]" }) === taskById("crawl").prompt && !/Gmail|Slack/.test(taskById("crawl").prompt));
      $("#crx").click();
      Object.assign(cq, { boards: true, gmail: true, slack: true, slackCh: "", otherTxt: "", win: "since" }); cqSave();
      // search from any page
      $("[data-v=overview]").click(); setVal("#q", "Beta");
      ok("search from Overview jumps to Listings and filters", state.view === "list" && $$("#plist .pc").length === 1 && /Beta Inc/.test($("#plist").textContent));
      ok("the search shows as one chip, and Clear all appears only with two or more filters", /Search: \u201cBeta\u201d/.test($("#fbar").textContent) && !$("#fbar [data-clear=all]") && /1 of 3 roles/.test($("#fbar").textContent));
      ok("tab counts follow the search", $("#tabs [data-t=none]").textContent === "Not Rated1" && $("#tabs [data-t='0']").textContent === "Any match1");
      setVal("#q", "");
      // more menu
      $("#tbmore").click();
      ok("more menu opens with the tour and the theme switch", !$("#tbmenu").hidden && $("#tbmore").getAttribute("aria-expanded") === "true" && !!$("#tbmenu #onb-open") && $$("#tbmenu [data-theme-set]").length === 3);
      ok("the menu is Settings, with a gear icon", $("#tbmore").getAttribute("aria-label") === "Settings" && !!$("#tbmore svg circle[r='3']") && !$("#tbmore svg circle[r='1.6']"));
      ok("the hourly pep talk switch lives in Settings and Send me one now is gone", !!$("#tbmenu #pep-on") && !$(".sidebar #pep-on") && !$("#pep-now") && !/Send me one now/.test($("#tbmenu").textContent));
      ok("the side nav bottom shows the version and no update notice when current", /^Version \d+\.\d+/.test($(".sidebar #verl").textContent) && $("#updn").hidden);
      APP_BUILD.behind = 2; APP_BUILD.latest = "9.9.9"; renderVersion();
      ok("an Update available note appears when the build says it is behind", !$("#updn").hidden && /9\.9\.9/.test($("#updv").textContent));
      APP_BUILD.notice = { checked: "2026-11-12", changes: ["Fixture change one.", "Fixture change two."], steps: ["Fixture step."] }; $("#updn").click();
      ok("the update button opens a modal with what Claude read from the repo and a copy button", $("#upd").open && /1\.1\.0/.test($("#updlead").textContent) && /9\.9\.9/.test($("#upd").textContent) && $$("#updlist li").length === 2 && /Fixture step/.test($("#updsteps").textContent) && /Copy update prompt/.test($("#updcopy").textContent) && /Open Claude Code in your project folder/.test($("#upd").textContent)); $("#upd").close(); delete APP_BUILD.notice;
      ok("the update prompt pulls, explains the changelog and rebuilds without touching your data", /git pull/.test(updatePrompt()) && /CHANGELOG\.md/.test(updatePrompt()) && /Do not change tracker\.csv/.test(updatePrompt()));
      APP_BUILD.behind = 0; APP_BUILD.latest = ""; renderVersion();
      ok("every Claude Code prompt starts with the read-only update check", [crawlPrompt(), marketPrompt(), TASKS.filter(x => x.where === "claude-code").map(x => x.prompt).join("\n")].every(x => /tools\/check_update\.py/.test(x)) && TASKS.filter(x => x.where === "claude-code").every(x => x.prompt.startsWith("First, check whether this tracker has an update")) && onbPrompts().every(x => x.p.startsWith("First, check whether this tracker has an update")));
      {
        setView("list"); state.q = ""; savePlace();
        const saved = JSON.parse(localStorage.getItem("jt-place") || "null");
        ok("the place you were at is saved", saved && saved.v === "list");
        setView("overview"); placeDone = false; placeData = null; applyPlace();
        ok("coming back restores the screen you were on", state.view === "list" && !$("#tab-list").hidden);
        setView("overview");
      }
      $("#tbmore").click();
      document.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape", bubbles: true }));
      ok("Escape closes the menu", $("#tbmenu").hidden && $("#tbmore").getAttribute("aria-expanded") === "false");
      $("#tbmore").click(); $("#onb-open").click();
      ok("Welcome tour opens from the menu and the menu closes", $("#onb").open && $("#tbmenu").hidden); $("#onb-skip").click();
      $("[data-v=overview]").click();
    }

    // --- theme, guide, upload ---
    $("[data-theme-set=dark]").click(); ok("theme switch works", document.documentElement.dataset.theme === "dark"); $("[data-theme-set=auto]").click();
    openCcg(); ok("Claude Code guide opens", $("#ccg").open && /npm install/.test($("#ccg").textContent)); $("#ccg-x").click();
    openOnb(1);
    const pick = async file => { const dt = new DataTransfer(); dt.items.add(file); const i = $("#o-file"); i.files = dt.files; i.dispatchEvent(new Event("change", { bubbles: true })); await until(() => !(onb.f && onb.f.busy)); };
    await pick(new File(["Jordan Lee\nProduct Manager with eight years of experience shipping software for small teams.\nSkills: roadmaps, SQL."], "cv.txt", { type: "text/plain" }));
    ok("upload: .txt fills the box", /Jordan Lee/.test($("#o-resume").value));
    const z = new JSZip(); z.file("word/document.xml", '<w:document><w:body><w:p><w:r><w:t>Sam Park</w:t></w:r></w:p><w:p><w:r><w:t>Engineer &amp; tech lead with nine years of experience building web services.</w:t></w:r></w:p></w:body></w:document>');
    await pick(new File([await z.generateAsync({ type: "blob" })], "cv.docx"));
    ok("upload: .docx fills the box", /Sam Park\nEngineer & tech lead/.test($("#o-resume").value));
    const doc = new jspdf.jsPDF(); doc.text("Riley Chen", 10, 20); doc.text("Support engineer with seven years of experience in SaaS.", 10, 30);
    await pick(new File([doc.output("blob")], "cv.pdf", { type: "application/pdf" }));
    ok("upload: .pdf fills the box", /Riley Chen/.test($("#o-resume").value));
    await pick(new File([new Uint8Array(10)], "cv.pages"));
    ok("upload: unsupported type gives export advice", onb.f.err && /PDF or Word/.test(onb.f.msg));
    $("#onb-skip").click();
    ok("the tour does not come back after it was finished", lsGet("jt-onb-done") === "1");
  } catch (e) { window.__R.push("FAIL exception: " + e.message + " " + ((e.stack || "").split("\n")[1] || "")); }
  finish();
})();
