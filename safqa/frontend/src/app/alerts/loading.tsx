import { CSSProperties } from "react";

const wrapperStyle: CSSProperties = {
  display: "flex",
  flexDirection: "column",
  gap: "12px",
  paddingTop: "24px",
};

const headerStyle: CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  marginBottom: "8px",
};

const titleStyle: CSSProperties = {
  height: "28px",
  width: "120px",
};

const buttonStyle: CSSProperties = {
  height: "36px",
  width: "100px",
};

const cardStyle: CSSProperties = {
  height: "100px",
};

export default function AlertsLoading() {
  return (
    <div className="container" style={wrapperStyle}>
      <div style={headerStyle}>
        <div className="skeleton" style={titleStyle} />
        <div className="skeleton" style={buttonStyle} />
      </div>
      {Array.from({ length: 3 }).map((_, i) => (
        <div key={i} className="skeleton" style={cardStyle} />
      ))}
    </div>
  );
}
