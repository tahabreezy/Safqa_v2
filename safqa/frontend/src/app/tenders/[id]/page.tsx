"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { api } from "@/lib/api";
import { use } from "react";

export default function TenderDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const { user } = useAuth();
  const router = useRouter();
  const qc = useQueryClient();

  const { data: tender, isLoading } = useQuery({
    queryKey: ["tender", id],
    queryFn: () => api.getTender(id),
  });

  const saveMutation = useMutation({
    mutationFn: () => api.saveTender(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["saved"] }),
  });

  const unsaveMutation = useMutation({
    mutationFn: () => api.unsaveTender(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["saved"] }),
  });

  if (isLoading) return <div className="spinner" />;
  if (!tender) return <div className="empty-state"><h2>Tender not found</h2></div>;

  const daysLeft = Math.ceil(
    (new Date(tender.deadline_at).getTime() - Date.now()) / (1000 * 60 * 60 * 24),
  );

  return (
    <div>
      <button className="btn btn-outline btn-sm" onClick={() => router.back()} style={{ marginBottom: "16px" }}>
        &larr; Back
      </button>

      <div className="card">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "16px" }}>
          <div>
            <h1 style={{ fontSize: "1.4rem", lineHeight: 1.3 }}>{tender.title}</h1>
            <p style={{ color: "var(--color-text-secondary)", marginTop: "4px" }}>{tender.authority}</p>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: "6px", alignItems: "flex-end" }}>
            <span className={`badge ${tender.is_urgent ? "badge-urgent" : tender.status === "active" ? "badge-active" : "badge-expired"}`}>
              {tender.is_urgent ? "URGENT" : tender.status}
            </span>
            {tender.is_urgent && (
              <span style={{ fontSize: "0.85rem", color: "var(--color-danger)", fontWeight: 600 }}>
                {daysLeft} day{daysLeft !== 1 ? "s" : ""} remaining
              </span>
            )}
          </div>
        </div>

        <div style={gridStyle}>
          <div>
            <span className="label">Reference</span>
            <p>{tender.reference_number}</p>
          </div>
          <div>
            <span className="label">Domain</span>
            <p>{tender.domain_label ?? tender.domain_code}</p>
          </div>
          {tender.city && (
            <div>
              <span className="label">City</span>
              <p>{tender.city}</p>
            </div>
          )}
          {tender.procedure_type && (
            <div>
              <span className="label">Procedure Type</span>
              <p>{tender.procedure_type}</p>
            </div>
          )}
          <div>
            <span className="label">Published</span>
            <p>{new Date(tender.published_at).toLocaleDateString("fr-FR")}</p>
          </div>
          <div>
            <span className="label">Deadline</span>
            <p style={{ color: tender.is_urgent ? "var(--color-danger)" : undefined, fontWeight: tender.is_urgent ? 600 : undefined }}>
              {new Date(tender.deadline_at).toLocaleDateString("fr-FR")}
            </p>
          </div>
          {tender.budget_mad != null && (
            <div>
              <span className="label">Budget</span>
              <p style={{ fontWeight: 600 }}>
                {tender.budget_mad.toLocaleString("fr-FR", { style: "currency", currency: "MAD", maximumFractionDigits: 0 })}
              </p>
            </div>
          )}
        </div>

        <div style={{ marginTop: "20px", display: "flex", gap: "10px" }}>
          {user && (
            <button
              className="btn btn-outline"
              onClick={() => {
                if (saveMutation.isIdle) saveMutation.mutate();
                else unsaveMutation.mutate();
              }}
              disabled={saveMutation.isPending || unsaveMutation.isPending}
            >
              {saveMutation.isIdle ? "Save" : "Unsave"}
            </button>
          )}
          {tender.source_url && (
            <a href={tender.source_url} target="_blank" rel="noopener noreferrer" className="btn btn-primary">
              View Original
            </a>
          )}
        </div>
      </div>
    </div>
  );
}

const gridStyle: React.CSSProperties = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))",
  gap: "16px",
};
