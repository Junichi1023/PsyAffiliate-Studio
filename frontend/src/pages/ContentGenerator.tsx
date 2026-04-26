import { FormEvent, useEffect, useMemo, useState } from "react";
import { Save, ShieldCheck, Sparkles } from "lucide-react";
import { api } from "../api/client";
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
          <h3>投稿生成</h3>
          <Sparkles size={18} />
        </div>
        <label>
          テーマ
          <input value={form.theme} onChange={(event) => setForm({ ...form, theme: event.target.value })} required />
        </label>
        <label>
          読者
          <input value={form.target_reader} onChange={(event) => setForm({ ...form, target_reader: event.target.value })} required />
        </label>
        <div className="two-columns">
          <label>
            platform
            <select value={form.platform} onChange={(event) => setForm({ ...form, platform: event.target.value as Platform })}>
              <option value="threads">threads</option>
              <option value="instagram">instagram</option>
              <option value="both">both</option>
            </select>
          </label>
          <label>
            tone
            <select value={form.tone} onChange={(event) => setForm({ ...form, tone: event.target.value as Tone })}>
              <option value="empathy">empathy</option>
              <option value="practical">practical</option>
              <option value="story">story</option>
              <option value="educational">educational</option>
              <option value="soft_sales">soft_sales</option>
            </select>
          </label>
        </div>
        <label>
          商品
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
        <div className="two-columns">
          <label>
            fortune_type
            <select value={form.fortune_type ?? ""} onChange={(event) => setForm({ ...form, fortune_type: event.target.value })}>
              <option value="tarot">tarot</option>
              <option value="astrology">astrology</option>
              <option value="numerology">numerology</option>
              <option value="oracle">oracle</option>
              <option value="money_luck">money_luck</option>
              <option value="love_luck">love_luck</option>
              <option value="work_luck">work_luck</option>
              <option value="general">general</option>
            </select>
          </label>
          <label>
            affiliate_intent
            <select value={form.affiliate_intent ?? "none"} onChange={(event) => setForm({ ...form, affiliate_intent: event.target.value as AffiliateIntent })}>
              <option value="none">none</option>
              <option value="soft">soft</option>
              <option value="moderate">moderate</option>
            </select>
          </label>
        </div>
        <label>
          persona_pain
          <select
            value={form.persona_pain_id ?? ""}
            onChange={(event) => setForm({ ...form, persona_pain_id: event.target.value ? Number(event.target.value) : null })}
          >
            <option value="">なし</option>
            {personas.map((persona) => (
              <option key={persona.id} value={persona.id}>
                {persona.name} / {persona.category}
              </option>
            ))}
          </select>
        </label>
        <label>
          fortune_template
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
              <span className="badge">{generated.platform}</span>
              <span className={scoreClass(generated.compliance_score)}>{generated.compliance_score}</span>
              <span className={scoreClass(generated.empathy_score)}>{generated.empathy_score ?? "-"}</span>
              <span className="badge green">{generated.pr_disclosure}</span>
            </div>
            <h3>{generated.theme}</h3>
            <pre>{generated.body}</pre>
            {generated.caption && (
              <>
                <h4>Instagram caption</h4>
                <pre>{generated.caption}</pre>
              </>
            )}
            <h4>CTA</h4>
            <p>{generated.cta}</p>
            <div className="note-list">
              {generated.risk_notes.map((note) => (
                <span key={note}>{note}</span>
              ))}
            </div>
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
