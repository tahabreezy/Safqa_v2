"use client";

import { useQuery } from "@tanstack/react-query";
import { useRouter, useSearchParams } from "next/navigation";
import { useCallback } from "react";
import { api } from "@/lib/api";
import SearchBar from "@/components/SearchBar";
import FilterPanel from "@/components/FilterPanel";
import TenderCard from "@/components/TenderCard";
import Pagination from "@/components/Pagination";
import type { SearchParams } from "@/types/tender";

export default function SearchPage() {
  const router = useRouter();
  const sp = useSearchParams();

  const params: SearchParams = {
    q: sp.get("q") || undefined,
    domain: sp.get("domain") || undefined,
    city: sp.get("city") || undefined,
    type: sp.get("type") || undefined,
    status: sp.get("status") || undefined,
    sort: sp.get("sort") || undefined,
    page: Number(sp.get("page")) || 1,
    limit: 20,
  };

  const { data, isLoading } = useQuery({
    queryKey: ["search", params],
    queryFn: () => api.searchTenders(params),
  });

  const updateParams = useCallback(
    (next: SearchParams) => {
      const qs = new URLSearchParams();
      for (const [k, v] of Object.entries(next)) {
        if (v !== undefined && v !== "" && v !== null) qs.set(k, String(v));
      }
      router.push(`?${qs.toString()}`, { scroll: false });
    },
    [router],
  );

  return (
    <div>
      <SearchBar value={params.q ?? ""} onChange={(q) => updateParams({ ...params, q, page: 1 })} />

      <div style={{ marginTop: "16px" }}>
        <FilterPanel params={params} onChange={updateParams} />
      </div>

      {isLoading && <div className="spinner" />}

      {data && (
        <>
          <p style={{ fontSize: "0.85rem", color: "var(--color-text-secondary)", marginBottom: "12px" }}>
            {data.total} tender{data.total !== 1 ? "s" : ""} found
          </p>

          <div style={gridStyle}>
            {data.data.map((tender) => (
              <TenderCard key={tender.id} tender={tender} />
            ))}
          </div>

          {data.data.length === 0 && (
            <div className="empty-state">
              <h2>No tenders found</h2>
              <p>Try adjusting your search or filters</p>
            </div>
          )}

          <Pagination
            page={data.page}
            totalPages={data.total_pages}
            onChange={(p) => updateParams({ ...params, page: p })}
          />
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
