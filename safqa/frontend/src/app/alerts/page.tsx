"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import AlertCard from "@/components/AlertCard";
import AlertForm from "@/components/AlertForm";
import type { Alert } from "@/types/tender";

export default function AlertsPage() {
  const { user, loading } = useAuth();
  const router = useRouter();
  const qc = useQueryClient();
  const [showForm, setShowForm] = useState(false);

  useEffect(() => {
    if (!loading && !user) router.push("/login");
  }, [user, loading, router]);

  const { data: alerts = [], isLoading } = useQuery({
    queryKey: ["alerts"],
    queryFn: () => api.getAlerts(),
    enabled: !!user,
  });

  const createAlert = useMutation({
    mutationFn: (data: { label: string; filters: Record<string, string>; email: string }) =>
      api.createAlert(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["alerts"] });
      setShowForm(false);
    },
  });

  const toggleAlert = useMutation({
    mutationFn: ({ id, isActive }: { id: string; isActive: boolean }) =>
      api.toggleAlert(id, isActive),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["alerts"] }),
  });

  const deleteAlert = useMutation({
    mutationFn: (id: string) => api.deleteAlert(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["alerts"] }),
  });

  if (loading) return <div className="spinner" />;
  if (!user) return null;

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
        <h1 style={{ fontSize: "1.4rem" }}>Alerts</h1>
        <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
          {showForm ? "Cancel" : "New Alert"}
        </button>
      </div>

      {showForm && (
        <AlertForm
          onSubmit={async (label, filters, email) => {
            await createAlert.mutateAsync({ label, filters, email });
          }}
          onCancel={() => setShowForm(false)}
        />
      )}

      {isLoading && <div className="spinner" />}

      {!isLoading && alerts.length === 0 && (
        <div className="empty-state">
          <h2>No alerts</h2>
          <p>Create an alert to get notified about new tenders</p>
        </div>
      )}

      <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
        {alerts.map((alert: Alert) => (
          <AlertCard
            key={alert.id}
            alert={alert}
            onToggle={() => toggleAlert.mutate({ id: alert.id, isActive: !alert.is_active })}
            onDelete={() => deleteAlert.mutate(alert.id)}
          />
        ))}
      </div>
    </div>
  );
}
