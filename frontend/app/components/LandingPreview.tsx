"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import type { PredictResponse } from "../lib/types";
import { fetchJson } from "../lib/api";
import { formatDate, modelLabel, riskTone } from "../lib/format";
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip } from "recharts";

export function LandingPreview() {
  const [forecast, setForecast] = useState<PredictResponse | null>(null);
  const [status, setStatus] = useState("Loading live forecast from the deployed API...");
  const [isCached, setIsCached] = useState(false);

  useEffect(() => {
    // 1. Try to load cached data from localStorage
    const cached = localStorage.getItem("cached_forecast");
    if (cached) {
      try {
        const parsed = JSON.parse(cached);
        setForecast(parsed);
        setStatus("Restored from offline cache. Syncing fresh forecast...");
        setIsCached(true);
      } catch (e) {
        console.error("Failed to parse cached forecast", e);
      }
    }

    let active = true;
    fetchJson<PredictResponse>("/predict")
      .then((payload) => {
        if (active) {
          setForecast(payload);
          setStatus("Live forecast synced from MongoDB Atlas and Render API");
          setIsCached(false);
          localStorage.setItem("cached_forecast", JSON.stringify(payload));
        }
      })
      .catch((error) => {
        if (active) {
          if (cached) {
            setStatus("Offline cache active. Prediction service is waking up...");
          } else {
            // Load realistic fallback/simulated data so we never have empty dashes
            const fallback: PredictResponse = {
              city: "Islamabad",
              generated_at: new Date().toISOString(),
              model: { day_1: "ridge", day_2: "random_forest", day_3: "random_forest" },
              predictions: [
                { date: new Date(Date.now() + 86400000).toISOString(), aqi: 87.9, risk: "Moderate" },
                { date: new Date(Date.now() + 86400000 * 2).toISOString(), aqi: 86.4, risk: "Moderate" },
                { date: new Date(Date.now() + 86400000 * 3).toISOString(), aqi: 100.5, risk: "Unhealthy for Sensitive Groups" }
              ],
              available_models: ["ridge", "random_forest", "gradient_boosting", "mlp"],
              selection_mode: "waking_fallback"
            };
            setForecast(fallback);
            setStatus("Live connection waking. Displaying simulated forecast...");
          }
        }
      });

    return () => {
      active = false;
    };
  }, []);

  const chartData = (forecast?.predictions || []).map((item, index) => ({
    ...item,
    label: `Day +${index + 1}`,
    displayDate: item.date ? formatDate(item.date) : `Day +${index + 1}`
  }));

  const isWaking = !forecast || forecast.selection_mode === "waking_fallback";

  return (
    <div className="landing-preview-card">
      <div className="preview-header">
        <div>
          <p className="eyebrow">Live preview</p>
          <h2>3-day Islamabad AQI forecast</h2>
        </div>
        <span className={`status-chip ${isWaking ? "warning" : "good"}`}>
          {isWaking ? (isCached ? "Cached" : "Waking") : "Online"}
        </span>
      </div>
      <p className="muted-copy">{status}</p>
      
      <div className="mini-forecast-grid">
        {(forecast?.predictions || [1, 2, 3].map((day) => ({ date: "", aqi: 0, risk: `Day ${day}` }))).map((item, index) => (
          <article key={`${item.date}-${index}`} className="mini-forecast-card">
            <span className={`pill ${riskTone(item.risk)}`}>{item.risk}</span>
            <strong>{item.aqi ? item.aqi.toFixed(0) : "--"}</strong>
            <p>{item.date ? formatDate(item.date) : `Day +${index + 1}`}</p>
            <small>{modelLabel(forecast?.model?.[`day_${index + 1}`] || "--")}</small>
          </article>
        ))}
      </div>

      {/* Real Visual Graph Preview */}
      {chartData.length > 0 && (
        <div className="mini-chart-container" style={{ marginTop: "20px", marginBottom: "20px", height: "130px", width: "100%" }}>
          <p className="eyebrow" style={{ fontSize: "0.68rem", marginBottom: "8px" }}>72-Hour Prediction Trend</p>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData} margin={{ top: 4, right: 6, left: -28, bottom: 0 }}>
              <defs>
                <linearGradient id="previewAqiTrend" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#0f766e" stopOpacity={0.24} />
                  <stop offset="95%" stopColor="#0f766e" stopOpacity={0.01} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#e1e8f0" />
              <XAxis dataKey="label" stroke="#8da2bb" style={{ fontSize: "0.68rem", fontWeight: 700 }} />
              <YAxis stroke="#8da2bb" style={{ fontSize: "0.68rem", fontWeight: 700 }} width={32} />
              <Tooltip formatter={(value: number) => [Number(value).toFixed(0), "AQI"]} />
              <Area type="monotone" dataKey="aqi" stroke="#0f766e" strokeWidth={3} fill="url(#previewAqiTrend)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}

      <Link className="text-link" href="/dashboard">Open full analytics dashboard</Link>
    </div>
  );
}

