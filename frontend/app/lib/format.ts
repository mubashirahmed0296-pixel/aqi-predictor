import type { Horizon } from "./types";

export const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";
export const HORIZONS: Horizon[] = ["day_1", "day_2", "day_3"];

export function riskTone(risk: string): "good" | "warning" | "danger" {
  if (risk.includes("Hazardous") || risk.includes("Very")) return "danger";
  if (risk.includes("Unhealthy") || risk.includes("Moderate")) return "warning";
  return "good";
}

export function formatDate(value: string) {
  if (!value) return "Pending";
  return new Intl.DateTimeFormat("en", { month: "short", day: "numeric" }).format(new Date(value));
}

export function formatDateTime(value?: string) {
  if (!value) return "Not available";
  return new Intl.DateTimeFormat("en", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

export function horizonLabel(horizon: string) {
  return horizon.replace("day_", "Day +");
}

export function modelLabel(model: string) {
  if (!model || model === "--") return "--";
  if (model === "champion") return "Horizon champions";
  return model.replaceAll("_", " ");
}

export function formatNumber(value?: number, digits = 2) {
  if (value === undefined || Number.isNaN(value)) return "--";
  return value.toFixed(digits);
}

export function unique<T>(items: T[]) {
  return Array.from(new Set(items));
}

export function aqiPercent(aqi?: number) {
  if (!aqi) return 0;
  return Math.max(0, Math.min(100, (aqi / 300) * 100));
}
