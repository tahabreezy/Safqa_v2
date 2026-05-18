import { CSSProperties } from "react";

const wrapperStyle: CSSProperties = {
  display: "flex",
  flexDirection: "column",
  gap: "16px",
  paddingTop: "24px",
};

const backStyle: CSSProperties = {
  height: "32px",
  width: "80px",
};

const cardStyle: CSSProperties = {
  height: "320px",
  padding: "24px",
};

const rowStyle: CSSProperties = {
  display: "flex",
  justifyContent: "space-between",
  marginBottom: "24px",
};

const titleBlock: CSSProperties = {
  display: "flex",
  flexDirection: "column",
  gap: "8px",
};

const titleLineStyle: CSSProperties = {
  height: "20px",
  width: "300px",
};

const subtitleLineStyle: CSSProperties = {
  height: "16px",
  width: "200px",
};

const badgeStyle: CSSProperties = {
  height: "24px",
  width: "80px",
};

const gridStyle: CSSProperties = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))",
  gap: "16px",
};

const fieldStyle: CSSProperties = {
  height: "40px",
};

const buttonRowStyle: CSSProperties = {
  display: "flex",
  gap: "10px",
  marginTop: "20px",
};

const btnStyle: CSSProperties = {
  height: "36px",
  width: "100px",
};

export default function TenderDetailLoading() {
  return (
    <div className="container" style={wrapperStyle}>
      <div className="skeleton" style={backStyle} />
      <div className="card" style={cardStyle}>
        <div style={rowStyle}>
          <div style={titleBlock}>
            <div className="skeleton" style={titleLineStyle} />
            <div className="skeleton" style={subtitleLineStyle} />
          </div>
          <div className="skeleton" style={badgeStyle} />
        </div>
        <div style={gridStyle}>
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="skeleton" style={fieldStyle} />
          ))}
        </div>
        <div style={buttonRowStyle}>
          <div className="skeleton" style={btnStyle} />
          <div className="skeleton" style={btnStyle} />
        </div>
      </div>
    </div>
  );
}
