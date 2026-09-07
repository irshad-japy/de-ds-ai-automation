from ml.common import FEATURES


def test_no_obvious_post_outcome_leakage_features():
    forbidden_tokens = ["actual_delivery", "delay_minutes", "refund", "complaint", "delivered_at"]
    joined = " ".join(FEATURES).lower()
    assert not any(token in joined for token in forbidden_tokens)
    assert len(FEATURES) == 8
