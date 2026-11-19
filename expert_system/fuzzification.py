"""
Modul Agregasi Fakta & Fuzzifikasi (Numerik ke Linguistik)
Menggabungkan:
1. Hasil Analisis 10-20 Berita Harian (Perbandingan Headline vs Isi Berita & Bobot Sumber)
2. Agregasi Dua Tingkat: Berita Spesifik Emiten (65%) + Berita Makro IHSG (35%)
3. Indikator Teknikal Pasar Modal Indonesia (Tren vs MA-20, RSI-14, Volatilitas 20 Hari)
"""

from typing import List, Dict, Any, Union
import numpy as np
from .nlp import (
    headline_sentiment,
    analyze_article_headline_vs_body,
    preprocess,
    LEXICON,
    ASPECTS,
)


def level(x: float, vneg: float = -0.14, neg: float = -0.03, pos: float = 0.03, vpos: float = 0.14) -> str:
    if x <= vneg:
        return 'very_neg'
    if x <= neg:
        return 'neg'
    if x >= vpos:
        return 'very_pos'
    if x >= pos:
        return 'pos'
    return 'neutral'


def asp_level(x: float, t: float = 0.035) -> str:
    return 'neg' if x <= -t else 'pos' if x >= t else 'none'


def trend_level(x: float) -> str:
    """Fuzzifikasi jarak harga terhadap Moving Average 20 hari (MA-20)."""
    if x <= -0.045:
        return 'oversold'
    if x <= -0.012:
        return 'down'
    if x >= 0.045:
        return 'overextended'
    if x >= 0.012:
        return 'up'
    return 'flat'


def rsi_level(rsi: float) -> str:
    """Fuzzifikasi Relative Strength Index (RSI-14) menurut Murphy (1999)."""
    if rsi <= 35.0:
        return 'oversold'
    if rsi <= 46.0:
        return 'bearish'
    if rsi >= 68.0:
        return 'overbought'
    if rsi >= 54.0:
        return 'bullish'
    return 'neutral'


def delta_level(x: float, t: float = 0.025) -> str:
    return 'improving' if x >= t else 'deteriorating' if x <= -t else 'stable'


def vol_level(x: float) -> str:
    return 'high' if x >= 0.016 else 'low' if x <= 0.007 else 'normal'


def fear_level(x: float, t: float = 0.15) -> str:
    return 'high' if x >= t else 'none'


def credibility_level(clickbait_ratio: float, avg_discrepancy: float) -> str:
    if clickbait_ratio >= 0.35 or avg_discrepancy >= 0.22:
        return 'clickbait_heavy'
    if clickbait_ratio <= 0.15 and avg_discrepancy <= 0.12:
        return 'high_verified'
    return 'moderate'


def fuzzify(f: Dict[str, Any]) -> Dict[str, str]:
    """Memetakan metrik kuantitatif hasil ekstraksi berita & harga ke label linguistik."""
    return {
        'sent': level(f.get('sent_effective', f.get('sent_ma3', 0.0))),
        'sent_head': level(f.get('sent_headline_only', 0.0)),
        'delta': delta_level(f.get('sent_delta', 0.0)),
        'trend': trend_level(f.get('trend', 0.0)),
        'rsi': rsi_level(f.get('rsi', 50.0)),
        'vol': vol_level(f.get('vol', 0.010)),
        'fear': fear_level(f.get('fear', 0.0)),
        'credibility': credibility_level(f.get('clickbait_ratio', 0.0), f.get('avg_discrepancy', 0.0)),
        'mon': asp_level(f.get('a_monetary', 0.0), 0.035),
        'rupiah': asp_level(f.get('a_rupiah_fx', 0.0), 0.035),
        'fin': asp_level(f.get('a_financial', 0.0), 0.035),
        'infl': asp_level(f.get('a_inflation', 0.0), 0.035),
        'comm': asp_level(f.get('a_commodity_sector', 0.0), 0.035),
        'econ': asp_level(f.get('econ', 0.0), 0.030),
        'mkt': asp_level(f.get('a_market', 0.0), 0.035),
        'volume': 'low' if f.get('n', 0) <= 2 else 'high' if f.get('n', 0) >= 10 else 'normal',
    }


def make_facts(
    headlines: Union[List[str], List[Dict[str, Any]]],
    trend: float = 0.0,
    vol: float = 0.010,
    prev_sent: float = 0.0,
    filler: bool = False,
    rsi: float = 50.0,
    ticker: str = "^JKSE",
) -> Dict[str, Any]:
    """
    Membangun kamus fakta numerik dari daftar artikel berita (masing-masing punya Headline + Isi Berita)
    serta indikator teknikal saham.
    Mendukung input berupa List[Dict] (artikel lengkap dengan headline & body) maupun List[str] (headline/teks).
    """
    analyzed_articles: List[Dict[str, Any]] = []

    for item in headlines or []:
        if isinstance(item, dict):
            h_text = str(item.get("headline") or item.get("title") or "").strip()
            b_text = str(item.get("body") or item.get("description") or "").strip()
            if not h_text:
                continue
            art = analyze_article_headline_vs_body(
                headline=h_text,
                body=b_text,
                source=str(item.get("source") or "Media Finansial"),
                url=str(item.get("url") or ""),
                published_at=str(item.get("published_at") or ""),
                scope=str(item.get("scope") or "MACRO_IHSG"),
            )
            analyzed_articles.append(art)
        elif isinstance(item, str) and item.strip():
            raw = item.strip()
            # Jika user memisahkan Judul dan Isi dengan tanda "||" di textarea simulator
            if "||" in raw:
                parts = raw.split("||", 1)
                h_text, b_text = parts[0].strip(), parts[1].strip()
            else:
                h_text, b_text = raw, ""
            art = analyze_article_headline_vs_body(
                headline=h_text,
                body=b_text,
                source="Simulator Input",
                scope="TICKER_SPECIFIC" if ticker != "^JKSE" else "MACRO_IHSG",
            )
            analyzed_articles.append(art)

    n = len(analyzed_articles)
    if n == 0:
        empty_facts: Dict[str, Any] = {
            'n': 0,
            'sent_effective': 0.0,
            'sent_headline_only': 0.0,
            'sent_ma3': 0.0,
            'sent_delta': -prev_sent,
            'trend': float(trend),
            'rsi': float(rsi),
            'vol': float(vol),
            'fear': 0.0,
            'avg_discrepancy': 0.0,
            'clickbait_count': 0,
            'confirmed_count': 0,
            'divergent_count': 0,
            'clickbait_ratio': 0.0,
            'ticker_specific_count': 0,
            'macro_news_count': 0,
            'econ': 0.0,
            'fin': 0.0,
            'articles_analysis': [],
        }
        for a in ASPECTS:
            empty_facts['a_' + a] = 0.0
        return empty_facts

    # Pisahkan berita spesifik saham vs berita makro IHSG untuk agregasi dua tingkat
    ticker_arts = [a for a in analyzed_articles if a["scope"] == "TICKER_SPECIFIC"]
    macro_arts = [a for a in analyzed_articles if a["scope"] != "TICKER_SPECIFIC"]

    def _weighted_avg(arts: List[Dict[str, Any]], key: str) -> float:
        if not arts:
            return 0.0
        weights = [float(a.get("source_weight", 1.0)) for a in arts]
        vals = [float(a.get(key, 0.0)) for a in arts]
        return float(np.average(vals, weights=weights))

    if ticker != "^JKSE" and ticker_arts and macro_arts:
        # 65% Berita Spesifik Emiten + 35% Berita Makroekonomi/IHSG
        sent_eff = 0.65 * _weighted_avg(ticker_arts, "effective_score") + 0.35 * _weighted_avg(macro_arts, "effective_score")
        sent_head = 0.65 * _weighted_avg(ticker_arts, "headline_score") + 0.35 * _weighted_avg(macro_arts, "headline_score")
        sent_body = 0.65 * _weighted_avg(ticker_arts, "body_score") + 0.35 * _weighted_avg(macro_arts, "body_score")
    else:
        sent_eff = _weighted_avg(analyzed_articles, "effective_score")
        sent_head = _weighted_avg(analyzed_articles, "headline_score")
        sent_body = _weighted_avg(analyzed_articles, "body_score")

    # Hitung agregasi aspek
    asp_Buckets: Dict[str, List[float]] = {a: [] for a in ASPECTS}
    fear_hits = 0
    for art in analyzed_articles:
        for k, v in art["aspect_scores"].items():
            if k in asp_Buckets:
                asp_Buckets[k].append(v * art["source_weight"])
        # Fear diukur dari isi berita (jika ada) atau judul yang terkonfirmasi
        check_text = art["body"] if art["body"] else art["headline"]
        if any(LEXICON.get(w, 0.0) <= -0.70 for w in preprocess(check_text)):
            fear_hits += 1

    clickbait_count = sum(1 for a in analyzed_articles if a["verification_status"] == "CLICKBAIT_EXAGGERATED")
    confirmed_count = sum(1 for a in analyzed_articles if a["verification_status"] == "CONFIRMED_CONSISTENT")
    divergent_count = sum(1 for a in analyzed_articles if a["verification_status"] == "DIVERGENT_CONTENT")
    avg_disc = float(np.mean([a["discrepancy"] for a in analyzed_articles]))

    f: Dict[str, Any] = {
        'n': n,
        'sent_effective': round(float(sent_eff), 4),
        'sent_headline_only': round(float(sent_head), 4),
        'sent_body_only': round(float(sent_body), 4),
        'sent_ma3': round(float(sent_eff), 4),  # Alias kompatibilitas
        'sent_delta': round(float(sent_eff - prev_sent), 4),
        'trend': round(float(trend), 4),
        'rsi': round(float(rsi), 2),
        'vol': round(float(vol), 4),
        'fear': round(float(fear_hits / n), 4),
        'avg_discrepancy': round(avg_disc, 4),
        'clickbait_count': clickbait_count,
        'confirmed_count': confirmed_count,
        'divergent_count': divergent_count,
        'clickbait_ratio': round(float(clickbait_count / n), 4),
        'ticker_specific_count': len(ticker_arts),
        'macro_news_count': len(macro_arts),
        'articles_analysis': analyzed_articles,
    }

    for k, vals in asp_Buckets.items():
        f['a_' + k] = round(float(np.mean(vals)) if vals else 0.0, 4)

    f['econ'] = round(
        float(np.mean([f['a_economy'], f['a_inflation'], f['a_commodity_sector']])), 4
    )
    f['fin'] = round(
        float(np.mean([f['a_financial'], f['a_monetary'], f['a_rupiah_fx']])), 4
    )
    return f
