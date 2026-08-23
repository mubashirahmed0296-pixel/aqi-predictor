import Link from "next/link";
import { LandingPreview } from "./components/LandingPreview";
import { API_BASE } from "./lib/format";

const proofCards = [
  { value: "Hourly", label: "Feature Ingestion", detail: "Automated collection of weather and pollutant data." },
  { value: "Daily", label: "Model Training", detail: "Daily retraining pipeline to find the most accurate models." },
  { value: "3 Days", label: "Forecast Horizon", detail: "Serving Day +1, Day +2, and Day +3 AQI forecasts." },
  { value: "Cloud", label: "Secure Storage", detail: "MongoDB Atlas stores features, metrics, and registered models." },
];

const architectureCards = [
  {
    title: "Feature Store",
    text: "Clean hourly weather and pollutant features are validated and stored securely in MongoDB Atlas.",
    metrics: ["17 Parameters", "Hourly Ingestion", "Quality Audited"],
    details: "Deduplication & boundary checks run 24/7."
  },
  {
    title: "Model Registry",
    text: "Ridge, Random Forest, Gradient Boosting, and MLP models compete daily. The best performers are registered.",
    metrics: ["Ridge, RF, GBDT, MLP", "GridFS Versioning", "Temporal Validation"],
    details: "Models validated with honest forward-chaining split."
  },
  {
    title: "Prediction API",
    text: "A robust FastAPI backend retrieves the latest registered model artifact and returns 72-hour predictions.",
    metrics: ["GET /predict", "Latency < 85ms", "FastAPI + CORS"],
    details: "Serves live coefficients and predicted values instantly."
  },
  {
    title: "Visual Analytics",
    text: "A modern analytics interface turns complex model outputs into decision-ready predictions.",
    metrics: ["Recharts Area", "SWR Caching", "Symmetry Layout"],
    details: "Interactive 72-hour trend and model ranking telemetry."
  },
];

export default function HomePage() {
  return (
    <main className="page-shell landing-page">
      {/* Hero Section */}
      <section className="landing-hero">
        <div className="hero-panel reveal-card">
          <div className="hero-badge-row">
            <span className="status-chip good">Islamabad Live System</span>
            <span className="status-chip neutral">Production Ready</span>
          </div>
          <p className="eyebrow">Pearls AQI Predictor</p>
          <h1>Air quality forecasting, explained like an intelligent control room.</h1>
          <p className="hero-lede">
            An advanced air quality forecasting platform for Islamabad that combines automated feature ingestion,
            daily model retraining, and a cloud model registry to deliver live, 3-day AQI predictions.
          </p>
          <div className="hero-actions">
            <Link href="/dashboard">Explore dashboard</Link>
            <a href={`${API_BASE}/predict`} target="_blank" rel="noreferrer">Open backend API</a>
          </div>
        </div>

        <div className="hero-visual reveal-card delay-1" aria-label="AQI system visual">
          <div className="orbital-system">
            <span className="orbit orbit-one" />
            <span className="orbit orbit-two" />
            <span className="orbit orbit-three" />
            <div className="core-node">
              <strong>AQI</strong>
              <small>72h</small>
            </div>
            <div className="floating-chip chip-a">PM2.5</div>
            <div className="floating-chip chip-b">NO2</div>
            <div className="floating-chip chip-c">Models</div>
          </div>
        </div>
      </section>

      {/* Product Ribbon */}
      <section className="product-ribbon">
        <span>Live AQI Intelligence</span>
        <span>Automated Training</span>
        <span>Cloud Model Registry</span>
        <span>Production-Ready ML Pipeline</span>
      </section>

      {/* Proof Strip */}
      <section className="proof-strip">
        {proofCards.map((card, index) => (
          <article className="proof-card reveal-card" style={{ animationDelay: `${index * 90}ms` }} key={card.label}>
            <strong>{card.value}</strong>
            <span>{card.label}</span>
            <p>{card.detail}</p>
          </article>
        ))}
      </section>

      {/* Split Section / Preview */}
      <section className="split-section">
        <div className="section-kicker">
          <p className="eyebrow">Real-Time Forecast</p>
          <h2>A fully operational machine learning product.</h2>
          <p>
            Observe the entire pipeline: fresh data enters the cloud store, models train and update automatically,
            predictions are served via an API, and the dashboard presents the results with model explanation.
          </p>
          
          {/* Live Pipeline Analytics Grid */}
          <div className="mini-metrics-panel">
            <div className="metric-box">
              <small>Feature store</small>
              <strong>17 Active</strong>
              <span>Seasonality, lags &amp; trends</span>
            </div>
            <div className="metric-box">
              <small>Serving speed</small>
              <strong>&lt; 85ms</strong>
              <span>FastAPI response time</span>
            </div>
            <div className="metric-box">
              <small>Pipeline audits</small>
              <strong>100% Passed</strong>
              <span>Zero duplicates or nulls</span>
            </div>
            <div className="metric-box">
              <small>Scikit Models</small>
              <strong>4 Evaluated</strong>
              <span>Ridge, RF, GBDT, MLP</span>
            </div>
          </div>

          {/* Telemetry status bar to balance column height and fill empty space */}
          <div className="metric-box telemetry-status-panel" style={{
            marginTop: "14px",
            background: "rgba(255, 255, 255, 0.4)",
            border: "1px solid rgba(15, 118, 110, 0.12)",
            display: "flex",
            flexDirection: "column",
            gap: "12px",
            padding: "16px 20px"
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span className="eyebrow" style={{ fontSize: "0.68rem", margin: 0 }}>Active Pipeline Telemetry</span>
              <span className="status-chip good" style={{ minHeight: "22px", fontSize: "0.68rem", padding: "2px 8px" }}>Operational</span>
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px 16px", fontSize: "0.78rem", fontWeight: 700, color: "var(--ink-strong)" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                <span className="status-dot good" style={{ width: "8px", height: "8px", boxShadow: "none" }} />
                <span>Ingestion: <span style={{ color: "var(--muted)", fontWeight: 500 }}>Hourly Sync</span></span>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                <span className="status-dot good" style={{ width: "8px", height: "8px", boxShadow: "none" }} />
                <span>Retraining: <span style={{ color: "var(--muted)", fontWeight: 500 }}>Daily Cron</span></span>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                <span className="status-dot good" style={{ width: "8px", height: "8px", boxShadow: "none" }} />
                <span>Database: <span style={{ color: "var(--muted)", fontWeight: 500 }}>GridFS Storage</span></span>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                <span className="status-dot good" style={{ width: "8px", height: "8px", boxShadow: "none" }} />
                <span>API Gateway: <span style={{ color: "var(--muted)", fontWeight: 500 }}>FastAPI Host</span></span>
              </div>
            </div>
          </div>
        </div>
        <LandingPreview />
      </section>

      {/* System Map / Architecture */}
      <section className="architecture-section">
        <div className="section-kicker centered">
          <p className="eyebrow">System Map</p>
          <h2>Four integrated layers powering the platform.</h2>
        </div>
        <div className="story-grid">
          {architectureCards.map((card, index) => (
            <article className="story-card reveal-card" style={{ animationDelay: `${index * 80}ms` }} key={card.title}>
              <span className="story-number">0{index + 1}</span>
              <h3>{card.title}</h3>
              <p>{card.text}</p>
              <div className="card-sub-metrics" style={{ marginTop: "16px", display: "flex", flexWrap: "wrap", gap: "6px" }}>
                {card.metrics.map(metric => (
                  <span key={metric} style={{
                    fontSize: "0.72rem",
                    fontWeight: 800,
                    padding: "4px 8px",
                    background: "rgba(15, 118, 110, 0.08)",
                    color: "var(--teal)",
                    borderRadius: "999px"
                  }}>
                    {metric}
                  </span>
                ))}
              </div>
              <p style={{ margin: "12px 0 0 0", fontSize: "0.78rem", fontWeight: 700, color: "var(--muted)" }}>
                {card.details}
              </p>
            </article>
          ))}
        </div>
      </section>

      {/* Call to Action */}
      <section className="cta-band">
        <div>
          <p className="eyebrow">Ready for review</p>
          <h2>View live predictions, compare models, and inspect pipeline evidence.</h2>
        </div>
        <Link href="/dashboard">Launch the live dashboard</Link>
      </section>
    </main>
  );
}
