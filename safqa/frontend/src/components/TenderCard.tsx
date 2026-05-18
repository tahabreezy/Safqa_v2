"use client";

import type { Tender } from "@/types/tender";
import Link from "next/link";

export default function TenderCard({ tender }: { tender: Tender }) {
  const domainLabel = tender.domain_label ?? tender.domain_code;
  const daysLeft = Math.ceil(
    (new Date(tender.deadline_at).getTime() - Date.now()) / (1000 * 60 * 60 * 24),
  );

  return (
    <Link href={`/tenders/${tender.id}`} style={{ textDecoration: "none" }}>
      <div className="card" style={cardStyle}>
        <div style={topStyle}>
          <span className={`badge ${tender.is_urgent ? "badge-urgent" : "badge-active"}`}>
            {tender.is_urgent ? "Urgent" : tender.status}
          </span>
          <span style={{ fontSize: "0.8rem", color: "var(--color-text-secondary)" }}>
            {daysLeft > 0 ? `${daysLeft}d left` : "Expired"}
          </span>
        </div>

        <h3 style={titleStyle}>{tender.title}</h3>

        <p style={authorityStyle}>{tender.authority}</p>

        <div style={metaStyle}>
          <span>{domainLabel}</span>
          {tender.city && <span>{tender.city}</span>}
          {tender.procedure_type && <span>{tender.procedure_type}</span>}
        </div>

        {tender.budget_mad != null && (
          <div style={budgetStyle}>
            {tender.budget_mad.toLocaleString("fr-FR", {
              style: "currency",
              currency: "MAD",
              maximumFractionDigits: 0,
            })}
          </div>
        )}

        <div style={refStyle}>Ref: {tender.reference_number}</div>
      </div>
    </Link>
  );
}

const cardStyle: React.CSSProperties = {
  display: "flex",
  flexDirection: "column",
  gap: "8px",
  height: "100%",
};

const topStyle: React.CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
};

const titleStyle: React.CSSProperties = {
  fontSize: "1rem",
  fontWeight: 600,
  color: "var(--color-text)",
  lineHeight: 1.3,
};

const authorityStyle: React.CSSProperties = {
  fontSize: "0.85rem",
  color: "var(--color-text-secondary)",
};

const metaStyle: React.CSSProperties = {
  display: "flex",
  flexWrap: "wrap",
  gap: "6px",
  fontSize: "0.8rem",
  color: "var(--color-text-secondary)",
};

const budgetStyle: React.CSSProperties = {
  fontSize: "0.9rem",
  fontWeight: 600,
  color: "var(--color-primary)",
};

const refStyle: React.CSSProperties = {
  fontSize: "0.75rem",
  color: "var(--color-text-secondary)",
};
