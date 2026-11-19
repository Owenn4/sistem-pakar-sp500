"""
Mesin Inferensi Forward Chaining & Certainty Factor MYCIN (Keputusan Murni BUY vs SELL)
Dilengkapi Natural Language Explanation Generator (Reason to Buy & Reason to Sell)
sesuai masukan Dosen Penguji Sistem Pakar.
"""

from typing import Dict, Any, List, Tuple, Optional
from .rules import RULES, MIN_CF, MIN_MARGIN
from .nlp import ASPECT_LABELS_ID


def infer(F: Dict[str, str], raw_facts: Optional[Dict[str, Any]] = None) -> Tuple[str, Dict[str, float], List[Dict[str, Any]], Dict[str, Any]]:
    """
    Forward chaining pada 14 aturan produksi IF-THEN + kombinasi Certainty Factor MYCIN.
    Rumus kombinasi MYCIN (Wildan & Sari, 2022 [5]):
        CF_gabungan = CF_1 + CF_2 * (1 - CF_1)

    Mengembalikan:
        best_decision: 'BUY' | 'SELL'
        cf_summary: {'BUY': float, 'SELL': float}
        fired_rules: daftar aturan yang aktif beserta alasan manusia & referensi pakar
        trace: rincian langkah inferensi, alasan utama (Reason to Buy / Sell), dan ringkasan eksekutif
    """
    cf: Dict[str, float] = {'BUY': 0.0, 'SELL': 0.0}
    fired: List[Dict[str, Any]] = []
    compounding_steps: Dict[str, List[Dict[str, Any]]] = {'BUY': [], 'SELL': []}
    reasons_to_buy: List[str] = []
    reasons_to_sell: List[str] = []

    for rule_tuple in RULES:
        rid, name, cond, act, c, src, if_text = rule_tuple[:7]
        human_reason = rule_tuple[7] if len(rule_tuple) > 7 else src

        if cond(F):
            prev_cf = cf[act]
            new_cf = prev_cf + c * (1.0 - prev_cf)
            cf[act] = new_cf

            rule_entry = {
                "id": rid,
                "name": name,
                "action": act,
                "rule_cf": c,
                "condition": if_text,
                "source": src,
                "human_reason": human_reason,
            }
            fired.append(rule_entry)

            compounding_steps[act].append({
                "rule_id": rid,
                "rule_name": name,
                "rule_cf": c,
                "prev_cf": round(prev_cf, 4),
                "formula": f"{prev_cf:.2f} + {c:.2f} × (1 - {prev_cf:.2f}) = {new_cf:.2f}",
                "result_cf": round(new_cf, 4),
            })

            if act == 'BUY':
                reasons_to_buy.append(f"[{rid} - {name}] {human_reason}")
            else:
                reasons_to_sell.append(f"[{rid} - {name}] {human_reason}")

    # Tambahkan alasan berbasis data faktual dari raw_facts jika tersedia
    headline_vs_body_insight = ""
    if raw_facts:
        sent_eff = float(raw_facts.get('sent_effective', 0.0))
        sent_head = float(raw_facts.get('sent_headline_only', 0.0))
        cb_count = int(raw_facts.get('clickbait_count', 0))
        conf_count = int(raw_facts.get('confirmed_count', 0))
        div_count = int(raw_facts.get('divergent_count', 0))
        n_art = int(raw_facts.get('n', 0))

        if n_art > 0:
            headline_vs_body_insight = (
                f"Dari {n_art} berita yang dianalisis, skor rata-rata Headline adalah {sent_head:+.3f} "
                f"sedangkan skor efektif setelah verifikasi Isi Berita adalah {sent_eff:+.3f} "
                f"({conf_count} berita terkonfirmasi fakta isi, {cb_count} headline hiperbolis/clickbait didiskon, "
                f"dan {div_count} berita memiliki divergensi judul vs isi)."
            )

        # Tambahkan bukti aspek terkuat ke dalam alasan
        aspect_keys = [
            ('a_monetary', 'monetary'),
            ('a_rupiah_fx', 'rupiah_fx'),
            ('a_financial', 'financial'),
            ('a_inflation', 'inflation'),
            ('a_commodity_sector', 'commodity_sector'),
            ('a_economy', 'economy'),
        ]
        for fk, ak in aspect_keys:
            val = float(raw_facts.get(fk, 0.0))
            label_id = ASPECT_LABELS_ID.get(ak, ak)
            if val >= 0.04:
                reasons_to_buy.append(
                    f"Sentimen aspek {label_id} bernilai positif ({val:+.3f}) dari hasil pembacaan isi berita."
                )
            elif val <= -0.04:
                reasons_to_sell.append(
                    f"Sentimen aspek {label_id} bernilai negatif ({val:+.3f}) yang memberikan tekanan pada pasar."
                )

    # Penentuan Keputusan Murni Binary: BUY vs SELL
    buy_cf = cf['BUY']
    sell_cf = cf['SELL']
    margin = abs(buy_cf - sell_cf)

    if buy_cf > sell_cf:
        best = 'BUY'
        if margin >= 0.35:
            confidence_tier = "Sangat Kuat"
        elif margin >= 0.15:
            confidence_tier = "Kuat"
        else:
            confidence_tier = "Moderat (Unggul Tipis)"
        resolution_reason = (
            f"Rekomendasi BUY terpilih dengan CF {buy_cf:.2f} mengungguli SELL (CF {sell_cf:.2f}) "
            f"dengan selisih keyakinan +{margin:.2f} (Kategori: {confidence_tier})."
        )
    elif sell_cf > buy_cf:
        best = 'SELL'
        if margin >= 0.35:
            confidence_tier = "Sangat Kuat"
        elif margin >= 0.15:
            confidence_tier = "Kuat"
        else:
            confidence_tier = "Moderat (Unggul Tipis)"
        resolution_reason = (
            f"Rekomendasi SELL terpilih dengan CF {sell_cf:.2f} mengungguli BUY (CF {buy_cf:.2f}) "
            f"dengan selisih keyakinan +{margin:.2f} (Kategori: {confidence_tier})."
        )
    else:
        # Tie-breaker transparan jika CF BUY == CF SELL (misal saat pasar sangat netral/datar)
        sent_eff = float(raw_facts.get('sent_effective', 0.0)) if raw_facts else 0.0
        trend_val = float(raw_facts.get('trend', 0.0)) if raw_facts else 0.0
        rsi_val = float(raw_facts.get('rsi', 50.0)) if raw_facts else 50.0

        # Skor komposit tie-breaker: sentimen isi berita + posisi teknikal
        tie_score = (sent_eff * 0.70) + (trend_val * 0.30) - ((rsi_val - 50.0) * 0.001)
        if tie_score >= 0.0:
            best = 'BUY'
            cf['BUY'] = max(cf['BUY'], 0.32)
            confidence_tier = "Moderat (Tie-Breaker Bias Positif)"
            resolution_reason = (
                f"Skor aturan seimbang; Tie-Breaker memilih BUY (CF {cf['BUY']:.2f}) karena kombinasi sentimen efektif isi berita "
                f"({sent_eff:+.3f}) dan tren teknikal ({trend_val*100:+.1f}% vs MA-20) menunjukkan bias akumulasi positif."
            )
            if not reasons_to_buy:
                reasons_to_buy.append(
                    "Kondisi pasar stabil tanpa tekanan berita negatif, disertai bias sentimen/tren yang mendukung akumulasi beli."
                )
        else:
            best = 'SELL'
            cf['SELL'] = max(cf['SELL'], 0.32)
            confidence_tier = "Moderat (Tie-Breaker Bias Defensif)"
            resolution_reason = (
                f"Skor aturan seimbang; Tie-Breaker memilih SELL (CF {cf['SELL']:.2f}) karena kombinasi sentimen efektif isi berita "
                f"({sent_eff:+.3f}) dan tren teknikal ({trend_val*100:+.1f}% vs MA-20) cenderung melemah."
            )
            if not reasons_to_sell:
                reasons_to_sell.append(
                    "Sentimen berita dan momentum harga cenderung melemah di bawah rata-rata, sehingga disarankan mengurangi risiko (Sell)."
                )

    primary_reasons = reasons_to_buy if best == 'BUY' else reasons_to_sell
    counter_reasons = reasons_to_sell if best == 'BUY' else reasons_to_buy

    executive_summary = (
        f"Sistem Pakar merekomendasikan {best} (CF: {cf[best]:.2f} - {confidence_tier}). "
        + (primary_reasons[0] if primary_reasons else resolution_reason)
    )

    trace = {
        "raw_winner": best,
        "final_decision": best,
        "confidence_tier": confidence_tier,
        "resolution_reason": resolution_reason,
        "executive_summary": executive_summary,
        "headline_vs_body_insight": headline_vs_body_insight,
        "reasons_to_buy": reasons_to_buy,
        "reasons_to_sell": reasons_to_sell,
        "primary_reasons": primary_reasons,
        "counter_reasons": counter_reasons,
        "compounding_steps": compounding_steps,
        "min_cf_threshold": MIN_CF,
        "min_margin_threshold": MIN_MARGIN,
        "margin": round(abs(cf['BUY'] - cf['SELL']), 4),
    }

    return best, cf, fired, trace
