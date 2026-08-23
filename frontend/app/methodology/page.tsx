const pipelineSteps = [
  {
    title: "1. Hourly feature pipeline",
    body: "GitHub Actions runs the feature workflow every hour. It fetches Islamabad weather and pollutant data, builds lag/rolling/time features, deduplicates records, and writes them into MongoDB Atlas.",
  },
  {
    title: "2. Daily training pipeline",
    body: "The training workflow runs daily with a backup trigger. It reads historical features from the cloud feature store, trains multiple models, evaluates them with time-aware validation, and stores metrics for every horizon.",
  },
  {
    title: "3. Champion selection",
    body: "Models compete separately for Day +1, Day +2, and Day +3. The dashboard also exposes an overall ranking so users can understand both horizon-level and global performance.",
  },
  {
    title: "4. Prediction service",
    body: "FastAPI reads the latest registry artifact from MongoDB GridFS and serves predictions to the frontend. Users can use the champion setup or force one model for comparison.",
  },
];

const featureFamilies = [
  "Pollutants: PM10, PM2.5, CO, NO2, SO2, O3",
  "Time features: day and month",
  "Trend features: AQI delta and AQI lags",
  "Rolling features: short-window pollutant means",
  "Quality checks: duplicates, nulls, out-of-range AQI, leakage hints",
];

export default function MethodologyPage() {
  return (
    <main className="page-shell content-page">
      <section className="split-hero methodology-hero">
        <div>
          <p className="eyebrow">Methodology</p>
          <h1>How the AQI system thinks, trains, and stays alive.</h1>
          <p>
            This page documents the system's architecture, data pipeline operations, and methodologies. 
            It explains the full machine-learning workflow in a clean, transparent format.
          </p>
        </div>
        <aside className="method-summary-card">
          <span className="status-chip good">Automated</span>
          <h2>Current schedule</h2>
          <p><strong>Feature pipeline:</strong> hourly with a primary trigger at minute 17 and a backup trigger at minute 47.</p>
          <p><strong>Training pipeline:</strong> daily at 00:37 UTC with a 01:07 UTC backup, plus a catch-up check after feature runs.</p>
        </aside>
      </section>

      <section className="timeline-section">
        <div className="section-kicker centered">
          <p className="eyebrow">Workflow</p>
          <h2>The project flow from raw data to dashboard.</h2>
        </div>
        <div className="process-rail">
          {pipelineSteps.map((step) => (
            <article className="process-step" key={step.title}>
              <h3>{step.title}</h3>
              <p>{step.body}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="method-grid">
        <article className="method-card wide-method-card">
          <p className="eyebrow">Model strategy</p>
          <h2>Multiple models, no hardcoded winner.</h2>
          <p>
            The training code experiments with Ridge Regression, Random Forest, Gradient Boosting, and an MLP neural network.
            Each model is scored with RMSE, MAE, and R2. The registry stores the metrics, the trained artifact,
            the horizon champions, and the overall leaderboard.
          </p>
        </article>
        <article className="method-card">
          <p className="eyebrow">Validation</p>
          <h2>Time-aware split</h2>
          <p>
            The pipeline avoids random shuffling for evaluation, because AQI is a time-series problem. Newer records are held out
            for testing so the metrics represent future forecasting behavior more honestly.
          </p>
        </article>
        <article className="method-card">
          <p className="eyebrow">Safety</p>
          <h2>System Integrity</h2>
          <p>
            The frontend shows useful registry evidence and hides raw artifact IDs by default, keeping the public experience readable
            while the database still stores full technical proof.
          </p>
        </article>
      </section>

      <section className="feature-family-section">
        <div>
          <p className="eyebrow">Feature engineering</p>
          <h2>Signals the model uses.</h2>
          <p>
            The feature set combines pollutant concentration, temporal context, historical AQI memory, and rolling pollution behavior.
          </p>
        </div>
        <div className="feature-family-list">
          {featureFamilies.map((feature) => <span key={feature}>{feature}</span>)}
        </div>
      </section>
    </main>
  );
}
