"use client";

import type { Alert } from "@/types/tender";

export default function AlertCard({
  alert,
  onToggle,
  onDelete,
}: {
  alert: Alert;
  onToggle: () => void;
  onDelete: () => void;
}) {
  const filterEntries = Object.entries(alert.filters);

  return (
    <div className="card" style={cardStyle}>
      <div style={topStyle}>
        <strong>{alert.label}</strong>
        <span className={`badge ${alert.is_active ? "badge-active" : "badge-expired"}`}>
          {alert.is_active ? "Active" : "Paused"}
        </span>
      </div>

      <div style={{ fontSize: "0.85rem", color: "var(--color-text-secondary)" }}>
        {alert.email}
      </div>

      {filterEntries.length > 0 && (
        <div style={filterStyle}>
          {filterEntries.map(([k, v]) => (
            <span key={k} className="badge" style={{ background: "var(--color-bg)" }}>
              {k}: {v}
            </span>
          ))}
        </div>
      )}

      <div style={actionStyle}>
        <button className="btn btn-outline btn-sm" onClick={onToggle}>
          {alert.is_active ? "Pause" : "Activate"}
        </button>
        <button className="btn btn-danger btn-sm" onClick={onDelete}>
          Delete
        </button>
      </div>
    </div>
  );
}

const cardStyle: React.CSSProperties = {
  display: "flex",
  flexDirection: "column",
  gap: "8px",
};

const topStyle: React.CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
};

const filterStyle: React.CSSProperties = {
  display: "flex",
  flexWrap: "wrap",
  gap: "4px",
};

const actionStyle: React.CSSProperties = {
  display: "flex",
  gap: "8px",
  marginTop: "4px",
};
