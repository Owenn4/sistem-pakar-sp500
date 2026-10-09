import os
from typing import List, Optional
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from expert_system import (
    headline_sentiment,
    analyze_headline_detail,
    make_facts,
    fuzzify,
    RULES,
    infer,
    run_test_cases,
    run_unit_tests,
    MODEL_COMPARISON,
    SIGNAL_PRECISION,
    BACKTEST_METRICS,
    RULE_FREQUENCY_TOP,
    HISTORICAL_EVENTS,
    LEXICON,
    ASPECTS
)

app = FastAPI(
    title="Sistem Pakar S&P 500",
    description="Explainable Expert System for S&P 500 Market Signals based on FiGAS Aspect Sentiment & MYCIN Certainty Factor",
    version="1.0.0"
)

# Setup static files and templates
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(TEMPLATES_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

class AnalyzeRequest(BaseModel):
    headlines: List[str]
    trend: float = 0.0
    volatility: float = 0.010
    prev_sentiment: float = 0.0
    use_filler: bool = True

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "Sistem Pakar S&P 500",
            "rules_count": len(RULES),
            "lexicon_count": len(LEXICON)
        }
    )

@app.post("/api/analyze")
async def analyze_market(req: AnalyzeRequest):
    # 1. Detailed headline analysis
    headline_analysis = [analyze_headline_detail(h) for h in req.headlines if h.strip()]

    # 2. Extract facts and fuzzify
    raw_facts = make_facts(
        headlines=req.headlines,
        trend=req.trend,
        vol=req.volatility,
        prev_sent=req.prev_sentiment,
        filler=req.use_filler
    )
    linguistic_facts = fuzzify(raw_facts)

    # 3. Forward chaining inference & MYCIN CF
    decision, cf, fired, trace = infer(linguistic_facts)

    return {
        "decision": decision,
        "certainty_factors": {k: round(v, 4) for k, v in cf.items()},
        "numeric_facts": {k: (round(v, 4) if isinstance(v, (int, float)) else v) for k, v in raw_facts.items()},
        "linguistic_facts": linguistic_facts,
        "fired_rules": fired,
        "trace": trace,
        "headline_analysis": headline_analysis
    }

@app.get("/api/rules")
async def get_rules():
    rules_data = []
    for rid, name, cond, act, c, src, if_text in RULES:
        rules_data.append({
            "id": rid,
            "name": name,
            "action": act,
            "cf": c,
            "condition": if_text,
            "source": src
        })
    return {"rules": rules_data, "total": len(rules_data)}

@app.get("/api/test-cases")
async def get_test_cases():
    results = run_test_cases()
    passed_count = sum(1 for r in results if r["passed"])
    return {
        "test_cases": results,
        "passed": passed_count,
        "total": len(results),
        "pass_rate": f"{passed_count / len(results):.1%}"
    }

@app.get("/api/unit-tests")
async def get_unit_tests():
    results = run_unit_tests()
    passed_count = sum(1 for r in results if r["passed"])
    return {
        "unit_tests": results,
        "passed": passed_count,
        "total": len(results),
        "pass_rate": f"{passed_count / len(results):.1%}"
    }

@app.get("/api/benchmarks")
async def get_benchmarks():
    return {
        "model_comparison": MODEL_COMPARISON,
        "signal_precision": SIGNAL_PRECISION,
        "backtest_metrics": BACKTEST_METRICS,
        "rule_frequency": RULE_FREQUENCY_TOP
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
            "sentiment": "Positif" if score > 0 else "Negatif" if score < 0 else "Netral"
        })
    # Sort positive to negative
    items.sort(key=lambda x: -x["score"])
    return {
        "total": len(items),
        "lexicon": items[:150]  # Return top results or query matches
    }
