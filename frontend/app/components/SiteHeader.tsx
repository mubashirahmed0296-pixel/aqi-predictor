import Link from "next/link";

const navItems = [
  { href: "/", label: "Home" },
  { href: "/dashboard", label: "Dashboard" },
  { href: "/methodology", label: "Methodology" },
];

export function SiteHeader() {
  return (
    <header className="site-header">
      <Link
        className="brand-mark"
        href="/"
        aria-label="Pearls AQI Predictor home"
      >
        <span className="brand-symbol">AQ</span>

        <span className="brand-copy">
          <strong>Pearls AQI</strong>
          <small>Islamabad Forecast Lab</small>
        </span>
      </Link>

      <nav className="site-nav" aria-label="Primary navigation">
        {navItems.map((item) => (
          <Link href={item.href} key={item.href}>
            {item.label}
          </Link>
        ))}
      </nav>

      <Link className="header-cta" href="/dashboard">
        Launch dashboard
      </Link>
    </header>
  );
}