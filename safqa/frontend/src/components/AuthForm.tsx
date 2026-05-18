"use client";

import { useState, type FormEvent } from "react";

type Mode = "login" | "register";

export default function AuthForm({
  mode,
  onSubmit,
  error,
}: {
  mode: Mode;
  onSubmit: (email: string, password: string) => Promise<void>;
  error: string | null;
}) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    try {
      await onSubmit(email, password);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} style={formStyle}>
      <h1 style={{ fontSize: "1.5rem", marginBottom: "8px" }}>
        {mode === "login" ? "Sign In" : "Create Account"}
      </h1>
      <p style={{ fontSize: "0.9rem", color: "var(--color-text-secondary)", marginBottom: "24px" }}>
        {mode === "login" ? "Welcome back to Safqa" : "Register for a Safqa account"}
      </p>

      {error && (
        <div style={errorStyle}>{error}</div>
      )}

      <div>
        <label className="label" htmlFor="email">Email</label>
        <input
          id="email"
          className="input"
          type="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
      </div>

      <div>
        <label className="label" htmlFor="password">Password</label>
        <input
          id="password"
          className="input"
          type="password"
          required
          minLength={6}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
      </div>

      <button className="btn btn-primary" type="submit" disabled={submitting} style={{ width: "100%", padding: "10px" }}>
        {submitting ? "Please wait..." : mode === "login" ? "Sign In" : "Create Account"}
      </button>
    </form>
  );
}

const formStyle: React.CSSProperties = {
  maxWidth: "400px",
  margin: "60px auto",
  display: "flex",
  flexDirection: "column",
  gap: "16px",
  background: "var(--color-surface)",
  padding: "32px",
  borderRadius: "var(--radius)",
  boxShadow: "var(--shadow-lg)",
};

const errorStyle: React.CSSProperties = {
  background: "#fef2f2",
  color: "var(--color-danger)",
  padding: "10px 14px",
  borderRadius: "var(--radius)",
  fontSize: "0.85rem",
};
