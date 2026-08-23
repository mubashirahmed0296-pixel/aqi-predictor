from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .db import db, ensure_indexes
from .github_status import latest_workflow_runs
from .predict import latest_model_catalog, predict_next_3_days
from .quality import run_data_quality_audit


app = FastAPI(title=settings.project_name)
allowed_origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=settings.cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    ensure_indexes()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "city": settings.city}


@app.get("/pipeline/health")
def pipeline_health() -> dict:
    runs = list(db[settings.pipeline_runs_collection].find({}, {"_id": 0}).sort("run_at", -1).limit(10))
    return {"recent_runs": runs, "github_actions": latest_workflow_runs()}


@app.get("/metrics/latest")
def latest_metrics() -> dict:
    doc = db[settings.metrics_collection].find_one(sort=[("evaluated_at", -1)], projection={"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="No metrics found.")
    return doc


@app.get("/models/latest")
def models_latest() -> dict:
    try:
        return latest_model_catalog()
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex)) from ex


@app.get("/predict")
def predict(model: str | None = None) -> dict:
    try:
        return predict_next_3_days(model_name=model)
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex)) from ex


@app.get("/quality/latest")
def quality_latest() -> dict:
    doc = db["quality_audits"].find_one(sort=[("audited_at", -1)], projection={"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="No quality audit found.")
    return doc


@app.post("/quality/run")
def quality_run() -> dict:
    try:
        return run_data_quality_audit()
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex)) from ex
