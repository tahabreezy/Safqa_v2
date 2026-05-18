"use client";

import { useState, type FormEvent } from "react";

export default function AlertForm({
  onSubmit,
  onCancel,
}: {
  onSubmit: (label: string, filters: Record<string, string>, email: string) => Promise<void>;
  onCancel: () => void;
}) {
  const [label, setLabel] = useState("");
  const [email, setEmail] = useState("");
  const [domainCode, setDomainCode] = useState("");
  const [city, setCity] = useState("");
  const [procedureType, setProcedureType] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!label.trim() || !email.trim()) return;
    setSubmitting(true);
    setError(null);
    try {
      const filters: Record<string, string> = {};
      if (domainCode) filters.domain_code = domainCode;
      if (city) filters.city = city;
      if (procedureType) filters.procedure_type = procedureType;
      await onSubmit(label, filters, email);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to create alert");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} style={formStyle}>
      <h3 style={{ marginBottom: "12px" }}>New Alert</h3>

      {error && <div style={errorStyle}>{error}</div>}

      <div>
        <label className="label">Label</label>
        <input className="input" required value={label} onChange={(e) => setLabel(e.target.value)} placeholder="My alert" />
      </div>

      <div>
        <label className="label">Email</label>
        <input className="input" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
      </div>

      <div>
        <label className="label">Domain code (optional)</label>
        <input className="input" value={domainCode} onChange={(e) => setDomainCode(e.target.value)} placeholder="e.g. 1.15" />
      </div>

      <div>
        <label className="label">City (optional)</label>
        <input className="input" value={city} onChange={(e) => setCity(e.target.value)} placeholder="e.g. Casablanca" />
      </div>

      <div>
        <label className="label">Procedure type (optional)</label>
        <input className="input" value={procedureType} onChange={(e) => setProcedureType(e.target.value)} placeholder="e.g. AO Ouvert" />
      </div>

      <div style={{ display: "flex", gap: "8px" }}>
        <button className="btn btn-primary" type="submit" disabled={submitting}>
          {submitting ? "Creating..." : "Create"}
        </button>
        <button className="btn btn-outline" type="button" onClick={onCancel}>
          Cancel
        </button>
      </div>
    </form>
  );
}

const formStyle: React.CSSProperties = {
  display: "flex",
  flexDirection: "column",
  gap: "12px",
  background: "var(--color-surface)",
  padding: "20px",
  borderRadius: "var(--radius)",
  border: "1px solid var(--color-border-light)",
  marginBottom: "16px",
};

const errorStyle: React.CSSProperties = {
  background: "#fef2f2",
  color: "var(--color-danger)",
  padding: "8px 12px",
  borderRadius: "var(--radius)",
  fontSize: "0.85rem",
};
