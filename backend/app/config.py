from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        protected_namespaces=("settings_",),
    )

    project_name: str = "Pearls AQI Predictor"
    city: str = "Islamabad"
    latitude: float = 33.6844
    longitude: float = 73.0479
    timezone: str = "Asia/Karachi"
    api_provider: str = "open-meteo"

    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "aqi_predictor"

    model_storage_dir: str = "./artifacts/models"
    feature_collection: str = "features_v1"
    pipeline_runs_collection: str = "pipeline_runs"
    metrics_collection: str = "model_metrics"
    registry_collection: str = "model_registry"
    predictions_collection: str = "predictions"

    github_repo: str = ""
    github_token: str = ""
    github_branch: str = "main"
    cors_origins: str = (
        "http://localhost:3000,http://127.0.0.1:3000,"
        "http://localhost:3001,http://127.0.0.1:3001"
    )
    cors_origin_regex: str = (
        r"https://.*\.vercel\.app|"
        r"http://localhost:\d+|"
        r"http://127\.0\.0\.1:\d+"
    )


settings = Settings()
