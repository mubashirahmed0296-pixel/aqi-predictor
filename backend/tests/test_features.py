import pandas as pd

from app.features import create_time_series_features


def test_feature_generation_adds_lags() -> None:
    df = pd.DataFrame(
        {
            "timestamp": pd.date_range("2026-01-01", periods=10, freq="h"),
            "aqi": range(10),
            "pm10": range(10),
            "pm2_5": range(10),
            "co": range(10),
            "no2": range(10),
            "so2": range(10),
            "o3": range(10),
        }
    )
    out = create_time_series_features(df)
    assert "aqi_lag_1" in out.columns
    assert "pm2_5_roll_3" in out.columns
