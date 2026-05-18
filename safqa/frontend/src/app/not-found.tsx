"use client";

import Link from "next/link";

const wrapperStyle: React.CSSProperties = {
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  justifyContent: "center",
  minHeight: "60vh",
  textAlign: "center",
};

const codeStyle: React.CSSProperties = {
  fontSize: "6rem",
  fontWeight: 700,
  color: "var(--color-primary)",
  lineHeight: 1,
  marginBottom: "8px",
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

export default function NotFound() {
  return (
    <div className="container" style={wrapperStyle}>
      <div style={codeStyle}>404</div>
      <h1 style={titleStyle}>Page introuvable</h1>
      <p style={messageStyle}>
        La page que vous recherchez n&apos;existe pas ou a été déplacée.
      </p>
      <Link href="/" className="btn btn-primary">
        Retour à l&apos;accueil
      </Link>
    </div>
  );
}
