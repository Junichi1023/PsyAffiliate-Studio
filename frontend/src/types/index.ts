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
  GeneratedContent,
  GenerateContentRequest,
  KnowledgeItem,
  KnowledgePayload,
  PersonaPain,
  PersonaPainPayload,
  Platform,
  PublishResult,
  Tone,
} from "../api/client";

export type Page =
  | "dashboard"
  | "knowledge"
  | "products"
  | "persona-pains"
  | "fortune-templates"
  | "generator"
  | "drafts"
  | "settings";
