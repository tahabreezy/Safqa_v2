"use client";

import { QueryClientProvider } from "@tanstack/react-query";
import { Inter } from "next/font/google";
import { queryClient } from "@/lib/query-client";
import { AuthProvider } from "@/lib/auth-context";
import Navbar from "@/components/Navbar";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr" className={inter.className}>
      <body>
        <QueryClientProvider client={queryClient}>
          <AuthProvider>
            <Navbar />
            <main className="container" style={{ paddingTop: "24px", paddingBottom: "48px" }}>
              {children}
            </main>
          </AuthProvider>
        </QueryClientProvider>
      </body>
    </html>
  );
}
