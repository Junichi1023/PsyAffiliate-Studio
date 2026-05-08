export const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export type Platform = "threads" | "instagram" | "both";
export type Tone = "empathy" | "practical" | "story" | "educational" | "soft_sales";
export type DraftStatus = "draft" | "needs_review" | "approved" | "scheduled" | "posted" | "failed";
export type AffiliateIntent = "none" | "soft" | "moderate";
export type ScheduleMode = "draft_only" | "next_free_slot" | "scheduled_time";

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
  pain_category?: string | null;
  post_type?: string | null;
  note_page_id?: number | null;
  fortune_offer_id?: number | null;
  threads_template_id?: number | null;
  cta_template_id?: number | null;
  typefully_schedule_mode?: ScheduleMode | null;
  typefully_scheduled_at?: string | null;
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
  note_page_id?: number | null;
  fortune_offer_id?: number | null;
  threads_template_id?: number | null;
  typefully_job_id?: number | null;
  traffic_destination?: string | null;
  direct_a8_link_detected: boolean;
  profile_note_cta_included: boolean;
  human_review_required: boolean;
  created_at?: string | null;
  updated_at?: string | null;
}

export type DraftPayload = Omit<
  Draft,
  | "id"
  | "created_at"
  | "updated_at"
  | "publish_ready"
  | "publish_block_reason"
  | "direct_a8_link_detected"
  | "profile_note_cta_included"
  | "human_review_required"
> &
  Partial<Pick<Draft, "publish_ready" | "publish_block_reason" | "direct_a8_link_detected" | "profile_note_cta_included" | "human_review_required">>;

export interface DashboardStats {
  knowledge_count: number;
  affiliate_product_count: number;
  persona_pain_count: number;
  fortune_template_count: number;
  draft_count: number;
  pending_review: number;
  publish_ready_count: number;
  risky_draft_count: number;
  today_drafts: number;
  active_products: number;
  today_scheduled_count: number;
  typefully_waiting_count: number;
  note_missing_draft_count: number;
  a8_link_detected_count: number;
  facebook_candidate_count: number;
  plan_done_count: number;
  plan_total_count: number;
  weekly_post_type_distribution: Record<string, number>;
  recent_drafts: Draft[];
}

export interface AppSettings {
  openai_api_key_set: boolean;
  openai_model: string;
  default_platform: Platform;
  default_pr_disclosure: string;
  brand_voice_summary: string;
  typefully_api_key_set: boolean;
  typefully_social_set_id?: string | null;
  typefully_default_schedule_mode: ScheduleMode;
  profile_note_url?: string | null;
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

export interface NoteFunnelPage {
  id: number;
  title: string;
  note_url: string;
  purpose?: string | null;
  target_theme?: string | null;
  target_reader?: string | null;
  article_type?: string | null;
  pr_disclosure?: string | null;
  status?: string | null;
  memo?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
}

export type NoteFunnelPagePayload = Omit<NoteFunnelPage, "id" | "created_at" | "updated_at">;

export interface FortuneA8Offer {
  id: number;
  offer_name: string;
  advertiser_name?: string | null;
  service_type?: string | null;
  affiliate_url?: string | null;
  lp_url?: string | null;
  reward_amount?: number | null;
  conversion_condition?: string | null;
  rejection_conditions?: string | null;
  first_time_bonus?: string | null;
  consultation_genres?: string | null;
  lp_impression?: string | null;
  approval_rate?: string | null;
  recommended_use?: string | null;
  prohibited_claims?: string | null;
  is_active: boolean;
  created_at?: string | null;
  updated_at?: string | null;
}

export type FortuneA8OfferPayload = Omit<FortuneA8Offer, "id" | "created_at" | "updated_at">;

export interface ThreadsPostTemplate {
  id: number;
  name: string;
  template_type: string;
  target_theme?: string | null;
  structure: string;
  example_post?: string | null;
  cta_style?: string | null;
  prohibited_patterns?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
}

export type ThreadsPostTemplatePayload = Omit<ThreadsPostTemplate, "id" | "created_at" | "updated_at">;

export interface NoteCtaTemplate {
  id: number;
  name: string;
  cta_type: string;
  text: string;
  target_note_page_id?: number | null;
  use_pr_disclosure: boolean;
  created_at?: string | null;
  updated_at?: string | null;
}

export type NoteCtaTemplatePayload = Omit<NoteCtaTemplate, "id" | "created_at" | "updated_at">;

export interface ImportSession {
  id: number;
  source_type: string;
  source_name?: string | null;
  status: string;
  total_items: number;
  sanitized_items: number;
  candidate_count: number;
  redaction_summary?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface ImportCandidate {
  id: number;
  session_id: number;
  title: string;
  category: string;
  content: string;
  source?: string | null;
  confidence_score: number;
  redaction_notes?: string | null;
  selected: boolean;
}

export interface FacebookPreviewOptions {
  use_ai_summary?: boolean;
  include_messages?: boolean;
  max_items?: number;
}

export interface Threads30DayPlanTask {
  id: number;
  day_number: number;
  phase: string;
  title: string;
  description?: string | null;
  status: string;
}

export interface Threads30DayPlan {
  tasks: Threads30DayPlanTask[];
  post_type_distribution: Record<string, number>;
}

export interface TypefullyScheduleJob {
  id: number;
  draft_id: number;
  typefully_draft_id?: string | null;
  social_set_id?: string | null;
  scheduled_at?: string | null;
  status: string;
  schedule_mode?: string | null;
  typefully_url?: string | null;
  error_message?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface TypefullyScheduleResult {
  ok: boolean;
  job: TypefullyScheduleJob;
  provider_result: Record<string, unknown>;
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
    throw new Error(await extractErrorMessage(response));
  }

  if (response.status === 204) {
    return undefined as T;
  }
  return response.json() as Promise<T>;
}

async function extractErrorMessage(response: Response): Promise<string> {
  const text = await response.text();
  if (!text) return response.statusText;
  try {
    const parsed = JSON.parse(text);
    if (typeof parsed.detail === "string") return parsed.detail;
    if (Array.isArray(parsed.detail)) return parsed.detail.map((item: { msg?: string }) => item.msg ?? JSON.stringify(item)).join(" / ");
  } catch {
    return text;
  }
  return text;
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

  listNoteFunnelPages: () => request<NoteFunnelPage[]>("/api/note-funnel-pages"),
  createNoteFunnelPage: (payload: NoteFunnelPagePayload) =>
    request<NoteFunnelPage>("/api/note-funnel-pages", { method: "POST", body: JSON.stringify(payload) }),
  updateNoteFunnelPage: (id: number, payload: Partial<NoteFunnelPagePayload>) =>
    request<NoteFunnelPage>(`/api/note-funnel-pages/${id}`, { method: "PUT", body: JSON.stringify(payload) }),
  deleteNoteFunnelPage: (id: number) => request<void>(`/api/note-funnel-pages/${id}`, { method: "DELETE" }),

  listFortuneA8Offers: () => request<FortuneA8Offer[]>("/api/fortune-a8-offers"),
  createFortuneA8Offer: (payload: FortuneA8OfferPayload) =>
    request<FortuneA8Offer>("/api/fortune-a8-offers", { method: "POST", body: JSON.stringify(payload) }),
  updateFortuneA8Offer: (id: number, payload: Partial<FortuneA8OfferPayload>) =>
    request<FortuneA8Offer>(`/api/fortune-a8-offers/${id}`, { method: "PUT", body: JSON.stringify(payload) }),
  deleteFortuneA8Offer: (id: number) => request<void>(`/api/fortune-a8-offers/${id}`, { method: "DELETE" }),

  listThreadsPostTemplates: () => request<ThreadsPostTemplate[]>("/api/threads-post-templates"),
  createThreadsPostTemplate: (payload: ThreadsPostTemplatePayload) =>
    request<ThreadsPostTemplate>("/api/threads-post-templates", { method: "POST", body: JSON.stringify(payload) }),
  updateThreadsPostTemplate: (id: number, payload: Partial<ThreadsPostTemplatePayload>) =>
    request<ThreadsPostTemplate>(`/api/threads-post-templates/${id}`, { method: "PUT", body: JSON.stringify(payload) }),
  deleteThreadsPostTemplate: (id: number) => request<void>(`/api/threads-post-templates/${id}`, { method: "DELETE" }),

  listNoteCtaTemplates: () => request<NoteCtaTemplate[]>("/api/note-cta-templates"),
  createNoteCtaTemplate: (payload: NoteCtaTemplatePayload) =>
    request<NoteCtaTemplate>("/api/note-cta-templates", { method: "POST", body: JSON.stringify(payload) }),
  updateNoteCtaTemplate: (id: number, payload: Partial<NoteCtaTemplatePayload>) =>
    request<NoteCtaTemplate>(`/api/note-cta-templates/${id}`, { method: "PUT", body: JSON.stringify(payload) }),
  deleteNoteCtaTemplate: (id: number) => request<void>(`/api/note-cta-templates/${id}`, { method: "DELETE" }),

  uploadFacebookZipPreview: async (file: File, options: FacebookPreviewOptions = {}) => {
    const form = new FormData();
    form.append("file", file);
    form.append("use_ai_summary", String(options.use_ai_summary ?? false));
    form.append("include_messages", String(options.include_messages ?? false));
    form.append("max_items", String(options.max_items ?? 2000));
    const response = await fetch(`${API_BASE}/api/import/facebook/preview`, { method: "POST", body: form });
    if (!response.ok) throw new Error(await extractErrorMessage(response));
    return response.json() as Promise<ImportSession>;
  },
  listImportSessions: () => request<ImportSession[]>("/api/import/sessions"),
  listImportCandidates: (sessionId: number) => request<ImportCandidate[]>(`/api/import/sessions/${sessionId}/candidates`),
  updateImportCandidate: (id: number, payload: Partial<ImportCandidate>) =>
    request<ImportCandidate>(`/api/import/candidates/${id}`, { method: "PUT", body: JSON.stringify(payload) }),
  commitImportSession: (sessionId: number) =>
    request<{ committed_count: number; knowledge_items: KnowledgeItem[] }>(`/api/import/sessions/${sessionId}/commit`, { method: "POST" }),

  getThreads30DayPlan: () => request<Threads30DayPlan>("/api/threads-30day-plan"),
  updateThreads30DayPlanTask: (id: number, payload: Partial<Threads30DayPlanTask>) =>
    request<Threads30DayPlanTask>(`/api/threads-30day-plan/${id}`, { method: "PUT", body: JSON.stringify(payload) }),

  listTypefullyJobs: () => request<TypefullyScheduleJob[]>("/api/typefully/jobs"),
  scheduleTypefullyDraft: (draftId: number, payload: { schedule_mode: ScheduleMode; scheduled_at?: string | null }) =>
    request<TypefullyScheduleResult>(`/api/typefully/drafts/${draftId}/schedule`, { method: "POST", body: JSON.stringify(payload) }),
  cancelTypefullyJobLocal: (id: number) =>
    request<TypefullyScheduleJob>(`/api/typefully/jobs/${id}/cancel-local`, { method: "PUT" }),

  getSettings: () => request<AppSettings>("/api/settings"),
  updateSettings: (payload: Partial<AppSettings> & { openai_api_key?: string; typefully_api_key?: string }) =>
    request<AppSettings>("/api/settings", { method: "PUT", body: JSON.stringify(payload) }),
};
