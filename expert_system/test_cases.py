from .nlp import headline_sentiment
from .fuzzification import make_facts, fuzzify
from .inference import infer

TEST_CASES = [
    ("TC01", "Pasar tenang, berita netral", ["Stocks little changed ahead of jobs data"], 0.00, 0.004, 0.00, "HOLD", "R01 pasar tenang"),
    ("TC02", "Panik + harga jatuh dalam (oversold)", ["Stocks plunge as fears of recession grow", "Wall Street tumbles on worst selloff in months"], -0.09, 0.020, 0.00, "BUY", "R04/R06 kontrarian"),
    ("TC03", "Ekonomi & sektor keuangan sama-sama negatif", ["Economy shrinks as banks report heavy losses", "Bank lending falls sharply, economic growth slows"], -0.01, 0.012, 0.00, "SELL", "R07 resesi ganda"),
    ("TC04", "Bank sentral menurunkan suku bunga", ["Fed cuts rates to boost economy", "Central bank easing lifts stocks"], 0.01, 0.010, 0.00, "BUY", "R08 pelonggaran moneter"),
    ("TC05", "Inflasi tinggi + kenaikan suku bunga", ["Inflation is not easing as Fed hikes rates", "Rising prices force central bank to raise rates"], 0.00, 0.010, 0.00, "SELL", "R09 inflasi+bunga"),
    ("TC06", "Ekonomi & manufaktur kuat", ["Economy grows strongly as manufacturing output rises", "Factory production jumps, economic growth robust"], 0.01, 0.010, 0.00, "BUY", "R10 ekspansi riil"),
    ("TC07", "PHK massal & pengangguran naik", ["Layoffs surge as unemployment rises", "Job losses mount, jobless claims jump"], -0.01, 0.010, 0.00, "SELL", "R11 tenaga kerja negatif"),
    ("TC08", "Euforia, harga jenuh beli → jangan mengejar", ["Stocks soar to record high as bulls cheer", "Markets surge on booming profits"], 0.07, 0.012, 0.00, "HOLD", "R15 (>R02) tidak kejar momentum"),
    ("TC09", "Tidak ada berita sama sekali", [], 0.00, 0.010, 0.00, "HOLD", "R12/R16 informasi kurang"),
    ("TC10", "Panik mereda setelah crash", ["Stocks rebound as fears ease after crash", "Panic subsides, markets recover"], -0.03, 0.015, -0.15, "BUY", "R05 panik mereda"),
    ("TC11", "Volatilitas tinggi & tren turun", ["Stocks swing wildly as investors weigh data"], -0.03, 0.022, 0.00, "BUY", "R06 capitulation"),
    ("TC12", "Tren naik tenang, sentimen positif", ["Stocks edge higher"], 0.03, 0.005, 0.00, "HOLD", "R01/R14/R15"),
    ("TC13", "Sentimen positif, harga datar (tanpa aturan cocok)", ["Stocks gain on upbeat earnings"], 0.00, 0.010, 0.00, "HOLD", "default HOLD"),
    ("TC14", "Crash headline, harga belum turun dalam", ["Stocks crash in worst rout since 2008", "Panic selling wipes out trillions"], -0.01, 0.015, 0.00, "BUY", "R13 kontrarian"),
    ("TC15", "Sinyal bertentangan (R03 SELL vs R13 BUY)", ["Stocks slide as worries grow", "Wall Street falls on weak data"], -0.03, 0.012, 0.02, "HOLD", "conflict resolution → HOLD"),
    ("TC16", "Pelonggaran moneter tapi harga jenuh beli", ["Fed cuts rates as economy weakens"], 0.06, 0.010, 0.00, "HOLD", "R08 diblokir jenuh beli"),
    ("TC17", "Krisis keuangan + resesi", ["Economy slips into recession as banks fail", "Financial crisis deepens, economic outlook grim"], -0.01, 0.012, 0.00, "SELL", "R07 unggul atas R13"),
    ("TC18", "Rally berita bagus, tren naik", ["Wall Street rallies on strong jobs report", "Stocks climb as hopes rise for more stimulus"], 0.02, 0.011, -0.02, "HOLD", "R14/R15 tidak kejar momentum"),
    ("TC19", "Pesimis ringan, memburuk, tren turun", ["Dow drops as investors worry about slowing growth"], -0.025, 0.014, 0.03, "SELL", "R03 pesimis + tren turun"),
    ("TC20", "Berita campur, menunggu keputusan Fed", ["Stocks mixed as investors await Fed decision", "Markets quiet before earnings"], 0.00, 0.011, 0.00, "HOLD", "R12 netral & datar"),
]

UNIT_TESTS = [
    ("Fed cuts rates", lambda o, a: o > 0, "'rate cut' bernilai positif"),
    ("Fed does not cut rates", lambda o, a: o < headline_sentiment("Fed cuts rates")[0], "negasi menurunkan skor"),
    ("Stocks fall", lambda o, a: o < 0, "kata negatif → negatif"),
    ("Stocks fall sharply", lambda o, a: o < headline_sentiment("Stocks fall")[0], "intensifier memperkuat"),
    ("Stocks fall slightly", lambda o, a: o > headline_sentiment("Stocks fall")[0], "dampener memperlemah"),
    ("Unemployment falls sharply", lambda o, a: o > 0 and a.get('unemployment', 0) > 0, "pengangguran turun = positif (polaritas dibalik)"),
    ("Inflation rises to worrying levels", lambda o, a: a.get('inflation', 0) < 0, "inflasi naik = negatif"),
    ("The company opened a new office", lambda o, a: o == 0, "tanpa kata sentimen → 0"),
]

def run_test_cases():
    results = []
    for tid, desc, hl, tr, vo, ps, exp, why in TEST_CASES:
        f = make_facts(hl, tr, vo, ps)
        F = fuzzify(f)
        dec, cf, fired, trace = infer(F)
        passed = (dec == exp)
        results.append({
            "id": tid,
            "scenario": desc,
            "headlines": hl,
            "trend": tr,
            "volatility": vo,
            "prev_sentiment": ps,
            "expected": exp,
            "actual": dec,
            "fired_rules": [r["id"] for r in fired],
            "cf": {k: round(v, 2) for k, v in cf.items()},
            "passed": passed,
            "reason": why
        })
    return results

def run_unit_tests():
    results = []
    for h, cond, note in UNIT_TESTS:
        o, a = headline_sentiment(h)
        passed = bool(cond(o, a))
        results.append({
            "headline": h,
            "overall_score": round(o, 3),
            "aspects": {k: round(v, 2) for k, v in a.items()},
            "test_note": note,
            "passed": passed
        })
    return results
