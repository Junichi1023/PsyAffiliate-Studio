export type {
  AffiliateIntent,
  AffiliateProduct,
  AffiliateProductPayload,
  AppSettings,
  ComplianceCheckResult,
  DashboardStats,
  Draft,
  DraftPayload,
  DraftStatus,
  EmpathyCheckResult,
  FortuneTemplate,
  FortuneTemplatePayload,
  FortuneA8Offer,
  FortuneA8OfferPayload,
  GeneratedContent,
  GenerateContentRequest,
  ImportCandidate,
  ImportSession,
  KnowledgeItem,
  KnowledgePayload,
  NoteCtaTemplate,
  NoteCtaTemplatePayload,
  NoteFunnelPage,
  NoteFunnelPagePayload,
  PersonaPain,
  PersonaPainPayload,
  Platform,
  PublishResult,
  ScheduleMode,
  Threads30DayPlan,
  Threads30DayPlanTask,
  ThreadsPostTemplate,
  ThreadsPostTemplatePayload,
  TypefullyScheduleJob,
  TypefullyScheduleResult,
  Tone,
} from "../api/client";

export type Page =
  | "dashboard"
  | "thirty-day-plan"
  | "typefully-jobs"
  | "knowledge"
  | "facebook-import"
  | "products"
  | "note-funnel"
  | "fortune-a8-offers"
  | "note-ctas"
  | "persona-pains"
  | "fortune-templates"
  | "threads-templates"
  | "generator"
  | "drafts"
  | "typefully-settings"
  | "settings";
