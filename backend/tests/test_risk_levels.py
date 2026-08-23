from app.utils import risk_level


def test_risk_levels() -> None:
    assert risk_level(30) == "Good"
    assert risk_level(90) == "Moderate"
    assert risk_level(140) == "Unhealthy for Sensitive Groups"
    assert risk_level(190) == "Unhealthy"
    assert risk_level(280) == "Very Unhealthy"
    assert risk_level(350) == "Hazardous"
