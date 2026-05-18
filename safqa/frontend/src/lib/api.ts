import type { Alert, DomainResponse, SearchResponse, StatsResponse, Tender, TokenResponse, User } from "@/types/tender";

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost/v1";

let accessToken: string | null = null;

export function setAccessToken(token: string | null) {
  accessToken = token;
}

export function getAccessToken(): string | null {
  return accessToken;
}

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (accessToken) {
    headers["Authorization"] = `Bearer ${accessToken}`;
  }

  let res = await fetch(`${BASE}${path}`, { ...options, headers });

  if (res.status === 401 && accessToken) {
    const refreshed = await tryRefresh();
    if (refreshed) {
      headers["Authorization"] = `Bearer ${accessToken}`;
      res = await fetch(`${BASE}${path}`, { ...options, headers });
    }
  }

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.message ?? `Request failed: ${res.status}`);
  }

  if (res.status === 204) return undefined as T;
  return res.json();
}

async function tryRefresh(): Promise<boolean> {
  try {
    const res = await fetch("/api/auth/refresh", { method: "POST" });
    if (!res.ok) return false;
    const data: TokenResponse = await res.json();
    accessToken = data.access_token;
    return true;
  } catch {
    return false;
  }
}

export const api = {
  // Auth
  register: (email: string, password: string) =>
    request<TokenResponse>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  login: (email: string, password: string) =>
    request<TokenResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  refresh: () => request<TokenResponse>("/auth/refresh", { method: "POST" }),

  getMe: () => request<User>("/auth/me"),

  // Tenders
  searchTenders: (params: {
    q?: string;
    domain?: string;
    city?: string;
    type?: string;
    status?: string;
    sort?: string;
    page?: number;
    limit?: number;
  }) => {
    const sp = new URLSearchParams();
    for (const [k, v] of Object.entries(params)) {
      if (v !== undefined && v !== "" && v !== null) sp.set(k, String(v));
    }
    return request<SearchResponse>(`/tenders?${sp.toString()}`);
  },

  getTender: (id: string) => request<Tender>(`/tenders/${id}`),

  getTenderByRef: (ref: string) => request<Tender>(`/tenders/ref/${ref}`),

  getStats: () => request<StatsResponse>("/tenders/stats"),

  getDomains: () => request<DomainResponse[]>("/tenders/domains"),

  // Saved
  getSaved: (page = 1, limit = 20) =>
    request<{ data: Tender[]; page: number; limit: number; total: number }>(
      `/saved?page=${page}&limit=${limit}`,
    ),

  saveTender: (tenderId: string) =>
    request<{ status: string }>(`/saved/${tenderId}`, { method: "POST" }),

  unsaveTender: (tenderId: string) =>
    request<{ status: string }>(`/saved/${tenderId}`, { method: "DELETE" }),

  // Alerts
  getAlerts: () => request<Alert[]>("/alerts"),

  createAlert: (data: { label: string; filters: Record<string, string>; email: string }) =>
    request<Alert>("/alerts", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  toggleAlert: (id: string, isActive: boolean) =>
    request<Alert>(`/alerts/${id}`, {
      method: "PATCH",
      body: JSON.stringify({ is_active: isActive }),
    }),

  deleteAlert: (id: string) =>
    request<{ status: string }>(`/alerts/${id}`, { method: "DELETE" }),
};
