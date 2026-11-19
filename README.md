# Sistem Pakar Rekomendasi Saham Indonesia (IHSG & LQ45) — Headline vs Isi Berita & MYCIN CF

Sistem Pakar berbasis aturan (*rule-based expert system*) yang menghasilkan rekomendasi keputusan **BUY** atau **SELL** pada **Indeks Harga Saham Gabungan (`^JKSE`)** dan **Saham Unggulan LQ45 Bursa Efek Indonesia (`BBCA.JK`, `BBRI.JK`, `BMRI.JK`, `TLKM.JK`, `ASII.JK`, `ADRO.JK`, serta request kode saham BEI lainnya)** dengan membandingkan sentimen **Judul Berita (*Headline*) vs Isi Artikel (*Full Body Text*)** dari portal berita nasional & internasional (**Reuters**) serta indikator harga historis 2 tahun terakhir (`yfinance`).

---

## 1. Inovasi Utama & Jawaban atas Evaluasi Dosen

1. **Data Pasar Modal Indonesia Terbaru (Rentang 2 Tahun Terakhir: 2024–2026)**
   - Fokus pada **IHSG (`^JKSE`)** dan saham *Blue Chip* Indonesia (`BBCA.JK`, `BBRI.JK`, `BMRI.JK`, `TLKM.JK`, `ASII.JK`, `ADRO.JK`, plus fitur *Custom Ticker Request*).
   - Mengambil data harga saham harian selama 2 tahun terakhir secara *real-time* melalui `yfinance` untuk menghitung **Tren vs MA-20**, **RSI-14**, dan **Volatilitas 20 Hari**.
   - Mengambil 10–15 berita harian dari sumber nasional (**CNBC Indonesia Market, Antara Ekonomi, Detik Finance, Kontan**) dan internasional (**Reuters**) secara etis (*Polite RSS & Article Body Extraction* dengan *rate-limiting* dan *caching*).

2. **Inovasi Perbandingan *Headline* vs *Isi Berita* (*Clickbait Discount & Content Verification*)**
   - Mengatasi masalah judul berita finansial yang sering dilebih-lebihkan (*clickbait/hiperbolis*) dengan membandingkan skor sentimen judul ($S_{\text{head}}$) terhadap skor sentimen isi berita lengkap ($S_{\text{body}}$):
     - **Headline Hiperbolis / Clickbait (`CLICKBAIT_EXAGGERATED`)**: Bobot judul didiskon menjadi **20%**, dan bobot isi berita dinaikkan menjadi **80%**.
     - **Divergensi Judul vs Isi (`DIVERGENT_CONTENT`)**: Ketika judul tampak netral/optimistis namun isi berita mengungkap risiko negatif (utang bengkak, rugi, *outflow*), sistem memprioritaskan **85% bobot pada isi berita**.
     - **Terkonfirmasi Fakta Isi (`CONFIRMED_CONSISTENT`)**: Kombinasi seimbang **35% Judul + 65% Isi Berita**.

3. **Kamus Sentimen Bilingual (Bahasa Indonesia + Inggris) Berbasis 7 Aspek (FiGAS)**
   - ~450 kata & frasa ekonomi dalam Bahasa Indonesia dan Bahasa Inggris (Reuters) dengan bobot `[-1.0, +1.0]`.
   - 7 Aspek Pasar Modal Indonesia: **Moneter & Suku Bunga (BI Rate/Fed)**, **Rupiah & Arus Modal Asing**, **Keuangan & Laba Emiten**, **Inflasi & Daya Beli**, **Komoditas & Sektor Riil**, **Makroekonomi & Fiskal**, serta **Sentimen Bursa/IHSG**.
   - Dilengkapi penanganan *Intensifiers*, *Dampeners*, *Negations*, dan *Directional Polarity Flip* (misal: `"inflasi melandai"` atau `"pengangguran turun"` bernilai **Positif (+)**, sedangkan `"suku bunga acuan naik"` bernilai **Negatif (-)**).

4. **Keputusan Biner Tegas (`BUY` vs `SELL`) & 14 Aturan Pakar Ber-Referensi ([1]–[8])**
   - Keputusan disederhanakan menjadi murni **BUY** dan **SELL**.
   - 14 aturan produksi `IF–THEN` (`R01` s/d `R14`) dilengkapi rujukan literatur ilmiah eksplisit (`[1]` s/d `[8]`) dan **Penjelasan Alasan Bahasa Manusia (*Reason to Buy / Reason to Sell*)**.

5. **Evaluasi Historis 2 Tahun (2024–2026) Terhadap Harga Saham Asli ($t+1$)**
   - Menguji rekomendasi hari ke-$t$ langsung terhadap pergerakan harga penutupan asli pada hari bursa berikutnya ($t+1$) dari `yfinance` pada 224 hari bursa evaluasi (560 artikel berita):
     - **Baseline Sistem Pakar (Hanya Headline)**: Akurasi **41,5%** (Macro-F1: `0.415`) — terkecoh oleh judul *clickbait*.
     - **Sistem Pakar Baru (Headline + Verifikasi Isi Berita)**: Akurasi **62,1%** (Macro-F1: `0.620`, Presisi BUY: `62,0%`, Presisi SELL: `62,1%`) — peningkatan **+20,6%** dan melampaui target akurasi realistis `> 0.50`.

---

## 2. Struktur Repositori

```
.
├── expert_system/
│   ├── nlp.py                 # Bilingual FiGAS Lexicon (ID+EN) & Headline-vs-Body Discrepancy Engine
│   ├── fuzzification.py       # Agregasi 2-Tingkat (65% Emiten + 35% Makro IHSG) & Fuzzifikasi
│   ├── rules.py               # 14 Aturan IF-THEN (BUY vs SELL) + Sitasi Referensi [1]-[8]
│   ├── inference.py           # Forward Chaining, Kombinasi MYCIN CF & Natural Language Reasoning
│   ├── indo_market.py         # Akuisisi Harga 2 Tahun (yfinance) & Polite Multi-Source News Scraper
│   ├── test_cases.py          # 14 Regression Test Cases Indonesia & 10 Unit Tests Bilingual NLP
│   └── benchmark.py           # Evaluasi Historis 2 Tahun (2024-2026) vs Harga Asli t+1
├── data/
│   └── indo_historical_2y_dataset.json  # Dataset Evaluasi 2 Tahun (7 Instrumen BEI, 560 Artikel)
├── scripts/
│   └── build_indo_2y_dataset.py         # Generator & Evaluator Dataset 2 Tahun (yfinance + Korpus Berita)
├── notebooks/
│   └── Sistem_Pakar_Saham_Indonesia_v4.ipynb  # Jupyter Notebook Pendamping Laporan
├── static/
│   ├── app.js                 # Controller UI 5-Tab (Live Stock Request, Simulator, Flowchart, Rules, Evaluasi)
│   └── styles.css             # Desain Editorial Minimalis
├── templates/
│   └── index.html             # Dashboard Web App Interaktif
├── tests/
│   └── test_expert_system.py  # Automated Pytest Suite
├── main.py                    # Server FastAPI
└── requirements.txt
```

---

## 3. Cara Menjalankan

```bash
pip install -r requirements.txt
python3 -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```
Buka di browser: **http://127.0.0.1:8000**

Untuk menjalankan pengujian otomatis:
```bash
python3 -m pytest tests/test_expert_system.py -v
```

---

## 4. Daftar Pustaka (Seluruh Referensi [1]–[8] Dikutip Eksplisit di Sistem & Aturan)

1. **[1] L. Barbaglia, S. Consoli, and S. Manzan (2023)**, “Forecasting with Economic News,” *Journal of Business & Economic Statistics*, vol. 41, no. 3, pp. 708–719.
2. **[2] A. Maghyereh and H. Abdoh (2022)**, “Can news-based economic sentiment predict bubbles in precious metal markets?,” *Financial Innovation*, vol. 8, art. no. 35.
3. **[3] S. Consoli, L. Barbaglia, and S. Manzan (2022)**, “Fine-grained, aspect-based sentiment analysis on economic and financial lexicon,” *Knowledge-Based Systems*, vol. 247, art. no. 108781.
4. **[4] J. Bi (2022)**, “Stock Market Prediction Based on Financial News Text Mining and Investor Sentiment Recognition,” *Mathematical Problems in Engineering*, vol. 2022, art. no. 2427389.
5. **[5] A. Wildan and R. Sari (2022)**, “Metode Certainty Factor pada Sistem Pakar,” *Journal of Informatic and Information Security*, vol. 3, no. 1, pp. 125–136.
6. **[6] A. K. Aprianto, I. Permadi, and B. Wijayanto (2023)**, “Expert System Using Forward Chaining Method,” *Jurnal Teknik Informatika (JUTIF)*, vol. 4, no. 4.
7. **[7] K. Du, F. Xing, R. Mao, and E. Cambria (2024)**, “Financial sentiment analysis: Techniques and applications,” *ACM Computing Surveys*, vol. 56, no. 9, Art. no. 220.
8. **[8] J. J. Murphy (1999)**, *Technical Analysis of the Financial Markets*, New York Institute of Finance.
