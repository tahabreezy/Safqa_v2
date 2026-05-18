import { Suspense } from "react";
import SearchPage from "./SearchPage";

export default function HomePage() {
  return (
    <Suspense fallback={<div className="spinner" />}>
      <SearchPage />
    </Suspense>
  );
}
