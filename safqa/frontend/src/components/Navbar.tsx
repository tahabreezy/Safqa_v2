"use client";

import Link from "next/link";
import { useAuth } from "@/lib/auth-context";

export default function Navbar() {
  const { user, loading, logout } = useAuth();

  return (
    <nav style={navStyle}>
      <div className="container" style={innerStyle}>
        <Link href="/" style={logoStyle}>
          Safqa
        </Link>

        <div style={linksStyle}>
          <Link href="/" style={linkStyle}>
            Search
          </Link>
          {user ? (
            <>
              <Link href="/saved" style={linkStyle}>
                Saved
              </Link>
              <Link href="/alerts" style={linkStyle}>
                Alerts
              </Link>
              <span style={{ fontSize: "0.85rem", color: "#9ca3af" }}>
                {user.email}
              </span>
              <button onClick={logout} className="btn btn-outline btn-sm">
                Logout
              </button>
            </>
          ) : (
            <>
              <Link href="/login" style={linkStyle}>
                Login
              </Link>
              <Link
                href="/register"
                className="btn btn-primary btn-sm"
                style={{ color: "#fff" }}
              >
                Register
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}

const navStyle: React.CSSProperties = {
  background: "#fff",
  borderBottom: "1px solid var(--color-border-light)",
  padding: "12px 0",
  position: "sticky",
  top: 0,
  zIndex: 100,
};

const innerStyle: React.CSSProperties = {
  display: "flex",
  alignItems: "center",
  justifyContent: "space-between",
};

const logoStyle: React.CSSProperties = {
  fontSize: "1.3rem",
  fontWeight: 700,
  color: "var(--color-primary)",
  textDecoration: "none",
};

const linksStyle: React.CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: "16px",
};

const linkStyle: React.CSSProperties = {
  fontSize: "0.9rem",
  color: "var(--color-text)",
  textDecoration: "none",
};
