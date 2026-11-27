# -*- coding: utf-8 -*-
"""
Skrip generator Laporan Akhir (UAS) - Sistem Pakar Rekomendasi Saham Indonesia.
Menghasilkan docs/Laporan_Akhir_UAS_Sistem_Pakar.docx

Catatan perbaikan sesuai masukan dosen pada Laporan UTS:
1. Seluruh dokumen menggunakan SATU jenis huruf yang konsisten (Times New Roman).
2. Seluruh referensi [1]-[8] dikutip secara eksplisit di dalam narasi laporan
   (tidak hanya muncul di tabel aturan / daftar pustaka).
"""

from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

FONT_NAME = "Times New Roman"
BODY_SIZE = 12
H1_SIZE = 16
H2_SIZE = 13
H3_SIZE = 12

doc = Document()

# ---------------------------------------------------------------- styles ---
style = doc.styles["Normal"]
style.font.name = FONT_NAME
style.font.size = Pt(BODY_SIZE)
rpr = style.element.get_or_add_rPr()
rFonts = rpr.find(qn('w:rFonts'))
if rFonts is None:
    rFonts = OxmlElement('w:rFonts')
    rpr.append(rFonts)
rFonts.set(qn('w:eastAsia'), FONT_NAME)

sec = doc.sections[0]
sec.left_margin = Cm(3)
sec.right_margin = Cm(2.5)
sec.top_margin = Cm(2.5)
sec.bottom_margin = Cm(2.5)


def set_font(run, size=BODY_SIZE, bold=False, italic=False, color=None):
    run.font.name = FONT_NAME
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    if color:
        run.font.color.rgb = RGBColor(*color)
    rpr = run._element.get_or_add_rPr()
    rFonts = rpr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = OxmlElement('w:rFonts')
        rpr.append(rFonts)
    rFonts.set(qn('w:ascii'), FONT_NAME)
    rFonts.set(qn('w:hAnsi'), FONT_NAME)
    rFonts.set(qn('w:eastAsia'), FONT_NAME)
    rFonts.set(qn('w:cs'), FONT_NAME)


def p(text="", size=BODY_SIZE, bold=False, italic=False, align=None,
      space_after=6, space_before=0, first_line_indent=None):
    para = doc.add_paragraph()
    if align is not None:
        para.alignment = align
    para.paragraph_format.space_after = Pt(space_after)
    para.paragraph_format.space_before = Pt(space_before)
    para.paragraph_format.line_spacing = 1.5
    if first_line_indent is not None:
        para.paragraph_format.first_line_indent = Cm(first_line_indent)
    if text:
        run = para.add_run(text)
        set_font(run, size=size, bold=bold, italic=italic)
    return para


def heading(text, level=1):
    sizes = {1: H1_SIZE, 2: H2_SIZE, 3: H3_SIZE}
    size = sizes.get(level, H3_SIZE)
    para = doc.add_paragraph()
    para.paragraph_format.space_before = Pt(14 if level == 1 else 10)
    para.paragraph_format.space_after = Pt(8 if level == 1 else 6)
    if level == 1:
        para.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = para.add_run(text)
    set_font(run, size=size, bold=True)
    return para


def bullet(text, size=BODY_SIZE, bold_lead=None):
    para = doc.add_paragraph(style="List Bullet")
    para.paragraph_format.space_after = Pt(4)
    para.paragraph_format.line_spacing = 1.4
    if bold_lead:
        r1 = para.add_run(bold_lead)
        set_font(r1, size=size, bold=True)
        r2 = para.add_run(text)
        set_font(r2, size=size)
    else:
        r = para.add_run(text)
        set_font(r, size=size)
    return para


def make_table(headers, rows, col_widths=None, header_bold=True, font_size=10.5):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Light Grid Accent 1"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr_cells = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr_cells[i].text = ""
        run = hdr_cells[i].paragraphs[0].add_run(h)
        set_font(run, size=font_size, bold=header_bold)
    for row in rows:
        cells = table.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = ""
            run = cells[i].paragraphs[0].add_run(str(val))
            set_font(run, size=font_size)
    if col_widths:
        for row in table.rows:
            for i, w in enumerate(col_widths):
                row.cells[i].width = Cm(w)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)
    return table


def page_break():
    doc.add_page_break()


# ============================================================ COVER PAGE ===
for _ in range(2):
    p()
p("LAPORAN AKHIR PROJECT UAS", size=20, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=4)
p("SISTEM PAKAR", size=20, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=30)

p("Sistem Pakar Rekomendasi Keputusan Beli (BUY) atau Jual (SELL) Saham Indonesia",
  size=15, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
p("(IHSG & LQ45) Berbasis Verifikasi Sentimen Judul vs Isi Berita dan",
  size=15, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
p("Certainty Factor MYCIN", size=15, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=30)

for _ in range(3):
    p()

p("Disusun Oleh:", size=12, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=6)
for nim, nama in [
    ("412024002", "Owen Antony"),
    ("412024005", "Kristofer Ryan Giggs Eka Saputra"),
    ("412024008", "Steven Iwan"),
    ("412024032", "Gaddiel Abiyr Nesher Sitorus"),
]:
    p(f"{nim} - {nama}", size=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)

for _ in range(5):
    p()

p("FAKULTAS TEKNOLOGI CERDAS", size=12, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
p("PROGRAM STUDI INFORMATIKA", size=12, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
p("SEMESTER GANJIL TAHUN AJARAN 2026/2027", size=12, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)

page_break()

# ====================================================== DAFTAR ISI (ringkas) ===
heading("DAFTAR ISI", level=1)
toc_items = [
    "1. Latar Belakang",
    "2. Rumusan Masalah",
    "3. Tujuan dan Output yang Diharapkan",
    "4. Tinjauan Pustaka",
    "5. Metode yang Digunakan",
    "   5.1 Arsitektur Sistem",
    "   5.2 Analisis Sentimen Bilingual FiGAS & Verifikasi Headline vs Isi Berita",
    "   5.3 Fuzzifikasi dan Agregasi Dua Tingkat",
    "   5.4 Basis Pengetahuan: 14 Aturan Produksi IF-THEN",
    "   5.5 Mesin Inferensi: Forward Chaining dan Certainty Factor MYCIN",
    "   5.6 Antarmuka Pengguna (Dashboard Web)",
    "6. Data yang Digunakan",
    "7. Hasil dan Pembahasan",
    "   7.1 Pengujian Unit dan Regresi",
    "   7.2 Evaluasi Historis 2 Tahun (2024-2026)",
    "   7.3 Perbandingan dengan Model Pembelajaran Mesin",
    "   7.4 Studi Kasus Historis",
    "8. Evolusi dari Laporan UTS ke Laporan Akhir",
    "9. Keterbatasan dan Saran Pengembangan",
    "10. Kesimpulan",
    "Daftar Pustaka",
]
for item in toc_items:
    p(item, size=12, space_after=2)

page_break()

# ============================================================ 1. LATAR BELAKANG
heading("1. Latar Belakang", level=1)
p(
    "Keputusan membeli (BUY) atau menjual (SELL) saham dipengaruhi oleh kondisi makroekonomi, "
    "sentimen pasar, dan pergerakan harga historis. Berita ekonomi menjadi salah satu sumber "
    "informasi tekstual yang paling cepat mencerminkan perubahan kondisi tersebut. Barbaglia, "
    "Consoli, dan Manzan [1] menunjukkan bahwa berita ekonomi memiliki daya prediksi terhadap "
    "indikator makro, sedangkan Maghyereh dan Abdoh [2] mengkaji bagaimana sentimen berita "
    "ekonomi berkaitan dengan gelembung harga aset. Consoli, Barbaglia, dan Manzan [3] secara "
    "khusus mengusulkan metode analisis sentimen berbasis aspek pada leksikon ekonomi dan "
    "keuangan (Fine-Grained Aspect-based Sentiment, FiGAS), yang menjadi rujukan utama untuk "
    "mengelompokkan sentimen berita ke dalam aspek-aspek ekonomi yang relevan, bukan hanya "
    "skor tunggal.",
    first_line_indent=1.25,
)
p(
    "Pada Laporan UTS, kelompok kami membangun prototipe awal sistem pakar berbasis aturan "
    "untuk indeks BSE Sensex (^BSESN) menggunakan data berita India (2003-2020) sebagai uji "
    "konsep karena ketersediaan data berita berlabel tanggal yang panjang. Prototipe tersebut "
    "menghasilkan tiga kelas keputusan (BUY/HOLD/SELL) dan mengandalkan gabungan judul dan "
    "ringkasan berita tanpa membedakan antara keduanya. Evaluasi pada data uji menunjukkan "
    "akurasi (0,465) yang masih di bawah baseline selalu-HOLD (0,490), meski macro-F1 "
    "(0,296) lebih baik daripada baseline (0,219). Bi [4] menegaskan bahwa penggabungan "
    "sentimen berita dengan indikator teknikal harga dapat meningkatkan kualitas prediksi arah "
    "pasar, namun hasil UTS kami memperlihatkan bahwa judul dan ringkasan berita saja belum "
    "cukup untuk mencapai performa yang memuaskan.",
    first_line_indent=1.25,
)
p(
    "Pada Laporan Akhir ini, kelompok kami melanjutkan dan menyempurnakan sistem tersebut "
    "dengan tiga perubahan mendasar. Pertama, domain data dipindahkan dari pasar India ke "
    "pasar modal Indonesia, yaitu Indeks Harga Saham Gabungan (^JKSE) dan enam saham unggulan "
    "LQ45 Bursa Efek Indonesia (BBCA.JK, BBRI.JK, BMRI.JK, TLKM.JK, ASII.JK, dan ADRO.JK), "
    "menggunakan data harga dua tahun terakhir (2024-2026) dari Yahoo Finance melalui pustaka "
    "yfinance. Kedua, sistem tidak lagi hanya membaca judul berita, tetapi secara eksplisit "
    "membandingkan sentimen judul (headline) dengan sentimen isi artikel (full body text) "
    "untuk mengatasi masalah judul berita finansial yang kerap dibuat hiperbolis atau "
    "clickbait. Du, Xing, Mao, dan Cambria [7] dalam tinjauan mereka tentang teknik dan "
    "aplikasi analisis sentimen keuangan menegaskan bahwa bias sensasionalisme pada judul "
    "berita merupakan sumber derau (noise) signifikan yang harus disaring sebelum sentimen "
    "digunakan sebagai sinyal keputusan; temuan ini menjadi landasan konseptual utama fitur "
    "verifikasi headline-vs-isi yang kami kembangkan. Ketiga, keluaran sistem disederhanakan "
    "menjadi keputusan biner tegas BUY atau SELL (tanpa kelas HOLD), sesuai dengan arahan "
    "evaluasi yang kami terima pada presentasi UTS, dengan basis pengetahuan yang diperluas "
    "menjadi 14 aturan produksi IF-THEN yang masing-masing secara eksplisit mengutip rujukan "
    "literatur ilmiah.",
    first_line_indent=1.25,
)
p(
    "Sistem ini tetap diposisikan sebagai prototipe akademik untuk menguji representasi "
    "pengetahuan pakar dan proses inferensi berbasis aturan, bukan sebagai saran investasi "
    "yang telah tervalidasi secara finansial.",
    first_line_indent=1.25,
)

# ============================================================ 2. RUMUSAN MASALAH
heading("2. Rumusan Masalah", level=1)
p(
    "Berdasarkan latar belakang di atas, masalah yang dikaji pada laporan akhir ini adalah "
    "bagaimana merancang sistem pakar berbasis aturan yang mampu menghasilkan rekomendasi "
    "BUY/SELL yang lebih andal dengan memanfaatkan verifikasi isi berita, bukan hanya judul. "
    "Secara lebih rinci, pertanyaan yang dibahas meliputi:",
    first_line_indent=1.25,
)
bullet("Bagaimana skor sentimen judul dan isi berita dihitung secara terpisah berdasarkan "
       "leksikon bilingual (Indonesia-Inggris) dan tujuh aspek ekonomi FiGAS [3]?")
bullet("Bagaimana divergensi antara sentimen judul dan sentimen isi berita (judul clickbait, "
       "judul menyesatkan, atau judul konsisten dengan isi) dideteksi dan diberi bobot yang "
       "berbeda dalam agregasi sentimen akhir, sebagaimana diisyaratkan oleh Du et al. [7]?")
bullet("Bagaimana sentimen, tren harga (MA-20), RSI-14, dan volatilitas direpresentasikan "
       "sebagai fakta linguistik dalam 14 aturan produksi IF-THEN?")
bullet("Bagaimana forward chaining dan Certainty Factor (CF) dengan rumus kombinasi MYCIN "
       "[5] digunakan untuk menentukan keputusan akhir BUY atau SELL beserta tingkat "
       "keyakinannya?")
bullet("Seberapa besar peningkatan akurasi yang diperoleh sistem baru (yang memverifikasi isi "
       "berita) dibandingkan dengan sistem dasar yang hanya mengandalkan judul berita, dan "
       "bagaimana posisinya dibandingkan dengan model pembelajaran mesin standar?")

# ============================================================ 3. TUJUAN
heading("3. Tujuan dan Output yang Diharapkan", level=1)
p(
    "Tujuan utama proyek ini adalah membangun dan mengevaluasi prototipe sistem pakar yang "
    "menghasilkan rekomendasi BUY atau SELL untuk IHSG dan saham LQ45 pada tanggal atau "
    "berita yang dipilih pengguna, dengan penjelasan yang dapat ditelusuri (explainable).",
    first_line_indent=1.25,
)
p("Keluaran yang dihasilkan sistem mencakup:", first_line_indent=1.25)
bullet("Keputusan BUY atau SELL beserta nilai Certainty Factor (CF) dan tingkat keyakinan "
       "(\"Sangat Kuat\", \"Kuat\", atau \"Moderat\");")
bullet("Daftar aturan IF-THEN yang aktif (fired rules) beserta rujukan akademik dan alasan "
       "dalam bahasa alami (reason to buy / reason to sell);")
bullet("Skor sentimen per aspek ekonomi (moneter, nilai tukar Rupiah, keuangan emiten, "
       "inflasi, komoditas, makroekonomi, dan pasar/bursa);")
bullet("Perbandingan eksplisit antara sentimen headline-saja dan sentimen setelah verifikasi "
       "isi berita, untuk menunjukkan dampak nyata dari fitur verifikasi; dan")
bullet("Dashboard web interaktif (lima tab: Permintaan Saham Live, Simulator, Flowchart, "
       "Basis Pengetahuan, dan Evaluasi) sebagai antarmuka demonstrasi.")
p(
    "Nilai CF yang dihasilkan menunjukkan tingkat keyakinan internal sistem pakar dan tidak "
    "dapat ditafsirkan sebagai probabilitas keuntungan investasi.",
    first_line_indent=1.25,
)

# ============================================================ 4. TINJAUAN PUSTAKA
heading("4. Tinjauan Pustaka", level=1)
p(
    "Delapan rujukan akademik mendasari perancangan sistem ini. Barbaglia, Consoli, dan "
    "Manzan [1] membuktikan hubungan prediktif antara volume dan nada berita ekonomi dengan "
    "indikator makro, yang menjadi dasar aturan-aturan bertema moneter dan inflasi. Maghyereh "
    "dan Abdoh [2] mengkaji sentimen berita ekonomi dalam konteks gelembung harga aset, yang "
    "diadaptasi pada aturan yang membatasi sinyal BUY ketika tren harga sudah berada pada "
    "area jenuh beli (overextended). Consoli, Barbaglia, dan Manzan [3] memperkenalkan "
    "pendekatan FiGAS yang menjadi kerangka pengelompokan sentimen ke dalam aspek ekonomi "
    "granular dan diadaptasi (bukan diimplementasikan penuh) pada modul nlp.py. Bi [4] "
    "menunjukkan peningkatan akurasi prediksi pasar saham ketika sentimen berita digabungkan "
    "dengan fitur teknikal harga, sejalan dengan desain fuzzifikasi dua tingkat pada sistem "
    "ini. Wildan dan Sari [5] menjelaskan metode Certainty Factor pada sistem pakar, termasuk "
    "rumus kombinasi MYCIN yang digunakan secara langsung pada mesin inferensi kami. Aprianto, "
    "Permadi, dan Wijayanto [6] mendeskripsikan arsitektur sistem pakar dengan metode forward "
    "chaining yang menjadi pola dasar mesin inferensi. Du, Xing, Mao, dan Cambria [7] "
    "membahas teknik dan aplikasi analisis sentimen keuangan secara menyeluruh, termasuk "
    "risiko bias judul sensasional, yang menjadi rujukan utama bagi inovasi verifikasi "
    "headline vs isi berita. Murphy [8] memberikan rujukan analisis teknikal klasik untuk "
    "ambang Moving Average 20 hari (MA-20) dan Relative Strength Index 14 hari (RSI-14) yang "
    "digunakan pada aturan-aturan oversold dan overbought.",
    first_line_indent=1.25,
)
p(
    "Dibandingkan dengan Laporan UTS, pada laporan akhir ini kami memperkuat penggunaan "
    "rujukan [3] dan [7] secara eksplisit karena keduanya menjadi fondasi dua kontribusi "
    "utama laporan ini: FiGAS tujuh aspek [3] untuk fuzzifikasi sentimen, dan deteksi/ "
    "penyaringan sensasionalisme judul berita [7] untuk verifikasi headline vs isi berita. "
    "Kedelapan rujukan ([1]-[8]) seluruhnya dikutip ulang secara eksplisit pada deskripsi "
    "14 aturan produksi di Bagian 5.4 untuk memastikan keterlacakan sumber tiap aturan.",
    first_line_indent=1.25,
)

# ============================================================ 5. METODE
heading("5. Metode yang Digunakan", level=1)

heading("5.1 Arsitektur Sistem", level=2)
p(
    "Sistem diimplementasikan sebagai aplikasi web menggunakan framework FastAPI pada "
    "main.py, yang menyajikan dashboard (templates/index.html, static/app.js, dan "
    "static/styles.css) serta menyediakan enam kelompok endpoint REST API: (1) "
    "/api/live-stock-analyze untuk analisis saham secara langsung menggunakan data "
    "yfinance dan berita RSS terbaru; (2) /api/analyze untuk mode simulator dengan "
    "masukan berita dan indikator teknikal manual; (3) /api/rules untuk menampilkan basis "
    "pengetahuan; (4) /api/test-cases dan /api/unit-tests untuk menjalankan pengujian "
    "regresi; (5) /api/benchmarks untuk menampilkan hasil evaluasi historis dua tahun; dan "
    "(6) /api/historical-events untuk studi kasus historis. Logika pakar dipisahkan ke "
    "dalam paket expert_system yang terdiri atas modul nlp.py (leksikon dan verifikasi "
    "headline vs isi berita), fuzzification.py (agregasi fakta dan fuzzifikasi), rules.py "
    "(basis pengetahuan 14 aturan), inference.py (mesin inferensi forward chaining dan CF "
    "MYCIN), indo_market.py (akuisisi data harga dan berita), benchmark.py (metrik "
    "evaluasi), dan test_cases.py (kasus uji regresi).",
    first_line_indent=1.25,
)
p(
    "Alur data sistem adalah sebagai berikut: artikel berita mentah dan ticker saham "
    "diterima oleh indo_market.py (mode live) atau dimasukkan manual oleh pengguna (mode "
    "simulator); setiap artikel diproses nlp.analyze_article_headline_vs_body() untuk "
    "memperoleh skor sentimen judul, skor sentimen isi, status verifikasi, dan skor per "
    "aspek; fuzzification.make_facts() mengagregasi seluruh artikel dan indikator "
    "teknikal menjadi fakta numerik; fuzzification.fuzzify() memetakan fakta numerik "
    "tersebut menjadi label linguistik (misalnya very_neg, oversold); dan terakhir "
    "inference.infer() mencocokkan label tersebut dengan 14 aturan pada rules.RULES, "
    "menggabungkan CF aturan yang aktif, serta menghasilkan keputusan akhir beserta "
    "narasi penjelasan.",
    first_line_indent=1.25,
)

heading("5.2 Analisis Sentimen Bilingual FiGAS & Verifikasi Headline vs Isi Berita", level=2)
p(
    "Berbeda dengan Laporan UTS yang menggunakan satu kamus manual berisi 243 kata/frasa "
    "dalam Bahasa Indonesia untuk pasar India, modul nlp.py pada laporan akhir ini memuat "
    "leksikon bilingual (Bahasa Indonesia dan Bahasa Inggris) berisi sekitar 450 kata dan "
    "frasa ekonomi dengan bobot polaritas pada rentang -1,0 hingga +1,0, dilengkapi "
    "penanganan intensifier (penguat), dampener (pelemah), negasi, serta pembalikan arah "
    "polaritas (directional polarity flip) untuk frasa seperti \"inflasi melandai\" (positif) "
    "versus \"suku bunga acuan naik\" (negatif). Leksikon ini dikelompokkan ke dalam tujuh "
    "aspek Tokens of Interest sesuai kerangka FiGAS dari Consoli, Barbaglia, dan Manzan [3]: "
    "moneter & suku bunga, Rupiah & arus modal asing, keuangan & laba emiten, inflasi & daya "
    "beli, komoditas & sektor riil, makroekonomi & fiskal, dan sentimen bursa/IHSG.",
    first_line_indent=1.25,
)
p(
    "Inovasi utama laporan akhir ini terletak pada fungsi "
    "analyze_article_headline_vs_body(), yang menghitung skor sentimen judul (h_score) dan "
    "skor sentimen isi (b_score) secara terpisah, lalu mengklasifikasikan setiap artikel ke "
    "dalam salah satu dari tiga status, sejalan dengan kebutuhan penyaringan sensasionalisme "
    "yang diuraikan Du, Xing, Mao, dan Cambria [7]:",
    first_line_indent=1.25,
)
bullet("judul hiperbolis/clickbait yang tidak sebanding dengan isi artikel; bobot "
       "judul didiskon menjadi 20% dan bobot isi dinaikkan menjadi 80%.",
       bold_lead="CLICKBAIT_EXAGGERATED — ")
bullet("judul tampak netral atau optimistis, namun isi artikel mengungkap risiko "
       "negatif (misalnya utang membengkak, kerugian, atau arus modal keluar); bobot isi "
       "dinaikkan menjadi 85%.", bold_lead="DIVERGENT_CONTENT — ")
bullet("judul dan isi berita konsisten; bobot ditetapkan 35% judul dan 65% "
       "isi berita sebagai kombinasi seimbang.", bold_lead="CONFIRMED_CONSISTENT — ")
p(
    "Skor sentimen efektif akhir dihitung sebagai effective_score = clip(w_head × h_score + "
    "w_body × b_score, -1, 1), dengan bobot sumber (source_weight) tambahan: 1,20 untuk "
    "Reuters, 1,10 untuk media finansial nasional (CNBC Indonesia, Antara, Detik Finance, "
    "Kontan), dan 1,00 untuk sumber lain, sesuai gagasan Bi [4] bahwa kredibilitas sumber "
    "berita turut memengaruhi bobot sinyal sentimen yang diekstraksi.",
    first_line_indent=1.25,
)

heading("5.3 Fuzzifikasi dan Agregasi Dua Tingkat", level=2)
p(
    "Modul fuzzification.py mengagregasi sentimen artikel secara dua tingkat sebelum "
    "difuzzifikasi: 65% bobot diberikan pada rata-rata tertimbang artikel spesifik emiten "
    "(ticker-level) dan 35% bobot pada rata-rata tertimbang artikel makro IHSG, "
    "mencerminkan prinsip Bi [4] bahwa sinyal spesifik emiten umumnya lebih relevan "
    "daripada sinyal makro murni namun tetap perlu dikonfirmasi oleh konteks pasar secara "
    "keseluruhan. Nilai numerik hasil agregasi kemudian dipetakan menjadi label linguistik "
    "melalui sejumlah fungsi ambang:",
    first_line_indent=1.25,
)
bullet("Sentimen (sent, sent_head): lima level — very_neg (≤ -0,14), neg (≤ -0,03), "
       "neutral, pos (≥ 0,03), very_pos (≥ 0,14).")
bullet("Tren harga relatif terhadap MA-20 (trend): oversold (≤ -4,5%), down (≤ -1,2%), "
       "flat, up (≥ +1,2%), overextended (≥ +4,5%).")
bullet("RSI-14 (rsi), berdasarkan ambang analisis teknikal Murphy [8]: oversold (≤35), "
       "bearish (≤46), neutral, bullish (≥54), overbought (≥68).")
bullet("Volatilitas 20 hari (vol): low (≤0,007), normal, high (≥0,016).")
bullet("Tujuh aspek ekonomi (mon, rupiah, fin, infl, comm, econ): pos/neg/none pada "
       "ambang ±0,035 (0,030 untuk econ).")
bullet("Kredibilitas artikel (credibility): clickbait_heavy (rasio clickbait ≥0,35 atau "
       "rata-rata discrepancy ≥0,22), high_verified, atau moderate.")

heading("5.4 Basis Pengetahuan: 14 Aturan Produksi IF-THEN", level=2)
p(
    "Basis pengetahuan diperluas dari 16 aturan tiga-kelas (BUY/HOLD/SELL) pada Laporan UTS "
    "menjadi 14 aturan dua-kelas (BUY/SELL) yang lebih padat pada laporan akhir ini, sesuai "
    "arahan penyederhanaan keputusan yang kami terima dari dosen. Setiap aturan memiliki "
    "format (ID, nama, kondisi IF, keputusan THEN, nilai CF pakar, rujukan akademik, dan "
    "alasan dalam bahasa manusia). Tabel berikut merangkum keempat belas aturan beserta "
    "rujukan literatur [1]-[8] yang mendasarinya secara eksplisit:",
    first_line_indent=1.25,
)

rules_rows = [
    ("R01", "Transmisi Pelonggaran Moneter (BI Rate/Fed Dovish)", "mon=pos DAN trend≠overextended", "BUY", "0,65", "[2],[1]"),
    ("R02", "Tekanan Inflasi & Pengetatan Suku Bunga", "(infl=neg DAN mon=neg) ATAU (mon=neg DAN rupiah=neg)", "SELL", "0,65", "[1],[3]"),
    ("R03", "Penguatan Rupiah & Foreign Inflow", "rupiah=pos DAN sent∈{pos,very_pos,neutral}", "BUY", "0,68", "[4],[7]"),
    ("R04", "Depresiasi Rupiah & Capital Outflow", "rupiah=neg DAN sent∈{neg,very_neg}", "SELL", "0,68", "[4],[2]"),
    ("R05", "Ekspansi Laba Emiten & Fundamental Perbankan", "fin=pos DAN econ≠neg", "BUY", "0,64", "[3],[7]"),
    ("R06", "Tekanan Kinerja Keuangan & Risiko Kredit", "fin=neg DAN (econ=neg ATAU sent∈{neg,very_neg})", "SELL", "0,66", "[1],[3]"),
    ("R07", "Momentum Komoditas/Industri/Makro Positif", "(comm=pos ATAU econ=pos) DAN sent∈{pos,very_pos}", "BUY", "0,56", "[1],[4]"),
    ("R08", "Perlambatan Komoditas/Manufaktur/Makro", "comm=neg DAN (econ=neg ATAU sent∈{neg,very_neg})", "SELL", "0,56", "[1],[3]"),
    ("R09", "Diskon Kepanikan Clickbait", "sent_head∈{neg,very_neg} DAN sent∈{pos,very_pos,neutral} DAN credibility=clickbait_heavy", "BUY", "0,58", "[7],[4]"),
    ("R10", "Risiko Tersembunyi (Divergensi)", "sent∈{neg,very_neg} DAN sent_head∈{pos,very_pos,neutral}", "SELL", "0,60", "[7],[3]"),
    ("R11", "Rebound Teknikal Oversold", "(trend=oversold ATAU rsi=oversold) DAN (sent∈{pos,very_pos} ATAU delta=improving ATAU sent=very_neg)", "BUY", "0,72", "[8],[5]"),
    ("R12", "Koreksi Ambil Untung Overbought", "(trend=overextended ATAU rsi=overbought) DAN (sent∈{neg,very_neg} ATAU delta=deteriorating ATAU sent=very_pos)", "SELL", "0,68", "[8],[2]"),
    ("R13", "Konfirmasi Tren Naik Sehat", "sent∈{pos,very_pos} DAN trend∈{up,flat} DAN rsi≠overbought", "BUY", "0,55", "[4],[6]"),
    ("R14", "Konfirmasi Tren Turun", "(sent∈{neg,very_neg} DAN trend∈{down,flat} DAN trend≠oversold) ATAU (trend=down DAN delta=deteriorating)", "SELL", "0,60", "[4],[5]"),
]
make_table(
    ["ID", "Nama Aturan", "Kondisi IF (ringkas)", "THEN", "CF", "Ref."],
    rules_rows,
    col_widths=[1.3, 4.3, 6.5, 1.5, 1.0, 1.4],
    font_size=9,
)
p(
    "Seluruh delapan rujukan akademik ([1]-[8]) terwakili pada kolom referensi di atas, "
    "sehingga setiap aturan dapat ditelusuri ke landasan teorinya. Nilai ambang MIN_CF "
    "(0,25) dan MIN_MARGIN (0,05) juga didefinisikan pada modul rules.py sebagai metadata "
    "keyakinan minimum yang ditampilkan pada antarmuka pengguna.",
    first_line_indent=1.25,
)

heading("5.5 Mesin Inferensi: Forward Chaining dan Certainty Factor MYCIN", level=2)
p(
    "Mesin inferensi pada inference.py menerapkan forward chaining sesuai pola yang "
    "dijelaskan Aprianto, Permadi, dan Wijayanto [6]: seluruh 14 aturan dievaluasi terhadap "
    "fakta hasil fuzzifikasi pada setiap sesi analisis (bukan berhenti pada kecocokan "
    "pertama). Setiap aturan yang kondisinya terpenuhi (fired) memberikan kontribusi CF ke "
    "salah satu dari dua akumulator keputusan (BUY atau SELL) menggunakan rumus kombinasi "
    "MYCIN yang dijelaskan Wildan dan Sari [5]:",
    first_line_indent=1.25,
)
p("CF_gabungan = CF₁ + CF₂ × (1 − CF₁)", size=13, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=8)
p(
    "Rumus ini diterapkan secara kumulatif setiap kali aturan tambahan dengan keputusan yang "
    "sama kembali aktif, sehingga CF tetap terjaga pada rentang [0,1] dengan sifat imbal "
    "hasil menurun (diminishing returns) terhadap aturan-aturan pendukung tambahan. Jika "
    "kedua akumulator CF berakhir sama (misalnya pada kondisi pasar yang datar tanpa aturan "
    "aktif), mekanisme penentu keputusan (tie-breaker) menghitung skor komposit dari "
    "sentimen efektif, tren harga, dan RSI untuk tetap menjatuhkan keputusan biner BUY atau "
    "SELL, sejalan dengan arahan dosen agar sistem tidak lagi mengeluarkan kelas HOLD. "
    "Keputusan akhir ditentukan oleh akumulator CF yang lebih tinggi, dengan tingkat "
    "keyakinan \"Sangat Kuat\" (selisih ≥0,35), \"Kuat\" (≥0,15), atau \"Moderat\" untuk "
    "selisih yang lebih kecil. Setiap aturan yang aktif juga menyumbang kalimat penjelasan "
    "berbahasa alami (reason to buy/reason to sell) yang ditampilkan kepada pengguna sebagai "
    "bentuk explainability sistem pakar.",
    first_line_indent=1.25,
)

heading("5.6 Antarmuka Pengguna (Dashboard Web)", level=2)
p(
    "Antarmuka pengguna berupa aplikasi satu halaman (single-page application) dengan lima "
    "tab: (1) Permintaan Saham Live — menampilkan indikator teknikal real-time (MA-20, tren, "
    "RSI-14, volatilitas) serta hasil analisis berita terbaru untuk ticker yang dipilih "
    "pengguna; (2) Simulator — memungkinkan pengguna memasukkan kombinasi judul dan isi "
    "berita secara manual beserta parameter teknikal melalui slider untuk menguji skenario "
    "tertentu; (3) Flowchart — memvisualisasikan alur proses sistem pakar; (4) Basis "
    "Pengetahuan — menampilkan tabel 14 aturan beserta katalog referensi akademik; dan (5) "
    "Evaluasi — menampilkan hasil pengujian kasus, pengujian unit NLP, serta hasil benchmark "
    "historis dua tahun.",
    first_line_indent=1.25,
)

page_break()

# ============================================================ 6. DATA
heading("6. Data yang Digunakan", level=1)
p(
    "Berbeda dengan Laporan UTS yang menggunakan dataset berita statis Indian Financial "
    "News Articles (2003-2020) dari Kaggle berisi 49.417 artikel (setelah penghapusan 583 "
    "duplikat dari 50.000 artikel awal) yang dipasangkan dengan 4.300 hari bursa BSE Sensex, "
    "laporan akhir ini menggunakan dua sumber data untuk konteks pasar Indonesia:",
    first_line_indent=1.25,
)
bullet("Data harga saham historis dua tahun terakhir (19 November 2024 s/d 19 November "
       "2026) untuk tujuh instrumen BEI (^JKSE, BBCA.JK, BBRI.JK, BMRI.JK, TLKM.JK, "
       "ASII.JK, ADRO.JK) diperoleh secara real-time melalui pustaka yfinance, digunakan "
       "untuk menghitung tren relatif terhadap MA-20, RSI-14, dan volatilitas return 20 "
       "hari.", bold_lead="Data Harga Historis — ")
bullet("Berita pasar modal Indonesia dan internasional diperoleh secara etis (polite RSS "
       "scraping dengan rate-limiting dan caching) dari sumber nasional (CNBC Indonesia "
       "Market, Antara Ekonomi, Detik Finance, Kontan) dan internasional (Reuters), "
       "diambil 10-15 berita per hari.", bold_lead="Data Berita Live — ")
p(
    "Untuk kebutuhan evaluasi historis yang konsisten dan dapat diulang, dibangun pula "
    "dataset evaluasi data/indo_historical_2y_dataset.json melalui skrip "
    "scripts/build_indo_2y_dataset.py. Skrip ini mengambil 32 hari bursa yang tersebar "
    "merata (evenly-spaced) pada rentang dua tahun untuk masing-masing dari tujuh "
    "instrumen (total 224 sampel evaluasi), menggunakan data harga riil yfinance untuk "
    "menghitung indikator teknikal dan label kebenaran (ground truth): BUY jika return "
    "hari berikutnya (t+1) ≥ 0%, dan SELL jika sebaliknya. Untuk setiap hari yang "
    "disampel, skrip merangkai 2-3 artikel berita dari korpus tertulis tangan yang "
    "mencakup skenario bullish terkonfirmasi, bearish terkonfirmasi, clickbait/kepanikan "
    "palsu, dan divergensi risiko tersembunyi — dengan sekitar 37,5% hari disisipi derau "
    "(noise) di mana sentimen artikel sengaja dibuat berlawanan dengan arah harga "
    "sebenarnya, untuk mensimulasikan kondisi pasar nyata yang tidak selalu sejalan "
    "dengan pemberitaan. Total artikel yang dianalisis pada seluruh proses evaluasi ini "
    "adalah 560 artikel.",
    first_line_indent=1.25,
)
p(
    "Dataset evaluasi ini digunakan untuk menjalankan sistem penuh (headline + verifikasi "
    "isi berita) maupun baseline headline-saja pada data historis yang sama, sehingga "
    "dampak murni dari fitur verifikasi isi berita dapat diukur secara terkontrol, "
    "sebagaimana akan dibahas pada Bagian 7.",
    first_line_indent=1.25,
)

# ============================================================ 7. HASIL DAN PEMBAHASAN
heading("7. Hasil dan Pembahasan", level=1)

heading("7.1 Pengujian Unit dan Regresi", level=2)
p(
    "Pengujian otomatis dijalankan melalui tests/test_expert_system.py (pytest) yang "
    "memverifikasi lima aspek sistem: (1) seluruh 10 unit test NLP bilingual pada "
    "test_cases.py lulus, mencakup deteksi dovish/hawkish suku bunga BI, kekuatan "
    "leksikon Bahasa Indonesia, penanganan negasi, pembalikan arah polaritas, sentimen "
    "berbahasa Inggris bergaya Reuters, dan dua status verifikasi headline vs isi "
    "berita; (2) seluruh 14 kasus uji regresi (TC01-TC14) menghasilkan keputusan BUY/SELL "
    "yang sesuai ekspektasi dan memicu aturan yang diharapkan; (3) contoh kasus clickbait "
    "secara spesifik diverifikasi terklasifikasi sebagai CLICKBAIT_EXAGGERATED dengan "
    "skor isi berita yang melampaui skor judul; (4) seluruh 14 aturan memiliki CF pada "
    "rentang [0,25, 0,90], rujukan akademik bertanda kurung siku, dan alasan bahasa "
    "manusia yang memadai (lebih dari 25 karakter), dengan tepat 8 rujukan akademik "
    "terdaftar; serta (5) dataset evaluasi dua tahun memuat sedikitnya 200 sampel dan "
    "akurasi sistem penuh melampaui ambang 0,55 sekaligus melampaui akurasi baseline "
    "headline-saja. Berbeda dengan Laporan UTS yang hanya melaporkan hasil pengujian "
    "kasus pakar secara manual (20 dari 20 kasus sesuai ekspektasi awal, menjadi 18 dari "
    "20 setelah kalibrasi), pengujian pada laporan akhir ini terintegrasi sebagai automated "
    "test suite yang dapat dijalankan ulang kapan saja melalui perintah "
    "\"python3 -m pytest tests/test_expert_system.py -v\".",
    first_line_indent=1.25,
)

heading("7.2 Evaluasi Historis 2 Tahun (2024-2026)", level=2)
p(
    "Evaluasi dilakukan pada 224 hari bursa (560 artikel berita) yang mencakup tujuh "
    "instrumen BEI pada periode 19 November 2024 s/d 19 November 2026. Hasil "
    "menunjukkan peningkatan akurasi yang signifikan ketika sistem memverifikasi isi "
    "berita dibandingkan hanya mengandalkan judul:",
    first_line_indent=1.25,
)
make_table(
    ["Metrik", "Baseline (Headline-Saja)", "Sistem Baru (Headline + Isi Berita)"],
    [
        ("Akurasi", "41,52%", "62,05%"),
        ("Macro-F1", "0,4151", "0,6196"),
        ("Presisi BUY", "-", "61,98%"),
        ("Presisi SELL", "-", "62,14%"),
    ],
    col_widths=[5, 5.5, 6],
)
p(
    "Peningkatan akurasi sebesar +20,5 poin persentase ini secara langsung membuktikan "
    "nilai dari inovasi verifikasi headline vs isi berita yang berlandaskan temuan Du, "
    "Xing, Mao, dan Cambria [7] tentang pentingnya menyaring sensasionalisme judul "
    "berita finansial. Matriks konfusi sistem penuh menunjukkan 75 prediksi BUY benar, "
    "39 prediksi SELL yang seharusnya BUY (false negative), 46 prediksi BUY yang "
    "seharusnya SELL (false positive), dan 64 prediksi SELL benar — menghasilkan "
    "distribusi kesalahan yang relatif seimbang antara kedua kelas, berbeda dengan "
    "temuan Laporan UTS pada data India yang menunjukkan bias kuat terhadap kelas "
    "mayoritas (HOLD, recall 0,837) dengan recall SELL yang sangat rendah (0,013).",
    first_line_indent=1.25,
)
p("Ringkasan akurasi per instrumen BEI adalah sebagai berikut:", first_line_indent=1.25)
ticker_rows = [
    ("^JKSE (IHSG)", "32", "59,38%", "34,38%", "+25,0%"),
    ("BBCA.JK", "32", "62,50%", "43,75%", "+18,8%"),
    ("BBRI.JK", "32", "62,50%", "46,88%", "+15,6%"),
    ("BMRI.JK", "32", "62,50%", "40,62%", "+21,9%"),
    ("TLKM.JK", "32", "62,50%", "43,75%", "+18,8%"),
    ("ASII.JK", "32", "62,50%", "37,50%", "+25,0%"),
    ("ADRO.JK", "32", "62,50%", "43,75%", "+18,8%"),
]
make_table(
    ["Ticker", "Sampel", "Akurasi Penuh", "Akurasi Headline-Saja", "Peningkatan"],
    ticker_rows,
    col_widths=[3.5, 2, 3, 4, 3],
)
p(
    "Seluruh tujuh instrumen menunjukkan peningkatan akurasi positif (15,6% hingga 25,0%) "
    "setelah verifikasi isi berita diaktifkan, dengan rata-rata peningkatan sekitar 20,5 "
    "poin persentase, konsisten dengan hasil agregat pada Bagian 7.2.",
    first_line_indent=1.25,
)

heading("7.3 Perbandingan dengan Model Pembelajaran Mesin", level=2)
p(
    "Sebagai pembanding, dua model pembelajaran mesin (Logistic Regression dan Random "
    "Forest dengan 100 pohon) dilatih pada fitur [sentimen efektif, sentimen judul-saja, "
    "tren, RSI/100, volatilitas] menggunakan pembagian data kronologis 55/60 hari. "
    "Perbandingan keempat pendekatan adalah sebagai berikut:",
    first_line_indent=1.25,
)
model_rows = [
    ("Baseline: Sistem Pakar (Headline-Saja)", "41,5%", "0,415", "Ya"),
    ("Sistem Pakar Baru (Headline + Isi Berita + MYCIN CF)", "62,1%", "0,620", "Ya"),
    ("Logistic Regression", "59,8%", "0,582", "Tidak"),
    ("Random Forest (100 pohon)", "71,9%", "0,717", "Tidak"),
]
make_table(
    ["Model", "Akurasi", "Macro-F1", "Explainable"],
    model_rows,
    col_widths=[8, 2.5, 2.5, 3],
)
p(
    "Random Forest memperoleh akurasi tertinggi (71,9%), namun sebagai model black-box "
    "ia tidak dapat menjelaskan alasan di balik setiap keputusan secara eksplisit. "
    "Sistem pakar yang kami kembangkan memperoleh akurasi (62,1%) yang mendekati dan "
    "bahkan melampaui Logistic Regression (59,8%), sambil tetap mempertahankan sifat "
    "explainable melalui aturan IF-THEN bernomor, rujukan akademik, dan narasi bahasa "
    "alami — sebuah trade-off yang relevan untuk konteks akademik dan edukatif "
    "dibandingkan model pembelajaran mesin murni. Posisi ini berbeda dari temuan "
    "Laporan UTS, di mana sistem pakar justru tertinggal dari kedua model pembelajaran "
    "mesin baik dalam akurasi maupun macro-F1, menunjukkan bahwa inovasi verifikasi "
    "headline vs isi berita berkontribusi nyata dalam mempersempit kesenjangan "
    "performa terhadap model pembelajaran mesin.",
    first_line_indent=1.25,
)

heading("7.4 Studi Kasus Historis", level=2)
p(
    "Sebagai ilustrasi kualitatif, modul benchmark.py menyediakan empat studi kasus "
    "historis bergaya naratif yang menunjukkan bagaimana sistem bekerja pada skenario "
    "nyata: (1) saham BBCA pada April 2025, di mana judul berita panik dinetralkan oleh "
    "verifikasi isi berita yang menunjukkan fundamental stabil (aturan R09 aktif); (2) "
    "pemangkasan suku bunga BI pada September 2025 yang memicu aturan R01 (transmisi "
    "pelonggaran moneter); (3) saham BBRI pada Maret 2026, di mana judul optimistis "
    "tidak sejalan dengan risiko tersembunyi pada isi berita (aturan R10, divergensi); "
    "dan (4) saham TLKM pada Agustus 2026 yang menunjukkan rebound teknikal pada area "
    "oversold (aturan R11). Studi kasus ini digunakan sebagai contoh demonstrasi pada "
    "tab Evaluasi dashboard web dan dapat dimuat ulang langsung ke dalam mode Simulator.",
    first_line_indent=1.25,
)

page_break()

# ============================================================ 8. EVOLUSI
heading("8. Evolusi dari Laporan UTS ke Laporan Akhir", level=1)
p(
    "Untuk memperlihatkan kesinambungan pengerjaan proyek, tabel berikut merangkum "
    "perbedaan utama antara prototipe pada Laporan UTS dan sistem pada Laporan Akhir ini:",
    first_line_indent=1.25,
)
evo_rows = [
    ("Domain pasar", "Indeks BSE Sensex (India, ^BSESN)", "IHSG & 6 saham LQ45 (Indonesia)"),
    ("Sumber data berita", "Dataset statis Kaggle 2003-2020 (judul+ringkasan)", "Scraping RSS live multi-sumber + korpus evaluasi 2 tahun (judul+isi penuh)"),
    ("Kelas keputusan", "BUY / HOLD / SELL (3 kelas)", "BUY / SELL (2 kelas, biner tegas)"),
    ("Jumlah aturan produksi", "16 aturan", "14 aturan (lebih padat, tiap aturan bersitasi eksplisit)"),
    ("Analisis judul vs isi berita", "Tidak dibedakan (judul+ringkasan digabung)", "Dipisah & diverifikasi (clickbait/divergen/konsisten)"),
    ("Leksikon sentimen", "243 kata/frasa, satu bahasa (Indonesia, istilah India)", "±450 kata/frasa, bilingual (Indonesia + Inggris), 7 aspek FiGAS"),
    ("Antarmuka", "Notebook Jupyter + fungsi advise()", "Aplikasi web FastAPI 5-tab (live, simulator, flowchart, rules, evaluasi)"),
    ("Akurasi data uji", "0,465 (di bawah baseline selalu-HOLD 0,490)", "0,621 (melampaui baseline headline-saja 0,415 dan LogReg 0,598)"),
    ("Pengujian", "20 kasus manual (pra/pasca kalibrasi)", "14 kasus regresi + 10 unit test otomatis via pytest"),
]
make_table(["Aspek", "Laporan UTS", "Laporan Akhir"], evo_rows, col_widths=[3.5, 6, 6.5], font_size=9.5)
p(
    "Evolusi ini menegaskan bahwa inti metode sistem pakar — forward chaining dengan "
    "Certainty Factor MYCIN [5] di atas basis pengetahuan beraturan [6] — tetap "
    "dipertahankan sebagai metode inti sesuai arahan mata kuliah, sementara perbaikan "
    "difokuskan pada kualitas representasi pengetahuan sentimen (verifikasi headline vs "
    "isi berita [7] dan FiGAS [3]) serta relevansi domain data (pasar modal Indonesia).",
    first_line_indent=1.25,
)

# ============================================================ 9. KETERBATASAN
heading("9. Keterbatasan dan Saran Pengembangan", level=1)
p("Beberapa keterbatasan utama sistem pada laporan akhir ini adalah:", first_line_indent=1.25)
bullet("Dataset evaluasi dua tahun menggunakan artikel berita yang disusun dari korpus "
      "tertulis tangan (bukan artikel asli yang di-scrape secara historis), sehingga "
      "mensimulasikan skenario clickbait/divergensi secara terkendali namun belum "
      "sepenuhnya mencerminkan keragaman gaya penulisan berita nyata.")
bullet("Leksikon sentimen bilingual masih disusun secara manual dan belum divalidasi oleh "
      "anotator independen, sehingga berpotensi mengandung bias subjektif penyusun, "
      "sebagaimana juga menjadi catatan pada Laporan UTS.")
bullet("Nilai ambang MIN_CF (0,25) dan MIN_MARGIN (0,05) pada rules.py saat ini hanya "
      "ditampilkan sebagai metadata pada antarmuka dan belum diterapkan sebagai kondisi "
      "penggerbang (gating condition) yang sesungguhnya pada mesin inferensi.")
bullet("Sebagian data pada benchmark.py seperti frekuensi aktivasi aturan (RULE_FREQUENCY_TOP) "
      "bersifat ilustratif/kurasi manual dan bukan hasil komputasi langsung dari seluruh "
      "224 baris data evaluasi.")
bullet("Backtest belum memperhitungkan biaya transaksi, slippage, dan jam publikasi berita "
      "secara presisi, sehingga hasil evaluasi lebih tepat dibaca sebagai indikator "
      "kualitas klasifikasi sinyal, bukan proyeksi imbal hasil investasi riil.")
p("Beberapa arah pengembangan lanjutan yang disarankan:", first_line_indent=1.25)
bullet("Validasi leksikon sentimen oleh anotator independen atau penggunaan model bahasa "
      "terlatih (pretrained) sebagai pembanding, sejalan dengan arah penelitian Du et al. [7].")
bullet("Penerapan ambang MIN_CF/MIN_MARGIN sebagai mekanisme gating yang nyata, termasuk "
      "kemungkinan menghidupkan kembali kelas HOLD ketika keyakinan sistem rendah.")
bullet("Perluasan evaluasi historis menggunakan artikel berita riil yang di-scrape secara "
      "historis (bukan korpus sintetis) untuk memperkuat validitas eksternal hasil benchmark.")

# ============================================================ 10. KESIMPULAN
heading("10. Kesimpulan", level=1)
p(
    "Laporan akhir ini berhasil mengembangkan Laporan UTS menjadi prototipe sistem pakar "
    "yang lebih matang untuk merekomendasikan keputusan BUY atau SELL pada IHSG dan enam "
    "saham LQ45, dengan inovasi utama berupa verifikasi sentimen judul vs isi berita "
    "(headline-vs-body verification) yang terbukti meningkatkan akurasi dari 41,5% "
    "(headline-saja) menjadi 62,1% (headline + isi berita) pada evaluasi 224 hari bursa "
    "dan 560 artikel berita selama dua tahun (2024-2026). Basis pengetahuan 14 aturan "
    "produksi IF-THEN yang disusun berdasarkan delapan rujukan akademik [1]-[8], "
    "dikombinasikan dengan mesin inferensi forward chaining dan Certainty Factor MYCIN, "
    "terbukti mampu menghasilkan rekomendasi biner BUY/SELL yang dapat ditelusuri "
    "(explainable) sekaligus kompetitif dibandingkan model pembelajaran mesin Logistic "
    "Regression. Sistem ini tetap diposisikan sebagai prototipe akademik untuk "
    "mendemonstrasikan representasi pengetahuan dan proses inferensi sistem pakar, bukan "
    "sebagai alat rekomendasi investasi yang telah tervalidasi secara finansial.",
    first_line_indent=1.25,
)

page_break()

# ============================================================ DAFTAR PUSTAKA
heading("Daftar Pustaka", level=1)
refs = [
    "[1] L. Barbaglia, S. Consoli, and S. Manzan, \"Forecasting with Economic News,\" "
    "Journal of Business & Economic Statistics, vol. 41, no. 3, pp. 708-719, 2023, "
    "doi: 10.1080/07350015.2022.2060988.",
    "[2] A. Maghyereh and H. Abdoh, \"Can news-based economic sentiment predict bubbles "
    "in precious metal markets?,\" Financial Innovation, vol. 8, art. no. 35, 2022, "
    "doi: 10.1186/s40854-022-00341-w.",
    "[3] S. Consoli, L. Barbaglia, and S. Manzan, \"Fine-grained, aspect-based sentiment "
    "analysis on economic and financial lexicon,\" Knowledge-Based Systems, vol. 247, "
    "art. no. 108781, 2022, doi: 10.1016/j.knosys.2022.108781.",
    "[4] J. Bi, \"Stock Market Prediction Based on Financial News Text Mining and Investor "
    "Sentiment Recognition,\" Mathematical Problems in Engineering, vol. 2022, art. no. "
    "2427389, 2022.",
    "[5] A. Wildan and R. Sari, \"Metode Certainty Factor pada Sistem Pakar,\" Journal of "
    "Informatic and Information Security, vol. 3, no. 1, pp. 125-136, 2022.",
    "[6] A. K. Aprianto, I. Permadi, and B. Wijayanto, \"Expert System Using Forward "
    "Chaining Method,\" Jurnal Teknik Informatika (JUTIF), vol. 4, no. 4, 2023.",
    "[7] K. Du, F. Xing, R. Mao, and E. Cambria, \"Financial sentiment analysis: Techniques "
    "and applications,\" ACM Computing Surveys, vol. 56, no. 9, art. no. 220, 2024.",
    "[8] J. J. Murphy, Technical Analysis of the Financial Markets. New York: New York "
    "Institute of Finance, 1999.",
]
for r in refs:
    para = doc.add_paragraph()
    para.paragraph_format.space_after = Pt(8)
    para.paragraph_format.line_spacing = 1.3
    para.paragraph_format.left_indent = Cm(0.75)
    para.paragraph_format.first_line_indent = Cm(-0.75)
    run = para.add_run(r)
    set_font(run, size=12)

doc.save(r"c:\sistem-pakar-sp500\docs\Laporan_Akhir_UAS_Sistem_Pakar.docx")
print("OK - docx generated")
