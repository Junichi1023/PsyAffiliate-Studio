import type { Draft, DraftStatus, Platform } from "../types";

export const PAGE_LABELS = {
  dashboard: "ダッシュボード",
  knowledge: "ナレッジ",
  products: "アフィリエイト商品",
  "persona-pains": "悩みペルソナ",
  "fortune-templates": "占いテンプレート",
  generator: "投稿作成",
  drafts: "下書き・投稿管理",
  settings: "設定",
} as const;

export const PLATFORM_LABELS = {
  threads: "Threads",
  instagram: "Instagram",
  both: "Threads + Instagram",
} as const;

export const TONE_LABELS = {
  empathy: "共感寄り",
  practical: "実用寄り",
  story: "体験談風",
  educational: "解説風",
  soft_sales: "やさしい紹介",
} as const;

export const AFFILIATE_INTENT_LABELS = {
  none: "紹介しない",
  soft: "控えめに紹介",
  moderate: "自然に紹介",
} as const;

export const FORTUNE_TYPE_LABELS = {
  general: "総合運",
  money_luck: "金運",
  love_luck: "恋愛運",
  work_luck: "仕事運",
  relationship: "人間関係",
  tarot: "タロット",
  astrology: "星占い",
  numerology: "数秘術",
  oracle: "オラクルカード",
} as const;

export const PERSONA_CATEGORY_LABELS = {
  money: "金運・お金",
  love: "恋愛",
  work: "仕事",
  relationship: "人間関係",
  future: "将来不安",
  self_confidence: "自己肯定感",
} as const;

export const DRAFT_STATUS_LABELS: Record<DraftStatus, string> = {
  draft: "下書き",
  needs_review: "要確認",
  approved: "承認済み",
  scheduled: "予約済み",
  posted: "投稿済み",
  failed: "失敗",
};

export const KNOWLEDGE_CATEGORY_LABELS = {
  profile: "プロフィール",
  brand_voice: "投稿の口調",
  psychology: "心理学",
  ai_prompt: "AIプロンプト",
  fortune_telling_method: "占いノウハウ",
  tarot_reading: "タロット",
  astrology: "星占い",
  numerology: "数秘術",
  oracle_card: "オラクルカード",
  money_luck: "金運",
  love_luck: "恋愛運",
  work_luck: "仕事運",
  relationship_worry: "人間関係の悩み",
  spiritual_expression: "スピリチュアル表現",
  fortune_disclaimer: "占い注意書き",
  affiliate_offer: "商品紹介導線",
  cta_template: "CTAテンプレート",
  persona_pain: "悩みペルソナ補足",
  threads_hook: "Threads冒頭フック",
  prohibited_expression: "禁止表現",
  past_post: "過去投稿",
  note_article: "note記事",
  winning_post: "反応が良かった投稿",
  failed_post: "反応が悪かった投稿",
} as const;

export const SCORE_HELP_TEXT = {
  compliance: "PR表記、誇大表現、医療的断定、収益保証、不安煽りがないかを確認します。",
  empathy: "読者の感情を受け止めているか、責めていないか、占い依存や恐怖訴求になっていないかを確認します。",
} as const;

export function platformLabel(platform: Platform | string) {
  return PLATFORM_LABELS[platform as Platform] ?? platform;
}

export function genericLabel<T extends Record<string, string>>(labels: T, value?: string | null) {
  if (!value) return "-";
  return labels[value as keyof T] ?? value;
}

export function complianceStatus(score?: number | null) {
  if (score == null) return "未チェック";
  if (score >= 90) return "安全性 高";
  if (score >= 70) return "軽微な修正推奨";
  if (score >= 40) return "要レビュー";
  return "投稿非推奨";
}

export function empathyStatus(score?: number | null) {
  if (score == null) return "未チェック";
  if (score >= 85) return "寄り添い度 高";
  if (score >= 75) return "良好";
  if (score >= 60) return "改善推奨";
  return "寄り添い不足";
}

export function publishReadyLabel(ready: boolean) {
  return ready ? "投稿準備OK" : "未準備";
}

export function mockPublishDisabledReason(draft: Draft) {
  if (draft.status !== "approved") return "まだ承認済みではありません";
  if ((draft.compliance_score ?? 0) < 90) return "安全性スコアが90未満です";
  if ((draft.empathy_score ?? 0) < 75) return "寄り添いスコアが75未満です";
  if (!draft.publish_ready) return "投稿準備OKになっていません";
  return null;
}
