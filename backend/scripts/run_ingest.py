from datetime import date

from app.ingest import fetch_open_meteo_air_quality, upsert_features


def main() -> None:
    today = date.today().isoformat()
    rows = fetch_open_meteo_air_quality(today, today)
    summary = upsert_features(rows)
    print(summary)


if __name__ == "__main__":
    main()
