RULES = [
    (
        'R01',
        'Pasar tenang',
        lambda F: F['vol'] == 'low',
        'HOLD',
        0.55,
        'Volatility clustering: pasar tenang → pergerakan kecil (data latih ±67% HOLD)',
        "IF volatilitas = low"
    ),
    (
        'R02',
        'Euforia + jenuh beli',
        lambda F: F['sent'] == 'very_pos' and F['trend'] == 'overextended',
        'SELL',
        0.30,
        'Risiko bubble saat sentimen ekstrem (Maghyereh & Abdoh, 2022)',
        "IF sentimen = very_pos AND tren = overextended"
    ),
    (
        'R03',
        'Pesimis + tren turun',
        lambda F: F['sent'] in ('neg', 'very_neg') and F['delta'] == 'deteriorating' and F['trend'] == 'down',
        'SELL',
        0.35,
        'Sentimen memburuk sejalan dengan tren turun',
        "IF sentimen ∈ {neg, very_neg} AND delta = deteriorating AND tren = down"
    ),
    (
        'R04',
        'Kontrarian oversold',
        lambda F: F['sent'] in ('neg', 'very_neg') and F['trend'] == 'oversold',
        'BUY',
        0.60,
        'Sentimen bearish ekstrem + harga jatuh dalam → peluang rebound (Maghyereh & Abdoh, 2022)',
        "IF sentimen ∈ {neg, very_neg} AND tren = oversold"
    ),
    (
        'R05',
        'Panik mereda',
        lambda F: F['fear'] == 'high' and F['delta'] == 'improving',
        'BUY',
        0.40,
        'Kata krisis/crash banyak namun sentimen mulai membaik',
        "IF fear = high AND delta = improving"
    ),
    (
        'R06',
        'Volatilitas tinggi + turun',
        lambda F: F['vol'] == 'high' and F['trend'] in ('down', 'oversold'),
        'BUY',
        0.45,
        'Capitulation / mean reversion jangka pendek (data latih ±50% BUY)',
        "IF volatilitas = high AND tren ∈ {down, oversold}"
    ),
    (
        'R07',
        'Resesi ganda',
        lambda F: F['econ'] == 'neg' and F['fin'] == 'neg',
        'SELL',
        0.55,
        'Sentimen ekonomi & sektor keuangan sama-sama negatif (Barbaglia et al., 2022)',
        "IF aspek ekonomi = neg AND aspek keuangan = neg"
    ),
    (
        'R08',
        'Pelonggaran moneter',
        lambda F: F['mon'] == 'pos' and F['trend'] != 'overextended',
        'BUY',
        0.40,
        'Kebijakan longgar mendorong aset berisiko (Maghyereh & Abdoh, 2022)',
        "IF aspek moneter = pos AND tren ≠ overextended"
    ),
    (
        'R09',
        'Inflasi + suku bunga naik',
        lambda F: F['infl'] == 'neg' and F['mon'] == 'neg',
        'SELL',
        0.40,
        'Tekanan inflasi & pengetatan moneter',
        "IF aspek inflasi = neg AND aspek moneter = neg"
    ),
    (
        'R10',
        'Ekonomi & manufaktur +',
        lambda F: F['econ'] == 'pos' and F['manuf'] == 'pos',
        'BUY',
        0.45,
        'Sinyal ekspansi sektor riil (Barbaglia et al., 2022)',
        "IF aspek ekonomi = pos AND aspek manufaktur = pos"
    ),
    (
        'R11',
        'Tenaga kerja negatif',
        lambda F: F['unemp'] == 'neg' and F['sent'] in ('neg', 'very_neg', 'neutral'),
        'SELL',
        0.55,
        'PHK/pengangguran naik → indikasi pelemahan ekonomi',
        "IF aspek pengangguran = neg AND sentimen ∈ {neg, very_neg, neutral}"
    ),
    (
        'R12',
        'Netral & datar',
        lambda F: F['sent'] == 'neutral' and F['trend'] == 'flat',
        'HOLD',
        0.45,
        'Tidak ada sinyal kuat',
        "IF sentimen = neutral AND tren = flat"
    ),
    (
        'R13',
        'Sentimen sangat negatif',
        lambda F: F['sent'] == 'very_neg',
        'BUY',
        0.35,
        'Kontrarian: pesimisme ekstrem sering diikuti pemulihan',
        "IF sentimen = very_neg"
    ),
    (
        'R14',
        'Tren naik stabil',
        lambda F: F['trend'] == 'up' and F['vol'] != 'high',
        'HOLD',
        0.50,
        'Tren naik berjalan pelan (data latih ±67% HOLD)',
        "IF tren = up AND volatilitas ≠ high"
    ),
    (
        'R15',
        'Optimis + tren naik',
        lambda F: F['sent'] in ('pos', 'very_pos') and F['trend'] in ('up', 'overextended'),
        'HOLD',
        0.45,
        'Tidak ada keunggulan mengejar momentum (data latih ±64% HOLD)',
        "IF sentimen ∈ {pos, very_pos} AND tren ∈ {up, overextended}"
    ),
    (
        'R16',
        'Berita sedikit',
        lambda F: F['volume'] == 'low' and F['sent'] == 'neutral',
        'HOLD',
        0.25,
        'Informasi tidak memadai',
        "IF volume berita = low AND sentimen = neutral"
    ),
]

MIN_CF = 0.30
MIN_MARGIN = 0.15
