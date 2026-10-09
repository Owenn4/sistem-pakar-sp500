// Sistem Pakar S&P 500 - Editorial Frontend Controller

const PRESETS = {
  ratecut: {
    headlines: [
      "Fed signals rate cut to support economic growth",
      "Central bank monetary easing lifts Wall Street stocks",
      "Markets rally as lower interest rates boost optimism"
    ],
    trend: 0.015,
    vol: 0.010,
    prev_sent: 0.00
  },
  inflation: {
    headlines: [
      "Inflation is not easing as Fed hikes interest rates again",
      "Rising consumer prices squeeze corporate profits and factories",
      "Bond yields surge as aggressive tightening threatens growth"
    ],
    trend: -0.015,
    vol: 0.014,
    prev_sent: 0.02
  },
  contrarian: {
    headlines: [
      "Stocks plunge in worst rout since 2008 as recession fears spread",
      "Wall Street tumbles on panic selling, market crashes to multi-year low"
    ],
    trend: -0.085,
    vol: 0.024,
    prev_sent: 0.00
  },
  calm: {
    headlines: [
      "Stocks little changed ahead of quarterly earnings report",
      "Trading volume quiet in afternoon session",
      "Markets steady as investors review calm economic calendar"
    ],
    trend: 0.000,
    vol: 0.004,
    prev_sent: 0.00
  },
  conflict: {
    headlines: [
      "Economy shrinks as banks report heavy losses",
      "Dow drops as investors worry about slowing global growth"
    ],
    trend: -0.035,
    vol: 0.012,
    prev_sent: 0.02
  }
};

let debounceTimer = null;
let allRulesData = [];

document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  initSliders();
  loadRules();
  loadTestCases();
  loadUnitTests();
  loadBenchmarks();
  loadHistoricalEvents();
  
  // Default scenario
  loadPreset('ratecut');
});

// Theme Management
function initTheme() {
  const saved = localStorage.getItem("sp_editorial_theme");
  if (saved === "dark") {
    document.documentElement.classList.add("dark");
    document.getElementById("theme-icon-sun").classList.remove("hidden");
    document.getElementById("theme-icon-moon").classList.add("hidden");
  } else {
    document.documentElement.classList.remove("dark");
    document.getElementById("theme-icon-sun").classList.add("hidden");
    document.getElementById("theme-icon-moon").classList.remove("hidden");
  }
}

function toggleDarkMode() {
  const isDark = document.documentElement.classList.toggle("dark");
  localStorage.setItem("sp_editorial_theme", isDark ? "dark" : "light");
  document.getElementById("theme-icon-sun").classList.toggle("hidden", !isDark);
  document.getElementById("theme-icon-moon").classList.toggle("hidden", isDark);
}

// Navigation Tabs
function switchTab(tabId) {
  document.querySelectorAll(".tab-content").forEach(el => el.classList.add("hidden"));
  document.getElementById(`tab-${tabId}`).classList.remove("hidden");

  document.querySelectorAll(".tab-btn").forEach(btn => {
    btn.classList.remove("active-tab", "text-[#121212]", "dark:text-white", "bg-white", "dark:bg-[#262A34]");
    btn.classList.add("text-[#6E6D6A]", "dark:text-[#9E9D99]");
  });

  const activeBtn = document.getElementById(`tab-btn-${tabId}`);
  if (activeBtn) {
    activeBtn.classList.add("active-tab", "text-[#121212]", "dark:text-white", "bg-white", "dark:bg-[#262A34]");
    activeBtn.classList.remove("text-[#6E6D6A]", "dark:text-[#9E9D99]");
  }
}

// Presets
function loadPreset(name) {
  const p = PRESETS[name];
  if (!p) return;
  document.getElementById("input-headlines").value = p.headlines.join("\n");
  document.getElementById("input-trend").value = p.trend;
  document.getElementById("input-vol").value = p.vol;
  document.getElementById("input-prevsent").value = p.prev_sent;
  updateSliderLabels();
  runAnalysis();
}

function clearHeadlines() {
  document.getElementById("input-headlines").value = "";
  runAnalysis();
}

// Sliders and Inputs
function initSliders() {
  updateSliderLabels();
  ["input-trend", "input-vol", "input-prevsent"].forEach(id => {
    document.getElementById(id).addEventListener("input", () => {
      updateSliderLabels();
      triggerDebouncedAnalysis();
    });
  });
  document.getElementById("input-headlines").addEventListener("input", triggerDebouncedAnalysis);
  document.getElementById("check-filler").addEventListener("change", runAnalysis);
}

function updateSliderLabels() {
  const tr = parseFloat(document.getElementById("input-trend").value);
  const vo = parseFloat(document.getElementById("input-vol").value);
  const ps = parseFloat(document.getElementById("input-prevsent").value);

  const trTag = tr <= -0.06 ? 'oversold' : tr <= -0.02 ? 'down' : tr >= 0.05 ? 'overextended' : tr >= 0.02 ? 'up' : 'flat';
  document.getElementById("label-trend-val").textContent = `${(tr * 100).toFixed(1)}% (${trTag})`;

  const voTag = vo >= 0.018 ? 'high' : vo <= 0.006 ? 'low' : 'normal';
  document.getElementById("label-vol-val").textContent = `${vo.toFixed(3)} (${voTag})`;

  const psTag = ps <= -0.02 ? 'pesimis' : ps >= 0.02 ? 'optimis' : 'stable';
  document.getElementById("label-prevsent-val").textContent = `${ps >= 0 ? '+' : ''}${ps.toFixed(2)} (${psTag})`;
}

function triggerDebouncedAnalysis() {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(runAnalysis, 180);
}

// Inference Engine API Call
async function runAnalysis() {
  const text = document.getElementById("input-headlines").value;
  const headlines = text.split("\n").map(s => s.trim()).filter(s => s.length > 0);
  const trend = parseFloat(document.getElementById("input-trend").value);
  const volatility = parseFloat(document.getElementById("input-vol").value);
  const prev_sentiment = parseFloat(document.getElementById("input-prevsent").value);
  const use_filler = document.getElementById("check-filler").checked;

  try {
    const res = await fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        headlines,
        trend,
        volatility,
        prev_sentiment,
        use_filler
      })
    });
    const data = await res.json();
    renderAnalysisResult(data);
  } catch (err) {
    console.error("Error executing infer:", err);
  }
}

// Render Results with Minimalist Badges & Clean Spot Pastels
function renderAnalysisResult(data) {
  const dec = data.decision;
  const cf = data.certainty_factors;
  const trace = data.trace;

  // 1. Hero Decision Badge
  const badge = document.getElementById("badge-decision");
  const badgeText = document.getElementById("badge-decision-text");
  const badgeDot = document.getElementById("badge-dot-indicator");
  const cfText = document.getElementById("badge-cf-text");

  badge.className = "text-2xl font-mono font-bold px-3 py-1 rounded border inline-flex items-center space-x-2 ";
  badgeDot.className = "w-2.5 h-2.5 rounded-full ";

  if (dec === "BUY") {
    badge.classList.add("badge-buy");
    badgeDot.classList.add("bg-[#2B6434]", "dark:bg-[#88C493]");
    badgeText.textContent = "BUY";
  } else if (dec === "HOLD") {
    badge.classList.add("badge-hold");
    badgeDot.classList.add("bg-[#8C5E00]", "dark:bg-[#D8A63A]");
    badgeText.textContent = "HOLD";
  } else if (dec === "SELL") {
    badge.classList.add("badge-sell");
    badgeDot.classList.add("bg-[#9F2F2D]", "dark:bg-[#DE7775]");
    badgeText.textContent = "SELL";
  }
  cfText.textContent = (cf[dec] || 0.00).toFixed(2);
  document.getElementById("resolution-reason-text").textContent = trace.resolution_reason;

  // 2. CF Compound Progress Bars
  const buyVal = cf.BUY || 0;
  const holdVal = cf.HOLD || 0;
  const sellVal = cf.SELL || 0;

  document.getElementById("val-cf-buy").textContent = buyVal.toFixed(2);
  document.getElementById("val-cf-hold").textContent = holdVal.toFixed(2);
  document.getElementById("val-cf-sell").textContent = sellVal.toFixed(2);

  document.getElementById("bar-cf-buy").style.width = `${Math.min(100, buyVal * 100)}%`;
  document.getElementById("bar-cf-hold").style.width = `${Math.min(100, holdVal * 100)}%`;
  document.getElementById("bar-cf-sell").style.width = `${Math.min(100, sellVal * 100)}%`;

  // 3. Linguistic Facts Chips
  const factsContainer = document.getElementById("facts-chips-container");
  factsContainer.innerHTML = "";
  const lf = data.linguistic_facts;
  for (const [key, val] of Object.entries(lf)) {
    let colorClass = "bg-[#F0EFEA] text-[#6E6D6A] border-[#EAEAEA] dark:bg-[#1A1E26] dark:text-[#A8A7A3] dark:border-[#2A2E38]";
    if (val === "very_neg" || val === "neg" || val === "oversold" || val === "high") {
      colorClass = "bg-[#FDEBEC] text-[#9F2F2D] border-[#F9D2D4] dark:bg-[rgba(159,47,45,0.18)] dark:text-[#DE7775] dark:border-[rgba(230,133,131,0.3)]";
    } else if (val === "very_pos" || val === "pos" || val === "improving") {
      colorClass = "bg-[#EDF3EC] text-[#2B6434] border-[#D2E3D1] dark:bg-[rgba(43,100,52,0.18)] dark:text-[#88C493] dark:border-[rgba(136,196,147,0.3)]";
    }
    const chip = document.createElement("span");
    chip.className = `px-2 py-0.5 rounded border ${colorClass} font-mono text-[11px]`;
    chip.textContent = `${key}: ${val}`;
    factsContainer.appendChild(chip);
  }

  // 4. Fired Rules List
  const firedContainer = document.getElementById("fired-rules-container");
  const countBadge = document.getElementById("fired-rules-count-badge");
  countBadge.textContent = `${data.fired_rules.length} Aturan Aktif`;

  if (data.fired_rules.length === 0) {
    firedContainer.innerHTML = `<p class="text-xs text-[#9E9D99] font-serif italic">Tidak ada aturan yang aktif. Sistem merekomendasikan HOLD secara default.</p>`;
  } else {
    firedContainer.innerHTML = "";
    data.fired_rules.forEach(r => {
      let actionClass = "bg-[#F0EFEA] text-[#6E6D6A]";
      if (r.action === "BUY") actionClass = "badge-buy";
      if (r.action === "HOLD") actionClass = "badge-hold";
      if (r.action === "SELL") actionClass = "badge-sell";

      const card = document.createElement("div");
      card.className = "p-3 rounded border border-[#EAEAEA] dark:border-[#22262E] bg-[#FBFBFA] dark:bg-[#1A1E26] text-xs space-y-1.5";
      card.innerHTML = `
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-2">
            <span class="font-mono font-bold text-[#121212] dark:text-white">[${r.id}]</span>
            <span class="font-semibold text-[#121212] dark:text-[#E8E8E6]">${r.name}</span>
          </div>
          <div class="flex items-center space-x-1.5">
            <span class="px-2 py-0.5 rounded text-[10px] font-mono font-bold border ${actionClass}">${r.action}</span>
            <span class="font-mono text-[#9E9D99] text-[11px] tabular-nums">CF ${r.rule_cf.toFixed(2)}</span>
          </div>
        </div>
        <div class="font-mono text-[11px] text-[#6E6D6A] dark:text-[#A8A7A3]">
          ${r.condition} &rarr; <strong>${r.action}</strong>
        </div>
        <div class="text-[10px] text-[#9E9D99] pt-1 border-t border-[#EAEAEA] dark:border-[#2A2E38] font-serif italic">
          Dasar teori: ${r.source}
        </div>
      `;
      firedContainer.appendChild(card);
    });
  }

  // 5. MYCIN Compounding Sequence
  const stepsContainer = document.getElementById("mycin-steps-list");
  stepsContainer.innerHTML = "";
  let hasSteps = false;

  for (const act of ["BUY", "HOLD", "SELL"]) {
    const steps = trace.compounding_steps[act];
    if (steps && steps.length > 0) {
      hasSteps = true;
      const grp = document.createElement("div");
      grp.className = "pt-1";
      grp.innerHTML = `<span class="font-bold text-[#121212] dark:text-white">${act}:</span>`;
      steps.forEach(st => {
        const item = document.createElement("div");
        item.className = "pl-2 text-[11px] text-[#6E6D6A] dark:text-[#A8A7A3]";
        item.innerHTML = `&bull; ${st.rule_id} (${st.rule_name}): <code class="font-bold">${st.formula}</code>`;
        grp.appendChild(item);
      });
      stepsContainer.appendChild(grp);
    }
  }
  if (!hasSteps) {
    stepsContainer.innerHTML = `<span class="italic text-[#9E9D99] font-serif">Tidak ada aturan bertumpuk untuk skenario ini.</span>`;
  }

  // 6. Aspect Analysis & Token Breakdown (FiGAS)
  const tokContainer = document.getElementById("headline-tokens-container");
  tokContainer.innerHTML = "";
  if (!data.headline_analysis || data.headline_analysis.length === 0) {
    tokContainer.innerHTML = `<p class="text-xs text-[#9E9D99] font-serif italic">Tidak ada headline yang diinput.</p>`;
  } else {
    data.headline_analysis.forEach(ha => {
      const block = document.createElement("div");
      block.className = "p-3 rounded border border-[#EAEAEA] dark:border-[#22262E] bg-[#FBFBFA] dark:bg-[#1A1E26] space-y-2 text-xs";

      let aspTags = "";
      for (const [asp, score] of Object.entries(ha.aspect_scores)) {
        let aspColor = `aspect-${asp}`;
        aspTags += `<span class="px-2 py-0.5 rounded text-[10px] font-mono font-medium ${aspColor}">${asp}: ${score > 0 ? '+' : ''}${score.toFixed(2)}</span> `;
      }

      let tokensHtml = "";
      ha.tokens.forEach(t => {
        let tokStyle = "text-[#6E6D6A] dark:text-[#9E9D99]";
        if (t.adjusted_score > 0) tokStyle = "bg-[#EDF3EC] text-[#2B6434] border border-[#D2E3D1] dark:bg-[rgba(43,100,52,0.18)] dark:text-[#88C493] dark:border-[rgba(136,196,147,0.3)] font-semibold";
        else if (t.adjusted_score < 0) tokStyle = "bg-[#FDEBEC] text-[#9F2F2D] border border-[#F9D2D4] dark:bg-[rgba(159,47,45,0.18)] dark:text-[#DE7775] dark:border-[rgba(230,133,131,0.3)] font-semibold";
        else if (t.is_toi) tokStyle = "bg-[#E1F3FE] text-[#1F6C9F] border border-[#C6E5FD] dark:bg-[rgba(31,108,159,0.18)] dark:text-[#82C4EE] dark:border-[rgba(130,196,238,0.3)]";

        tokensHtml += `<span class="inline-block px-1.5 py-0.5 m-0.5 rounded text-[11px] font-mono ${tokStyle}">${t.token}</span>`;
      });

      block.innerHTML = `
        <div class="flex items-center justify-between">
          <span class="font-medium text-[#121212] dark:text-white font-sans text-xs">"${ha.text}"</span>
          <span class="font-mono text-xs font-bold tabular-nums ${ha.overall_score > 0 ? 'text-[#2B6434]' : ha.overall_score < 0 ? 'text-[#9F2F2D]' : 'text-[#6E6D6A]'}">
            Skor: ${ha.overall_score > 0 ? '+' : ''}${ha.overall_score.toFixed(3)}
          </span>
        </div>
        <div>${tokensHtml}</div>
        ${aspTags ? `<div class="pt-1.5 flex flex-wrap gap-1 items-center border-t border-[#EAEAEA] dark:border-[#2A2E38]">${aspTags}</div>` : ''}
      `;
      tokContainer.appendChild(block);
    });
  }
}

// Load Rules Knowledge Base
async function loadRules() {
  try {
    const res = await fetch("/api/rules");
    const data = await res.json();
    allRulesData = data.rules;
    renderRulesTable(allRulesData);
  } catch (err) {
    console.error("Error loading rules:", err);
  }
}

function filterRules(action) {
  document.querySelectorAll(".rule-filter-btn").forEach(btn => {
    btn.classList.remove("bg-white", "dark:bg-[#282C36]", "text-[#121212]", "dark:text-white");
    btn.classList.add("text-[#6E6D6A]");
  });
  event.target.classList.add("bg-white", "dark:bg-[#282C36]", "text-[#121212]", "dark:text-white");
  event.target.classList.remove("text-[#6E6D6A]");

  if (action === "ALL") {
    renderRulesTable(allRulesData);
  } else {
    renderRulesTable(allRulesData.filter(r => r.action === action));
  }
}

function renderRulesTable(rules) {
  const tbody = document.getElementById("rules-table-body");
  tbody.innerHTML = "";
  rules.forEach(r => {
    let actionBadge = "badge-hold";
    if (r.action === "BUY") actionBadge = "badge-buy";
    if (r.action === "SELL") actionBadge = "badge-sell";

    const tr = document.createElement("tr");
    tr.className = "hover:bg-[#FBFBFA] dark:hover:bg-[#1A1E26] transition";
    tr.innerHTML = `
      <td class="py-2.5 px-3 font-mono font-bold text-[#121212] dark:text-white">${r.id}</td>
      <td class="py-2.5 px-3 font-semibold text-[#121212] dark:text-white whitespace-nowrap">${r.name}</td>
      <td class="py-2.5 px-3 font-mono text-[#6E6D6A] dark:text-[#A8A7A3] text-[11px]">${r.condition}</td>
      <td class="py-2.5 px-3"><span class="px-2 py-0.5 rounded text-[10px] font-mono font-bold border ${actionBadge}">${r.action}</span></td>
      <td class="py-2.5 px-3 font-mono font-bold text-[#121212] dark:text-white tabular-nums">${r.cf.toFixed(2)}</td>
      <td class="py-2.5 px-3 text-[#6E6D6A] dark:text-[#8C8B87] text-[11px] leading-relaxed font-serif italic">${r.source}</td>
    `;
    tbody.appendChild(tr);
  });
}

// Load Test Cases
async function loadTestCases() {
  try {
    const res = await fetch("/api/test-cases");
    const data = await res.json();
    const list = document.getElementById("test-cases-list");
    list.innerHTML = "";

    data.test_cases.forEach(tc => {
      const item = document.createElement("div");
      item.className = "p-2.5 rounded border border-[#EAEAEA] dark:border-[#22262E] bg-[#FBFBFA] dark:bg-[#1A1E26] text-xs space-y-1";
      item.innerHTML = `
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-2">
            <span class="font-mono font-bold text-[#121212] dark:text-white">[${tc.id}]</span>
            <span class="font-medium text-[#121212] dark:text-white">${tc.scenario}</span>
          </div>
          <span class="px-1.5 py-0.5 rounded text-[10px] font-mono font-bold bg-[#EDF3EC] text-[#2B6434] border border-[#D2E3D1]">
            LULUS (${tc.actual})
          </span>
        </div>
        <div class="text-[11px] text-[#6E6D6A] flex justify-between font-mono">
          <span>Ekspektasi: <strong>${tc.expected}</strong></span>
          <span>Aturan: ${tc.fired_rules.join(", ") || "-"}</span>
        </div>
      `;
      list.appendChild(item);
    });
  } catch (err) {
    console.error("Error loading test cases:", err);
  }
}

// Load Unit Tests
async function loadUnitTests() {
  try {
    const res = await fetch("/api/unit-tests");
    const data = await res.json();
    const list = document.getElementById("unit-tests-list");
    list.innerHTML = "";

    data.unit_tests.forEach(ut => {
      const item = document.createElement("div");
      item.className = "p-2.5 rounded border border-[#EAEAEA] dark:border-[#22262E] bg-[#FBFBFA] dark:bg-[#1A1E26] text-xs space-y-1";
      item.innerHTML = `
        <div class="flex items-center justify-between">
          <span class="font-medium text-[#121212] dark:text-white">"${ut.headline}"</span>
          <span class="font-mono text-[10px] font-bold text-[#2B6434] bg-[#EDF3EC] px-1.5 py-0.5 rounded border border-[#D2E3D1]">LULUS</span>
        </div>
        <div class="text-[11px] text-[#6E6D6A] flex justify-between font-mono">
          <span>${ut.test_note}</span>
          <span class="tabular-nums">Skor: ${ut.overall_score}</span>
        </div>
      `;
      list.appendChild(item);
    });
  } catch (err) {
    console.error("Error loading unit tests:", err);
  }
}

// Load Benchmarks and ML Comparison
async function loadBenchmarks() {
  try {
    const res = await fetch("/api/benchmarks");
    const data = await res.json();
    const cards = document.getElementById("models-comparison-cards");
    cards.innerHTML = "";

    data.model_comparison.forEach(m => {
      const isExpert = m.explainable;
      const card = document.createElement("div");
      card.className = `p-4 rounded border ${isExpert ? 'border-[#121212] dark:border-white bg-[#FBFBFA] dark:bg-[#1A1E26]' : 'border-[#EAEAEA] dark:border-[#22262E] bg-white dark:bg-[#14171D]'} space-y-3`;
      card.innerHTML = `
        <div class="flex items-center justify-between">
          <span class="text-[10px] font-mono uppercase tracking-wider text-[#9E9D99]">${m.type}</span>
          ${isExpert ? '<span class="text-[10px] font-mono px-1.5 py-0.5 rounded bg-[#121212] dark:bg-white text-white dark:text-[#121212]">Explainable</span>' : '<span class="text-[10px] text-[#9E9D99] font-mono">Black Box</span>'}
        </div>
        <div>
          <h4 class="font-semibold text-xs text-[#121212] dark:text-white">${m.model}</h4>
          <p class="text-[11px] text-[#6E6D6A] dark:text-[#8C8B87] mt-0.5 font-serif italic">${m.description}</p>
        </div>
        <div class="grid grid-cols-2 gap-2 pt-2 border-t border-[#EAEAEA] dark:border-[#22262E]">
          <div>
            <span class="text-[10px] font-mono text-[#9E9D99] block">Akurasi</span>
            <span class="font-mono font-bold text-sm text-[#121212] dark:text-white tabular-nums">${(m.accuracy * 100).toFixed(1)}%</span>
          </div>
          <div>
            <span class="text-[10px] font-mono text-[#9E9D99] block">Macro-F1</span>
            <span class="font-mono font-bold text-sm text-[#121212] dark:text-white tabular-nums">${m.macro_f1.toFixed(3)}</span>
          </div>
        </div>
      `;
      cards.appendChild(card);
    });
  } catch (err) {
    console.error("Error loading benchmarks:", err);
  }
}

// Load Historical Events
async function loadHistoricalEvents() {
  try {
    const res = await fetch("/api/historical-events");
    const data = await res.json();
    const grid = document.getElementById("historical-events-grid");
    grid.innerHTML = "";

    data.events.forEach(evt => {
      let actBadge = "badge-hold";
      if (evt.expected_action === "BUY") actBadge = "badge-buy";
      if (evt.expected_action === "SELL") actBadge = "badge-sell";

      const card = document.createElement("div");
      card.className = "p-5 rounded border border-[#EAEAEA] dark:border-[#22262E] bg-white dark:bg-[#14171D] space-y-3";
      
      const headlinesList = evt.headlines.map(h => `<li class="font-serif italic text-xs text-[#6E6D6A] dark:text-[#A8A7A3]">&bull; "${h}"</li>`).join("");

      card.innerHTML = `
        <div class="flex items-center justify-between">
          <span class="font-mono text-xs font-semibold text-[#121212] dark:text-white">${evt.date}</span>
          <span class="px-2 py-0.5 rounded text-[10px] font-mono font-bold border ${actBadge}">Sistem: ${evt.expected_action}</span>
        </div>
        <div>
          <h3 class="font-semibold text-xs text-[#121212] dark:text-white">${evt.title}</h3>
          <p class="text-[11px] text-[#6E6D6A] font-mono mt-0.5 tabular-nums">S&amp;P 500: ${evt.sp500_price.toFixed(2)} &bull; Return Aktual: <strong class="${evt.actual_next_return.startsWith('+') ? 'text-[#2B6434]' : 'text-[#9F2F2D]'}">${evt.actual_next_return}</strong></p>
        </div>
        <ul class="space-y-1 border-l-2 border-[#EAEAEA] dark:border-[#2A2E38] pl-3 py-0.5">
          ${headlinesList}
        </ul>
        <p class="text-[11px] text-[#6E6D6A] dark:text-[#8C8B87] font-serif italic">${evt.summary}</p>
        <button onclick='loadHistoricalEventToSimulator(${JSON.stringify(evt).replace(/'/g, "&apos;")})' class="w-full mt-2 py-1.5 px-3 rounded text-xs font-mono border border-[#EAEAEA] dark:border-[#2E333D] bg-[#FBFBFA] dark:bg-[#1A1E26] text-[#121212] dark:text-white hover:border-[#121212] dark:hover:border-white transition">
          Muat ke Simulator &rarr;
        </button>
      `;
      grid.appendChild(card);
    });
  } catch (err) {
    console.error("Error loading historical events:", err);
  }
}

function loadHistoricalEventToSimulator(evt) {
  document.getElementById("input-headlines").value = evt.headlines.join("\n");
  document.getElementById("input-trend").value = evt.trend;
  document.getElementById("input-vol").value = evt.volatility;
  document.getElementById("input-prevsent").value = evt.prev_sentiment;
  updateSliderLabels();
  switchTab("simulator");
  runAnalysis();
}

function openAuthorsModal() {
  document.getElementById("authors-modal").classList.remove("hidden");
}
function closeAuthorsModal() {
  document.getElementById("authors-modal").classList.add("hidden");
}
