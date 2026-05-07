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
  FortuneA8Offer,
  FortuneTemplate,
  GeneratedContent,
  GenerateContentRequest,
  NoteCtaTemplate,
  NoteFunnelPage,
  PersonaPain,
  Platform,
  ScheduleMode,
  ThreadsPostTemplate,
  Tone,
} from "../types";
import { EmptyState, scoreClass } from "./shared";

const toneOptions = Object.entries(TONE_LABELS);
const affiliateIntentOptions = Object.entries(AFFILIATE_INTENT_LABELS);
const fortuneTypeOptions = Object.entries(FORTUNE_TYPE_LABELS);

export default function ContentGenerator() {
  const [products, setProducts] = useState<AffiliateProduct[]>([]);
  const [personas, setPersonas] = useState<PersonaPain[]>([]);
  const [templates, setTemplates] = useState<FortuneTemplate[]>([]);
  const [notePages, setNotePages] = useState<NoteFunnelPage[]>([]);
  const [threadsTemplates, setThreadsTemplates] = useState<ThreadsPostTemplate[]>([]);
  const [ctas, setCtas] = useState<NoteCtaTemplate[]>([]);
  const [offers, setOffers] = useState<FortuneA8Offer[]>([]);
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
    pain_category: "復縁",
    post_type: "empathy",
    note_page_id: null,
    fortune_offer_id: null,
    threads_template_id: null,
    cta_template_id: null,
    typefully_schedule_mode: "draft_only",
    typefully_scheduled_at: null,
  });

  useEffect(() => {
    api.listProducts().then(setProducts);
    api.listPersonaPains().then(setPersonas);
    api.listFortuneTemplates().then(setTemplates);
    api.listNoteFunnelPages().then(setNotePages);
    api.listThreadsPostTemplates().then(setThreadsTemplates);
    api.listNoteCtaTemplates().then(setCtas);
    api.listFortuneA8Offers().then(setOffers);
    api.getSettings().then(() => setForm((current) => ({ ...current, platform: "threads" })));
  }, []);

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
      note_page_id: form.note_page_id ?? null,
      fortune_offer_id: form.fortune_offer_id ?? null,
      threads_template_id: form.threads_template_id ?? null,
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
          恋愛・復縁・片思いの悩みに寄り添うThreads投稿を作成します。A8リンクは本文に入れず、プロフィールのnoteへ自然に誘導します。
        </p>
        <label>
          1. どんな悩みに向ける？
          <input value={form.theme} onChange={(event) => setForm({ ...form, theme: event.target.value })} required />
        </label>
        <label>
          誰の悩みに向けるか
          <input value={form.target_reader} onChange={(event) => setForm({ ...form, target_reader: event.target.value })} required />
        </label>
        <div className="two-columns">
          <label>
            悩みカテゴリ
            <select value={form.pain_category ?? ""} onChange={(event) => setForm({ ...form, pain_category: event.target.value })}>
              {["復縁", "元彼・元カノ", "片思い", "相手の気持ち", "音信不通", "曖昧な関係", "婚期", "職場の人間関係", "仕事運", "将来不安"].map((item) => (
                <option key={item} value={item}>{item}</option>
              ))}
            </select>
          </label>
          <label>
            2. どの投稿タイプで作る？
            <select value={form.post_type ?? "empathy"} onChange={(event) => setForm({ ...form, post_type: event.target.value })}>
              <option value="empathy">共感型</option>
              <option value="checklist">チェックリスト型</option>
              <option value="avoid_mistake">失敗回避型</option>
              <option value="question_examples">質問例型</option>
              <option value="self_reflection">自分の考え型</option>
              <option value="soft_note_cta">note誘導型</option>
            </select>
          </label>
        </div>
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
            旧占いテンプレート
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
        <label>
          Threads投稿テンプレート
          <select value={form.threads_template_id ?? ""} onChange={(event) => setForm({ ...form, threads_template_id: event.target.value ? Number(event.target.value) : null })}>
            <option value="">なし</option>
            {threadsTemplates.map((template) => <option key={template.id} value={template.id}>{template.name}</option>)}
          </select>
        </label>
        <label>
          3. どのnote記事へつなげる？
          <select value={form.note_page_id ?? ""} onChange={(event) => setForm({ ...form, note_page_id: event.target.value ? Number(event.target.value) : null })}>
            <option value="">未設定</option>
            {notePages.map((page) => <option key={page.id} value={page.id}>{page.title}</option>)}
          </select>
        </label>
        <label>
          4. どのCTAを使う？
          <select value={form.cta_template_id ?? ""} onChange={(event) => setForm({ ...form, cta_template_id: event.target.value ? Number(event.target.value) : null })}>
            <option value="">自動</option>
            {ctas.map((cta) => <option key={cta.id} value={cta.id}>{cta.name}</option>)}
          </select>
        </label>
        <div className="two-columns">
          <label>
            5. どんなトーンで書く？
            <select value={form.tone} onChange={(event) => setForm({ ...form, tone: event.target.value as Tone })}>
              {toneOptions.map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </label>
          <label>
            Typefully予約予定
            <select value={form.typefully_schedule_mode ?? "draft_only"} onChange={(event) => setForm({ ...form, typefully_schedule_mode: event.target.value as ScheduleMode })}>
              <option value="draft_only">下書きのみ</option>
              <option value="next_free_slot">次の空き枠</option>
              <option value="scheduled_time">指定日時</option>
            </select>
          </label>
        </div>
        <label>
          note内で使うA8占い案件（Threads本文には入れない）
          <select
            value={form.fortune_offer_id ?? ""}
            onChange={(event) => setForm({ ...form, fortune_offer_id: event.target.value ? Number(event.target.value) : null })}
          >
            <option value="">なし</option>
            {offers.filter((offer) => offer.is_active).map((offer) => (
              <option key={offer.id} value={offer.id}>
                {offer.offer_name}
              </option>
            ))}
          </select>
        </label>
        <div className="info-strip">投稿先はThreads固定です。予約投稿は承認後にTypefullyへ送ります。</div>
        <p className="field-note">6. 生成結果を確認 → 7. 下書き保存 → 8. 承認後にTypefully予約、の順で進めます。</p>
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
