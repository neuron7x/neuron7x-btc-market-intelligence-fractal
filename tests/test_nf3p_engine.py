from btcmi import nf3p_engine


def test_variant2_basic_prediction():
    data = [1, 2, 3, 4, 5]
    model = nf3p_engine.Variant2()
    model.fit(data)
    pred = model.predict(data)
    assert pred in (-1.0, 1.0)
    size = model.size_positions(pred, capital=10.0)
    assert -10.0 <= size <= 10.0
    preds, pnl = model.backtest(data)
    assert len(preds) == len(data) - 1
    preds2, pnl2 = model.walk_forward(data, window=2)
    assert len(preds2) == len(data) - 2


def test_variant2_optional_features():
    data = [1, 2, 3, 4, 5, 6]
    model = nf3p_engine.Variant2(use_dfa=True, use_mfdfa=True, use_apen=True)
    model.fit(data)
    assert "dfa" in model.features_
    assert "mfdfa" in model.features_
    assert "apen" in model.features_

