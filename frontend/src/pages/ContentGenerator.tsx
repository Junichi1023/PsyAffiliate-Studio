import { FormEvent, useEffect, useMemo, useState } from "react";
import { Save, ShieldCheck, Sparkles } from "lucide-react";
import { api } from "../api/client";
import { AffiliateProduct, DraftStatus, GeneratedContent, GenerateContentRequest, Platform, Tone } from "../types";
import { EmptyState, scoreClass } from "./shared";

export default function ContentGenerator() {
  const [products, setProducts] = useState<AffiliateProduct[]>([]);
  const [generated, setGenerated] = useState<GeneratedContent | null>(null);
  const [generating, setGenerating] = useState(false);
  const [form, setForm] = useState<GenerateContentRequest>({
    theme: "",
    target_reader: "",
    platform: "threads",
    tone: "empathy",
    selected_product_id: null,
  });

  useEffect(() => {
    api.listProducts().then(setProducts);
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
