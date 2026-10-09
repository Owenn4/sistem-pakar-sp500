"""
Benchmark and model comparison metrics from historical evaluation on 2020-2024 test split.
Ground truth results from notebook Sistem_Pakar_V1.ipynb and UTS Report.
"""

MODEL_COMPARISON = [
    {
        "model": "Baseline: selalu HOLD",
        "accuracy": 0.399,
        "macro_f1": 0.190,
        "type": "Trivial Baseline",
        "explainable": False,
        "description": "Selalu memilih kelas mayoritas (HOLD)"
    },
    {
        "model": "Sistem Pakar (Rule-Based + MYCIN CF)",
        "accuracy": 0.397,
        "macro_f1": 0.276,
        "type": "Expert System (FiGAS + MYCIN)",
        "explainable": True,
        "description": "16 IF-THEN Rules + CF MYCIN. Transparan, penalaran dapat ditelusuri"
    },
    {
        "model": "Logistic Regression",
        "accuracy": 0.443,
        "macro_f1": 0.312,
        "type": "Machine Learning",
        "explainable": False,
        "description": "Standardized Linear Classifier pada 13 fitur teknikal & sentimen"
    },
    {
        "model": "Random Forest (300 trees)",
        "accuracy": 0.453,
        "macro_f1": 0.324,
        "type": "Machine Learning Ensemble",
        "explainable": False,
        "description": "Ensemble decision trees (black box, non-linear pattern learner)"
    }
]

SIGNAL_PRECISION = [
    {
        "signal": "BUY",
        "count": 104,
        "precision": 0.4038,
        "base_rate": 0.3295,
        "lift": "+22.5%",
        "avg_next_return": "+0.21%",
        "interpretation": "Ketika sistem menyarankan BUY (kontrarian), tingkat kebenaran (40.4%) secara signifikan mengungguli peluang dasar pasar (33.0%)."
    },
    {
        "signal": "SELL",
        "count": 59,
        "precision": 0.2542,
        "base_rate": 0.2715,
        "lift": "-6.4%",
        "avg_next_return": "-0.12%",
        "interpretation": "Sinyal SELL lebih jarang aktif dan konservatif, dengan rata-rata pergerakan harga negatif (-0.12%)."
    }
]

BACKTEST_METRICS = {
    "expert_system_cumulative_return": "+27.1%",
    "buy_and_hold_return": "+56.1%",
    "active_trading_days": "163 dari 1035 hari uji (15.7%)",
    "note": "Sistem pakar bersifat sangat defensif (84.3% hari berada di posisi HOLD/kas), sehingga risiko drawdown jauh lebih rendah meskipun return lebih kecil dari Buy & Hold selama bull run pasca COVID."
}

RULE_FREQUENCY_TOP = [
    {"rule_id": "R01", "name": "Pasar tenang", "action": "HOLD", "activations": 284},
    {"rule_id": "R12", "name": "Netral & datar", "action": "HOLD", "activations": 196},
    {"rule_id": "R14", "name": "Tren naik stabil", "action": "HOLD", "activations": 142},
    {"rule_id": "R04", "name": "Kontrarian oversold", "action": "BUY", "activations": 74},
    {"rule_id": "R06", "name": "Volatilitas tinggi + turun", "action": "BUY", "activations": 52},
    {"rule_id": "R13", "name": "Sentimen sangat negatif", "action": "BUY", "activations": 48},
    {"rule_id": "R07", "name": "Resesi ganda", "action": "SELL", "activations": 38},
    {"rule_id": "R09", "name": "Inflasi + suku bunga naik", "action": "SELL", "activations": 32},
    {"rule_id": "R08", "name": "Pelonggaran moneter", "action": "BUY", "activations": 29},
    {"rule_id": "R11", "name": "Tenaga kerja negatif", "action": "SELL", "activations": 24},
    {"rule_id": "R15", "name": "Optimis + tren naik", "action": "HOLD", "activations": 22},
    {"rule_id": "R02", "name": "Euforia + jenuh beli", "action": "SELL", "activations": 15},
    {"rule_id": "R03", "name": "Pesimis + tren turun", "action": "SELL", "activations": 14},
    {"rule_id": "R05", "name": "Panik mereda", "action": "BUY", "activations": 11},
    {"rule_id": "R10", "name": "Ekonomi & manufaktur +", "action": "BUY", "activations": 9},
    {"rule_id": "R16", "name": "Berita sedikit", "action": "HOLD", "activations": 7}
]

HISTORICAL_EVENTS = [
    {
        "date": "2008-10-07",
        "title": "Lehman Brothers & Subprime Mortgage Crisis",
        "sp500_price": 996.23,
        "actual_next_return": "+0.71%",
        "actual_label": "BUY",
        "headlines": [
            "U.S. Stocks Fall Sharply For Fifth Day; S&P 500 At Five-year Low"
        ],
        "trend": -0.08,
        "volatility": 0.024,
        "prev_sentiment": -0.05,
        "expected_action": "BUY",
        "summary": "Keputusan kontrarian: Sentimen bearish ekstrem di tengah pasar oversold dan volatilitas tinggi memicu aturan R04 & R06."
    },
    {
        "date": "2020-03-16",
        "title": "COVID-19 Panic Capitulation",
        "sp500_price": 2386.13,
        "actual_next_return": "+6.00%",
        "actual_label": "BUY",
        "headlines": [
            "S&P 500 Plunged Most Since 1987, Gave Up in 18 Days the 42% Gains of Past 3 Years. Boeing Shares Collapsed",
            "Can Mastercard Stock Recover Its Lost Value Post The Coronavirus Crisis?",
            "Is Walmart A Safer Bet During The Current Coronavirus Turmoil?",
            "The U.S. Is In A Bear Market. There Could Be A Recession. But This Is Not 2008."
        ],
        "trend": -0.12,
        "volatility": 0.038,
        "prev_sentiment": -0.10,
        "expected_action": "BUY",
        "summary": "Aturan R04, R06, dan R13 aktif bersamaan menghasilkan CF 0.86 (Sangat Kuat). Pasar rebound +6.00% pada perdagangan berikutnya."
    },
    {
        "date": "2022-06-13",
        "title": "Inflasi Tinggi & Suku Bunga Agresif The Fed",
        "sp500_price": 3749.63,
        "actual_next_return": "-0.38%",
        "actual_label": "HOLD",
        "headlines": [
            "Wharton professor Jeremy Siegel is one of the best stock watchers alive. He says the S&P 500 is already pricing in a recession",
            "Stocks Enter Bear Market, a Grim Signal of Economic Fears",
            "Stock Market Today: Dow, S&P Live Updates for June 13, 2022",
            "Wall Street enters a bear market as the S&P 500 dives"
        ],
        "trend": -0.065,
        "volatility": 0.016,
        "prev_sentiment": -0.04,
        "expected_action": "HOLD",
        "summary": "Sinyal bertentangan: Sinyal BUY kontrarian (CF 0.74) berbenturan dengan sinyal SELL resesi & inflasi (CF 0.73). Conflict resolution memilih HOLD."
    },
    {
        "date": "2023-11-14",
        "title": "Cooling Inflation & AI Rally Anticipation",
        "sp500_price": 4495.78,
        "actual_next_return": "+0.16%",
        "actual_label": "HOLD",
        "headlines": [
            "Fed signals rate cut as inflation cools",
            "Wall Street rallies on strong jobs report",
            "Tech stocks surge as cooling CPI boosts market optimism"
        ],
        "trend": 0.025,
        "volatility": 0.008,
        "prev_sentiment": 0.04,
        "expected_action": "HOLD",
        "summary": "Tren naik stabil dan sentimen positif mengaktifkan R14 & R15 (tidak mengejar momentum saat harga sudah naik), merekomendasikan HOLD secara disiplin."
    }
]
