"""
Knowledge Base (Basis Pengetahuan) Sistem Pakar Saham Indonesia (IHSG & LQ45)
Berisi 14 Aturan Produksi IF-THEN untuk Keputusan Murni BUY vs SELL.

Setiap aturan dilengkapi:
1. ID dan Nama Aturan
2. Fungsi Kondisi (Premis IF)
3. Keputusan (BUY atau SELL) — sesuai arahan penyederhanaan keputusan dosen
4. Bobot Certainty Factor (CF Pakar) [0.0 - 1.0]
5. Referensi Pakar / Literatur Akademik ([1] s/d [8] + Murphy 1999)
6. Template Kondisi IF
7. Penjelasan Alasan Bahasa Manusia (Reason to Buy / Reason to Sell)
"""

from typing import List, Tuple, Callable, Dict, Any

ACADEMIC_REFERENCES: List[Dict[str, str]] = [
    {
        "id": "[1]",
        "authors": "L. Barbaglia, S. Consoli, and S. Manzan (2023)",
        "title": "Forecasting with Economic News",
        "venue": "Journal of Business & Economic Statistics, vol. 41, no. 3, pp. 708–719",
        "role": "Landasan hubungan berita aspek makroekonomi, moneter, dan inflasi terhadap pergerakan pasar."
    },
    {
        "id": "[2]",
        "authors": "A. Maghyereh and H. Abdoh (2022)",
        "title": "Can news-based economic sentiment predict bubbles in precious metal markets?",
        "venue": "Financial Innovation, vol. 8, art. no. 35",
        "role": "Landasan aturan pelonggaran moneter dan risiko gelembung harga (overextended/euforia)."
    },
    {
        "id": "[3]",
        "authors": "S. Consoli, L. Barbaglia, and S. Manzan (2022)",
        "title": "Fine-grained, aspect-based sentiment analysis on economic and financial lexicon",
        "venue": "Knowledge-Based Systems, vol. 247, art. no. 108781",
        "role": "Landasan metode FiGAS (Tokens of Interest, jendela kata ±5, dan pembalikan arah polaritas)."
    },
    {
        "id": "[4]",
        "authors": "J. Bi (2022)",
        "title": "Stock Market Prediction Based on Financial News Text Mining and Investor Sentiment Recognition",
        "venue": "Mathematical Problems in Engineering, vol. 2022, art. no. 2427389",
        "role": "Landasan penggabungan sentimen berita harian dan indikator tren harga saham."
    },
    {
        "id": "[5]",
        "authors": "A. Wildan and R. Sari (2022)",
        "title": "Metode Certainty Factor pada Sistem Pakar",
        "venue": "Journal of Informatic and Information Security, vol. 3, no. 1, pp. 125–136",
        "role": "Landasan rumus kombinasi keyakinan MYCIN: CF_gab = CF1 + CF2 * (1 - CF1)."
    },
    {
        "id": "[6]",
        "authors": "A. K. Aprianto, I. Permadi, and B. Wijayanto (2023)",
        "title": "Expert System Using Forward Chaining Method",
        "venue": "Jurnal Teknik Informatika (JUTIF), vol. 4, no. 4",
        "role": "Landasan arsitektur mesin inferensi Forward Chaining berbasis aturan produksi IF-THEN."
    },
    {
        "id": "[7]",
        "authors": "K. Du, F. Xing, R. Mao, and E. Cambria (2024)",
        "title": "Financial sentiment analysis: Techniques and applications",
        "venue": "ACM Computing Surveys, vol. 56, no. 9, Art. no. 220",
        "role": "Landasan penyaringan bias sensasionalisme/clickbait judul berita vs ekstraksi isi artikel."
    },
    {
        "id": "[8]",
        "authors": "J. J. Murphy (1999)",
        "title": "Technical Analysis of the Financial Markets",
        "venue": "New York Institute of Finance",
        "role": "Rujukan pakar analisis teknikal untuk ambang Moving Average (MA-20) dan Relative Strength Index (RSI-14)."
    },
]

# Format Tuple RULES:
# (id, name, cond_fn, action, cf, academic_ref, if_text, human_reason)
RULES: List[Tuple[str, str, Callable[[Dict[str, Any]], bool], str, float, str, str, str]] = [
    (
        'R01',
        'Transmisi Pelonggaran Moneter (BI Rate / Fed Dovish)',
        lambda F: F['mon'] == 'pos' and F['trend'] != 'overextended',
        'BUY',
        0.65,
        'Maghyereh & Abdoh (2022) [2]; Barbaglia et al. (2023) [1]',
        "IF aspek moneter = pos AND tren ≠ overextended",
        "Penurunan suku bunga acuan (BI Rate / The Fed) atau sinyal moneter dovish menurunkan biaya pinjaman korporasi dan meningkatkan valuasi saham."
    ),
    (
        'R02',
        'Tekanan Inflasi & Pengetatan Suku Bunga (Hawkish)',
        lambda F: (F['infl'] == 'neg' and F['mon'] == 'neg') or (F['mon'] == 'neg' and F['rupiah'] == 'neg'),
        'SELL',
        0.65,
        'Barbaglia, Consoli & Manzan (2023) [1]; Consoli et al. (2022) [3]',
        "IF (inflasi = neg AND moneter = neg) OR (moneter = neg AND rupiah = neg)",
        "Kenaikan suku bunga acuan (hawkish) akibat lonjakan inflasi atau tekanan kurs Rupiah memperberat beban bunga emiten dan menekan daya beli."
    ),
    (
        'R03',
        'Penguatan Rupiah & Akumulasi Modal Asing (Foreign Inflow)',
        lambda F: F['rupiah'] == 'pos' and F['sent'] in ('pos', 'very_pos', 'neutral'),
        'BUY',
        0.68,
        'Bi (2022) [4]; Du et al. (2024) [7]',
        "IF aspek rupiah_fx = pos AND sentimen_isi ∈ {pos, very_pos, neutral}",
        "Apresiasi nilai tukar Rupiah yang disertai arus modal asing masuk (foreign net buy) mendorong penguatan saham-saham berkapitalisasi besar (Blue Chip/IHSG)."
    ),
    (
        'R04',
        'Depresiasi Rupiah & Arus Modal Asing Keluar (Capital Outflow)',
        lambda F: F['rupiah'] == 'neg' and F['sent'] in ('neg', 'very_neg'),
        'SELL',
        0.68,
        'Bi (2022) [4]; Maghyereh & Abdoh (2022) [2]',
        "IF aspek rupiah_fx = neg AND sentimen_isi ∈ {neg, very_neg}",
        "Pelemahan nilai tukar Rupiah yang dibarengi aksi jual bersih investor asing (foreign net sell) memberikan tekanan distribusi langsung pada bursa."
    ),
    (
        'R05',
        'Ekspansi Laba Emiten & Fundamental Perbankan Solid',
        lambda F: F['fin'] == 'pos' and F['econ'] != 'neg',
        'BUY',
        0.64,
        'Consoli, Barbaglia & Manzan (2022) [3]; Du et al. (2024) [7]',
        "IF aspek keuangan_emiten = pos AND aspek makro ≠ neg",
        "Pertumbuhan laba bersih kuartalan, pembagian dividen, atau ekspansi kredit yang sehat membuktikan fundamental emiten sedang bertumbuh kuat."
    ),
    (
        'R06',
        'Tekanan Kinerja Keuangan Emiten & Risiko Kredit',
        lambda F: F['fin'] == 'neg' and (F['econ'] == 'neg' or F['sent'] in ('neg', 'very_neg')),
        'SELL',
        0.66,
        'Barbaglia et al. (2023) [1]; Consoli et al. (2022) [3]',
        "IF aspek keuangan_emiten = neg AND (makro = neg OR sentimen_isi ∈ {neg, very_neg})",
        "Penurunan laba bersih, kenaikan rasio kredit bermasalah (NPL), atau membengkaknya beban keuangan menurunkan prospek valuasi saham."
    ),
    (
        'R07',
        'Momentum Positif Sektor Komoditas, Industri & Makro',
        lambda F: (F['comm'] == 'pos' or F['econ'] == 'pos') and F['sent'] in ('pos', 'very_pos'),
        'BUY',
        0.56,
        'Barbaglia, Consoli & Manzan (2023) [1]; Bi (2022) [4]',
        "IF (sektor_komoditas = pos OR ekonomi = pos) AND sentimen_isi ∈ {pos, very_pos}",
        "Penguatan harga komoditas ekspor utama Indonesia (batu bara, nikel, CPO) serta ekspansi manufaktur/PDB berdampak positif pada pendapatan emiten."
    ),
    (
        'R08',
        'Perlambatan Sektor Komoditas, Manufaktur & Makroekonomi',
        lambda F: F['comm'] == 'neg' and (F['econ'] == 'neg' or F['sent'] in ('neg', 'very_neg')),
        'SELL',
        0.56,
        'Barbaglia et al. (2023) [1]; Consoli et al. (2022) [3]',
        "IF sektor_komoditas = neg AND (ekonomi = neg OR sentimen_isi ∈ {neg, very_neg})",
        "Pelemahan harga komoditas global dan melambatnya aktivitas industri/ekspor menekan margin keuntungan emiten sektor riil di BEI."
    ),
    (
        'R09',
        'Diskon Kepanikan Clickbait (Headline Negatif Lebay vs Isi Berita Stabil)',
        lambda F: F['sent_head'] in ('neg', 'very_neg') and F['sent'] in ('pos', 'very_pos', 'neutral') and F['credibility'] == 'clickbait_heavy',
        'BUY',
        0.58,
        'Du, Xing, Mao & Cambria (2024) [7]; Bi (2022) [4]',
        "IF sentimen_headline ∈ {neg, very_neg} AND sentimen_isi ∈ {pos, very_pos, neutral} AND kredibilitas = clickbait_heavy",
        "Judul berita terdeteksi hiperbolis/clickbait menakut-nakuti pasar, tetapi verifikasi isi berita menunjukkan kondisi fundamental tetap stabil (peluang Buy on Weakness)."
    ),
    (
        'R10',
        'Deteksi Risiko Tersembunyi di Isi Berita (Divergensi Judul vs Isi)',
        lambda F: F['sent'] in ('neg', 'very_neg') and F['sent_head'] in ('pos', 'very_pos', 'neutral'),
        'SELL',
        0.60,
        'Du et al. (2024) [7]; Consoli et al. (2022) [3]',
        "IF sentimen_isi ∈ {neg, very_neg} AND sentimen_headline ∈ {pos, very_pos, neutral}",
        "Meskipun judul berita tampak netral/positif, analisis mendalam pada isi artikel mengungkap risiko fundamental negatif (seperti utang, rugi, atau tekanan regulasi)."
    ),
    (
        'R11',
        'Peluang Rebound Teknikal pada Area Jenuh Jual (Oversold MA-20 / RSI-14)',
        lambda F: (F['trend'] == 'oversold' or F['rsi'] == 'oversold') and (F['sent'] in ('pos', 'very_pos') or F['delta'] == 'improving' or F['sent'] == 'very_neg'),
        'BUY',
        0.72,
        'Murphy (1999) [8]; Wildan & Sari (2022) [5]',
        "IF (tren = oversold OR rsi = oversold) AND (sentimen_isi positif/membaik OR pesimisme ekstrem)",
        "Harga saham sudah terkoreksi terlalu dalam di bawah MA-20 atau RSI-14 ≤ 35 (jenuh jual/oversold), sehingga secara teknikal berpeluang mengalami technical rebound."
    ),
    (
        'R12',
        'Risiko Koreksi Ambil Untung pada Area Jenuh Beli (Overbought)',
        lambda F: (F['trend'] == 'overextended' or F['rsi'] == 'overbought') and (F['sent'] in ('neg', 'very_neg') or F['delta'] == 'deteriorating' or F['sent'] == 'very_pos'),
        'SELL',
        0.68,
        'Murphy (1999) [8]; Maghyereh & Abdoh (2022) [2]',
        "IF (tren = overextended OR rsi = overbought) AND (sentimen memburuk OR euforia jenuh beli)",
        "Harga saham telah naik terlalu tinggi melampaui MA-20 atau RSI-14 ≥ 68 (jenuh beli/overbought), sehingga rawan terkena aksi ambil untung (profit taking)."
    ),
    (
        'R13',
        'Konfirmasi Tren Naik Sehat & Sentimen Isi Berita Positif',
        lambda F: F['sent'] in ('pos', 'very_pos') and F['trend'] in ('up', 'flat') and F['rsi'] != 'overbought',
        'BUY',
        0.55,
        'Bi (2022) [4]; Aprianto et al. (2023) [6]',
        "IF sentimen_isi ∈ {pos, very_pos} AND tren ∈ {up, flat} AND rsi ≠ overbought",
        "Sentimen isi berita harian yang positif terkonfirmasi oleh pergerakan harga yang stabil/uptrend di atas MA-20 dan belum memasuki zona jenuh beli."
    ),
    (
        'R14',
        'Konfirmasi Tren Turun & Sentimen Pasar Memburuk',
        lambda F: (F['sent'] in ('neg', 'very_neg') and F['trend'] in ('down', 'flat') and F['trend'] != 'oversold') or (F['trend'] == 'down' and F['delta'] == 'deteriorating'),
        'SELL',
        0.60,
        'Bi (2022) [4]; Wildan & Sari (2022) [5]',
        "IF (sentimen_isi ∈ {neg, very_neg} AND tren ∈ {down, flat}) OR (tren = down AND delta = deteriorating)",
        "Sentimen berita yang negatif selaras dengan pelemahan harga di bawah MA-20, mengindikasikan tekanan jual pasar masih mendominasi."
    ),
]

MIN_CF = 0.25
MIN_MARGIN = 0.05
