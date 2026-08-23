from datetime import date, timedelta

from app.ingest import fetch_open_meteo_air_quality, upsert_features


def main(days: int = 90) -> None:
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    rows = fetch_open_meteo_air_quality(start_date.isoformat(), end_date.isoformat())
    summary = upsert_features(rows)
    print(summary)


if __name__ == "__main__":
    main()
