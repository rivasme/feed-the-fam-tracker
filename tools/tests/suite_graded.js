/* Suite 2: a build with one graded role, a profile.json, strengths/gaps/axes and one crawl-log entry. No tour. */
(async () => {
  const { ok, $, $$, wait, until, setVal, finish, bad } = window.__T;
  try {
    ok("the role comes from tracker.csv", ROLES.length === 1 && ROLES[0].co === "Acme Analytics");
    ok("profile.json reaches the page (first name, pay floor)", pfirst() === "Maria" && numK(PROFILE().min) === 90);
    ok("search start comes from profile.json", SS === "2026-10-01");
    ok("tour is off in this build", !$("#onb").open);
    const rb = v2rubric();
    ok("rubric uses profile.json values", /\$90K/.test(rb) && /Austin, TX/.test(rb) && /\$110K/.test(rb) && /Data Analyst/.test(rb) && !/140K/.test(rb) && !bad.test(rb));
    $("[data-v=list]").click();
    ok("listing shows the role as a preview card", $$("#plist .pc").length === 1 && /Acme Analytics/.test($("#plist").textContent) && /Senior Data Analyst/.test($("#plist").textContent));
    ok("match tag is computed from the grades", /Match: .*(Apply now|Consider|Research first|Skip)/.test($("#plist .pc .mtag").textContent), $("#plist .pc").textContent);
    ok("card shows the status pill top right and the match tag in the bottom row", /Not applied|New/i.test($("#plist .pc .r1 .badge.st").textContent) && !!$("#plist .pc .r3 .mtag"));
    ok("Fit, Opportunity and Confidence chips render", $$("#list .sc").length === 3 && /Fit/.test($("#list .score").textContent) && /Opportunity/.test($("#list .score").textContent));
    ok("gates summary renders", /gates pass|gates not passed/.test($("#list details.gates summary").textContent));
    ok("strengths-and-gaps web has 8 axes", $$("#list .jweb .wd").length === 8 && /Skills/.test($("#list .jweb").textContent));
    ok("why, matched strengths and gaps show", /Why/.test($("#list").textContent) && /dashboards in Tableau|SQL/.test($("#list").textContent) && /No dbt experience/.test($("#list").textContent));
    ok("the AI note is read-only and your notes are separate", !!$(".ainote") && !$(".ainote textarea") && !!$("[data-k=pnotes]"));
    ok("New tag comes from the crawl note", /New/.test($("#list .tags").textContent));
    ok("detail has Tailor, Letter and Ask buttons", !!$("[data-tailor]") && !!$("[data-cover]") && !!$("[data-ask]"));
    $("[data-tailor]").click();
    ok("without a résumé, Tailor asks for one instead of failing", /Add your résumé first/.test($("#trbody").textContent)); $("#shclose").click();
    // status is a fact (solid pill), match is a suggestion (dashed tag) and fades once you act on the role
    {
      const r0 = ROLES[0], tag = () => $("#plist .pc .mtag"), hdr = () => $("#list .head .badge.st");
      ok("fixture role is graded Apply now and not yet applied", decisionOf(r0) === "apply" && statusOf(r0.id) === "new" && /Apply now/.test(tag().textContent) && !tag().classList.contains("done"), tag().textContent);
      ok("detail header shows the status pill and the match tag", !!hdr() && !!$("#list .meta .mtag"));
      const sel = $("[data-k=status]"); sel.value = "applied"; sel.dispatchEvent(new Event("change", { bubbles: true }));
      await new Promise(r => setTimeout(r, 300));
      ok("status is now Applied", statusOf(r0.id) === "applied");
      ok("the card status pill says Applied and the match tag stays but fades", /Applied/.test($("#plist .pc .r1 .badge.st").textContent) && /Apply now/.test(tag().textContent) && tag().classList.contains("done"), $("#plist .pc").textContent);
      ok("the grade still shows Fit and Opportunity", /Fit/.test($("#list .score").textContent) && /Opportunity/.test($("#list .score").textContent));
      const sel2 = $("[data-k=status]"); sel2.value = "new"; sel2.dispatchEvent(new Event("change", { bubbles: true }));
      await new Promise(r => setTimeout(r, 300));
      ok("match tag is full strength again when the role is set back to Not applied", !tag().classList.contains("done"), tag().className);
    }
    ok("role file feeds the page a condensed summary and the full posting", /Must-haves: SQL, Tableau/.test(ROLES[0].post) && !/Full posting/.test(ROLES[0].post) && /Full posting: Acme/.test(ROLES[0].full));
    // KPI filters
    $("[data-v=overview]").click();
    ok("Overview KPI cards are display-only", $$("#stats .stat").length === 9 && $$("#stats button").length === 0);
    $("[data-v=list]").click();
    ok("Listings status cards filter (7 cards, plus Interviewed and Not heard back as chips)", $$("#stats2 button.stat").length === 7 && $$("#subf [data-f]").length === 2);
    // Listings filters: Status cards and Match tabs are separate, labelled and count each other
    {
      const T = t => $("#tabs [data-t='" + t + "']"), C = f => $("#stats2 [data-f='" + f + "']");
      const fb = () => $("#fbar").textContent, rows = () => $$("#plist .pc").length, wait2 = () => new Promise(r => setTimeout(r, 150));
      $("[data-v=list]").click();
      ok("Listings labels its two filters Status and Match", /Status/.test($("#tab-list .frow .flab").textContent) && /Match/.test($("#tab-list .bar .flab").textContent));
      ok("the first tab says Any match and the first card says Any status", /^Any match/.test(T("0").textContent) && /Any status/.test(C("all").textContent));
      ok("tabs carry counts", T("0").textContent === "Any match1" && T("apply").textContent === "Apply now1" && T("consider").textContent === "Consider0");
      ok("an empty tab is dimmed, a selected one is not", T("consider").classList.contains("zero") && !T("0").classList.contains("zero"));
      ok("results line counts the list and shows no chips with no filters", /1 of 1 role/.test(fb()) && !$("#fbar .fchip"));
      T("consider").click();
      ok("choosing a match tab updates the status card counts", C("new").textContent.startsWith("0") && C("new").classList.contains("zero") && /Match: Consider/.test(fb()) && /0 of 1 role/.test(fb()));
      ok("sort stays visible on every tab", !$("#sortwrap").hidden);
      ok("empty result offers Clear all filters", /No roles match these filters/.test($("#plist").textContent) && !!$("#plist [data-clear=all]"));
      $("#plist [data-clear=all]").click();
      ok("Clear all filters resets the tab", state.tier === "0" && state.filter === "all" && rows() === 1);
      C("applied").click();
      ok("a status card filter is shown as a chip and the tab counts follow it", state.filter === "applied" && /Status: Applied/.test(fb()) && T("apply").textContent === "Apply now0" && rows() === 0);
      $("#fbar [data-clear=status]").click();
      ok("clearing the status chip brings the role back", state.filter === "all" && rows() === 1 && !$("#fbar .fchip"));
      // Apply now is a match tab only: it still lists a role you applied to, and the status card narrows it
      const sel = $("[data-k=status]"); sel.value = "applied"; sel.dispatchEvent(new Event("change", { bubbles: true })); await wait2();
      T("apply").click();
      ok("Apply now tab still lists a role after you applied", rows() === 1 && T("apply").textContent === "Apply now1");
      C("applied").click();
      ok("Apply now plus Applied is no longer an empty combination", rows() === 1 && /Status: Applied/.test(fb()) && /Match: Apply now/.test(fb()) && !!$("#fbar [data-clear=all]"));
      C("new").click();
      ok("Apply now plus Not applied is empty once you applied", rows() === 0 && C("new").getAttribute("aria-pressed") === "true");
      $("#fbar [data-clear=all]").click();
      ok("Clear all resets status and match together", state.filter === "all" && state.tier === "0" && rows() === 1);
      $("#subf [data-f=noreply]").click();
      ok("Not heard back is a chip under Status and shows in the filter line", rows() === 1 && /Status: Not heard back/.test(fb()) && $("#subf [data-f=noreply]").getAttribute("aria-pressed") === "true");
      $("#subf [data-f=noreply]").click();
      ok("clicking the chip again turns it off", state.filter === "all");
      setVal("#q", "zzz");
      ok("a search shows as a chip too", /Search: \u201czzz\u201d/.test(fb()) && rows() === 0);
      $("#fbar [data-clear=q]").click();
      ok("clearing the search chip empties the box", state.q === "" && $("#q").value === "" && rows() === 1);
      const s2 = $("[data-k=status]"); s2.value = "new"; s2.dispatchEvent(new Event("change", { bubbles: true })); await wait2();
      ok("status is back to Not applied", statusOf(ROLES[0].id) === "new");
    }
    // role detail: Status field, helper actions, one primary action, matching note cards
    {
      $("[data-v=list]").click();
      const R = e => $(e).getBoundingClientRect();
      ok("detail has an action bar: Status field plus helper actions", !!$(".dbar .dstat [data-k=status]") && !!$(".dbar .dacts [data-tailor]") && !!$(".dbar .dacts [data-cover]") && !!$(".dbar .dacts [data-ask]"));
      ok("Open posting is the single primary button and opens in a new tab", $$(".dbar .btn.pri").length === 1 && /^Open posting/.test($(".dbar .btn.pri").textContent.trim()) && /example\.com/.test($(".dbar .btn.pri").href) && $(".dbar .btn.pri").target === "_blank" && /noopener/.test($(".dbar .btn.pri").rel));
      ok("helper actions are not primary", $$(".dbar .dacts .btn").length >= 3 && $$(".dbar .dacts .btn").every(b => !b.classList.contains("pri")));
      $(".dbar").style.width = "700px";
      ok("Open posting sits on the right of the Status row, helpers on the row below", Math.abs(R(".dopen").right - R(".dbar").right) < 2 && R(".dopen").top < R(".dacts").top && R(".dstat").top <= R(".dopen").bottom && R(".dstat").left < R(".dopen").left);
      $(".dbar").style.width = "";
      ok("both notes are cards with the same header structure", $$(".notes2 .ncard").length === 2 && /Left by Claude/.test($(".ainote .nh").textContent) && /Your notes/.test($(".mynote .nh").textContent) && !!$(".mynote textarea[data-k=pnotes]") && !$(".ainote textarea"));
      $(".notes2").style.width = "720px";
      ok("Left by Claude and Your notes sit side by side with the same height", Math.abs(R(".ainote").top - R(".mynote").top) < 2 && Math.abs(R(".ainote").height - R(".mynote").height) < 2 && R(".ainote").right <= R(".mynote").left + 1);
      $(".notes2").style.width = "";
      const tx = $(".mynote textarea"); tx.value = "Called the recruiter"; tx.dispatchEvent(new Event("input", { bubbles: true })); tx.dispatchEvent(new FocusEvent("focusout", { bubbles: true }));
      await new Promise(r => setTimeout(r, 150));
      ok("typing in Your notes still saves", myNote(ROLES[0].id) === "Called the recruiter");
      tx.value = ""; tx.dispatchEvent(new Event("input", { bubbles: true })); tx.dispatchEvent(new FocusEvent("focusout", { bubbles: true }));
      await new Promise(r => setTimeout(r, 150));
    }
    // Strengths & gaps from profile.json
    $("[data-v=str]").click();
    ok("radar renders from profile.json axes", !!$("#radar") && $$("#radar .rd").length === 4 && /Evidence strength/.test($("#insbody").textContent));
    ok("strengths and gaps lists come from profile.json", /Strengths \(2\)/.test($("#insbody").textContent) && /SQL and Tableau/.test($("#insbody").textContent));
    $("[data-ins=g]").click(); ok("gaps tab", /No dbt/.test($("#insbody").textContent));
    // crawl log from logs/crawl-log.json
    $("[data-sheet=cl]").click();
    ok("crawl log entry from logs/crawl-log.json renders", /Nov 1, 2026/.test($("#clbody").textContent) && /Fixture crawl/.test($("#clbody").textContent) && /Example board/.test($("#clbody").textContent));
    $("#shclose").click();
    // top bar status and the Crawl dialog read the crawl log
    ok("top bar shows when you last crawled", /Last crawled/.test($("#tblast").textContent), $("#tblast").textContent);
    $("#crawlbtn").click();
    ok("Crawl dialog starts from the last logged crawl", /since 2026-11-01/.test($("#cq-pre").textContent) && $("#cq-w-since").textContent === "Since last crawl" && /Nov 1, 2026/.test($("#cq-wl").textContent));
    ok("Crawl prompt uses the profile and has no personal data", /Austin, TX/.test($("#cq-pre").textContent) && !bad.test($("#cq-pre").textContent));
    $("#crx").click();
    $("[data-v=overview]").click(); setVal("#q", "zzzz");
    ok("search from Overview with no match shows no roles", state.view === "list" && $$("#plist .pc").length === 0);
    setVal("#q", "Acme"); ok("search finds the role", $$("#plist .pc").length === 1); setVal("#q", "");
    // facts and prompts
    ok("assistant facts include the profile facts", FACTS.some(f => /Search terms: minimum base \$90K/.test(f)) && FACTS.some(f => /Fixture fact/.test(f)));
    ok("Regrade prompt text has no personal data", !bad.test(chatRules() + v2rubric() + FACTS.join(" ")));
    ok("Overview timeline starts on the profile date", (($("[data-v=overview]").click(), $("#tl").textContent)).includes("started Oct 1"));
  } catch (e) { window.__R.push("FAIL exception: " + e.message + " " + ((e.stack || "").split("\n")[1] || "")); }
  finish();
})();
