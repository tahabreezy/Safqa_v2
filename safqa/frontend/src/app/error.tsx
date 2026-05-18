"use client";

import { useEffect } from "react";

const wrapperStyle: React.CSSProperties = {
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  justifyContent: "center",
  minHeight: "60vh",
  textAlign: "center",
};

const titleStyle: React.CSSProperties = {
  fontSize: "1.5rem",
  fontWeight: 600,
  marginBottom: "8px",
};

const messageStyle: React.CSSProperties = {
  color: "var(--color-text-secondary)",
  marginBottom: "24px",
  maxWidth: "400px",
};

export default function ErrorPage({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("Page error:", error);
  }, [error]);

  return (
    <div className="container" style={wrapperStyle}>
      <h1 style={titleStyle}>Une erreur est survenue</h1>
      <p style={messageStyle}>
        Quelque chose s&apos;est mal passé. Veuillez réessayer ou revenir à
        l&apos;accueil.
      </p>
      <div style={{ display: "flex", gap: "12px" }}>
        <button className="btn btn-primary" onClick={reset}>
          Réessayer
        </button>
        <a href="/" className="btn btn-outline">
          Accueil
        </a>
      </div>
    </div>
  );
}
