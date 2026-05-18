import { CSSProperties } from "react";

const wrapperStyle: CSSProperties = {
  display: "flex",
  flexDirection: "column",
  gap: "16px",
  paddingTop: "24px",
};

const barStyle: CSSProperties = {
  height: "40px",
  width: "100%",
};

const filterRowStyle: CSSProperties = {
  display: "flex",
  gap: "12px",
};

const filterStyle: CSSProperties = {
  height: "36px",
  flex: 1,
};

const gridStyle: CSSProperties = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))",
  gap: "16px",
  marginTop: "16px",
};

const cardStyle: CSSProperties = {
  height: "180px",
};

export default function Loading() {
  return (
    <div className="container" style={wrapperStyle}>
      <div className="skeleton" style={barStyle} />
      <div style={filterRowStyle}>
        <div className="skeleton" style={filterStyle} />
        <div className="skeleton" style={filterStyle} />
        <div className="skeleton" style={filterStyle} />
      </div>
      <div style={gridStyle}>
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="skeleton" style={cardStyle} />
        ))}
      </div>
    </div>
  );
}
