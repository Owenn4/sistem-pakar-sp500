// Sistem Pakar Saham Indonesia (IHSG & LQ45) - Frontend Controller

const PRESETS = {
  clickbait_panic: {
    headlines: [
      "IHSG Kebakaran dan Ambruk Rontok Berdarah di Awal Sesi! || Walaupun judul terdengar sangat panik, koreksi sebenarnya hanya tipis 0,12% akibat aksi ambil untung wajar, sedangkan laba perbankan tumbuh solid dan investor asing mencatat net buy.",
      "Geger! Saham Bank Besar Terancam Tumbang Dihantam Isu Global? || Kekhawatiran di judul berita dinilai berlebihan oleh analis. Faktanya, penyaluran kredit tetap meningkat kuat, rasio NPL turun terkendali, dan likuiditas Rupiah sangat stabil."
    ],
    trend: 0.008,
    rsi: 52.0,
    vol: 0.011,
    prev_sent: 0.00
  },
  bi_ratecut: {
    headlines: [
      "Bank Indonesia Pangkas Suku Bunga Acuan BI Rate 25 bps Guna Dorong Pertumbuhan Ekonomi || Rapat Dewan Gubernur BI menurunkan suku bunga acuan seiring inflasi domestik yang melandai rendah dan penguatan nilai tukar Rupiah.",
      "Indonesian shares rally as foreign investors post strong net buy on rupiah appreciation || JAKARTA (Reuters) - Indonesian equities surged as foreign institutional inflows and lower borrowing costs boosted banking and consumer stocks.",
      "Laba Bersih BBCA dan Perbankan LQ45 Tumbuh Solid Didukung Ekspansi Kredit || Kinerja keuangan emiten perbankan mencetak kenaikan laba bersih dan pembagian dividen tunai yang menarik."
    ],
    trend: 0.018,
    rsi: 57.0,
    vol: 0.010,
    prev_sent: 0.01
  },
  divergent_risk: {
    headlines: [
      "Manajemen Emiten Optimistis Target Pendapatan Tahun Ini Tercapai Sesuai Rencana || Namun di dalam rincian laporan keuangan, perusahaan justru mengalami kerugian bersih parah akibat beban bunga utang yang membengkak tajam, arus kas defisit, dan aksi net sell asing.",
      "Perdagangan Saham Hari Ini Dibuka Menguat pada Sejumlah Sektor || Di balik pembukaan tersebut, nilai tukar Rupiah melemah tajam akibat capital outflow asing dan lonjakan risiko kredit macet perbankan."
    ],
    trend: -0.018,
    rsi: 44.0,
    vol: 0.016,
    prev_sent: 0.03
  },
  bi_ratehike: {
    headlines: [
      "Rapat Dewan Gubernur BI Putuskan Suku Bunga Acuan Naik Akibat Tekanan Inflasi dan Rupiah || Kenaikan harga pangan dan depresiasi kurs Rupiah memaksa bank sentral menaikkan suku bunga BI Rate secara hawkish sehingga menekan daya beli.",
      "Jakarta stocks slide as rupiah weakens and foreign outflows accelerate || JAKARTA (Reuters) - Heavy foreign net sell hit Indonesian blue-chip stocks as rising inflation and tighter monetary policy weighed on corporate earnings."
    ],
    trend: -0.025,
    rsi: 41.0,
    vol: 0.018,
    prev_sent: 0.02
  },
  oversold_rebound: {
    headlines: [
      "Saham TLKM Mulai Pulih Didukung Rencana Buyback Setelah Koreksi Dalam || Setelah harga saham turun jauh di bawah rata-rata 20 hari ke area jenuh jual, manajemen menyiapkan buyback saham didukung pertumbuhan laba data center dan dividen."
    ],
    trend: -0.068,
    rsi: 31.0,
    vol: 0.019,
    prev_sent: -0.08
  }
};

let debounceTimer = null;
let allRulesData = [];
let currentLiveArticles = [];
let currentLiveStockInfo = null;

document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  initSliders();
  loadRules();
  loadTestCases();
  loadUnitTests();
  loadBenchmarks("ALL");
  loadHistoricalEvents();

  // Default: load Simulator preset + load Live Stock for ^JKSE (IHSG)
  loadPreset("clickbait_panic");
  selectLiveTicker("^JKSE");

  const customInput = document.getElementById("custom-ticker-input");
  if (customInput) {
    customInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        requestCustomTicker();
      }
    });
  }
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
  const target = document.getElementById(`tab-${tabId}`);
  if (target) target.classList.remove("hidden");

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

// ==================== TAB 1: LIVE STOCK & NEWS REQUEST ====================
function selectLiveTicker(ticker) {
  document.querySelectorAll(".ticker-pill-btn").forEach(btn => {
    const isMatch = btn.getAttribute("data-ticker") === ticker;
    if (isMatch) {
      btn.className = "ticker-pill-btn px-3 py-1.5 rounded text-xs font-mono border border-[#121212] dark:border-white bg-[#121212] text-white dark:bg-white dark:text-[#121212] transition";
    } else {
      btn.className = "ticker-pill-btn px-3 py-1.5 rounded text-xs font-mono border border-[#EAEAEA] dark:border-[#2E333D] bg-[#FBFBFA] dark:bg-[#1A1E26] text-[#121212] dark:text-[#E8E8E6] hover:border-[#121212] dark:hover:border-white transition";
    }
  });
  fetchLiveStockAnalysis(ticker);
}

function requestCustomTicker() {
  const raw = document.getElementById("custom-ticker-input").value.trim();
  if (!raw) return;
  selectLiveTicker(raw.toUpperCase());
}

async function fetchLiveStockAnalysis(ticker) {
  const loader = document.getElementById("live-loading-banner");
  const content = document.getElementById("live-dashboard-content");
  if (loader) loader.classList.remove("hidden");
  if (content) content.classList.add("opacity-50");

  try {
    const res = await fetch("/api/live-stock-analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ticker, max_articles: 12 })
    });
    const data = await res.json();
    currentLiveArticles = data.articles_analysis || [];
    currentLiveStockInfo = data.stock_info || null;
    renderLiveDashboard(data);
  } catch (err) {
    console.error("Error fetching live stock analysis:", err);
  } finally {
    if (loader) loader.classList.add("hidden");
    if (content) content.classList.remove("opacity-50");
  }
}

function renderLiveDashboard(data) {
  const st = data.stock_info;
  const dec = data.decision;
  const cf = data.certainty_factors;
  const trace = data.trace;
  const nf = data.numeric_facts;

  // 1. Stock Profile & Price
  document.getElementById("live-stock-ticker").textContent = st.ticker;
  document.getElementById("live-stock-sector").textContent = st.sector;
  document.getElementById("live-stock-name").textContent = st.name;

  const isIndex = st.ticker === "^JKSE";
  const priceStr = isIndex
    ? st.last_close.toLocaleString("id-ID", { minimumFractionDigits: 2, maximumFractionDigits: 2 })
    : `Rp ${st.last_close.toLocaleString("id-ID")}`;
  document.getElementById("live-stock-price").textContent = priceStr;

  const retEl = document.getElementById("live-stock-return");
  const retSign = st.daily_return_pct >= 0 ? "+" : "";
  retEl.textContent = `${retSign}${st.daily_return_pct.toFixed(2)}% (${st.last_date})`;
  retEl.className = `font-mono text-xs tabular-nums font-semibold ${st.daily_return_pct >= 0 ? "text-[#2B6434] dark:text-[#88C493]" : "text-[#9F2F2D] dark:text-[#E68583]"}`;

  document.getElementById("live-ind-ma20").textContent = isIndex ? st.ma20.toFixed(1) : `Rp ${Math.round(st.ma20).toLocaleString("id-ID")}`;
  document.getElementById("live-ind-trend").textContent = `${st.trend_pct >= 0 ? "+" : ""}${st.trend_pct.toFixed(2)}%`;
  document.getElementById("live-ind-rsi").textContent = `${st.rsi14.toFixed(1)}`;
  document.getElementById("live-ind-vol").textContent = `${st.volatility.toFixed(4)}`;
  document.getElementById("live-stock-dates").textContent = `${st.total_trading_days_2y} Hari Bursa (2 Tahun)`;

  renderPriceSparkline(st.history_60d || []);

  // 2. Decision Hero
  const badge = document.getElementById("live-badge-decision");
  const dot = document.getElementById("live-badge-dot");
  const txt = document.getElementById("live-badge-text");
  badge.className = "text-2xl font-mono font-bold px-3.5 py-1 rounded border inline-flex items-center space-x-2 ";
  dot.className = "w-2.5 h-2.5 rounded-full ";

  if (dec === "BUY") {
    badge.classList.add("badge-buy");
    dot.classList.add("bg-[#2B6434]", "dark:bg-[#88C493]");
    txt.textContent = "BUY (BELI)";
  } else {
    badge.classList.add("badge-sell");
    dot.classList.add("bg-[#9F2F2D]", "dark:bg-[#E68583]");
    txt.textContent = "SELL (JUAL)";
  }

  document.getElementById("live-cf-val").textContent = `${(cf[dec] || 0).toFixed(2)} (${Math.round((cf[dec] || 0) * 100)}%)`;
  document.getElementById("live-confidence-tier").textContent = `Kategori Keyakinan: ${trace.confidence_tier || "-"}`;

  // 3. Headline vs Body Score Comparison
  const sHead = nf.sent_headline_only || 0;
  const sEff = nf.sent_effective || 0;
  document.getElementById("live-sent-head-only").textContent = `${sHead >= 0 ? "+" : ""}${sHead.toFixed(3)}`;
  document.getElementById("live-sent-effective").textContent = `${sEff >= 0 ? "+" : ""}${sEff.toFixed(3)}`;
  document.getElementById("live-verification-counts").textContent =
    `${nf.confirmed_count || 0} Terkonfirmasi • ${nf.clickbait_count || 0} Clickbait Didiskon • ${nf.divergent_count || 0} Divergensi`;

  // 4. CF Progress Bars
  const bVal = cf.BUY || 0;
  const sVal = cf.SELL || 0;
  document.getElementById("live-bar-val-buy").textContent = bVal.toFixed(2);
  document.getElementById("live-bar-val-sell").textContent = sVal.toFixed(2);
  document.getElementById("live-bar-buy").style.width = `${Math.min(100, bVal * 100)}%`;
  document.getElementById("live-bar-sell").style.width = `${Math.min(100, sVal * 100)}%`;

  // 5. Natural Language Reasoning
  document.getElementById("live-reasoning-heading").textContent =
    dec === "BUY" ? "Alasan Merekomendasikan BUY (Reason to Buy):" : "Alasan Merekomendasikan SELL (Reason to Sell):";
  document.getElementById("live-fired-count").textContent = `${data.fired_rules.length} Aturan Pakar Aktif`;
  document.getElementById("live-hb-insight").textContent = trace.headline_vs_body_insight || "";

  const rList = document.getElementById("live-reasons-list");
  rList.innerHTML = "";
  const reasons = (trace.primary_reasons && trace.primary_reasons.length > 0)
    ? trace.primary_reasons
    : [trace.resolution_reason];
  reasons.forEach(r => {
    const li = document.createElement("li");
    li.className = "flex items-start space-x-2 leading-relaxed";
    li.innerHTML = `<span class="font-mono font-bold ${dec === 'BUY' ? 'text-[#2B6434]' : 'text-[#9F2F2D]'}">&rarr;</span><span>${r}</span>`;
    rList.appendChild(li);
  });

  // 6. Render Live News Cards (Headline vs Body Comparison)
  const artContainer = document.getElementById("live-articles-list");
  artContainer.innerHTML = "";
  (data.articles_analysis || []).forEach((art, idx) => {
    let statusBadge = "bg-[#EDF3EC] text-[#2B6434] border-[#D2E3D1] dark:bg-[rgba(43,100,52,0.2)] dark:text-[#88C493]";
    if (art.verification_status === "CLICKBAIT_EXAGGERATED") {
      statusBadge = "bg-[#FBF3DB] text-[#8C5E00] border-[#F5E6B8] dark:bg-[rgba(140,94,0,0.25)] dark:text-[#E2B653]";
    } else if (art.verification_status === "DIVERGENT_CONTENT") {
      statusBadge = "bg-[#FDEBEC] text-[#9F2F2D] border-[#F9D2D4] dark:bg-[rgba(159,47,45,0.25)] dark:text-[#E68583]";
    }

    const scopeBadge = art.scope === "TICKER_SPECIFIC"
      ? `<span class="px-1.5 py-0.5 rounded text-[10px] font-mono bg-[#E1F3FE] text-[#1F6C9F] border border-[#C6E5FD] dark:bg-[rgba(31,108,159,0.2)] dark:text-[#82C4EE]">Spesifik Emiten</span>`
      : `<span class="px-1.5 py-0.5 rounded text-[10px] font-mono bg-[#F0EFEA] text-[#6E6D6A] border border-[#EAEAEA] dark:bg-[#1E222A] dark:text-[#A8A7A3]">Makro / IHSG</span>`;

    let aspHtml = "";
    for (const [ak, av] of Object.entries(art.aspect_scores || {})) {
      aspHtml += `<span class="px-1.5 py-0.5 rounded text-[10px] font-mono aspect-${ak}">${ak}: ${av >= 0 ? "+" : ""}${av.toFixed(2)}</span> `;
    }

    const card = document.createElement("div");
    card.className = "p-4 rounded-lg border border-[#EAEAEA] dark:border-[#22262E] bg-[#FBFBFA] dark:bg-[#1A1E26] space-y-2.5 flex flex-col justify-between text-xs";
    card.innerHTML = `
      <div class="space-y-2">
        <div class="flex flex-wrap items-center justify-between gap-1.5">
          <div class="flex items-center space-x-1.5">
            <span class="font-mono font-bold text-[10px] text-[#9E9D99]">#${idx + 1}</span>
            <span class="font-mono font-semibold text-[11px] text-[#121212] dark:text-white">${art.source}</span>
            ${scopeBadge}
          </div>
          <span class="px-2 py-0.5 rounded text-[10px] font-mono font-semibold border ${statusBadge}">
            ${art.verification_label}
          </span>
        </div>

        <h4 class="font-semibold text-[#121212] dark:text-white leading-snug">
          ${art.url ? `<a href="${art.url}" target="_blank" rel="noopener" class="hover:underline">${art.headline} &nearr;</a>` : art.headline}
        </h4>

        <div class="p-2.5 rounded bg-white dark:bg-[#14171D] border border-[#EAEAEA] dark:border-[#22262E] text-[11px] text-[#6E6D6A] dark:text-[#A8A7A3] font-serif italic leading-relaxed">
          <strong class="font-mono not-italic text-[10px] uppercase text-[#9E9D99] block mb-0.5">Kutipan Bukti Isi Berita (Body Evidence):</strong>
          "${art.evidence_snippet || art.body}"
        </div>
      </div>

      <div class="space-y-2 pt-2 border-t border-[#EAEAEA] dark:border-[#2A2E38]">
        <div class="grid grid-cols-3 gap-2 font-mono text-[11px] text-center">
          <div class="p-1.5 rounded bg-white dark:bg-[#14171D] border border-[#EAEAEA] dark:border-[#22262E]">
            <span class="text-[9px] text-[#9E9D99] block">Skor Headline</span>
            <strong class="${art.headline_score > 0 ? 'text-[#2B6434]' : art.headline_score < 0 ? 'text-[#9F2F2D]' : 'text-[#6E6D6A]'}">
              ${art.headline_score >= 0 ? "+" : ""}${art.headline_score.toFixed(2)}
            </strong>
          </div>
          <div class="p-1.5 rounded bg-white dark:bg-[#14171D] border border-[#EAEAEA] dark:border-[#22262E]">
            <span class="text-[9px] text-[#9E9D99] block">Skor Isi Berita</span>
            <strong class="${art.body_score > 0 ? 'text-[#2B6434]' : art.body_score < 0 ? 'text-[#9F2F2D]' : 'text-[#6E6D6A]'}">
              ${art.body_score >= 0 ? "+" : ""}${art.body_score.toFixed(2)}
            </strong>
          </div>
          <div class="p-1.5 rounded bg-white dark:bg-[#14171D] border border-[#121212]/30 dark:border-white/30">
            <span class="text-[9px] text-[#121212] dark:text-white font-semibold block">Skor Efektif</span>
            <strong class="${art.effective_score > 0 ? 'text-[#2B6434]' : art.effective_score < 0 ? 'text-[#9F2F2D]' : 'text-[#6E6D6A]'}">
              ${art.effective_score >= 0 ? "+" : ""}${art.effective_score.toFixed(2)}
            </strong>
          </div>
        </div>
        <p class="text-[10px] text-[#6E6D6A] dark:text-[#8C8B87] font-sans">${art.verification_explanation}</p>
        ${aspHtml ? `<div class="flex flex-wrap gap-1 pt-0.5">${aspHtml}</div>` : ""}
      </div>
    `;
    artContainer.appendChild(card);
  });
}

function renderPriceSparkline(series) {
  const container = document.getElementById("live-price-chart-container");
  if (!series || series.length < 2) {
    container.innerHTML = `<span class="text-xs font-mono text-[#9E9D99]">Data grafik historis tidak tersedia</span>`;
    return;
  }
  const closes = series.map(d => d.close);
  const ma20s = series.map(d => d.ma20);
  const allVals = closes.concat(ma20s);
  const minV = Math.min(...allVals);
  const maxV = Math.max(...allVals);
  const span = Math.max(1e-4, maxV - minV);

  const w = 440;
  const h = 88;
  const toPoints = (arr) => arr.map((v, i) => {
    const x = (i / (arr.length - 1)) * (w - 12) + 6;
    const y = h - 8 - ((v - minV) / span) * (h - 16);
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  }).join(" ");

  const closePts = toPoints(closes);
  const ma20Pts = toPoints(ma20s);
  const isUp = closes[closes.length - 1] >= closes[0];
  const strokeColor = isUp ? "#2B6434" : "#9F2F2D";

  container.innerHTML = `
    <svg viewBox="0 0 ${w} ${h}" class="w-full h-full overflow-visible">
      <polyline fill="none" stroke="#9E9D99" stroke-width="1.25" stroke-dasharray="3,3" points="${ma20Pts}" />
      <polyline fill="none" stroke="${strokeColor}" stroke-width="2" points="${closePts}" />
    </svg>
  `;
}

function sendLiveArticlesToSimulator() {
  if (!currentLiveArticles || currentLiveArticles.length === 0) return;
  const lines = currentLiveArticles.map(a => `${a.headline} || ${a.body}`);
  document.getElementById("input-headlines").value = lines.join("\n");
  if (currentLiveStockInfo) {
    document.getElementById("input-trend").value = currentLiveStockInfo.trend;
    document.getElementById("input-rsi").value = currentLiveStockInfo.rsi14;
    document.getElementById("input-vol").value = currentLiveStockInfo.volatility;
  }
  updateSliderLabels();
  switchTab("simulator");
  runAnalysis();
}

// ==================== TAB 2: SIMULATOR HEADLINE VS ISI BERITA ====================
function loadPreset(name) {
  const p = PRESETS[name];
  if (!p) return;
  document.getElementById("input-headlines").value = p.headlines.join("\n");
  document.getElementById("input-trend").value = p.trend;
  document.getElementById("input-rsi").value = p.rsi || 50;
  document.getElementById("input-vol").value = p.vol;
  document.getElementById("input-prevsent").value = p.prev_sent;
  updateSliderLabels();
  runAnalysis();
}

function clearHeadlines() {
  document.getElementById("input-headlines").value = "";
  runAnalysis();
}

function initSliders() {
  updateSliderLabels();
  ["input-trend", "input-rsi", "input-vol", "input-prevsent"].forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener("input", () => {
        updateSliderLabels();
        triggerDebouncedAnalysis();
      });
    }
  });
  const hl = document.getElementById("input-headlines");
  if (hl) hl.addEventListener("input", triggerDebouncedAnalysis);
}

function updateSliderLabels() {
  const tr = parseFloat(document.getElementById("input-trend").value);
  const rsi = parseFloat(document.getElementById("input-rsi").value);
  const vo = parseFloat(document.getElementById("input-vol").value);
  const ps = parseFloat(document.getElementById("input-prevsent").value);

  const trTag = tr <= -0.045 ? "oversold" : tr <= -0.012 ? "down" : tr >= 0.045 ? "overextended" : tr >= 0.012 ? "up" : "flat";
  document.getElementById("label-trend-val").textContent = `${(tr * 100).toFixed(1)}% (${trTag})`;

  const rsiTag = rsi <= 35 ? "oversold" : rsi <= 46 ? "bearish" : rsi >= 68 ? "overbought" : rsi >= 54 ? "bullish" : "neutral";
  document.getElementById("label-rsi-val").textContent = `${rsi.toFixed(0)} (${rsiTag})`;

  const voTag = vo >= 0.016 ? "high" : vo <= 0.007 ? "low" : "normal";
  document.getElementById("label-vol-val").textContent = `${vo.toFixed(3)} (${voTag})`;

  const psTag = ps <= -0.025 ? "pesimis" : ps >= 0.025 ? "optimis" : "stable";
  document.getElementById("label-prevsent-val").textContent = `${ps >= 0 ? "+" : ""}${ps.toFixed(2)} (${psTag})`;
}

function triggerDebouncedAnalysis() {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(runAnalysis, 180);
}

async function runAnalysis() {
  const text = document.getElementById("input-headlines").value;
  const headlines = text.split("\n").map(s => s.trim()).filter(s => s.length > 0);
  const trend = parseFloat(document.getElementById("input-trend").value);
  const rsi = parseFloat(document.getElementById("input-rsi").value);
  const volatility = parseFloat(document.getElementById("input-vol").value);
  const prev_sentiment = parseFloat(document.getElementById("input-prevsent").value);

  try {
    const res = await fetch("/api/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        headlines,
        trend,
        rsi,
        volatility,
        prev_sentiment,
        use_filler: false
      })
    });
    const data = await res.json();
    renderAnalysisResult(data);
  } catch (err) {
    console.error("Error executing infer:", err);
  }
}

function renderAnalysisResult(data) {
  const dec = data.decision;
  const cf = data.certainty_factors;
  const trace = data.trace;
  const nf = data.numeric_facts || {};

  // 1. Hero Decision Badge (Murni BUY vs SELL)
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
  } else {
    badge.classList.add("badge-sell");
    badgeDot.classList.add("bg-[#9F2F2D]", "dark:bg-[#DE7775]");
    badgeText.textContent = "SELL";
  }
  cfText.textContent = (cf[dec] || 0.00).toFixed(2);
  document.getElementById("resolution-reason-text").textContent = trace.resolution_reason;

  const sHead = nf.sent_headline_only || 0;
  const sEff = nf.sent_effective || 0;
  document.getElementById("sim-hb-summary").textContent =
    `Skor Headline: ${sHead >= 0 ? "+" : ""}${sHead.toFixed(3)} → Skor Efektif (Judul+Isi): ${sEff >= 0 ? "+" : ""}${sEff.toFixed(3)}`;

  // 2. CF Progress Bars
  const buyVal = cf.BUY || 0;
  const sellVal = cf.SELL || 0;
  document.getElementById("val-cf-buy").textContent = buyVal.toFixed(2);
  document.getElementById("val-cf-sell").textContent = sellVal.toFixed(2);
  document.getElementById("bar-cf-buy").style.width = `${Math.min(100, buyVal * 100)}%`;
  document.getElementById("bar-cf-sell").style.width = `${Math.min(100, sellVal * 100)}%`;

  // 2b. Human Reasons List
  const humanList = document.getElementById("sim-human-reasons");
  humanList.innerHTML = "";
  const reasons = (trace.primary_reasons && trace.primary_reasons.length > 0)
    ? trace.primary_reasons
    : [trace.resolution_reason];
  reasons.forEach(r => {
    const li = document.createElement("li");
    li.innerHTML = `&bull; ${r}`;
    humanList.appendChild(li);
  });

  // 3. Linguistic Facts Chips
  const factsContainer = document.getElementById("facts-chips-container");
  factsContainer.innerHTML = "";
  const lf = data.linguistic_facts;
  for (const [key, val] of Object.entries(lf)) {
    let colorClass = "bg-[#F0EFEA] text-[#6E6D6A] border-[#EAEAEA] dark:bg-[#1A1E26] dark:text-[#A8A7A3] dark:border-[#2A2E38]";
    if (val === "very_neg" || val === "neg" || val === "oversold" || val === "high" || val === "clickbait_heavy") {
      colorClass = "bg-[#FDEBEC] text-[#9F2F2D] border-[#F9D2D4] dark:bg-[rgba(159,47,45,0.18)] dark:text-[#DE7775] dark:border-[rgba(230,133,131,0.3)]";
    } else if (val === "very_pos" || val === "pos" || val === "improving" || val === "high_verified") {
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
    firedContainer.innerHTML = `<p class="text-xs text-[#9E9D99] font-serif italic">Tidak ada aturan IF-THEN yang terpenuhi secara spesifik; menggunakan Tie-Breaker komposit sentimen isi berita & tren teknikal.</p>`;
  } else {
    firedContainer.innerHTML = "";
    data.fired_rules.forEach(r => {
      const actionClass = r.action === "BUY" ? "badge-buy" : "badge-sell";
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
        <div class="text-[11px] text-[#121212] dark:text-[#E8E8E6] pt-1 border-t border-[#EAEAEA] dark:border-[#2A2E38]">
          <strong>Alasan Pakar:</strong> ${r.human_reason || ""}
        </div>
        <div class="text-[10px] text-[#9E9D99] font-serif italic">
          Referensi Literatur: ${r.source}
        </div>
      `;
      firedContainer.appendChild(card);
    });
  }

  // 5. MYCIN Compounding Sequence
  const stepsContainer = document.getElementById("mycin-steps-list");
  stepsContainer.innerHTML = "";
  let hasSteps = false;

  for (const act of ["BUY", "SELL"]) {
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
    stepsContainer.innerHTML = `<span class="italic text-[#9E9D99] font-serif">Tidak ada kombinasi aturan bertumpuk pada skenario ini.</span>`;
  }

  // 6. Headline vs Body & Token Inspector
  const tokContainer = document.getElementById("headline-tokens-container");
  tokContainer.innerHTML = "";
  if (!data.headline_analysis || data.headline_analysis.length === 0) {
    tokContainer.innerHTML = `<p class="text-xs text-[#9E9D99] font-serif italic">Tidak ada berita yang diinput.</p>`;
  } else {
    data.headline_analysis.forEach(ha => {
      const block = document.createElement("div");
      block.className = "p-3.5 rounded border border-[#EAEAEA] dark:border-[#22262E] bg-[#FBFBFA] dark:bg-[#1A1E26] space-y-2 text-xs";

      let aspTags = "";
      for (const [asp, score] of Object.entries(ha.aspect_scores || {})) {
        aspTags += `<span class="px-2 py-0.5 rounded text-[10px] font-mono font-medium aspect-${asp}">${asp}: ${score > 0 ? "+" : ""}${score.toFixed(2)}</span> `;
      }

      let tokensHtml = "";
      ha.tokens.forEach(t => {
        let tokStyle = "text-[#6E6D6A] dark:text-[#9E9D99]";
        if (t.adjusted_score > 0) tokStyle = "bg-[#EDF3EC] text-[#2B6434] border border-[#D2E3D1] dark:bg-[rgba(43,100,52,0.18)] dark:text-[#88C493] font-semibold";
        else if (t.adjusted_score < 0) tokStyle = "bg-[#FDEBEC] text-[#9F2F2D] border border-[#F9D2D4] dark:bg-[rgba(159,47,45,0.18)] dark:text-[#DE7775] font-semibold";
        else if (t.is_toi) tokStyle = "bg-[#E1F3FE] text-[#1F6C9F] border border-[#C6E5FD] dark:bg-[rgba(31,108,159,0.18)] dark:text-[#82C4EE]";
        tokensHtml += `<span class="inline-block px-1.5 py-0.5 m-0.5 rounded text-[11px] font-mono ${tokStyle}">${t.token}</span>`;
      });

      block.innerHTML = `
        <div class="flex flex-wrap items-center justify-between gap-2">
          <span class="font-semibold text-[#121212] dark:text-white font-sans text-xs">Headline: "${ha.text}"</span>
          <span class="px-2 py-0.5 rounded text-[10px] font-mono font-bold border border-[#EAEAEA] dark:border-[#2E333D] bg-white dark:bg-[#14171D]">
            ${ha.verification_label || "Analisis"}
          </span>
        </div>
        ${ha.body_text ? `<div class="text-[11px] text-[#6E6D6A] dark:text-[#A8A7A3] font-serif italic bg-white dark:bg-[#14171D] p-2 rounded border border-[#EAEAEA] dark:border-[#22262E]"><strong>Isi Berita:</strong> "${ha.body_text}"</div>` : ""}
        <div class="flex flex-wrap items-center gap-3 font-mono text-[11px]">
          <span>Skor Headline: <strong>${ha.headline_score >= 0 ? "+" : ""}${(ha.headline_score || 0).toFixed(3)}</strong></span>
          <span>Skor Isi: <strong>${ha.body_score >= 0 ? "+" : ""}${(ha.body_score || 0).toFixed(3)}</strong></span>
          <span>Skor Efektif: <strong class="${ha.effective_score > 0 ? 'text-[#2B6434]' : ha.effective_score < 0 ? 'text-[#9F2F2D]' : ''}">${ha.effective_score >= 0 ? "+" : ""}${(ha.effective_score || 0).toFixed(3)}</strong></span>
        </div>
        <div>${tokensHtml}</div>
        ${aspTags ? `<div class="pt-1.5 flex flex-wrap gap-1 items-center border-t border-[#EAEAEA] dark:border-[#2A2E38]">${aspTags}</div>` : ""}
      `;
      tokContainer.appendChild(block);
    });
  }
}

// ==================== TAB 4: KNOWLEDGE BASE & REFERENCES ====================
async function loadRules() {
  try {
    const res = await fetch("/api/rules");
    const data = await res.json();
    allRulesData = data.rules;
    renderRulesTable(allRulesData);
    renderReferencesCatalog(data.references || []);
  } catch (err) {
    console.error("Error loading rules:", err);
  }
}

function filterRules(action, btnEl) {
  document.querySelectorAll(".rule-filter-btn").forEach(btn => {
    btn.classList.remove("bg-white", "dark:bg-[#282C36]", "text-[#121212]", "dark:text-white");
    btn.classList.add("text-[#6E6D6A]");
  });
  if (btnEl) {
    btnEl.classList.add("bg-white", "dark:bg-[#282C36]", "text-[#121212]", "dark:text-white");
    btnEl.classList.remove("text-[#6E6D6A]");
  }
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
    const actionBadge = r.action === "BUY" ? "badge-buy" : "badge-sell";
    const tr = document.createElement("tr");
    tr.className = "hover:bg-[#FBFBFA] dark:hover:bg-[#1A1E26] transition";
    tr.innerHTML = `
      <td class="py-2.5 px-3 font-mono font-bold text-[#121212] dark:text-white">${r.id}</td>
      <td class="py-2.5 px-3 font-semibold text-[#121212] dark:text-white">${r.name}</td>
      <td class="py-2.5 px-3 font-mono text-[#6E6D6A] dark:text-[#A8A7A3] text-[11px]">${r.condition}</td>
      <td class="py-2.5 px-3"><span class="px-2 py-0.5 rounded text-[10px] font-mono font-bold border ${actionBadge}">${r.action}</span></td>
      <td class="py-2.5 px-3 font-mono font-bold text-[#121212] dark:text-white tabular-nums">${r.cf.toFixed(2)}</td>
      <td class="py-2.5 px-3 text-[#121212] dark:text-[#E8E8E6] text-[11px] leading-relaxed">${r.human_reason || ""}</td>
      <td class="py-2.5 px-3 text-[#6E6D6A] dark:text-[#8C8B87] text-[11px] font-serif italic">${r.source}</td>
    `;
    tbody.appendChild(tr);
  });
}

function renderReferencesCatalog(refs) {
  const grid = document.getElementById("references-list-grid");
  if (!grid) return;
  grid.innerHTML = "";
  refs.forEach(ref => {
    const card = document.createElement("div");
    card.className = "p-3.5 rounded border border-[#EAEAEA] dark:border-[#22262E] bg-[#FBFBFA] dark:bg-[#1A1E26] space-y-1";
    card.innerHTML = `
      <div class="flex items-center space-x-2">
        <span class="font-mono font-bold text-[#121212] dark:text-white">${ref.id}</span>
        <span class="font-semibold text-[#121212] dark:text-white">${ref.authors}</span>
      </div>
      <div class="font-serif italic text-[#6E6D6A] dark:text-[#A8A7A3]">"${ref.title}" — ${ref.venue}</div>
      <div class="text-[11px] text-[#2B6434] dark:text-[#88C493] pt-1 font-sans">
        <strong>Peran di Sistem Pakar:</strong> ${ref.role}
      </div>
    `;
    grid.appendChild(card);
  });
}

// ==================== TAB 5: EVALUATION & 2-YEAR BACKTEST ====================
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

async function loadBenchmarks(tickerFilter = "ALL") {
  try {
    const res = await fetch(`/api/benchmarks?ticker=${encodeURIComponent(tickerFilter)}`);
    const data = await res.json();

    // Model Comparison Cards
    const cards = document.getElementById("models-comparison-cards");
    cards.innerHTML = "";
    (data.model_comparison || []).forEach(m => {
      const isMain = m.model.includes("Sistem Pakar Baru");
      const card = document.createElement("div");
      card.className = `p-4 rounded border ${isMain ? 'border-[#121212] dark:border-white bg-[#FBFBFA] dark:bg-[#1A1E26]' : 'border-[#EAEAEA] dark:border-[#22262E] bg-white dark:bg-[#14171D]'} space-y-2.5`;
      card.innerHTML = `
        <div class="flex items-center justify-between">
          <span class="text-[10px] font-mono uppercase tracking-wider text-[#9E9D99]">${m.type}</span>
          ${m.explainable ? '<span class="text-[10px] font-mono px-1.5 py-0.5 rounded bg-[#121212] dark:bg-white text-white dark:text-[#121212]">Explainable</span>' : '<span class="text-[10px] text-[#9E9D99] font-mono">Black Box</span>'}
        </div>
        <div>
          <h4 class="font-semibold text-xs text-[#121212] dark:text-white">${m.model}</h4>
          <p class="text-[11px] text-[#6E6D6A] dark:text-[#8C8B87] mt-0.5 font-serif italic">${m.description}</p>
        </div>
        <div class="grid grid-cols-2 gap-2 pt-2 border-t border-[#EAEAEA] dark:border-[#22262E]">
          <div>
            <span class="text-[10px] font-mono text-[#9E9D99] block">Akurasi (t+1)</span>
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

    // Per-Ticker Table
    const ptBody = document.getElementById("per-ticker-eval-tbody");
    if (ptBody && data.per_ticker_summary) {
      ptBody.innerHTML = "";
      data.per_ticker_summary.forEach(pt => {
        const tr = document.createElement("tr");
        tr.className = "hover:bg-[#FBFBFA] dark:hover:bg-[#1A1E26]";
        tr.innerHTML = `
          <td class="py-2 px-3 font-bold text-[#121212] dark:text-white">${pt.ticker}</td>
          <td class="py-2 px-3 font-sans text-[#6E6D6A] dark:text-[#A8A7A3]">${pt.name}</td>
          <td class="py-2 px-3">${pt.samples} Hari</td>
          <td class="py-2 px-3 text-[#9F2F2D]">${(pt.accuracy_headline_only * 100).toFixed(1)}%</td>
          <td class="py-2 px-3 font-bold text-[#2B6434] dark:text-[#88C493]">${(pt.accuracy_full * 100).toFixed(1)}%</td>
          <td class="py-2 px-3 text-[#2B6434] dark:text-[#88C493]">+${pt.improvement_pct.toFixed(1)}%</td>
          <td class="py-2 px-3 text-[#2B6434] dark:text-[#88C493]">${pt.avg_next_return_on_buy}</td>
          <td class="py-2 px-3 text-[#9F2F2D] dark:text-[#E68583]">${pt.avg_next_return_on_sell}</td>
        `;
        ptBody.appendChild(tr);
      });
    }

    // Backtest Day-by-Day Records Table (t vs t+1)
    const recBody = document.getElementById("backtest-records-tbody");
    if (recBody && data.records) {
      recBody.innerHTML = "";
      data.records.forEach(r => {
        const decBadge = r.predicted_full === "BUY" ? "badge-buy" : "badge-sell";
        const validBadge = r.correct_full
          ? `<span class="px-1.5 py-0.5 rounded bg-[#EDF3EC] text-[#2B6434] border border-[#D2E3D1] font-bold">AKURAT (${r.actual_label})</span>`
          : `<span class="px-1.5 py-0.5 rounded bg-[#FDEBEC] text-[#9F2F2D] border border-[#F9D2D4]">MELESET (Asli: ${r.actual_label})</span>`;

        const tr = document.createElement("tr");
        tr.className = "hover:bg-[#FBFBFA] dark:hover:bg-[#1A1E26]";
        tr.innerHTML = `
          <td class="py-2 px-3">${r.date}</td>
          <td class="py-2 px-3 font-bold text-[#121212] dark:text-white">${r.code}</td>
          <td class="py-2 px-3 tabular-nums">${r.close_t.toLocaleString("id-ID")}</td>
          <td class="py-2 px-3 tabular-nums">${r.close_t1.toLocaleString("id-ID")}</td>
          <td class="py-2 px-3 font-bold tabular-nums ${r.next_return_pct >= 0 ? 'text-[#2B6434]' : 'text-[#9F2F2D]'}">
            ${r.next_return_pct >= 0 ? "+" : ""}${r.next_return_pct.toFixed(2)}%
          </td>
          <td class="py-2 px-3 tabular-nums">
            Judul: ${r.sent_headline_only >= 0 ? "+" : ""}${r.sent_headline_only.toFixed(2)} &rarr; Isi: <strong>${r.sent_effective >= 0 ? "+" : ""}${r.sent_effective.toFixed(2)}</strong>
          </td>
          <td class="py-2 px-3">${r.predicted_headline_only} ${r.correct_headline_only ? "✓" : "✗"}</td>
          <td class="py-2 px-3">
            <span class="px-2 py-0.5 rounded text-[10px] font-bold border ${decBadge}">${r.predicted_full}</span>
            <span class="text-[10px] text-[#9E9D99] ml-1">[${r.fired_rules.join(",")}]</span>
          </td>
          <td class="py-2 px-3">${validBadge}</td>
        `;
        recBody.appendChild(tr);
      });
    }
  } catch (err) {
    console.error("Error loading benchmarks:", err);
  }
}

// Historical Events Cards (Tab 3)
async function loadHistoricalEvents() {
  try {
    const res = await fetch("/api/historical-events");
    const data = await res.json();
    const grid = document.getElementById("historical-events-grid");
    grid.innerHTML = "";

    data.events.forEach(evt => {
      const actBadge = evt.expected_action === "BUY" ? "badge-buy" : "badge-sell";
      const card = document.createElement("div");
      card.className = "p-5 rounded border border-[#EAEAEA] dark:border-[#22262E] bg-white dark:bg-[#14171D] space-y-3";

      const headlinesList = (evt.articles || []).map(a =>
        `<li class="text-xs text-[#6E6D6A] dark:text-[#A8A7A3]">
          <strong class="text-[#121212] dark:text-white font-sans">[${a.source}] Headline:</strong> "${a.headline}"<br>
          <span class="font-serif italic text-[11px]"><strong>Isi:</strong> "${a.body}"</span>
        </li>`
      ).join("");

      card.innerHTML = `
        <div class="flex items-center justify-between">
          <span class="font-mono text-xs font-semibold text-[#121212] dark:text-white">${evt.date} &bull; ${evt.ticker || "^JKSE"}</span>
          <span class="px-2 py-0.5 rounded text-[10px] font-mono font-bold border ${actBadge}">Keputusan: ${evt.expected_action}</span>
        </div>
        <div>
          <h3 class="font-semibold text-xs text-[#121212] dark:text-white">${evt.title}</h3>
          <p class="text-[11px] text-[#6E6D6A] font-mono mt-0.5 tabular-nums">${evt.price_label || ""} &bull; Return Saham Asli (t+1): <strong class="${evt.actual_next_return.startsWith('+') ? 'text-[#2B6434]' : 'text-[#9F2F2D]'}">${evt.actual_next_return}</strong></p>
        </div>
        <ul class="space-y-2 border-l-2 border-[#EAEAEA] dark:border-[#2A2E38] pl-3 py-0.5">
          ${headlinesList}
        </ul>
        <p class="text-[11px] text-[#6E6D6A] dark:text-[#8C8B87] font-serif italic">${evt.summary}</p>
        <button onclick='loadHistoricalEventToSimulator(${JSON.stringify(evt).replace(/'/g, "&apos;")})' class="w-full mt-2 py-1.5 px-3 rounded text-xs font-mono border border-[#EAEAEA] dark:border-[#2E333D] bg-[#FBFBFA] dark:bg-[#1A1E26] text-[#121212] dark:text-white hover:border-[#121212] dark:hover:border-white transition">
          Muat Kasus Ini ke Simulator &rarr;
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
  document.getElementById("input-rsi").value = evt.rsi || 50;
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
