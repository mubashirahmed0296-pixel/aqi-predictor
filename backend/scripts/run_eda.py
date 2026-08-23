from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from app.config import settings
from app.db import db


def main() -> None:
    docs = list(
        db[settings.feature_collection]
        .find({"city": settings.city}, {"_id": 0})
        .sort("timestamp", 1)
    )
    if not docs:
        raise RuntimeError("No feature data found for EDA.")

    df = pd.DataFrame(docs)
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    daily = (
        df.set_index("timestamp")
        .resample("D")
        .mean(numeric_only=True)
        .reset_index()
        .sort_values("timestamp")
    )

    out_dir = Path("artifacts/eda")
    out_dir.mkdir(parents=True, exist_ok=True)

    summary_file = out_dir / "summary_stats.csv"
    daily.describe().to_csv(summary_file)

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(daily["timestamp"], daily["aqi"], color="#0f766e", linewidth=2)
    ax.set_title(f"Daily AQI Trend - {settings.city}")
    ax.set_xlabel("Date")
    ax.set_ylabel("AQI")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    trend_file = out_dir / "daily_aqi_trend.png"
    fig.savefig(trend_file, dpi=140)
    plt.close(fig)

    corr = daily[["aqi", "pm2_5", "pm10", "co", "no2", "so2", "o3"]].corr()
    corr_file = out_dir / "correlations.csv"
    corr.to_csv(corr_file)

    print(f"Saved: {summary_file}")
    print(f"Saved: {trend_file}")
    print(f"Saved: {corr_file}")


if __name__ == "__main__":
    main()
