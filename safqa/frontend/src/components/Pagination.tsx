"use client";

export default function Pagination({
  page,
  totalPages,
  onChange,
}: {
  page: number;
  totalPages: number;
  onChange: (p: number) => void;
}) {
  if (totalPages <= 1) return null;

  const pages: (number | "...")[] = [];
  for (let i = 1; i <= totalPages; i++) {
    if (i === 1 || i === totalPages || (i >= page - 1 && i <= page + 1)) {
      pages.push(i);
    } else if (pages[pages.length - 1] !== "...") {
      pages.push("...");
    }
  }

  return (
    <div style={pagerStyle}>
      <button
        className="btn btn-outline btn-sm"
        disabled={page <= 1}
        onClick={() => onChange(page - 1)}
      >
        Prev
      </button>

      {pages.map((p, i) =>
        p === "..." ? (
          <span key={`e${i}`} style={{ padding: "0 4px", color: "var(--color-text-secondary)" }}>
            ...
          </span>
        ) : (
          <button
            key={p}
            className="btn btn-sm"
            style={{
              background: p === page ? "var(--color-primary)" : "transparent",
              color: p === page ? "#fff" : "var(--color-text)",
              border: p === page ? "none" : "1px solid var(--color-border)",
            }}
            onClick={() => onChange(p)}
          >
            {p}
          </button>
        ),
      )}

      <button
        className="btn btn-outline btn-sm"
        disabled={page >= totalPages}
        onClick={() => onChange(page + 1)}
      >
        Next
      </button>
    </div>
  );
}

const pagerStyle: React.CSSProperties = {
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  gap: "6px",
  marginTop: "24px",
};
