from backend.app.services.scoring_service import score_module


def test_score_module_returns_float():
    assert isinstance(score_module({}), float)


