export type Tender = {
  id: string;
  reference_number: string;
  title: string;
  authority: string;
  city: string | null;
  domain_code: string;
  domain_label: string | null;
  procedure_type: string | null;
  budget_raw: string | null;
  budget_mad: number | null;
  published_at: string;
  deadline_at: string;
  source_url: string | null;
  status: string;
  scraped_at: string | null;
  created_at: string | null;
  is_urgent: boolean;
};

export type SearchParams = {
  q?: string;
  domain?: string;
  city?: string;
  type?: string;
  status?: string;
  sort?: string;
  page?: number;
  limit?: number;
};

export type SearchResponse = {
  data: Tender[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
};

export type StatsResponse = {
  active: number;
  urgent: number;
  new_this_week: number;
  total: number;
};

export type DomainResponse = {
  domain_code: string;
  domain_label: string;
  count: number;
};

export type TokenResponse = {
  access_token: string;
  token_type: string;
};

export type Alert = {
  id: string;
  user_id: string;
  label: string;
  filters: Record<string, string>;
  email: string;
  is_active: boolean;
  created_at: string;
};

export type User = {
  id: string;
  email: string;
  created_at: string;
};
