"""
Modul Pengujian Regresi Aturan (14 Skenario Pasar Modal Indonesia) & Unit Test NLP Bilingual FiGAS
"""

from .nlp import headline_sentiment, analyze_article_headline_vs_body
from .fuzzification import make_facts, fuzzify
from .inference import infer

# Format: (id, scenario, articles_or_headlines, trend, vol, prev_sent, rsi, expected, reason)
TEST_CASES = [
    (
        "TC01",
        "Bank Indonesia memangkas suku bunga BI Rate (Dovish)",
        ["Bank Indonesia memangkas suku bunga acuan untuk mendorong pertumbuhan ekonomi || Rapat Dewan Gubernur BI menurunkan BI Rate 25 bps seiring inflasi terkendali rendah."],
        0.01, 0.010, 0.00, 52.0, "BUY", "R01 pelonggaran moneter BI Rate"
    ),
    (
        "TC02",
        "Lonjakan inflasi & kenaikan suku bunga BI Rate (Hawkish)",
        ["Rapat Dewan Gubernur BI putuskan suku bunga acuan naik akibat tekanan inflasi || Kenaikan harga pangan dan inflasi memaksa bank sentral menaikkan suku bunga dan menekan pasar."],
        -0.01, 0.014, 0.00, 46.0, "SELL", "R02 inflasi & pengetatan suku bunga"
    ),
    (
        "TC03",
        "Rupiah menguat & investor asing borong saham (Foreign Net Buy)",
        ["Nilai tukar Rupiah menguat tajam seiring aksi beli bersih investor asing || Aliran modal asing masuk (foreign inflow) memborong saham perbankan LQ45 di Bursa Efek Indonesia."],
        0.015, 0.010, 0.00, 56.0, "BUY", "R03 apresiasi Rupiah & foreign inflow"
    ),
    (
        "TC04",
        "Rupiah melemah & arus modal asing keluar (Capital Outflow)",
        ["Indonesian stocks slide as rupiah weakens on heavy foreign net sell || JAKARTA (Reuters) - Foreign outflows accelerated as the rupiah depreciated sharply against the US dollar."],
        -0.02, 0.016, 0.00, 42.0, "SELL", "R04 depresiasi Rupiah & foreign outflow"
    ),
    (
        "TC05",
        "Laba bersih BBCA melonjak & dividen meningkat",
        ["Laba bersih BBCA melonjak 15% didukung pertumbuhan kredit korporasi || PT Bank Central Asia Tbk membukukan kenaikan laba dan pembagian dividen tunai dengan rasio kredit macet turun."],
        0.02, 0.010, 0.00, 58.0, "BUY", "R05 ekspansi laba & fundamental perbankan"
    ),
    (
        "TC06",
        "Kinerja emiten merosot & kredit macet (NPL) membengkak",
        ["Laba perbankan tertekan akibat beban kredit macet membengkak || Penurunan pendapatan dan kerugian operasional memperburuk prospek ekonomi dan kinerja keuangan emiten."],
        -0.02, 0.015, 0.00, 43.0, "SELL", "R06 tekanan keuangan emiten & makro"
    ),
    (
        "TC07",
        "Harga komoditas batu bara & ekspor industri tumbuh kuat",
        ["Ekspor batu bara dan nikel Indonesia melonjak dorong surplus pertumbuhan ekonomi || Kenaikan harga komoditas energi dan ekspansi manufaktur meningkatkan keuntungan emiten."],
        0.01, 0.011, 0.00, 55.0, "BUY", "R07 momentum komoditas & sektor riil"
    ),
    (
        "TC08",
        "Harga komoditas anjlok & aktivitas manufaktur melambat",
        ["Harga batu bara merosot tajam dan ekspor industri manufaktur menyusut || Pelemahan permintaan komoditas global serta perlambatan ekonomi menekan laba sektor tambang."],
        -0.02, 0.014, 0.00, 44.0, "SELL", "R08 perlambatan komoditas & manufaktur"
    ),
    (
        "TC09",
        "Clickbait Filter: Headline panik lebay tetapi isi berita positif/stabil",
        ["IHSG Kebakaran dan Ambruk Rontok Berdarah di Awal Sesi! || Walaupun judul terdengar mengerikan, koreksi hanya tipis 0,1% dan investor asing justru melakukan net buy karena pertumbuhan laba emiten sangat solid dan stabil."],
        0.005, 0.010, 0.00, 51.0, "BUY", "R09 diskon clickbait (isi berita positif)"
    ),
    (
        "TC10",
        "Deteksi Divergensi: Headline tampak positif tetapi isi berita membongkar kerugian",
        ["Manajemen Emiten Optimistis Target Pendapatan Tahun Ini Tercapai || Namun di dalam rincian laporan keuangan, perusahaan mengalami kerugian bersih parah akibat beban utang membengkak, gagal bayar, dan aksi net sell asing."],
        -0.015, 0.015, 0.02, 45.0, "SELL", "R10 risiko tersembunyi di isi berita"
    ),
    (
        "TC11",
        "Rebound teknikal pada area jenuh jual (Oversold MA-20 & RSI-14)",
        ["Saham TLKM mulai pulih didukung rencana buyback setelah koreksi dalam || Arus kas perusahaan tetap sehat dan analis menilai harga saham sudah terlalu murah di area jenuh jual."],
        -0.065, 0.018, -0.10, 31.0, "BUY", "R11 technical rebound pada area oversold"
    ),
    (
        "TC12",
        "Rawan ambil untung pada area jenuh beli (Overextended / Overbought)",
        ["Saham mulai terkoreksi akibat aksi ambil untung setelah reli panjang || Valuasi saham sudah terlalu mahal di zona jenuh beli sehingga investor mulai melepas kepemilikan."],
        0.065, 0.016, 0.10, 74.0, "SELL", "R12 risiko profit taking saat overbought"
    ),
    (
        "TC13",
        "Tren naik sehat & sentimen isi berita positif terkonfirmasi",
        ["IHSG menguat didukung optimisme pasar dan pertumbuhan investasi domestik || Pergerakan bursa saham tetap berada dalam tren naik yang sehat seiring masuknya dana investor."],
        0.022, 0.009, 0.00, 57.0, "BUY", "R13 konfirmasi uptrend & sentimen positif"
    ),
    (
        "TC14",
        "Tren turun & sentimen berita memburuk",
        ["IHSG melemah tertekan kekhawatiran pasar dan aksi jual berlanjut || Tekanan penurunan harga saham semakin memburuk akibat sentimen negatif dan pelemahan indeks."],
        -0.028, 0.015, 0.05, 41.0, "SELL", "R14 konfirmasi downtrend & sentimen memburuk"
    ),
]

UNIT_TESTS = [
    (
        "Bank Indonesia memangkas suku bunga acuan",
        lambda o, a: o > 0 and a.get("monetary", 0) > 0,
        "BI Rate dipangkas = sentimen moneter positif (Dovish)"
    ),
    (
        "Rapat Dewan Gubernur BI putuskan suku bunga acuan naik",
        lambda o, a: o < 0 and a.get("monetary", 0) < 0,
        "BI Rate naik = sentimen moneter negatif (Hawkish)"
    ),
    (
        "Laba bersih BBCA melonjak tajam dan asing net buy",
        lambda o, a: o > 0.3 and a.get("financial", 0) > 0,
        "Kamus Bahasa Indonesia: laba melonjak + net buy = positif kuat"
    ),
    (
        "IHSG tidak jadi melemah berkat penguatan Rupiah",
        lambda o, a: o > headline_sentiment("IHSG melemah")[0],
        "Negasi Bahasa Indonesia ('tidak') membalikkan kata negatif"
    ),
    (
        "Inflasi domestik melandai dan pengangguran turun tajam",
        lambda o, a: o > 0 and a.get("inflation", 0) > 0,
        "Directional Polarity Flip: inflasi & pengangguran turun = positif (+)"
    ),
    (
        "Inflasi pangan melonjak dan rasio kredit macet naik",
        lambda o, a: o < 0 and a.get("inflation", 0) < 0,
        "Directional Polarity Flip: inflasi & kredit macet naik = negatif (-)"
    ),
    (
        "Indonesian shares rally as rupiah strengthens on foreign inflows",
        lambda o, a: o > 0 and a.get("rupiah_fx", 0) > 0,
        "Bilingual Reuters (EN): rally + foreign inflows = positif"
    ),
    (
        "Jakarta stocks plunge as rupiah weakens and foreign outflows surge",
        lambda o, a: o < 0 and a.get("rupiah_fx", 0) < 0,
        "Bilingual Reuters (EN): plunge + rupiah weakens + outflows = negatif"
    ),
    (
        "Clickbait Test: 'IHSG Kebakaran Ambruk!' vs Isi Berita Stabil & Net Buy",
        lambda o, a: analyze_article_headline_vs_body(
            "IHSG Kebakaran dan Ambruk Parah!",
            "Koreksi sebenarnya sangat tipis dan wajar, sementara laba perbankan tetap tumbuh kuat dan asing mencatat net buy."
        )["verification_status"] == "CLICKBAIT_EXAGGERATED",
        "Deteksi Clickbait: Headline ekstrem didiskon terhadap isi berita"
    ),
    (
        "Divergence Test: Headline Optimis vs Isi Berita Rugi & Utang Bengkak",
        lambda o, a: analyze_article_headline_vs_body(
            "Emiten Optimistis Pertumbuhan Pendapatan Meningkat",
            "Namun laporan keuangan menunjukkan perusahaan mengalami kerugian besar, gagal bayar utang, dan aksi net sell."
        )["verification_status"] == "DIVERGENT_CONTENT",
        "Deteksi Divergensi: Fakta risiko di isi berita diprioritaskan (85%)"
    ),
]


def run_test_cases():
    results = []
    for tid, desc, hl, tr, vo, ps, rsi_val, exp, why in TEST_CASES:
        f = make_facts(hl, trend=tr, vol=vo, prev_sent=ps, rsi=rsi_val)
        F = fuzzify(f)
        dec, cf, fired, trace = infer(F, f)
        passed = (dec == exp)
        results.append({
            "id": tid,
            "scenario": desc,
            "headlines": hl,
            "trend": tr,
            "rsi": rsi_val,
            "volatility": vo,
            "prev_sentiment": ps,
            "expected": exp,
            "actual": dec,
            "fired_rules": [r["id"] for r in fired],
            "cf": {k: round(v, 2) for k, v in cf.items()},
            "passed": passed,
            "reason": why,
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
            "passed": passed,
        })
    return results
