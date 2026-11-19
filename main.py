import os
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from expert_system import (
    headline_sentiment,
    analyze_headline_detail,
    analyze_article_headline_vs_body,
    make_facts,
    fuzzify,
    RULES,
    ACADEMIC_REFERENCES,
    infer,
    run_test_cases,
    run_unit_tests,
    MODEL_COMPARISON,
    SIGNAL_PRECISION,
    BACKTEST_METRICS,
    RULE_FREQUENCY_TOP,
    HISTORICAL_EVENTS,
    PER_TICKER_SUMMARY,
    OVERALL_METRICS,
    load_2y_dataset,
    LEXICON,
    ASPECTS,
    ASPECT_LABELS_ID,
    FEATURED_TICKERS,
    normalize_indo_ticker,
    fetch_stock_indicators,
    fetch_live_news_for_ticker,
)

app = FastAPI(
    title="Sistem Pakar Saham Indonesia (IHSG & LQ45)",
    description=(
        "Sistem Pakar Rekomendasi BUY vs SELL Saham Indonesia Berbasis Perbandingan Sentimen "
        "Headline vs Isi Berita (Bilingual FiGAS: Indonesia & Reuters) dan Certainty Factor MYCIN"
    ),
    version="2.0.0",
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


class ArticleInput(BaseModel):
    headline: str
    body: str = ""
    source: str = "Simulator Input"
    scope: str = "MACRO_IHSG"
    url: str = ""
    published_at: str = "Simulasi"


class AnalyzeRequest(BaseModel):
    headlines: List[str] = []
    articles: Optional[List[ArticleInput]] = None
    trend: float = 0.0
    rsi: float = 50.0
    volatility: float = 0.010
    prev_sentiment: float = 0.0
    use_filler: bool = False
    ticker: str = "^JKSE"


class LiveStockRequest(BaseModel):
    ticker: str = "^JKSE"
    max_articles: int = 12


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "Sistem Pakar Saham Indonesia (IHSG & LQ45)",
            "rules_count": len(RULES),
            "lexicon_count": len(LEXICON),
        },
    )


@app.get("/api/tickers")
async def get_tickers():
    return {
        "featured": list(FEATURED_TICKERS.values()),
        "default": "^JKSE",
    }


@app.post("/api/live-stock-analyze")
async def live_stock_analyze(req: LiveStockRequest):
    norm_tk = normalize_indo_ticker(req.ticker)
    stock_info = fetch_stock_indicators(norm_tk, period="2y")
    raw_articles = fetch_live_news_for_ticker(norm_tk, max_articles=req.max_articles)

    raw_facts = make_facts(
        headlines=raw_articles,
        trend=stock_info["trend"],
        vol=stock_info["volatility"],
        prev_sent=0.0,
        rsi=stock_info["rsi14"],
        ticker=norm_tk,
    )
    linguistic_facts = fuzzify(raw_facts)
    decision, cf, fired, trace = infer(linguistic_facts, raw_facts)

    # Hitung juga keputusan jika HANYA membaca Headline (sebagai pembanding di UI)
    headline_only_inputs = [
        {"headline": a["headline"], "body": "", "source": a.get("source", ""), "scope": a.get("scope", "MACRO_IHSG")}
        for a in raw_articles
    ]
    facts_head_only = make_facts(
        headlines=headline_only_inputs,
        trend=stock_info["trend"],
        vol=stock_info["volatility"],
        prev_sent=0.0,
        rsi=stock_info["rsi14"],
        ticker=norm_tk,
    )
    lf_head_only = fuzzify(facts_head_only)
    dec_head_only, cf_head_only, _, _ = infer(lf_head_only, facts_head_only)

    numeric_clean = {
        k: (round(v, 4) if isinstance(v, (int, float)) else v)
        for k, v in raw_facts.items()
        if k != "articles_analysis"
    }

    return {
        "stock_info": stock_info,
        "decision": decision,
        "certainty_factors": {k: round(v, 4) for k, v in cf.items()},
        "headline_only_comparison": {
            "decision": dec_head_only,
            "cf": {k: round(v, 4) for k, v in cf_head_only.items()},
            "sent_headline_only": raw_facts["sent_headline_only"],
            "sent_effective": raw_facts["sent_effective"],
        },
        "numeric_facts": numeric_clean,
        "linguistic_facts": linguistic_facts,
        "fired_rules": fired,
        "trace": trace,
        "articles_analysis": raw_facts["articles_analysis"],
    }


@app.post("/api/analyze")
async def analyze_market(req: AnalyzeRequest):
    if req.articles and len(req.articles) > 0:
        inputs: List[Any] = [a.model_dump() for a in req.articles if a.headline.strip()]
    else:
        inputs = [h for h in req.headlines if h.strip()]

    raw_facts = make_facts(
        headlines=inputs,
        trend=req.trend,
        vol=req.volatility,
        prev_sent=req.prev_sentiment,
        filler=req.use_filler,
        rsi=req.rsi,
        ticker=req.ticker,
    )
    linguistic_facts = fuzzify(raw_facts)
    decision, cf, fired, trace = infer(linguistic_facts, raw_facts)

    headline_analysis = []
    for art in raw_facts["articles_analysis"]:
        detail = analyze_headline_detail(art["headline"])
        detail["body_text"] = art["body"]
        detail["headline_score"] = art["headline_score"]
        detail["body_score"] = art["body_score"]
        detail["effective_score"] = art["effective_score"]
        detail["verification_status"] = art["verification_status"]
        detail["verification_label"] = art["verification_label"]
        detail["verification_explanation"] = art["verification_explanation"]
        detail["evidence_snippet"] = art["evidence_snippet"]
        detail["aspect_scores"] = art["aspect_scores"]
        headline_analysis.append(detail)

    numeric_clean = {
        k: (round(v, 4) if isinstance(v, (int, float)) else v)
        for k, v in raw_facts.items()
        if k != "articles_analysis"
    }

    return {
        "decision": decision,
        "certainty_factors": {k: round(v, 4) for k, v in cf.items()},
        "numeric_facts": numeric_clean,
        "linguistic_facts": linguistic_facts,
        "fired_rules": fired,
        "trace": trace,
        "headline_analysis": headline_analysis,
        "articles_analysis": raw_facts["articles_analysis"],
    }


@app.get("/api/rules")
async def get_rules():
    rules_data = []
    for rule_tuple in RULES:
        rid, name, cond, act, c, src, if_text = rule_tuple[:7]
        human_reason = rule_tuple[7] if len(rule_tuple) > 7 else src
        rules_data.append({
            "id": rid,
            "name": name,
            "action": act,
            "cf": c,
            "condition": if_text,
            "source": src,
            "human_reason": human_reason,
        })
    return {
        "rules": rules_data,
        "total": len(rules_data),
        "references": ACADEMIC_REFERENCES,
    }


@app.get("/api/test-cases")
async def get_test_cases():
    results = run_test_cases()
    passed_count = sum(1 for r in results if r["passed"])
    return {
        "test_cases": results,
        "passed": passed_count,
        "total": len(results),
        "pass_rate": f"{passed_count / len(results):.1%}",
    }


@app.get("/api/unit-tests")
async def get_unit_tests():
    results = run_unit_tests()
    passed_count = sum(1 for r in results if r["passed"])
    return {
        "unit_tests": results,
        "passed": passed_count,
        "total": len(results),
        "pass_rate": f"{passed_count / len(results):.1%}",
    }


@app.get("/api/benchmarks")
async def get_benchmarks(ticker: Optional[str] = None):
    dataset_2y = load_2y_dataset()
    records = dataset_2y.get("records", [])
    if ticker and ticker != "ALL":
        norm_t = normalize_indo_ticker(ticker)
        records = [r for r in records if r["ticker"] == norm_t]

    return {
        "period": dataset_2y.get("period", "2024-11-19 s/d 2026-11-19"),
        "overall_metrics": OVERALL_METRICS,
        "per_ticker_summary": PER_TICKER_SUMMARY,
        "model_comparison": MODEL_COMPARISON,
        "signal_precision": SIGNAL_PRECISION,
        "backtest_metrics": BACKTEST_METRICS,
        "rule_frequency": RULE_FREQUENCY_TOP,
        "records": records[:120],
    }


@app.get("/api/historical-events")
async def get_historical_events():
    return {"events": HISTORICAL_EVENTS}


@app.get("/api/lexicon")
async def get_lexicon(query: Optional[str] = None):
    items = []
    for word, score in LEXICON.items():
        if query and query.lower() not in word.lower():
            continue
        items.append({
            "word": word,
            "score": score,
            "sentiment": "Positif" if score > 0 else "Negatif" if score < 0 else "Netral",
        })
    items.sort(key=lambda x: -x["score"])
    return {
        "total": len(items),
        "lexicon": items[:200],
        "aspects": ASPECT_LABELS_ID,
    }
