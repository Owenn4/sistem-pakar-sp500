# Sistem Pakar Rekomendasi S&P 500 (FiGAS & MYCIN Engine)

Sistem Pakar berbasis aturan (*rule-based expert system*) yang menggabungkan analisis sentimen berita ekonomi (*Fine-Grained Aspect-Based Sentiment / FiGAS*) dengan indikator teknikal pasar untuk menghasilkan rekomendasi pasar (**BUY**, **HOLD**, **SELL**) pada indeks S&P 500 beserta penelusuran logika (*explainable reasoning*) yang transparan.

---

## 1. Ringkasan Metodologi

Sistem dirancang berdasarkan metodologi akademik berikut:

1. **Modul Analisis Sentimen Berita (Terinspirasi FiGAS)**
   - Kamus ekonomi dan keuangan (~220 token) dengan bobot skor `[-1.0, +1.0]`.
   - Klasifikasi 6 aspek ekonomi (*Tokens of Interest*): Ekonomi, Keuangan, Kebijakan Moneter, Inflasi, Pengangguran, Manufaktur.
   - Penanganan kata pengubah: *Intensifiers* (misal: "sharply"), *Dampeners* (misal: "slightly"), dan *Negations* (misal: "not", "no").
   - Pembalikan polaritas arah (*Directional Polarity Flip*): misal "unemployment falls" bernilai positif, "inflation rises" bernilai negatif.

2. **Fuzzifikasi (Numerik ke Linguistik)**
   - Memetakan metrik kuantitatif ke label kualitas:
     - Sentimen: `very_neg`, `neg`, `neutral`, `pos`, `very_pos`
     - Tren vs MA20: `oversold`, `down`, `flat`, `up`, `overextended`
     - Volatilitas: `low`, `normal`, `high`
     - Indeks Kepanikan: `high`, `none`

3. **Knowledge Base (16 Aturan IF–THEN)**
   - 16 aturan produksi yang mengadopsi teori literatur keuangan (*Barbaglia et al. 2022*, *Maghyereh & Abdoh 2022*) serta statistik data historis.
   - Mengakomodasi logika kontrarian (pasar jatuh dalam + pesimisme ekstrem $\rightarrow$ sinyal **BUY**) dan kedisiplinan momentum (tren naik tenang $\rightarrow$ sinyal **HOLD**).

4. **Inference Engine (Forward Chaining + Certainty Factor MYCIN)**
   - Menggunakan rumus kombinasi MYCIN saat beberapa aturan mendukung aksi yang sama:
     $$\text{CF}_{\text{gabungan}} = \text{CF}_1 + \text{CF}_2 \times (1 - \text{CF}_1)$$
   - Ambang batas keyakinan: $\text{CF} \ge 0.30$ dan margin pemenang sinyal (BUY vs SELL) $\ge 0.15$.
   - Resolusi konflik otomatis beralih ke **HOLD** jika sinyal bertentangan atau kepercayaan tidak memadai.

---

## 2. Struktur Repositori

```
.
├── expert_system/           # Inti logika sistem pakar
│   ├── nlp.py               # Lexicon, ToI, dan analisis sentimen FiGAS
│   ├── fuzzification.py     # Pemetaan linguistik fakta pasar
│   ├── rules.py             # 16 aturan produksi IF-THEN
│   ├── inference.py         # Forward chaining & Certainty Factor MYCIN
│   ├── test_cases.py        # 20 regression test cases & 8 unit test NLP
│   └── benchmark.py         # Data evaluasi historis & perbandingan ML
├── notebooks/
│   └── Sistem_Pakar_V1.ipynb # Jupyter Notebook penelitian & evaluasi lengkap
├── static/                  # Asset frontend (JavaScript & CSS)
│   ├── app.js               # Controller interaktif & visualisasi fakta
│   └── styles.css           # Desain editorial utilitarian & spot pastels
├── templates/
│   └── index.html           # Template UI Bento minimalis
├── main.py                  # Server FastAPI
├── requirements.txt         # Kebutuhan dependensi Python
└── README.md
```

---

## 3. Cara Menjalankan

### Prasyarat
- Python 3.10+ (disarankan)

### Langkah Instalasi
1. Clone repositori:
   ```bash
   git clone https://github.com/Owenn4/sistem-pakar-sp500.git
   cd sistem-pakar-sp500
   ```

2. Buat virtual environment (opsional namun disarankan):
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # Linux/macOS
   # venv\Scripts\activate    # Windows
   ```

3. Pasang dependensi:
   ```bash
   pip install -r requirements.txt
   ```

4. Jalankan aplikasi web:
   ```bash
   python3 -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
   ```

5. Buka peramban di: **http://127.0.0.1:8000**

---

## 4. Evaluasi & Tolok Ukur

- **Regression Test Cases**: 20 dari 20 skenario uji lulus (100% konsisten terhadap desain aturan).
- **Unit Test Komponen NLP**: 8 dari 8 uji logika negasi dan ToI lulus.
- **Sinyal BUY Kontrarian**: Memiliki tingkat presisi **40.38%**, mengungguli peluang dasar pasar (**32.95%**) dengan peningkatan relatif +22.5%.
- **Backtest Historis 2020–2024**: Menghasilkan return kumulatif **+27.1%** dengan 84.3% waktu berada di posisi kas (HOLD), menjaga stabilitas dari drawdown tajam.

---

## 5. Tim Pengembang (Proyek UTS Sistem Pakar)

- **Owen Antony** (412024002)
- **Kristofer Ryan Giggs Eka Saputra** (412024005)
- **Steven Iwan** (412024008)
- **Gaddiel Abiyr Nesher Sitorus** (412024032)

*Fakultas Teknologi Cerdas &bull; Program Studi Informatika*

---

## 6. Referensi Literatur
1. **Barbaglia, L., Consoli, S., & Manzan, S. (2022).** *Forecasting with Economic News*. Journal of Business & Economic Statistics.
2. **Maghyereh, A., & Abdoh, H. (2022).** *Can news-based economic sentiment predict bubbles in precious metal markets?* Resources Policy.
