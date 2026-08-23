import { LiveDashboard } from "../components/LiveDashboard";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Dashboard — Pearls AQI",
  description: "Live 3-day AQI forecast for Islamabad. Compare ML models, inspect metrics, and monitor pipeline health.",
};

export default function DashboardPage() {
  return (
    <main className="page-shell">
      <div className="dashboard-shell">
        <LiveDashboard />
      </div>
    </main>
  );
}
