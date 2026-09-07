from ml.generate_data import build_dataset
from ml.common import FEATURES, TARGET


def test_generate_data_is_deterministic_and_valid():
    a = build_dataset(200, 42)
    b = build_dataset(200, 42)
    assert a.equals(b)
    assert all(c in a.columns for c in FEATURES + [TARGET])
    assert set(a[TARGET].unique()).issubset({0, 1})
    assert a["historical_delay_rate"].between(0, 1).all()
