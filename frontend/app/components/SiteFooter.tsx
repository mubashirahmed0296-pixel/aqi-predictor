import Link from "next/link";
import { API_BASE } from "../lib/format";

export function SiteFooter() {
  return (
    <footer className="site-footer">
      <div className="footer-brand">
        <p className="eyebrow">Air Quality Forecasting Platform</p>

        <h2>Pearls AQI Predictor</h2>

        <p>
          Developed by <strong>Mubashir Ahmed</strong> as a cloud-backed
          data science platform for AQI forecasting, automated pipelines,
          model evaluation, and deployed prediction services.
        </p>

        <span className="footer-signature">
          Islamabad Forecast Lab
        </span>
      </div>

      <div className="footer-links">
        <Link href="/dashboard">Live dashboard</Link>
        <Link href="/methodology">Methodology</Link>

        <a
          href={`${API_BASE}/health`}
          target="_blank"
          rel="noreferrer"
        >
          Backend health
        </a>
      </div>
    </footer>
  );
}