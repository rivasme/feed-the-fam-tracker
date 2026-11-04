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
    ok("decision pill is computed from the grades", /Apply now|Consider|Research first|Skip/.test($("#plist .pc .badge.gr").textContent), $("#plist .pc").textContent);
    ok("Fit, Opportunity and Confidence chips render", $$("#list .sc").length === 3 && /Fit/.test($("#list .score").textContent) && /Opportunity/.test($("#list .score").textContent));
    ok("gates summary renders", /gates pass|gates not passed/.test($("#list details.gates summary").textContent));
    ok("strengths-and-gaps web has 8 axes", $$("#list .jweb .wd").length === 8 && /Skills/.test($("#list .jweb").textContent));
    ok("why, matched strengths and gaps show", /Why/.test($("#list").textContent) && /dashboards in Tableau|SQL/.test($("#list").textContent) && /No dbt experience/.test($("#list").textContent));
    ok("the AI note is read-only and your notes are separate", !!$(".ainote") && !$(".ainote textarea") && !!$("[data-k=pnotes]"));
    ok("New tag comes from the crawl note", /New/.test($("#list .tags").textContent));
    ok("detail has Tailor, Letter and Ask buttons", !!$("[data-tailor]") && !!$("[data-cover]") && !!$("[data-ask]"));
    $("[data-tailor]").click();
    ok("without a résumé, Tailor asks for one instead of failing", /Add your résumé first/.test($("#trbody").textContent)); $("#shclose").click();
    // "Apply now" badge goes away once a role is applied to
    {
      const r0 = ROLES[0], badges = () => $$("#list .pc .badge.gr, #list .head .badge.gr").map(b => b.textContent).join("|");
      ok("fixture role is graded Apply now and not yet applied", decisionOf(r0) === "apply" && statusOf(r0.id) === "new" && /Apply now/.test(badges()), badges());
      const sel = $("[data-k=status]"); sel.value = "applied"; sel.dispatchEvent(new Event("change", { bubbles: true }));
      await new Promise(r => setTimeout(r, 300));
      ok("status is now Applied", statusOf(r0.id) === "applied");
      ok("Apply now badge is hidden on the card and the detail header after applying", !/Apply now/.test(badges()), badges());
      ok("the grade still shows Fit and Opportunity", /Fit/.test($("#list .score").textContent) && /Opportunity/.test($("#list .score").textContent));
      const sel2 = $("[data-k=status]"); sel2.value = "new"; sel2.dispatchEvent(new Event("change", { bubbles: true }));
      await new Promise(r => setTimeout(r, 300));
      ok("badge comes back when the role is set back to Not applied", /Apply now/.test(badges()), badges());
    }
    // KPI filters
    $("[data-v=overview]").click();
    ok("Overview KPI cards are display-only", $$("#stats .stat").length === 9 && $$("#stats button").length === 0);
    $("[data-v=list]").click();
    ok("Listings KPI cards filter", $$("#stats2 button.stat").length === 9);
    // Strengths & gaps from profile.json
    $("[data-v=str]").click();
    ok("radar renders from profile.json axes", !!$("#radar") && $$("#radar .rd").length === 4 && /Evidence strength/.test($("#insbody").textContent));
    ok("strengths and gaps lists come from profile.json", /Strengths \(2\)/.test($("#insbody").textContent) && /SQL and Tableau/.test($("#insbody").textContent));
    $("[data-ins=g]").click(); ok("gaps tab", /No dbt/.test($("#insbody").textContent));
    // crawl log from logs/crawl-log.json
    $("[data-sheet=cl]").click();
    ok("crawl log entry from logs/crawl-log.json renders", /Nov 1, 2026/.test($("#clbody").textContent) && /Fixture crawl/.test($("#clbody").textContent) && /Example board/.test($("#clbody").textContent));
    $("#shclose").click();
    // facts and prompts
    ok("assistant facts include the profile facts", FACTS.some(f => /Search terms: minimum base \$90K/.test(f)) && FACTS.some(f => /Fixture fact/.test(f)));
    ok("Regrade prompt text has no personal data", !bad.test(chatRules() + v2rubric() + FACTS.join(" ")));
    ok("Overview timeline starts on the profile date", (($("[data-v=overview]").click(), $("#tl").textContent)).includes("started Oct 1"));
  } catch (e) { window.__R.push("FAIL exception: " + e.message + " " + ((e.stack || "").split("\n")[1] || "")); }
  finish();
})();
