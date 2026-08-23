import pandas as pd


def create_time_series_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values("timestamp").copy()
    df["hour"] = df["timestamp"].dt.hour
    df["day"] = df["timestamp"].dt.day
    df["month"] = df["timestamp"].dt.month
    df["aqi_delta"] = df["aqi"].diff()

    for lag in [1, 2, 3]:
        df[f"aqi_lag_{lag}"] = df["aqi"].shift(lag)
        df[f"pm2_5_lag_{lag}"] = df["pm2_5"].shift(lag)
        df[f"pm10_lag_{lag}"] = df["pm10"].shift(lag)

    df["pm2_5_roll_3"] = df["pm2_5"].rolling(window=3).mean()
    df["pm10_roll_3"] = df["pm10"].rolling(window=3).mean()
    df["no2_roll_3"] = df["no2"].rolling(window=3).mean()
    df["o3_roll_3"] = df["o3"].rolling(window=3).mean()

    return df


def make_day_targets(df: pd.DataFrame) -> pd.DataFrame:
    # Forecast horizon at daily scale using hourly records.
    daily = (
        df.set_index("timestamp")
        .resample("D")
        .mean(numeric_only=True)
        .reset_index()
        .sort_values("timestamp")
    )
    daily["target_day_1"] = daily["aqi"].shift(-1)
    daily["target_day_2"] = daily["aqi"].shift(-2)
    daily["target_day_3"] = daily["aqi"].shift(-3)
    return daily.dropna()
