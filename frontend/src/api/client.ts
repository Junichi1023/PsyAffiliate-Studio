export const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export type Platform = "threads" | "instagram" | "both";
export type Tone = "empathy" | "practical" | "story" | "educational" | "soft_sales";
export type DraftStatus = "draft" | "needs_review" | "approved" | "scheduled" | "posted" | "failed";
export type AffiliateIntent = "none" | "soft" | "moderate";

export interface KnowledgeItem {
  id: number;
  title: string;
  category: string;
  content: string;
  source?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
}

export type KnowledgePayload = Omit<KnowledgeItem, "id" | "created_at" | "updated_at">;

export interface AffiliateProduct {
  id: number;
  name: string;
  asp_name?: string | null;
  affiliate_url: string;
  display_url?: string | null;
  category?: string | null;
  target_pain?: string | null;
  commission_type?: string | null;
  commission_amount?: number | null;
  prohibited_claims?: string | null;
  priority: number;
  is_active: boolean;
  created_at?: string | null;
  updated_at?: string | null;
}

export type AffiliateProductPayload = Omit<AffiliateProduct, "id" | "created_at" | "updated_at">;

export interface PersonaPain {
  id: number;
  name: string;
  category: string;
  pain_summary: string;
  emotional_state?: string | null;
  desired_future?: string | null;
  forbidden_approach?: string | null;
  recommended_tone?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
}

export type PersonaPainPayload = Omit<PersonaPain, "id" | "created_at" | "updated_at">;

export interface FortuneTemplate {
  id: number;
  name: string;
  fortune_type: string;
  target_pain_category?: string | null;
  structure: string;
  example_output?: string | null;
  prohibited_patterns?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
}

export type FortuneTemplatePayload = Omit<FortuneTemplate, "id" | "created_at" | "updated_at">;

export interface GenerateContentRequest {
  theme: string;
  target_reader: string;
  platform: Platform;
  tone: Tone;
  selected_product_id?: number | null;
  fortune_type?: string | null;
  persona_pain_id?: number | null;
  fortune_template_id?: number | null;
  affiliate_intent?: AffiliateIntent;
}

export interface GeneratedContent {
  platform: Platform;
  theme: string;
  body: string;
  caption?: string | null;
  cta: string;
  pr_disclosure: string;
  affiliate_product_id?: number | null;
  compliance_score: number;
  risk_notes: string[];
  empathy_score?: number | null;
  empathy_notes: string[];
  suggested_hashtags: string[];
}

export interface ComplianceCheckResult {
  compliance_score: number;
  risk_level: string;
  risk_notes: string[];
  suggested_fix: string;
  has_pr_disclosure: boolean;
  flagged_terms: string[];
  recommendation: string;
}

export interface Draft {
  id: number;
  platform: Platform;
  theme: string;
  body: string;
  caption?: string | null;
  cta?: string | null;
  affiliate_product_id?: number | null;
  compliance_score?: number | null;
  risk_notes?: string | null;
  status: DraftStatus;
  scheduled_at?: string | null;
  posted_at?: string | null;
  fortune_type?: string | null;
  persona_pain_id?: number | null;
  fortune_template_id?: number | null;
  affiliate_intent?: AffiliateIntent | null;
  empathy_score?: number | null;
  empathy_notes?: string | null;
  publish_ready: boolean;
  publish_block_reason?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
}

export type DraftPayload = Omit<Draft, "id" | "created_at" | "updated_at" | "publish_ready" | "publish_block_reason"> &
  Partial<Pick<Draft, "publish_ready" | "publish_block_reason">>;

export interface DashboardStats {
  knowledge_count: number;
  affiliate_product_count: number;
  draft_count: number;
  pending_review: number;
  today_drafts: number;
  active_products: number;
  recent_drafts: Draft[];
}

export interface AppSettings {
  openai_api_key_set: boolean;
  openai_model: string;
  default_platform: Platform;
  default_pr_disclosure: string;
  brand_voice_summary: string;
}

export interface EmpathyCheckResult {
  empathy_score: number;
  risk_level: string;
  checks: Record<string, boolean>;
  notes: string[];
  suggested_fix: string;
}

export interface PublishResult {
  ok: boolean;
  draft_id: number;
  provider_results: Array<Record<string, unknown>>;
  message: string;
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers ?? {}),
    },
    ...options,
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || response.statusText);
  }

  if (response.status === 204) {
    return undefined as T;
  }
  return response.json() as Promise<T>;
}

export const api = {
  getDashboard: () => request<DashboardStats>("/api/dashboard"),
  listKnowledge: () => request<KnowledgeItem[]>("/api/knowledge"),
  createKnowledge: (payload: KnowledgePayload) =>
    request<KnowledgeItem>("/api/knowledge", { method: "POST", body: JSON.stringify(payload) }),
  updateKnowledge: (id: number, payload: Partial<KnowledgePayload>) =>
    request<KnowledgeItem>(`/api/knowledge/${id}`, { method: "PUT", body: JSON.stringify(payload) }),
  deleteKnowledge: (id: number) => request<void>(`/api/knowledge/${id}`, { method: "DELETE" }),

  listProducts: () => request<AffiliateProduct[]>("/api/affiliate-products"),
  createProduct: (payload: AffiliateProductPayload) =>
    request<AffiliateProduct>("/api/affiliate-products", { method: "POST", body: JSON.stringify(payload) }),
  updateProduct: (id: number, payload: Partial<AffiliateProductPayload>) =>
    request<AffiliateProduct>(`/api/affiliate-products/${id}`, { method: "PUT", body: JSON.stringify(payload) }),
  deleteProduct: (id: number) => request<void>(`/api/affiliate-products/${id}`, { method: "DELETE" }),

  listPersonaPains: () => request<PersonaPain[]>("/api/persona-pains"),
  createPersonaPain: (payload: PersonaPainPayload) =>
    request<PersonaPain>("/api/persona-pains", { method: "POST", body: JSON.stringify(payload) }),
  updatePersonaPain: (id: number, payload: Partial<PersonaPainPayload>) =>
    request<PersonaPain>(`/api/persona-pains/${id}`, { method: "PUT", body: JSON.stringify(payload) }),
  deletePersonaPain: (id: number) => request<void>(`/api/persona-pains/${id}`, { method: "DELETE" }),

  listFortuneTemplates: () => request<FortuneTemplate[]>("/api/fortune-templates"),
  createFortuneTemplate: (payload: FortuneTemplatePayload) =>
    request<FortuneTemplate>("/api/fortune-templates", { method: "POST", body: JSON.stringify(payload) }),
  updateFortuneTemplate: (id: number, payload: Partial<FortuneTemplatePayload>) =>
    request<FortuneTemplate>(`/api/fortune-templates/${id}`, { method: "PUT", body: JSON.stringify(payload) }),
  deleteFortuneTemplate: (id: number) => request<void>(`/api/fortune-templates/${id}`, { method: "DELETE" }),

  generateContent: (payload: GenerateContentRequest) =>
    request<GeneratedContent>("/api/content/generate", { method: "POST", body: JSON.stringify(payload) }),
  complianceCheck: (payload: { body: string; caption?: string | null; cta?: string | null; affiliate_product_id?: number | null }) =>
    request<ComplianceCheckResult>("/api/content/compliance-check", { method: "POST", body: JSON.stringify(payload) }),
  empathyCheck: (payload: { body: string; caption?: string | null; target_reader?: string | null; persona_pain_id?: number | null }) =>
    request<EmpathyCheckResult>("/api/content/empathy-check", { method: "POST", body: JSON.stringify(payload) }),

  listDrafts: () => request<Draft[]>("/api/drafts"),
  createDraft: (payload: DraftPayload) =>
    request<Draft>("/api/drafts", { method: "POST", body: JSON.stringify(payload) }),
  updateDraft: (id: number, payload: Partial<DraftPayload>) =>
    request<Draft>(`/api/drafts/${id}`, { method: "PUT", body: JSON.stringify(payload) }),
  deleteDraft: (id: number) => request<void>(`/api/drafts/${id}`, { method: "DELETE" }),
  mockPublishDraft: (id: number) => request<PublishResult>(`/api/publish/drafts/${id}/mock`, { method: "POST" }),

  getSettings: () => request<AppSettings>("/api/settings"),
  updateSettings: (payload: Partial<AppSettings> & { openai_api_key?: string }) =>
    request<AppSettings>("/api/settings", { method: "PUT", body: JSON.stringify(payload) }),
};
