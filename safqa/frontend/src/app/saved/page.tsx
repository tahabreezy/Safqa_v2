"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import TenderCard from "@/components/TenderCard";
import Pagination from "@/components/Pagination";

export default function SavedPage() {
  const { user, loading } = useAuth();
  const router = useRouter();
  const qc = useQueryClient();
  const [page, setPage] = useState(1);

  useEffect(() => {
    if (!loading && !user) router.push("/login");
  }, [user, loading, router]);

  const { data, isLoading } = useQuery({
    queryKey: ["saved", page],
    queryFn: () => api.getSaved(page),
    enabled: !!user,
  });

  const unsave = useMutation({
    mutationFn: (id: string) => api.unsaveTender(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["saved"] }),
  });

  if (loading) return <div className="spinner" />;
  if (!user) return null;

  return (
    <div>
      <h1 style={{ fontSize: "1.4rem", marginBottom: "20px" }}>Saved Tenders</h1>

      {isLoading && <div className="spinner" />}

      {data && (
        <>
          <div style={gridStyle}>
            {data.data.map((tender) => (
              <div key={tender.id} style={{ position: "relative" }}>
                <TenderCard tender={tender} />
                <button
                  className="btn btn-danger btn-sm"
                  style={{ position: "absolute", top: "8px", right: "8px" }}
                  onClick={() => unsave.mutate(tender.id)}
                  disabled={unsave.isPending}
                >
                  Unsave
                </button>
              </div>
            ))}
          </div>

          {data.data.length === 0 && (
            <div className="empty-state">
              <h2>No saved tenders</h2>
              <p>Save tenders from the search page to see them here</p>
            </div>
          )}

          <Pagination page={page} totalPages={Math.max(1, Math.ceil(data.total / 20))} onChange={setPage} />
        </>
      )}
    </div>
  );
}

const gridStyle: React.CSSProperties = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))",
  gap: "16px",
};
