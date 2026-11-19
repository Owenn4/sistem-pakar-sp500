import pytest
from expert_system.nlp import headline_sentiment, analyze_article_headline_vs_body
from expert_system.fuzzification import make_facts, fuzzify
from expert_system.inference import infer
from expert_system.test_cases import run_test_cases, run_unit_tests
from expert_system.benchmark import load_2y_dataset
from expert_system.rules import RULES, ACADEMIC_REFERENCES


def test_nlp_unit_tests():
    unit_results = run_unit_tests()
    assert len(unit_results) == 10
    for res in unit_results:
        assert res["passed"] is True, f"Failed NLP unit test: {res['headline']} - {res['test_note']}"


def test_indonesian_regression_test_cases():
    test_results = run_test_cases()
    assert len(test_results) == 14
    for res in test_results:
        assert res["actual"] in ("BUY", "SELL"), "Keputusan wajib murni BUY atau SELL"
        assert res["passed"] is True, f"Failed TC {res['id']}: expected {res['expected']}, got {res['actual']} ({res['reason']})"


def test_headline_vs_body_clickbait_discount():
    res = analyze_article_headline_vs_body(
        headline="IHSG Kebakaran dan Ambruk Rontok di Sesi Pagi!",
        body="Meski judul terdengar panik, koreksi sebenarnya sangat tipis dan wajar, sedangkan laba perbankan tumbuh kuat dan asing mencatat net buy.",
        source="Detik Finance",
        scope="MACRO_IHSG",
    )
    assert res["verification_status"] == "CLICKBAIT_EXAGGERATED"
    assert res["headline_score"] < -0.3
    assert res["body_score"] > 0.0
    assert res["effective_score"] > res["headline_score"]


def test_all_rules_have_academic_references_and_human_reasons():
    assert len(ACADEMIC_REFERENCES) == 8
    for r in RULES:
        rid, name, cond, act, cf, ref, if_text, human_reason = r
        assert act in ("BUY", "SELL")
        assert 0.25 <= cf <= 0.90
        assert "[" in ref and "]" in ref, f"Rule {rid} must cite academic reference"
        assert len(human_reason) > 25, f"Rule {rid} must provide human reasoning"


def test_2y_dataset_accuracy_and_clickbait_improvement():
    data = load_2y_dataset()
    metrics = data["overall_metrics"]
    assert data["total_samples"] >= 200
    assert metrics["accuracy_full"] > 0.55
    assert metrics["accuracy_full"] > metrics["accuracy_headline_only"]
