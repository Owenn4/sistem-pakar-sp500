"""
Modul NLP Sistem Pakar Saham Indonesia (Bilingual FiGAS: Bahasa Indonesia & Inggris)
Dilengkapi mekanisme:
1. Analisis Sentimen Berbasis Aspek (7 Aspek Pasar Modal Indonesia & Makroekonomi)
2. Penanganan Negasi, Penguat (Intensifiers), Pelemah (Dampeners), dan Pembalikan Polaritas Arah (Directional Flip)
3. Perbandingan Headline vs Isi Berita (Sensationalism / Clickbait Discount & Content Verification)

Referensi Akademik:
- [1] Barbaglia, Consoli, & Manzan (2023) - Forecasting with Economic News
- [3] Consoli, Barbaglia, & Manzan (2022) - Fine-grained, aspect-based sentiment analysis (FiGAS)
- [4] Bi (2022) - Stock Market Prediction Based on Financial News Text Mining
- [7] Du, Xing, Mao, & Cambria (2024) - Financial Sentiment Analysis: Techniques and Applications
"""

import re
import math
from typing import Dict, List, Tuple, Optional, Any
import numpy as np

# =====================================================================
# 1. KAMUS SENTIMEN KEUANGAN BILINGUAL (BAHASA INDONESIA + INGGRIS)
# =====================================================================
LEXICON: Dict[str, float] = {
    # --- BAHASA INDONESIA: POSITIF ---
    'menguat': 0.55, 'penguatan': 0.50, 'melonjak': 0.75, 'lonjakan': 0.65,
    'melesat': 0.80, 'meroket': 0.85, 'terbang': 0.70, 'naik': 0.45,
    'kenaikan': 0.40, 'tumbuh': 0.55, 'pertumbuhan': 0.50, 'meningkat': 0.50,
    'peningkatan': 0.45, 'laba': 0.55, 'untung': 0.55, 'keuntungan': 0.55,
    'cuan': 0.60, 'dividen': 0.55, 'surplus': 0.55, 'ekspansi': 0.55,
    'optimis': 0.60, 'optimisme': 0.60, 'optimistis': 0.60, 'positif': 0.45,
    'hijau': 0.45, 'cerah': 0.45, 'bergairah': 0.55, 'sumringah': 0.55,
    'kokoh': 0.50, 'solid': 0.55, 'kuat': 0.50, 'tangguh': 0.55,
    'pulih': 0.55, 'pemulihan': 0.55, 'bangkit': 0.55, 'rekor': 0.60,
    'tertinggi': 0.50, 'borong': 0.65, 'diborong': 0.65, 'akumulasi': 0.55,
    'apresiasi': 0.50, 'stimulus': 0.55, 'insentif': 0.50, 'pelonggaran': 0.50,
    'efisiensi': 0.45, 'stabil': 0.35, 'terkendali': 0.40, 'kondusif': 0.45,
    'prospek': 0.35, 'peluang': 0.40, 'unggulan': 0.45, 'primadona': 0.55,
    'menarik': 0.40, 'rekomendasibeli': 0.65, 'netbuy': 0.65, 'inflow': 0.55,
    'inflows': 0.55, 'dovish': 0.50, 'ratecut': 0.65, 'oversubscribed': 0.60,
    'buyback': 0.55, 'melampaui': 0.55, 'moncer': 0.65, 'kinclong': 0.60,
    'mendorong': 0.45, 'dorong': 0.45, 'didukung': 0.40, 'dukung': 0.40,
    'pangkas': -0.25, 'memangkas': -0.25, 'dipangkas': -0.25,
    'turunkan': -0.35, 'menurunkan': -0.35, 'diturunkan': -0.35,
    'naikkan': 0.35, 'menaikkan': 0.35, 'dinaikkan': 0.35,

    # --- BAHASA INDONESIA: NEGATIF ---
    'melemah': -0.55, 'pelemahan': -0.50, 'anjlok': -0.80, 'ambruk': -0.85,
    'rontok': -0.80, 'tumbang': -0.75, 'terjun': -0.80, 'terperosok': -0.75,
    'merosot': -0.65, 'turun': -0.45, 'penurunan': -0.45, 'terkoreksi': -0.50,
    'koreksi': -0.45, 'tertekan': -0.55, 'tekanan': -0.45, 'loyo': -0.55,
    'lesu': -0.55, 'melambat': -0.55, 'perlambatan': -0.55, 'menyusut': -0.55,
    'rugi': -0.70, 'kerugian': -0.70, 'boncos': -0.75, 'defisit': -0.55,
    'utang': -0.35, 'beban': -0.40, 'bengkak': -0.50, 'membengkak': -0.55,
    'macet': -0.65, 'gagalbayar': -0.85, 'pailit': -0.85, 'bangkrut': -0.85,
    'krisis': -0.80, 'resesi': -0.80, 'panik': -0.85, 'kepanikan': -0.80,
    'takut': -0.55, 'kekhawatiran': -0.50, 'khawatir': -0.50, 'waswas': -0.45,
    'cemas': -0.50, 'risiko': -0.35, 'ancaman': -0.55, 'terancam': -0.55,
    'gejolak': -0.55, 'bergejolak': -0.55, 'ketidakpastian': -0.50, 'merah': -0.45,
    'kebakaran': -0.75, 'berdarah': -0.80, ' suram': -0.65, 'pesimis': -0.60,
    'negatif': -0.45, 'buruk': -0.55, 'memburuk': -0.65, 'terendah': -0.55,
    'depresiasi': -0.55, 'netsell': -0.65, 'outflow': -0.60, 'outflows': -0.60,
    'kabur': -0.60, 'hengkang': -0.60, 'lepas': -0.35, 'obral': -0.50,
    'phk': -0.65, 'pengangguran': -0.55, 'sanksi': -0.60, 'denda': -0.50,
    'korupsi': -0.75, 'skandal': -0.75, 'pengetatan': -0.45, 'hawkish': -0.50,
    'ratehike': -0.60, 'inflasi': -0.35, 'mahal': -0.35, 'konflik': -0.55,
    'perang': -0.65, 'tarif': -0.30, 'suspend': -0.70, 'suspensi': -0.70,

    # --- ENGLISH (REUTERS & GLOBAL): POSITIVE ---
    'rally': 0.65, 'rallies': 0.65, 'rallied': 0.65, 'surge': 0.70, 'surges': 0.70,
    'surged': 0.70, 'soar': 0.80, 'soars': 0.80, 'soared': 0.80, 'jump': 0.55,
    'jumps': 0.55, 'jumped': 0.55, 'gain': 0.50, 'gains': 0.50, 'gained': 0.50,
    'rise': 0.40, 'rises': 0.40, 'rose': 0.40, 'rising': 0.40, 'climb': 0.50,
    'climbs': 0.50, 'climbed': 0.50, 'higher': 0.40, 'up': 0.20, 'advance': 0.45,
    'advances': 0.45, 'record': 0.55, 'boom': 0.70, 'booming': 0.70, 'strong': 0.50,
    'stronger': 0.60, 'strength': 0.50, 'robust': 0.60, 'upbeat': 0.60,
    'optimism': 0.60, 'optimistic': 0.60, 'bullish': 0.70, 'bull': 0.50,
    'recovery': 0.60, 'recover': 0.55, 'recovers': 0.55, 'rebound': 0.60,
    'rebounds': 0.60, 'growth': 0.50, 'expansion': 0.50, 'expand': 0.45,
    'profit': 0.55, 'profits': 0.55, 'beat': 0.50, 'beats': 0.50, 'upgrade': 0.55,
    'upgrades': 0.55, 'upgraded': 0.55, 'confidence': 0.45, 'improve': 0.50,
    'improves': 0.50, 'improved': 0.50, 'improving': 0.50, 'easing': 0.45,
    'positive': 0.45, 'resilient': 0.55, 'resilience': 0.55, 'boost': 0.55,
    'boosts': 0.55, 'boosted': 0.55, 'outperform': 0.55, 'relief': 0.50,
    'lift': 0.45, 'lifts': 0.45, 'steady': 0.25, 'stable': 0.35, 'stabilize': 0.45,
    'stabilizes': 0.45, 'upside': 0.50, 'breakout': 0.55, 'healthy': 0.50,
    'cheer': 0.45, 'cheers': 0.45, 'jobgain': 0.55, 'bullmarket': 0.70,

    # --- ENGLISH (REUTERS & GLOBAL): NEGATIVE ---
    'plunge': -0.80, 'plunges': -0.80, 'plunged': -0.80, 'crash': -0.90,
    'crashes': -0.90, 'crashed': -0.90, 'collapse': -0.90, 'collapses': -0.90,
    'tumble': -0.70, 'tumbles': -0.70, 'tumbled': -0.70, 'slump': -0.70,
    'slumps': -0.70, 'sink': -0.60, 'sinks': -0.60, 'sank': -0.60,
    'drop': -0.50, 'drops': -0.50, 'dropped': -0.50, 'fall': -0.50,
    'falls': -0.50, 'fell': -0.50, 'falling': -0.50, 'decline': -0.50,
    'declines': -0.50, 'declined': -0.50, 'lower': -0.40, 'down': -0.25,
    'loss': -0.55, 'losses': -0.55, 'lose': -0.50, 'loses': -0.50, 'lost': -0.50,
    'slide': -0.50, 'slides': -0.50, 'slid': -0.50, 'sell-off': -0.70,
    'selloff': -0.70, 'selling': -0.35, 'weak': -0.50, 'weaker': -0.60,
    'weakness': -0.50, 'weakens': -0.55, 'weakened': -0.55, 'fear': -0.60,
    'fears': -0.60, 'worry': -0.50, 'worries': -0.50, 'worried': -0.50,
    'concern': -0.45, 'concerns': -0.45, 'panic': -0.90, 'crisis': -0.80,
    'recession': -0.80, 'bear': -0.50, 'bearish': -0.70, 'pessimism': -0.60,
    'slowdown': -0.60, 'slowing': -0.50, 'contraction': -0.60, 'shrink': -0.55,
    'shrinks': -0.55, 'downgrade': -0.55, 'downgrades': -0.55, 'downgraded': -0.55,
    'miss': -0.45, 'misses': -0.45, 'risk': -0.35, 'risks': -0.35,
    'volatile': -0.40, 'volatility': -0.35, 'turmoil': -0.70, 'default': -0.75,
    'defaults': -0.75, 'bankruptcy': -0.85, 'layoffs': -0.60, 'layoff': -0.60,
    'fraud': -0.75, 'warning': -0.50, 'warns': -0.50, 'threat': -0.50,
    'threatens': -0.50, 'uncertainty': -0.50, 'negative': -0.45, 'bubble': -0.50,
    'correction': -0.50, 'downside': -0.50, 'pressure': -0.35, 'shock': -0.60,
    'dismal': -0.70, 'grim': -0.65, 'worst': -0.80, 'worse': -0.60,
    'hike': -0.25, 'hikes': -0.25, 'rout': -0.80, 'wipeout': -0.80,
    'tank': -0.70, 'tanks': -0.70, 'deteriorate': -0.60, 'sluggish': -0.45,
    'jitters': -0.45, 'fail': -0.60, 'failure': -0.70, 'bearmarket': -0.70,
    'npa': -0.50, 'npl': -0.50, 'deficit': -0.45, 'dip': -0.40, 'dips': -0.40,
    'slip': -0.40, 'slips': -0.40, 'slipped': -0.40, 'softens': -0.40,
}

# Frasa multi-kata yang dinormalisasi menjadi satu token sebelum skoring
PHRASES: Dict[str, str] = {
    # Bahasa Indonesia
    'pangkas suku bunga': 'ratecut',
    'memangkas suku bunga': 'ratecut',
    'penurunan suku bunga': 'ratecut',
    'suku bunga turun': 'ratecut',
    'bi rate turun': 'ratecut',
    'turunkan suku bunga': 'ratecut',
    'menurunkan suku bunga': 'ratecut',
    'kenaikan suku bunga': 'ratehike',
    'menaikkan suku bunga': 'ratehike',
    'naikkan suku bunga': 'ratehike',
    'suku bunga acuan naik': 'ratehike',
    'suku bunga acuan turun': 'ratecut',
    'suku bunga naik': 'ratehike',
    'bi rate naik': 'ratehike',
    'suku bunga acuan': 'sukubunga',
    'suku bunga': 'sukubunga',
    'bi rate': 'birate',
    'beli bersih': 'netbuy',
    'net buy': 'netbuy',
    'foreign net buy': 'netbuy',
    'asing borong': 'netbuy',
    'jual bersih': 'netsell',
    'net sell': 'netsell',
    'foreign net sell': 'netsell',
    'asing lepas': 'netsell',
    'asing keluar': 'outflow',
    'modal keluar': 'outflow',
    'capital outflow': 'outflow',
    'modal masuk': 'inflow',
    'capital inflow': 'inflow',
    'gagal bayar': 'gagalbayar',
    'kredit macet': 'npl',
    'rasio kredit macet': 'npl',
    'non performing loan': 'npl',
    'rekomendasi beli': 'rekomendasibeli',
    'ambil untung': 'koreksi',
    'profit taking': 'koreksi',
    'bank indonesia': 'bi',
    'bursa efek indonesia': 'bei',
    'batu bara': 'batubara',
    'daya beli': 'dayabeli',
    'tenaga kerja': 'tenagakerja',
    'nilai tukar': 'kurs',
    # English (Reuters / Yahoo Finance)
    'rate cut': 'ratecut', 'rate cuts': 'ratecut', 'cuts rates': 'ratecut',
    'cut rates': 'ratecut', 'lower rates': 'ratecut', 'lowers rates': 'ratecut',
    'cuts policy rate': 'ratecut', 'cuts benchmark rate': 'ratecut',
    'rate hike': 'ratehike', 'rate hikes': 'ratehike', 'raises rates': 'ratehike',
    'raise rates': 'ratehike', 'higher rates': 'ratehike', 'hikes rates': 'ratehike',
    'raised its policy rates': 'ratehike', 'raises policy rate': 'ratehike',
    'bear market': 'bearmarket', 'bull market': 'bullmarket', 'sell off': 'sell-off',
    'all-time high': 'record', 'all time high': 'record', 'record high': 'record',
    'job cuts': 'layoffs', 'job losses': 'layoffs', 'jobs added': 'jobgain',
    'beats expectations': 'beat', 'misses expectations': 'miss',
    'better than expected': 'beat', 'worse than expected': 'miss',
}

# Kata Penguat (Intensifiers), Pelemah (Dampeners), dan Negasi Bilingual
INTENSIFIERS: Dict[str, float] = {
    # Indonesia
    'sangat': 1.35, 'tajam': 1.45, 'drastis': 1.50, 'hebat': 1.45,
    'masif': 1.45, 'signifikan': 1.35, 'ekstrem': 1.50, 'parah': 1.45,
    'dalam': 1.30, 'tinggi': 1.25, 'besar': 1.25, 'kuat': 1.25,
    # English
    'sharply': 1.50, 'sharp': 1.40, 'steeply': 1.50, 'deeply': 1.40,
    'massive': 1.50, 'biggest': 1.40, 'huge': 1.40, 'more': 1.20,
    'very': 1.30, 'extremely': 1.50, 'rapid': 1.40, 'severe': 1.40,
}

DAMPENERS: Dict[str, float] = {
    # Indonesia
    'tipis': 0.55, 'sedikit': 0.60, 'terbatas': 0.60, 'wajar': 0.55,
    'moderat': 0.65, 'ringan': 0.60, 'sementara': 0.65, 'relatif': 0.70,
    # English
    'slightly': 0.60, 'modestly': 0.60, 'little': 0.60, 'mildly': 0.60,
    'marginally': 0.50, 'slight': 0.60, 'small': 0.70, 'edge': 0.65, 'edges': 0.65,
}

NEGATIONS = {
    # Indonesia
    'tidak', 'tak', 'bukan', 'belum', 'tanpa', 'batal', 'jangan',
    'hindari', 'terhindar', 'menepis', 'bantah', 'membantah',
    # English
    'not', 'no', 'never', 'without', "n't", 'nor', 'neither',
    'avoid', 'avoids', 'averts', 'avert',
}

# Kata hiperbolis khas clickbait media lokal (penanda sensasionalisme di Headline)
SENSATIONAL_WORDS = {
    'kebakaran', 'berdarah', 'ambruk', 'rontok', 'panik', 'kiamat', 'meledak',
    'meroket', 'terbang', 'hancur', 'menggila', 'geger', 'ngeri', 'boncos',
    'tumbang', 'crash', 'panic', 'wipeout', 'rout', 'collapse', 'soar',
}

# =====================================================================
# 2. 7 ASPEK EKONOMI & PASAR MODAL INDONESIA (Tokens of Interest - FiGAS)
# =====================================================================
ASPECTS: Dict[str, List[str]] = {
    'monetary': [
        'bi', 'sukubunga', 'birate', 'suku', 'bunga', 'ratecut', 'ratehike', 'moneter', 'likuiditas',
        'gwm', 'hawkish', 'dovish', 'fed', 'federal', 'powell', 'rates', 'rate',
        'fomc', 'easing', 'tightening', 'central', 'policy', 'acuan', 'bps'
    ],
    'rupiah_fx': [
        'rupiah', 'kurs', 'idr', 'dolar', 'dollar', 'usd', 'valas', 'asing',
        'netbuy', 'netsell', 'inflow', 'inflows', 'outflow', 'outflows',
        'foreign', 'fii', 'currency', 'yield', 'imbal', 'sbn', 'obligasi'
    ],
    'financial': [
        'bank', 'perbankan', 'kredit', 'laba', 'dividen', 'npl', 'ojk',
        'kinerja', 'kuartal', 'pendapatan', 'ekuitas', 'aset', 'dana', 'dpk',
        'bbca', 'bca', 'bbri', 'bri', 'bmri', 'mandiri', 'bbni', 'bni',
        'banks', 'banking', 'lender', 'lending', 'profit', 'profits', 'earnings', 'loans'
    ],
    'inflation': [
        'inflasi', 'harga', 'dayabeli', 'konsumsi', 'pangan', 'ihk', 'bbm',
        'tarif', 'ppn', 'subsidi', 'biaya', 'inflation', 'prices', 'cpi', 'ppi', 'costs'
    ],
    'commodity_sector': [
        'batubara', 'nikel', 'sawit', 'cpo', 'minyak', 'emas', 'tambang',
        'energi', 'manufaktur', 'otomotif', 'industri', 'pabrik', 'ekspor',
        'impor', 'komoditas', 'adro', 'adaro', 'antm', 'antam', 'asii', 'astra',
        'tlkm', 'telkom', 'goto', 'unvr', 'icbp', 'coal', 'nickel', 'oil',
        'gold', 'mining', 'manufacturing', 'factory', 'output', 'exports'
    ],
    'economy': [
        'ekonomi', 'makro', 'pdb', 'gdp', 'pertumbuhan', 'apbn', 'fiskal',
        'pajak', 'investasi', 'tenagakerja', 'phk', 'pengangguran', 'resesi',
        'defisit', 'surplus', 'economy', 'economic', 'growth', 'fiscal',
        'budget', 'unemployment', 'jobs', 'layoffs', 'recession'
    ],
    'market': [
        'ihsg', 'bursa', 'bei', 'idx', 'saham', 'lq45', 'indeks', 'pasar',
        'emiten', 'investor', 'perdagangan', 'sesi', 'kapitalisasi',
        'stocks', 'stock', 'market', 'markets', 'shares', 'index', 'equities', 'jakarta'
    ],
}

ASPECT_LABELS_ID: Dict[str, str] = {
    'monetary': 'Moneter & Suku Bunga (BI/Fed)',
    'rupiah_fx': 'Rupiah & Arus Modal Asing',
    'financial': 'Fundamental Perbankan & Laba Emiten',
    'inflation': 'Inflasi & Daya Beli',
    'commodity_sector': 'Sektor Riil, Komoditas & Industri',
    'economy': 'Makroekonomi & Fiskal',
    'market': 'Sentimen Bursa & IHSG',
}

TOI2ASPECT: Dict[str, str] = {w: a for a, ws in ASPECTS.items() for w in ws}
WINDOW = 5

# Kata arah yang membalikkan polaritas jika berdekatan dengan FLIP_TOI (misal "inflasi turun" -> positif)
DIRECTION = {
    # Indonesia
    'naik', 'kenaikan', 'melonjak', 'lonjakan', 'meningkat', 'peningkatan',
    'tinggi', 'bengkak', 'membengkak', 'naikkan', 'menaikkan', 'dinaikkan',
    'turun', 'penurunan', 'merosot', 'menyusut', 'melandai', 'rendah',
    'anjlok', 'terkendali', 'susut', 'pangkas', 'memangkas', 'dipangkas',
    'turunkan', 'menurunkan', 'diturunkan',
    # English
    'rise', 'rises', 'rose', 'rising', 'fall', 'falls', 'fell', 'falling',
    'drop', 'drops', 'dropped', 'decline', 'declines', 'declined', 'higher',
    'lower', 'jump', 'jumps', 'jumped', 'surge', 'surges', 'surged', 'climb',
    'climbs', 'climbed', 'plunge', 'plunges', 'slide', 'slides', 'sink', 'sinks',
    'ease', 'eases', 'eased', 'cool', 'cools', 'cooled', 'cut', 'cuts', 'hike', 'hikes',
}

# Konsep negatif bila naik, dan positif bila turun/melandai
FLIP_TOI = {
    'inflasi', 'pengangguran', 'phk', 'npl', 'utang', 'defisit', 'beban', 'biaya',
    'sukubunga', 'birate', 'bunga', 'rate', 'rates', 'tarif',
    'unemployment', 'jobless', 'inflation', 'cpi', 'ppi', 'prices', 'costs',
    'layoffs', 'layoff', 'claims', 'npa', 'deficit',
}

# Kata arah turun spesifik (apabila bertemu FLIP_TOI yang punya skor negatif bawaan, arahnya menjadi positif)
DOWN_WORDS = {
    'turun', 'penurunan', 'merosot', 'menyusut', 'melandai', 'rendah', 'terkendali', 'susut',
    'pangkas', 'memangkas', 'dipangkas', 'turunkan', 'menurunkan', 'diturunkan',
    'fall', 'falls', 'fell', 'falling', 'drop', 'drops', 'dropped', 'decline',
    'declines', 'declined', 'lower', 'ease', 'eases', 'eased', 'cool', 'cools', 'cooled',
    'cut', 'cuts',
}


def preprocess(text: str) -> List[str]:
    """Normalisasi teks, penggantian frasa multi-kata dengan batas kata, dan tokenisasi."""
    if not text:
        return []
    t = str(text).lower().replace("’", "'").replace("–", "-")
    for k, v in sorted(PHRASES.items(), key=lambda kv: -len(kv[0])):
        if k in t:
            t = re.sub(rf"\b{re.escape(k)}\b", v, t)
    return re.findall(r"s&p|[a-z]+(?:-[a-z]+)?(?:'t)?", t)


def _word_score(tokens: List[str], i: int) -> float:
    """Hitung skor token ke-i dengan memperhatikan penguat, pelemah, dan negasi di sekitarnya."""
    s = LEXICON.get(tokens[i], 0.0)
    if s == 0.0:
        return 0.0
    for j in range(max(0, i - 2), min(len(tokens), i + 2)):
        if j == i:
            continue
        w = tokens[j]
        if w in INTENSIFIERS:
            s *= INTENSIFIERS[w]
        elif w in DAMPENERS:
            s *= DAMPENERS[w]
        elif j < i and (w in NEGATIONS or w.endswith("n't")):
            s *= -0.8
    return max(-1.0, min(1.0, s))


def headline_sentiment(text: str) -> Tuple[float, Dict[str, float]]:
    """
    Menghitung (skor_sentimen_keseluruhan, {aspek: skor_aspek}) pada teks (Headline maupun Body).
    Skor berada pada rentang [-1.0, +1.0].
    """
    tok = preprocess(text)
    if not tok:
        return 0.0, {}

    scores = [_word_score(tok, i) for i in range(len(tok))]

    # Pembalikan polaritas kata arah di sekitar FLIP_TOI (misal: "inflasi melandai / turun" -> positif)
    for i, w in enumerate(tok):
        if w in DIRECTION:
            cands = [
                (abs(j - i), j, tok[j])
                for j in range(max(0, i - WINDOW), min(len(tok), i + WINDOW + 1))
                if j != i and tok[j] in TOI2ASPECT
            ]
            if cands:
                dist, near_idx, near = min(cands, key=lambda c: (c[0], c[2] not in FLIP_TOI))
                if near in FLIP_TOI and not any(c[0] == dist and c[2] not in FLIP_TOI for c in cands):
                    scores[i] = -scores[i] if scores[i] != 0 else (0.45 if w in DOWN_WORDS else -0.45)
                    # Jika FLIP_TOI itu sendiri punya skor negatif (misal 'pengangguran' -0.55) tapi ia turun, netralisir/balikkan
                    if w in DOWN_WORDS and scores[near_idx] < 0:
                        scores[near_idx] = abs(scores[near_idx]) * 0.5

    # Normalisasi dengan akar jumlah token yang bermuatan atau akar panjang teks agar teks panjang tidak terdilusi nol
    active_count = sum(1 for sc in scores if sc != 0.0)
    denom = max(1.0, math.sqrt(max(active_count * 2.2, min(len(tok), 16))))
    overall = float(np.clip(sum(scores) / denom, -1.0, 1.0))

    asp: Dict[str, List[float]] = {}
    for i, w in enumerate(tok):
        a = TOI2ASPECT.get(w)
        if a is None:
            continue
        lo, hi = max(0, i - WINDOW), min(len(tok), i + WINDOW + 1)
        # Sertakan juga skor dari kata TOI itu sendiri jika punya bobot di LEXICON (misal 'laba', 'dividen', 'netbuy')
        self_score = scores[i] * 0.75
        neighbor_score = sum(scores[j] / (1 + abs(j - i)) for j in range(lo, hi) if j != i)
        asp.setdefault(a, []).append(self_score + neighbor_score)

    asp_final = {a: float(np.clip(np.mean(v) * 1.4, -1.0, 1.0)) for a, v in asp.items() if abs(np.mean(v)) > 1e-4}
    return overall, asp_final


def analyze_headline_detail(text: str) -> Dict[str, Any]:
    """Mengembalikan rincian token demi token untuk visualisasi inspeksi FiGAS di UI."""
    tok = preprocess(text)
    raw_scores = [LEXICON.get(w, 0.0) for w in tok]
    adj_scores = [_word_score(tok, i) for i in range(len(tok))]

    flipped_flags = [False] * len(tok)
    for i, w in enumerate(tok):
        if w in DIRECTION:
            cands = [
                (abs(j - i), j, tok[j])
                for j in range(max(0, i - WINDOW), min(len(tok), i + WINDOW + 1))
                if j != i and tok[j] in TOI2ASPECT
            ]
            if cands:
                dist, near_idx, near = min(cands, key=lambda c: (c[0], c[2] not in FLIP_TOI))
                if near in FLIP_TOI and not any(c[0] == dist and c[2] not in FLIP_TOI for c in cands):
                    adj_scores[i] = -adj_scores[i] if adj_scores[i] != 0 else (0.45 if w in DOWN_WORDS else -0.45)
                    flipped_flags[i] = True
                    if w in DOWN_WORDS and adj_scores[near_idx] < 0:
                        adj_scores[near_idx] = abs(adj_scores[near_idx]) * 0.5
                        flipped_flags[near_idx] = True

    overall, asp = headline_sentiment(text)

    tokens_detail = []
    for i, w in enumerate(tok):
        tokens_detail.append({
            "token": w,
            "raw_score": round(raw_scores[i], 3),
            "adjusted_score": round(adj_scores[i], 3),
            "aspect": TOI2ASPECT.get(w),
            "is_toi": w in TOI2ASPECT,
            "is_intensifier": w in INTENSIFIERS,
            "is_dampener": w in DAMPENERS,
            "is_negation": w in NEGATIONS or w.endswith("n't"),
            "is_flipped": flipped_flags[i],
            "is_sensational": w in SENSATIONAL_WORDS,
        })

    return {
        "text": text,
        "overall_score": round(overall, 4),
        "aspect_scores": {k: round(v, 4) for k, v in asp.items()},
        "tokens": tokens_detail,
    }


def extract_key_evidence_sentence(body: str, headline: str = "") -> str:
    """
    Mengekstrak 1-2 kalimat paling padat fakta/sentimen dari isi berita (Body)
    sebagai bukti kutipan akademik (Evidence Snippet) tanpa membajak seluruh artikel.
    """
    if not body or not body.strip():
        return ""
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', body.strip()) if len(s.strip()) > 25]
    if not sentences:
        return body.strip()[:240]

    best_sent = sentences[0]
    best_weight = -1.0
    for s in sentences[:15]:
        toks = preprocess(s)
        toi_hits = sum(1 for w in toks if w in TOI2ASPECT)
        lex_hits = sum(abs(LEXICON.get(w, 0.0)) for w in toks)
        has_numbers = 1.2 if re.search(r'\d+(?:[.,]\d+)?%|\brp\s*\d+|\b\d+\s*(?:triliun|miliar|bps|poin|persen)\b', s.lower()) else 1.0
        weight = (toi_hits * 0.8 + lex_hits) * has_numbers
        if weight > best_weight:
            best_weight = weight
            best_sent = s
    return best_sent[:280]


def analyze_article_headline_vs_body(
    headline: str,
    body: str = "",
    source: str = "Media Finansial",
    url: str = "",
    published_at: str = "",
    scope: str = "MACRO_IHSG",
) -> Dict[str, Any]:
    """
    INOVASI INTI: Membandingkan Skor Headline vs Skor Isi Berita (Body).
    Menghitung:
    - head_score: sentimen judul berita
    - body_score: sentimen isi berita lengkap
    - discrepancy: |head_score - body_score|
    - verification_status:
        1. 'CLICKBAIT_EXAGGERATED' -> Headline hiperbolis/lebay tetapi isi berita jauh lebih tenang/netral.
           Bobot headline didiskon menjadi 20%, isi berita 80%.
        2. 'DIVERGENT_CONTENT'     -> Headline dan isi berita berlawanan arah (misal judul optimis tapi isi memuat risiko utang/rugi).
           Bobot isi berita diprioritaskan 85%, headline 15%.
        3. 'CONFIRMED_CONSISTENT'  -> Headline dan isi berita searah & saling menguatkan dengan bukti fakta.
           Kombinasi 35% headline + 65% isi berita.
        4. 'HEADLINE_ONLY'         -> Jika hanya judul yang tersedia.
    """
    h_score, h_asp = headline_sentiment(headline)
    h_toks = preprocess(headline)
    sensational_hits = [w for w in h_toks if w in SENSATIONAL_WORDS]

    has_body = bool(body and len(body.strip()) > 30 and body.strip().lower() != headline.strip().lower())

    if not has_body:
        b_score, b_asp = h_score, dict(h_asp)
        discrepancy = 0.0
        status = "HEADLINE_ONLY"
        status_label = "Hanya Headline (Tanpa Isi)"
        explanation = "Isi berita terpisah tidak tersedia; menggunakan skor judul secara langsung."
        w_head, w_body = 1.0, 0.0
    else:
        b_score, b_asp = headline_sentiment(body)
        discrepancy = abs(h_score - b_score)

        # Deteksi 1: Headline Clickbait / Hiperbolis (Judul jauh lebih ekstrem/sensasional dibanding substansi isi)
        is_hyperbolic = (
            (abs(h_score) >= 0.25 and (abs(h_score) - abs(b_score) >= 0.15))
            or (len(sensational_hits) > 0 and discrepancy >= 0.20)
        )
        # Deteksi 2: Divergensi Arah antara Judul dan Isi Berita (Judul tenang/optimis menyembunyikan risiko kuat di isi)
        is_divergent = (h_score * b_score < -0.015) and (abs(b_score) >= 0.12) and not is_hyperbolic

        if is_hyperbolic:
            status = "CLICKBAIT_EXAGGERATED"
            status_label = "Headline Hiperbolis / Clickbait Didiskon"
            w_head, w_body = 0.20, 0.80
            sens_str = f" (kata sensasional: {', '.join(sensational_hits)})" if sensational_hits else ""
            explanation = (
                f"Judul berita terdeteksi hiperbolis ({h_score:+.2f}){sens_str} dibanding substansi isi berita ({b_score:+.2f}). "
                f"Sistem menerapkan Clickbait Discount (20% Judul : 80% Isi)."
            )
        elif is_divergent:
            status = "DIVERGENT_CONTENT"
            status_label = "Divergensi Judul vs Isi (Prioritas Isi)"
            w_head, w_body = 0.15, 0.85
            explanation = (
                f"Judul ({h_score:+.2f}) berlawanan arah dengan fakta mendalam di isi berita ({b_score:+.2f}). "
                f"Sistem memprioritaskan 85% bobot pada isi artikel."
            )
        else:
            status = "CONFIRMED_CONSISTENT"
            status_label = "Terkonfirmasi Fakta Isi Berita"
            w_head, w_body = 0.35, 0.65
            explanation = (
                f"Sentimen judul ({h_score:+.2f}) konsisten dan didukung oleh penjabaran isi berita ({b_score:+.2f})."
            )

    effective_score = float(np.clip(w_head * h_score + w_body * b_score, -1.0, 1.0))

    # Gabungkan skor aspek dari headline dan body sesuai bobot (w_head, w_body)
    merged_aspects: Dict[str, float] = {}
    all_asp_keys = set(h_asp.keys()) | set(b_asp.keys())
    for k in all_asp_keys:
        if k in h_asp and k in b_asp:
            merged_aspects[k] = round(float(np.clip(w_head * h_asp[k] + w_body * b_asp[k], -1.0, 1.0)), 4)
        elif k in b_asp:
            merged_aspects[k] = round(float(b_asp[k] * (0.85 if has_body else 1.0)), 4)
        else:
            merged_aspects[k] = round(float(h_asp[k] * (w_head if has_body else 1.0)), 4)

    # Bobot Kredibilitas Sumber (Reuters, Antara, Kontan, CNBC Indonesia, Bisnis, Detik)
    src_lower = (source or "").lower()
    if "reuters" in src_lower:
        source_weight = 1.20
        source_tier = "Internasional / Reuters (Tier-1)"
    elif any(s in src_lower for s in ("antara", "kontan", "cnbc", "bisnis", "investor", "idx")):
        source_weight = 1.10
        source_tier = "Media Finansial Nasional (Tier-1)"
    else:
        source_weight = 1.00
        source_tier = "Media Berita Umum"

    evidence_snippet = extract_key_evidence_sentence(body, headline) if has_body else headline

    return {
        "headline": headline,
        "body": body,
        "evidence_snippet": evidence_snippet,
        "source": source,
        "source_tier": source_tier,
        "source_weight": source_weight,
        "url": url,
        "published_at": published_at,
        "scope": scope,  # 'TICKER_SPECIFIC' atau 'MACRO_IHSG'
        "headline_score": round(h_score, 4),
        "body_score": round(b_score, 4),
        "effective_score": round(effective_score, 4),
        "discrepancy": round(discrepancy, 4),
        "weights": {"headline": w_head, "body": w_body},
        "verification_status": status,
        "verification_label": status_label,
        "verification_explanation": explanation,
        "sensational_words": sensational_hits,
        "aspect_scores": merged_aspects,
        "headline_tokens": analyze_headline_detail(headline)["tokens"],
    }
