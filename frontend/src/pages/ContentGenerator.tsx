import { FormEvent, useEffect, useMemo, useState } from "react";
import { Save, ShieldCheck, Sparkles } from "lucide-react";
import { api } from "../api/client";
import {
  AFFILIATE_INTENT_LABELS,
  complianceStatus,
  empathyStatus,
  FORTUNE_TYPE_LABELS,
  genericLabel,
  PERSONA_CATEGORY_LABELS,
  PLATFORM_LABELS,
  SCORE_HELP_TEXT,
  TONE_LABELS,
} from "../constants/labels";
import {
  AffiliateIntent,
  AffiliateProduct,
  DraftStatus,
  FortuneTemplate,
  GeneratedContent,
  GenerateContentRequest,
  PersonaPain,
  Platform,
  Tone,
} from "../types";
import { EmptyState, scoreClass } from "./shared";

const platformOptions = Object.entries(PLATFORM_LABELS);
const toneOptions = Object.entries(TONE_LABELS);
const affiliateIntentOptions = Object.entries(AFFILIATE_INTENT_LABELS);
const fortuneTypeOptions = Object.entries(FORTUNE_TYPE_LABELS);

export default function ContentGenerator() {
  const [products, setProducts] = useState<AffiliateProduct[]>([]);
  const [personas, setPersonas] = useState<PersonaPain[]>([]);
  const [templates, setTemplates] = useState<FortuneTemplate[]>([]);
  const [generated, setGenerated] = useState<GeneratedContent | null>(null);
  const [generating, setGenerating] = useState(false);
  const [form, setForm] = useState<GenerateContentRequest>({
    theme: "",
    target_reader: "",
    platform: "threads",
    tone: "empathy",
    selected_product_id: null,
    fortune_type: "tarot",
    persona_pain_id: null,
    fortune_template_id: null,
    affiliate_intent: "none",
  });

  useEffect(() => {
    api.listProducts().then(setProducts);
    api.listPersonaPains().then(setPersonas);
    api.listFortuneTemplates().then(setTemplates);
    api.getSettings().then((settings) => setForm((current) => ({ ...current, platform: settings.default_platform })));
  }, []);

  const activeProducts = useMemo(() => products.filter((product) => product.is_active), [products]);
  const selectedGeneratedProduct = useMemo(
    () => products.find((product) => product.id === generated?.affiliate_product_id),
    [generated?.affiliate_product_id, products],
  );

  async function generate(event: FormEvent) {
    event.preventDefault();
    setGenerating(true);
    try {
      setGenerated(await api.generateContent(form));
    } finally {
      setGenerating(false);
    }
  }

  async function saveDraft() {
    if (!generated) return;
    const status: DraftStatus = generated.compliance_score >= 90 ? "draft" : "needs_review";
    await api.createDraft({
      platform: generated.platform,
      theme: generated.theme,
      body: generated.body,
      caption: generated.caption ?? null,
      cta: generated.cta,
      affiliate_product_id: generated.affiliate_product_id ?? null,
      compliance_score: generated.compliance_score,
      risk_notes: generated.risk_notes.join("\n"),
      fortune_type: form.fortune_type ?? null,
      persona_pain_id: form.persona_pain_id ?? null,
      fortune_template_id: form.fortune_template_id ?? null,
      affiliate_intent: form.affiliate_intent ?? "none",
      empathy_score: generated.empathy_score ?? null,
      empathy_notes: generated.empathy_notes.join("\n"),
      status,
      scheduled_at: null,
      posted_at: null,
    });
  }

  return (
    <section className="generator-layout">
      <form className="panel form-panel" onSubmit={generate}>
        <div className="panel-title">
          <h3>投稿作成</h3>
          <Sparkles size={18} />
        </div>
        <p className="page-description compact">
          悩み、占術、テンプレート、商品導線を選び、Threads/Instagram向け投稿を作成します。
        </p>
        <label>
          投稿テーマ
          <input value={form.theme} onChange={(event) => setForm({ ...form, theme: event.target.value })} required />
        </label>
        <label>
          誰の悩みに向けるか
          <input value={form.target_reader} onChange={(event) => setForm({ ...form, target_reader: event.target.value })} required />
        </label>
        <label>
          悩みペルソナ
          <select
            value={form.persona_pain_id ?? ""}
            onChange={(event) => setForm({ ...form, persona_pain_id: event.target.value ? Number(event.target.value) : null })}
          >
            <option value="">なし</option>
            {personas.map((persona) => (
              <option key={persona.id} value={persona.id}>
                {persona.name} / {genericLabel(PERSONA_CATEGORY_LABELS, persona.category)}
              </option>
            ))}
          </select>
        </label>
        <div className="two-columns">
          <label>
            占いジャンル
            <select value={form.fortune_type ?? ""} onChange={(event) => setForm({ ...form, fortune_type: event.target.value })}>
              {fortuneTypeOptions.map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </label>
          <label>
            占いテンプレート
            <select
              value={form.fortune_template_id ?? ""}
              onChange={(event) => setForm({ ...form, fortune_template_id: event.target.value ? Number(event.target.value) : null })}
            >
              <option value="">なし</option>
              {templates.map((template) => (
                <option key={template.id} value={template.id}>
                  {template.name}
                </option>
              ))}
            </select>
          </label>
        </div>
        <div className="two-columns">
          <label>
            投稿先
            <select value={form.platform} onChange={(event) => setForm({ ...form, platform: event.target.value as Platform })}>
              {platformOptions.map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </label>
          <label>
            文章トーン
            <select value={form.tone} onChange={(event) => setForm({ ...form, tone: event.target.value as Tone })}>
              {toneOptions.map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </label>
        </div>
        <label>
          紹介する商品
          <select
            value={form.selected_product_id ?? ""}
            onChange={(event) => setForm({ ...form, selected_product_id: event.target.value ? Number(event.target.value) : null })}
          >
            <option value="">なし</option>
            {activeProducts.map((product) => (
              <option key={product.id} value={product.id}>
                {product.name}
              </option>
            ))}
          </select>
        </label>
        <label>
          アフィリエイト導線の強さ
          <select value={form.affiliate_intent ?? "none"} onChange={(event) => setForm({ ...form, affiliate_intent: event.target.value as AffiliateIntent })}>
            {affiliateIntentOptions.map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </label>
        <button className="primary" type="submit" disabled={generating}>
          <Sparkles size={17} />
          {generating ? "生成中" : "生成"}
        </button>
      </form>

      <section className="panel result-panel">
        <div className="panel-title">
          <h3>生成結果</h3>
          <ShieldCheck size={18} />
        </div>
        {generated ? (
          <div className="generated-result">
            <div className="result-meta">
              <span className="badge">{PLATFORM_LABELS[generated.platform]}</span>
              <span className={scoreClass(generated.compliance_score)}>
                安全性 {generated.compliance_score} / {complianceStatus(generated.compliance_score)}
              </span>
              <span className={scoreClass(generated.empathy_score)}>
                寄り添い {generated.empathy_score ?? "-"} / {empathyStatus(generated.empathy_score)}
              </span>
              <span className="badge green">{generated.pr_disclosure}</span>
            </div>
            <h3>{generated.theme}</h3>
            {selectedGeneratedProduct && (
              <div className="info-strip">
                使用商品: {selectedGeneratedProduct.name}
              </div>
            )}
            <div className="score-explainers">
              <p><strong>安全性スコア:</strong> {SCORE_HELP_TEXT.compliance}</p>
              <p><strong>寄り添いスコア:</strong> {SCORE_HELP_TEXT.empathy}</p>
            </div>
            <pre>{generated.body}</pre>
            {generated.caption && (
              <>
                <h4>Instagramキャプション</h4>
                <pre>{generated.caption}</pre>
              </>
            )}
            <h4>CTA</h4>
            <p>{generated.cta}</p>
            <h4>PR表記</h4>
            <p>{generated.pr_disclosure}</p>
            <h4>リスクメモ</h4>
            <div className="note-list">
              {generated.risk_notes.map((note) => (
                <span key={note}>{note}</span>
              ))}
            </div>
            <h4>寄り添いメモ</h4>
            <div className="note-list empathy-notes">
              {generated.empathy_notes.map((note) => (
                <span key={note}>{note}</span>
              ))}
            </div>
            <div className="hashtag-row">
              {generated.suggested_hashtags.map((tag) => (
                <span key={tag}>{tag}</span>
              ))}
            </div>
            <div className="publish-conditions">
              投稿準備OKの条件: 承認済み / 安全性スコア90以上 / 寄り添いスコア75以上
            </div>
            <p className="field-note">
              保存後、承認済みにして安全性・寄り添い度の条件を満たすと投稿準備OKになります。
            </p>
            <button className="primary" onClick={saveDraft}>
              <Save size={17} />
              下書き保存
            </button>
          </div>
        ) : (
          <EmptyState label="生成結果はここに表示されます。" />
        )}
      </section>
    </section>
  );
}
