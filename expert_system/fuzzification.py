import numpy as np
from .nlp import headline_sentiment, preprocess, LEXICON, ASPECTS

FILLER = [
    "Investors watch earnings calendar this week",
    "Trading volume steady in afternoon session",
    "Analysts review quarterly reports"
]

def level(x, vneg=-0.08, neg=-0.03, pos=0.03, vpos=0.08):
    return 'very_neg' if x <= vneg else 'neg' if x <= neg else 'very_pos' if x >= vpos else 'pos' if x >= pos else 'neutral'

def asp_level(x, t=0.05):
    return 'neg' if x <= -t else 'pos' if x >= t else 'none'

def trend_level(x):
    return 'oversold' if x <= -0.06 else 'down' if x <= -0.02 else 'overextended' if x >= 0.05 else 'up' if x >= 0.02 else 'flat'

def delta_level(x, t=0.02):
    return 'improving' if x >= t else 'deteriorating' if x <= -t else 'stable'

def vol_level(x):
    return 'high' if x >= 0.018 else 'low' if x <= 0.006 else 'normal'

def fear_level(x):
    return 'high' if x >= 0.25 else 'none'

def fuzzify(f):
    """Maps continuous quantitative metrics to qualitative linguistic labels."""
    return {
        'sent': level(f['sent_ma3']),
        'delta': delta_level(f['sent_delta']),
        'trend': trend_level(f['trend']),
        'vol': vol_level(f['vol']),
        'fear': fear_level(f['fear']),
        'econ': asp_level(f['econ'], 0.03),
        'fin': asp_level(f['fin'], 0.05),
        'mon': asp_level(f['a_monetary'], 0.05),
        'infl': asp_level(f['a_inflation'], 0.05),
        'unemp': asp_level(f['a_unemployment'], 0.05),
        'manuf': asp_level(f['a_manufacturing'], 0.05),
        'volume': 'low' if f['n'] <= 1 else 'high' if f['n'] >= 15 else 'normal'
    }

def make_facts(headlines, trend=0.0, vol=0.01, prev_sent=0.0, filler=True):
    """Builds numerical facts dictionary from a list of headlines and market conditions."""
    hs = list(headlines) + (FILLER if (filler and headlines) else [])
    ov, asp, fear = [], {a: [] for a in ASPECTS}, 0
    for t in hs:
        o, a = headline_sentiment(t)
        ov.append(o)
        for k, v in a.items():
            asp[k].append(v)
        if any(LEXICON.get(w, 0) <= -0.7 for w in preprocess(t)):
            fear += 1

    m = lambda v: float(np.mean(v)) if v else 0.0
    s = m(ov)
    f = {
        'n': len(hs),
        'sent_ma3': s,
        'sent_delta': s - prev_sent,
        'trend': trend,
        'vol': vol,
        'fear': fear / len(hs) if hs else 0.0
    }
    for k, v in asp.items():
        f['a_' + k] = m(v)

    f['econ'] = float(np.mean([f['a_economy'], f['a_unemployment'], f['a_manufacturing'], f['a_inflation']]))
    f['fin']  = float(np.mean([f['a_financial'], f['a_monetary']]))
    return f
