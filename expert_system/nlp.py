import re
import math
import numpy as np

LEXICON = {
 # --- positif ---
 'rally':.6,'rallies':.6,'rallied':.6,'surge':.7,'surges':.7,'surged':.7,'soar':.8,'soars':.8,'soared':.8,'jump':.5,'jumps':.5,'jumped':.5,
 'gain':.5,'gains':.5,'gained':.5,'rise':.4,'rises':.4,'rose':.4,'rising':.4,'climb':.5,'climbs':.5,'climbed':.5,'higher':.4,'up':.2,
 'advance':.4,'advances':.4,'record':.5,'boom':.7,'booming':.7,'strong':.5,'stronger':.6,'strength':.5,'robust':.6,'upbeat':.6,
 'optimism':.6,'optimistic':.6,'bullish':.7,'bull':.5,'recovery':.6,'recover':.5,'recovers':.5,'rebound':.6,'rebounds':.6,'growth':.5,
 'expansion':.5,'expand':.4,'profit':.5,'profits':.5,'beat':.4,'beats':.4,'upgrade':.5,'upgrades':.5,'confidence':.4,'improve':.5,'improves':.5,
 'improved':.5,'improving':.5,'stimulus':.5,'easing':.4,'cut':.1,'cuts':.1,'positive':.4,'resilient':.5,'resilience':.5,'boost':.5,'boosts':.5,
 'opportunity':.4,'opportunities':.4,'hope':.3,'hopes':.3,'buy':.3,'outperform':.5,'calm':.3,'relief':.5,'lift':.4,'lifts':.4,'steady':.2,
 'stable':.3,'stabilize':.4,'stabilizes':.4,'upside':.5,'winners':.4,'winner':.4,'breakout':.5,'healthy':.5,'cheer':.4,'cheers':.4,
 # --- negatif ---
 'plunge':-.8,'plunges':-.8,'plunged':-.8,'crash':-.9,'crashes':-.9,'crashed':-.9,'collapse':-.9,'collapses':-.9,'tumble':-.7,'tumbles':-.7,
 'tumbled':-.7,'slump':-.7,'slumps':-.7,'sink':-.6,'sinks':-.6,'sank':-.6,'drop':-.5,'drops':-.5,'dropped':-.5,'fall':-.5,'falls':-.5,'fell':-.5,
 'falling':-.5,'decline':-.5,'declines':-.5,'declined':-.5,'lower':-.4,'down':-.2,'loss':-.5,'losses':-.5,'lose':-.5,'loses':-.5,'lost':-.5,
 'slide':-.5,'slides':-.5,'slid':-.5,'sell-off':-.7,'selloff':-.7,'selling':-.3,'sell':-.3,'weak':-.5,'weaker':-.6,'weakness':-.5,'fear':-.6,'fears':-.6,
 'worry':-.5,'worries':-.5,'worried':-.5,'concern':-.4,'concerns':-.4,'anxiety':-.5,'panic':-.9,'crisis':-.8,'recession':-.8,'recessions':-.8,
 'bear':-.5,'bearish':-.7,'pessimism':-.6,'pessimistic':-.6,'slowdown':-.6,'slowing':-.5,'slow':-.3,'contraction':-.6,'shrink':-.5,'shrinks':-.5,
 'downgrade':-.5,'downgrades':-.5,'miss':-.4,'misses':-.4,'risk':-.3,'risks':-.3,'risky':-.4,'volatile':-.4,'volatility':-.3,'turmoil':-.7,'trouble':-.5,
 'troubles':-.5,'default':-.7,'bankruptcy':-.8,'bankrupt':-.8,'layoffs':-.5,'layoff':-.5,'fraud':-.7,'warning':-.5,'warns':-.5,'warn':-.5,'threat':-.5,
 'threatens':-.5,'uncertainty':-.5,'uncertain':-.4,'negative':-.4,'bubble':-.5,'overvalued':-.5,'correction':-.5,'downside':-.5,'losers':-.4,'stagnant':-.4,
 'struggle':-.5,'struggles':-.5,'pressure':-.3,'shock':-.6,'inflationary':-.3,'dismal':-.7,'grim':-.6,'worst':-.8,'worse':-.6,'hike':-.2,'hikes':-.2,
 'rout':-.8,'spook':-.5,'wipeout':-.8,'wipes':-.5,'tank':-.7,'tanks':-.7,'deteriorate':-.6,'deteriorating':-.6,'sluggish':-.4,'spooks':-.5,'jitters':-.4,
 'fail':-.6,'fails':-.6,'failed':-.6,'failure':-.7,'freeze':-.5,
}

PHRASES = {
 'rate cut':'ratecut','rate cuts':'ratecut','cuts rates':'ratecut','cut rates':'ratecut','lower rates':'ratecut','lowers rates':'ratecut',
 'rate hike':'ratehike','rate hikes':'ratehike','raises rates':'ratehike','raise rates':'ratehike','higher rates':'ratehike','hikes rates':'ratehike',
 'bear market':'bearmarket','bull market':'bullmarket','sell off':'sell-off','all-time high':'record','all time high':'record','record high':'record',
 'job cuts':'layoffs','job losses':'layoffs','jobs added':'jobgain','job gains':'jobgain','beats expectations':'beat','misses expectations':'miss',
 'better than expected':'beat','worse than expected':'miss',
}

LEXICON.update({'ratecut':.5,'ratehike':-.5,'bearmarket':-.7,'bullmarket':.7,'jobgain':.5})

INTENSIFIERS = {'sharply':1.5,'sharp':1.4,'steeply':1.5,'deeply':1.4,'massive':1.5,'biggest':1.4,'worst':1.0,'huge':1.4,'more':1.2,'very':1.3,'extremely':1.5,'record':1.0,'rapid':1.4,'severe':1.4}
DAMPENERS   = {'slightly':0.6,'modestly':0.6,'little':0.6,'mildly':0.6,'marginally':0.5,'slight':0.6,'small':0.7}
NEGATIONS   = {'not','no','never','without',"n't",'nor','neither','avoid','avoids','averts','avert'}

# Tokens of Interest (ToI) per aspek – ide dari FiGAS (Barbaglia et al., 2022) + aspek 'market' untuk saham
ASPECTS = {
 'economy':       ['economy','economic','gdp','growth','consumer','spending','retail','housing'],
 'financial':     ['bank','banks','banking','lender','lending','credit','bond','bonds','treasury','yield','yields','financial','insurer','mortgage','debt'],
 'inflation':     ['inflation','prices','cpi','ppi','costs'],
 'manufacturing': ['manufacturing','factory','industrial','production','output','auto','ism','durable'],
 'monetary':      ['fed','federal','rates','rate','ratecut','ratehike','bernanke','powell','yellen','ecb','central','monetary','fomc','easing','tightening'],
 'unemployment':  ['unemployment','claims','jobs','job','payrolls','payroll','hiring','jobless','employment','layoffs','jobgain','labor'],
 'market':        ['stocks','stock','market','markets','dow','nasdaq','s&p','wall','equities','shares','index','indexes','indices'],
}

TOI2ASPECT = {w: a for a, ws in ASPECTS.items() for w in ws}
WINDOW = 5
DIRECTION = {'rise','rises','rose','rising','fall','falls','fell','falling','drop','drops','dropped','decline','declines','declined','higher','lower',
             'jump','jumps','jumped','surge','surges','surged','climb','climbs','climbed','gain','gains','gained','plunge','plunges','slide','slides','sink','sinks'}
FLIP_TOI = {'unemployment','jobless','inflation','cpi','ppi','prices','costs','layoffs','layoff','claims'}   # naik = buruk

def preprocess(text):
    t = str(text).lower().replace("’", "'")
    for k, v in sorted(PHRASES.items(), key=lambda kv: -len(kv[0])):
        t = t.replace(k, v)
    return re.findall(r"s&p|[a-z]+(?:-[a-z]+)?(?:'t)?", t)

def _word_score(tokens, i):
    s = LEXICON.get(tokens[i], 0.0)
    if s == 0: return 0.0
    for j in range(max(0, i-2), min(len(tokens), i+2)):  # 2 kata sebelum & 1 kata sesudah ("fall sharply")
        if j == i: continue
        w = tokens[j]
        if   w in INTENSIFIERS: s *= INTENSIFIERS[w]
        elif w in DAMPENERS:    s *= DAMPENERS[w]
        elif j < i and (w in NEGATIONS or w.endswith("n't")): s *= -0.8      # negasi hanya dari kata sebelumnya
    return max(-1.0, min(1.0, s))

def headline_sentiment(text):
    """Return (skor_umum, {aspek: skor}). Skor dalam [-1, 1]."""
    tok = preprocess(text)
    scores = [_word_score(tok, i) for i in range(len(tok))]
    for i, w in enumerate(tok):                          # pembalikan polaritas kata arah
        if w in DIRECTION:
            cands = [(abs(j-i), tok[j]) for j in range(max(0, i-WINDOW), min(len(tok), i+WINDOW+1)) if j != i and tok[j] in TOI2ASPECT]
            if cands:
                dist, near = min(cands, key=lambda c: (c[0], c[1] not in FLIP_TOI))
                if near in FLIP_TOI and not any(c[0] == dist and c[1] not in FLIP_TOI for c in cands):
                    scores[i] = -scores[i]
    overall = float(np.clip(sum(scores)/max(1, math.sqrt(len(tok))), -1, 1)) if tok else 0.0
    asp = {}
    for i, w in enumerate(tok):
        a = TOI2ASPECT.get(w)
        if a is None: continue
        lo, hi = max(0, i-WINDOW), min(len(tok), i+WINDOW+1)
        asp.setdefault(a, []).append(sum(scores[j]/(1+abs(j-i)) for j in range(lo, hi) if j != i))
    asp = {a: float(np.clip(np.mean(v)*1.5, -1, 1)) for a, v in asp.items()}
    return overall, asp

def analyze_headline_detail(text):
    """Returns detailed token-level breakdown for explainable UI inspection."""
    tok = preprocess(text)
    token_details = []
    for i, token in enumerate(tok):
        base_score = LEXICON.get(token, 0.0)
        adj_score = _word_score(tok, i)
        aspect = TOI2ASPECT.get(token, None)
        token_details.append({
            "token": token,
            "base_score": round(base_score, 2),
            "adjusted_score": round(adj_score, 2),
            "aspect": aspect,
            "is_toi": aspect is not None,
            "is_modifier": token in INTENSIFIERS or token in DAMPENERS or token in NEGATIONS
        })
    overall, asp = headline_sentiment(text)
    return {
        "text": text,
        "tokens": token_details,
        "overall_score": round(overall, 3),
        "aspect_scores": {k: round(v, 3) for k, v in asp.items()}
    }
