"use client";

import { useEffect, useRef, useState } from "react";

export default function SearchBar({
  value,
  onChange,
}: {
  value: string;
  onChange: (val: string) => void;
}) {
  const [local, setLocal] = useState(value);
  const timer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);

  useEffect(() => {
    setLocal(value);
  }, [value]);

  function handleChange(val: string) {
    setLocal(val);
    clearTimeout(timer.current);
    timer.current = setTimeout(() => onChange(val), 300);
  }

  return (
    <input
      className="input"
      type="search"
      placeholder="Search tenders..."
      value={local}
      onChange={(e) => handleChange(e.target.value)}
      style={{ fontSize: "1rem", padding: "10px 14px" }}
    />
  );
}
