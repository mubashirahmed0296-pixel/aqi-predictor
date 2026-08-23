import type { Metadata } from "next";
import "./globals.css";
import { SiteHeader } from "./components/SiteHeader";
import { SiteFooter } from "./components/SiteFooter";

export const metadata: Metadata = {
  title: "Pearls AQI Predictor | Islamabad Forecast Lab",
  description:
    "An advanced air quality forecasting platform for Islamabad. 3-day AQI predictions powered by automated machine learning pipelines, a cloud feature store, and a model registry.",
  keywords: ["AQI", "air quality", "Islamabad", "forecast", "machine learning", "Pearls AQI"],
  authors: [{ name: "Salman Khan", url: "https://github.com/s4lmankhan" }],
  openGraph: {
    title: "Pearls AQI Predictor | Islamabad Forecast Lab",
    description: "Real-time 3-day AQI forecasting for Islamabad powered by automated ML pipelines.",
    type: "website",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="ambient-layer" aria-hidden="true" />
        <SiteHeader />
        {children}
        <SiteFooter />
      </body>
    </html>
  );
}
