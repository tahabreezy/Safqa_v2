"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { SearchParams } from "@/types/tender";

const PROCEDURE_TYPES = [
  "AO Ouvert",
  "AO Restreint",
  "Consultation",
  "Appel d'Offres",
  "MARCHE DE REGIE",
  "Concours",
];

const SORT_OPTIONS = [
  { value: "deadline_asc", label: "Deadline (asc)" },
  { value: "deadline_desc", label: "Deadline (desc)" },
  { value: "budget_desc", label: "Budget (desc)" },
  { value: "budget_asc", label: "Budget (asc)" },
  { value: "published_desc", label: "Most recent" },
];

export default function FilterPanel({
  params,
  onChange,
}: {
  params: SearchParams;
  onChange: (p: SearchParams) => void;
}) {
  const { data: domains = [] } = useQuery({
    queryKey: ["domains"],
    queryFn: () => api.getDomains(),
  });

  function set(k: keyof SearchParams, v: string | undefined) {
    onChange({ ...params, [k]: v || undefined, page: 1 });
  }

  return (
    <div style={panelStyle}>
      <div style={rowStyle}>
        <div>
          <label className="label">Domain</label>
          <select
            className="select"
            value={params.domain ?? ""}
            onChange={(e) => set("domain", e.target.value)}
          >
            <option value="">All domains</option>
            {domains.map((d) => (
              <option key={d.domain_code} value={d.domain_code}>
                {d.domain_label} ({d.count})
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="label">City</label>
          <input
            className="input"
            placeholder="Any city"
            value={params.city ?? ""}
            onChange={(e) => set("city", e.target.value)}
          />
        </div>

        <div>
          <label className="label">Type</label>
          <select
            className="select"
            value={params.type ?? ""}
            onChange={(e) => set("type", e.target.value)}
          >
            <option value="">All types</option>
            {PROCEDURE_TYPES.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="label">Sort</label>
          <select
            className="select"
            value={params.sort ?? ""}
            onChange={(e) => set("sort", e.target.value)}
          >
            <option value="">Default</option>
            {SORT_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
}

const panelStyle: React.CSSProperties = {
  background: "var(--color-surface)",
  border: "1px solid var(--color-border-light)",
  borderRadius: "var(--radius)",
  padding: "16px",
  marginBottom: "16px",
};

const rowStyle: React.CSSProperties = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))",
  gap: "12px",
};
