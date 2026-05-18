import { CSSProperties } from "react";

const wrapperStyle: CSSProperties = {
  display: "flex",
  flexDirection: "column",
  gap: "16px",
  paddingTop: "24px",
};

const titleStyle: CSSProperties = {
  height: "28px",
  width: "180px",
};

const gridStyle: CSSProperties = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))",
  gap: "16px",
};

const cardStyle: CSSProperties = {
  height: "180px",
};

export default function SavedLoading() {
  return (
    <div className="container" style={wrapperStyle}>
      <div className="skeleton" style={titleStyle} />
      <div style={gridStyle}>
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="skeleton" style={cardStyle} />
        ))}
      </div>
    </div>
  );
}
