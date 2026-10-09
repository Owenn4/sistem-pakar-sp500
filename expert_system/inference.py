from .rules import RULES, MIN_CF, MIN_MARGIN

def infer(F):
    """
    Forward chaining + kombinasi Certainty Factor MYCIN.
    Rumus kombinasi: CF_gabungan = CF₁ + CF₂ × (1 - CF₁)
    
    Returns:
        best_decision: 'BUY' | 'HOLD' | 'SELL'
        cf_summary: {'BUY': float, 'SELL': float, 'HOLD': float}
        fired_rules: list of (rid, name, action, cf)
        trace: detailed step-by-step reasoning for explainable UI
    """
    cf = {'BUY': 0.0, 'SELL': 0.0, 'HOLD': 0.0}
    fired = []
    compounding_steps = {'BUY': [], 'SELL': [], 'HOLD': []}

    for rid, name, cond, act, c, src, if_text in RULES:
        if cond(F):
            prev_cf = cf[act]
            new_cf = prev_cf + c * (1.0 - prev_cf)
            cf[act] = new_cf
            fired.append({
                "id": rid,
                "name": name,
                "action": act,
                "rule_cf": c,
                "condition": if_text,
                "source": src
            })
            compounding_steps[act].append({
                "rule_id": rid,
                "rule_name": name,
                "rule_cf": c,
                "prev_cf": round(prev_cf, 4),
                "formula": f"{prev_cf:.2f} + {c:.2f} × (1 - {prev_cf:.2f}) = {new_cf:.2f}",
                "result_cf": round(new_cf, 4)
            })

    raw_best = max(cf, key=cf.get)
    best = raw_best
    resolution_reason = "Skor CF tertinggi dan memenuhi ambang batas keyakinan."

    if best in ('BUY', 'SELL'):
        other = 'SELL' if best == 'BUY' else 'BUY'
        margin = cf[best] - cf[other]
        if cf[best] < MIN_CF:
            best = 'HOLD'
            resolution_reason = f"CF {raw_best} ({cf[raw_best]:.2f}) < ambang batas minimum ({MIN_CF}) → Rekomendasi dialihkan ke HOLD (sinyal terlalu lemah)."
        elif margin < MIN_MARGIN:
            best = 'HOLD'
            resolution_reason = f"Selisih antara {raw_best} ({cf[raw_best]:.2f}) dan {other} ({cf[other]:.2f}) adalah {margin:.2f} (< {MIN_MARGIN}) → Rekomendasi dialihkan ke HOLD (sinyal bertentangan)."
        else:
            resolution_reason = f"{best} terpilih dengan CF {cf[best]:.2f} (unggul {margin:.2f} di atas {other}, ambang batas ≥ {MIN_MARGIN})."
    else:
        if cf['HOLD'] < MIN_CF:
            best = 'HOLD'
            resolution_reason = f"Tidak ada sinyal BUY/SELL yang aktif, fallback default adalah HOLD."
        else:
            resolution_reason = f"HOLD terpilih secara eksplisit dari aturan aktif dengan CF {cf['HOLD']:.2f}."

    trace = {
        "raw_winner": raw_best,
        "final_decision": best,
        "resolution_reason": resolution_reason,
        "compounding_steps": compounding_steps,
        "min_cf_threshold": MIN_CF,
        "min_margin_threshold": MIN_MARGIN,
        "margin": round(abs(cf['BUY'] - cf['SELL']), 4)
    }

    return best, cf, fired, trace
