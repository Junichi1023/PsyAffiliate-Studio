import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  BarChart3,
  BookOpen,
  CheckCircle2,
  Download,
  FileText,
  Package,
  Pencil,
  Plus,
  RefreshCw,
  Save,
  Settings as SettingsIcon,
  ShieldCheck,
  Sparkles,
  Trash2,
  X,
} from "lucide-react";
import {
  API_BASE,
  AffiliateProduct,
  AffiliateProductPayload,
  AppSettings,
  DashboardStats,
  Draft,
  DraftStatus,
  GeneratedContent,
  GenerateContentRequest,
  KnowledgeItem,
  KnowledgePayload,
  Platform,
  Tone,
  api,
} from "./lib/api";

type Page = "dashboard" | "knowledge" | "products" | "generator" | "drafts" | "settings";

const knowledgeCategories = [
  "profile",
  "brand_voice",
  "psychology",
  "ai_prompt",
  "prohibited_expression",
  "past_post",
  "note_article",
];

const statusOptions: DraftStatus[] = ["draft", "needs_review", "approved", "scheduled", "posted", "failed"];

const emptyKnowledge: KnowledgePayload = {
  title: "",
  category: "psychology",
  content: "",
  source: "",
};

const emptyProduct: AffiliateProductPayload = {
  name: "",
  asp_name: "",
  affiliate_url: "",
  display_url: "",
  category: "",
  target_pain: "",
  commission_type: "",
  commission_amount: null,
  prohibited_claims: "",
  priority: 0,
  is_active: true,
};

const defaultSettings: AppSettings = {
  openai_api_key_set: false,
  openai_model: "gpt-5.5",
  default_platform: "threads",
  default_pr_disclosure: "#PR",
  brand_voice_summary: "",
};

function formatDate(value?: string | null) {
  if (!value) return "-";
  return new Intl.DateTimeFormat("ja-JP", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

function scoreClass(score?: number | null) {
  if (score == null) return "score neutral";
  if (score >= 90) return "score good";
  if (score >= 70) return "score caution";
  if (score >= 40) return "score review";
  return "score danger";
}

function riskLines(text?: string | null) {
  if (!text) return [];
  return text
    .split(/\n|、/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function toRiskText(notes: string[]) {
  return notes.join("\n");
}

function App() {
  const [page, setPage] = useState<Page>("dashboard");
  const [knowledge, setKnowledge] = useState<KnowledgeItem[]>([]);
  const [products, setProducts] = useState<AffiliateProduct[]>([]);
  const [drafts, setDrafts] = useState<Draft[]>([]);
  const [dashboard, setDashboard] = useState<DashboardStats | null>(null);
  const [settings, setSettings] = useState<AppSettings>(defaultSettings);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const [knowledgeForm, setKnowledgeForm] = useState<KnowledgePayload>(emptyKnowledge);
  const [editingKnowledgeId, setEditingKnowledgeId] = useState<number | null>(null);

  const [productForm, setProductForm] = useState<AffiliateProductPayload>(emptyProduct);
  const [editingProductId, setEditingProductId] = useState<number | null>(null);

  const [generatorForm, setGeneratorForm] = useState<GenerateContentRequest>({
    theme: "",
    target_reader: "",
    platform: "threads",
    tone: "empathy",
    selected_product_id: null,
  });
  const [generated, setGenerated] = useState<GeneratedContent | null>(null);
  const [generating, setGenerating] = useState(false);

  const [settingsForm, setSettingsForm] = useState({
    openai_api_key: "",
    openai_model: "gpt-5.5",
    default_platform: "threads" as Platform,
    default_pr_disclosure: "#PR",
    brand_voice_summary: "",
  });

  const loadData = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [dashboardData, knowledgeData, productData, draftData, settingsData] = await Promise.all([
        api.getDashboard(),
        api.listKnowledge(),
        api.listProducts(),
        api.listDrafts(),
        api.getSettings(),
      ]);
      setDashboard(dashboardData);
      setKnowledge(knowledgeData);
      setProducts(productData);
      setDrafts(draftData);
      setSettings(settingsData);
      setSettingsForm({
        openai_api_key: "",
        openai_model: settingsData.openai_model,
        default_platform: settingsData.default_platform,
        default_pr_disclosure: settingsData.default_pr_disclosure,
        brand_voice_summary: settingsData.brand_voice_summary,
      });
      setGeneratorForm((current) => ({ ...current, platform: settingsData.default_platform }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "データ取得に失敗しました。");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const activeProducts = useMemo(() => products.filter((product) => product.is_active), [products]);

  async function saveKnowledge(event: FormEvent) {
    event.preventDefault();
    setError("");
    try {
      if (editingKnowledgeId) {
        await api.updateKnowledge(editingKnowledgeId, knowledgeForm);
        setNotice("ナレッジを更新しました。");
      } else {
        await api.createKnowledge(knowledgeForm);
        setNotice("ナレッジを追加しました。");
      }
      setKnowledgeForm(emptyKnowledge);
      setEditingKnowledgeId(null);
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : "保存に失敗しました。");
    }
  }

  async function removeKnowledge(id: number) {
    await api.deleteKnowledge(id);
    setNotice("ナレッジを削除しました。");
    await loadData();
  }

  function editKnowledge(item: KnowledgeItem) {
    setEditingKnowledgeId(item.id);
    setKnowledgeForm({
      title: item.title,
      category: item.category,
      content: item.content,
      source: item.source ?? "",
    });
  }

  async function saveProduct(event: FormEvent) {
    event.preventDefault();
    setError("");
    try {
      if (editingProductId) {
        await api.updateProduct(editingProductId, productForm);
        setNotice("商品を更新しました。");
      } else {
        await api.createProduct(productForm);
        setNotice("商品を追加しました。");
      }
      setProductForm(emptyProduct);
      setEditingProductId(null);
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : "保存に失敗しました。");
    }
  }

  async function removeProduct(id: number) {
    await api.deleteProduct(id);
    setNotice("商品を削除しました。");
    await loadData();
  }

  function editProduct(product: AffiliateProduct) {
    setEditingProductId(product.id);
    setProductForm({
      name: product.name,
      asp_name: product.asp_name ?? "",
      affiliate_url: product.affiliate_url,
      display_url: product.display_url ?? "",
      category: product.category ?? "",
      target_pain: product.target_pain ?? "",
      commission_type: product.commission_type ?? "",
      commission_amount: product.commission_amount ?? null,
      prohibited_claims: product.prohibited_claims ?? "",
      priority: product.priority,
      is_active: product.is_active,
    });
  }

  async function generateContent(event: FormEvent) {
    event.preventDefault();
    setGenerating(true);
    setError("");
    setGenerated(null);
    try {
      const result = await api.generateContent(generatorForm);
      setGenerated(result);
      setNotice("投稿案を生成しました。");
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : "生成に失敗しました。");
    } finally {
      setGenerating(false);
    }
  }

  async function saveGeneratedDraft() {
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
      risk_notes: toRiskText(generated.risk_notes),
      status,
      scheduled_at: null,
      posted_at: null,
    });
    setNotice("生成結果を下書きに保存しました。");
    await loadData();
    setPage("drafts");
  }

  async function updateDraftStatus(draft: Draft, status: DraftStatus) {
    await api.updateDraft(draft.id, { status });
    await loadData();
  }

  async function updateDraftSchedule(draft: Draft, scheduledAt: string) {
    await api.updateDraft(draft.id, { scheduled_at: scheduledAt || null });
    await loadData();
  }

  async function removeDraft(id: number) {
    await api.deleteDraft(id);
    setNotice("下書きを削除しました。");
    await loadData();
  }

  async function saveSettings(event: FormEvent) {
    event.preventDefault();
    const updated = await api.updateSettings(settingsForm);
    setSettings(updated);
    setSettingsForm((current) => ({ ...current, openai_api_key: "" }));
    setNotice("設定を保存しました。");
    await loadData();
  }

  const navItems = [
    { id: "dashboard", label: "Dashboard", icon: BarChart3 },
    { id: "knowledge", label: "Knowledge", icon: BookOpen },
    { id: "products", label: "Products", icon: Package },
    { id: "generator", label: "Generator", icon: Sparkles },
    { id: "drafts", label: "Drafts", icon: FileText },
    { id: "settings", label: "Settings", icon: SettingsIcon },
  ] as const;

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">PS</div>
          <div>
            <h1>PsyAffiliate Studio</h1>
            <span>Phase 1</span>
          </div>
        </div>
        <nav>
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                className={page === item.id ? "nav-item active" : "nav-item"}
                onClick={() => setPage(item.id)}
              >
                <Icon size={18} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </aside>

      <main className="workspace">
        <header className="topbar">
          <div>
            <p className="eyebrow">Ethical SNS Affiliate OS</p>
            <h2>{navItems.find((item) => item.id === page)?.label}</h2>
          </div>
          <button className="icon-button" title="再読み込み" onClick={loadData} disabled={loading}>
            <RefreshCw size={18} />
          </button>
        </header>

        {error && (
          <div className="alert error">
            <AlertTriangle size={18} />
            <span>{error}</span>
            <button title="閉じる" onClick={() => setError("")}>
              <X size={16} />
            </button>
          </div>
        )}
        {notice && (
          <div className="alert success">
            <CheckCircle2 size={18} />
            <span>{notice}</span>
            <button title="閉じる" onClick={() => setNotice("")}>
              <X size={16} />
            </button>
          </div>
        )}

        {page === "dashboard" && (
          <section className="page-grid">
            <div className="metrics">
              <Metric label="今日の下書き" value={dashboard?.today_drafts ?? 0} />
              <Metric label="承認待ち" value={dashboard?.pending_review ?? 0} tone="amber" />
              <Metric label="アクティブ商品" value={dashboard?.active_products ?? activeProducts.length} tone="teal" />
            </div>
            <section className="panel">
              <div className="panel-title">
                <h3>最近生成した投稿</h3>
                <FileText size={18} />
              </div>
              <div className="draft-list compact">
                {(dashboard?.recent_drafts ?? drafts.slice(0, 5)).map((draft) => (
                  <DraftCard
                    key={draft.id}
                    draft={draft}
                    onStatusChange={(status) => updateDraftStatus(draft, status)}
                    onScheduleChange={(value) => updateDraftSchedule(draft, value)}
                    onDelete={() => removeDraft(draft.id)}
                  />
                ))}
                {(dashboard?.recent_drafts ?? drafts).length === 0 && <EmptyState label="下書きはまだありません。" />}
              </div>
            </section>
          </section>
        )}

        {page === "knowledge" && (
          <section className="split-layout">
            <form className="panel form-panel" onSubmit={saveKnowledge}>
              <div className="panel-title">
                <h3>{editingKnowledgeId ? "ナレッジ編集" : "ナレッジ登録"}</h3>
                <BookOpen size={18} />
              </div>
              <label>
                title
                <input
                  value={knowledgeForm.title}
                  onChange={(event) => setKnowledgeForm({ ...knowledgeForm, title: event.target.value })}
                  required
                />
              </label>
              <label>
                category
                <select
                  value={knowledgeForm.category}
                  onChange={(event) => setKnowledgeForm({ ...knowledgeForm, category: event.target.value })}
                >
                  {knowledgeCategories.map((category) => (
                    <option key={category} value={category}>
                      {category}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                content
                <textarea
                  rows={8}
                  value={knowledgeForm.content}
                  onChange={(event) => setKnowledgeForm({ ...knowledgeForm, content: event.target.value })}
                  required
                />
              </label>
              <label>
                source
                <input
                  value={knowledgeForm.source ?? ""}
                  onChange={(event) => setKnowledgeForm({ ...knowledgeForm, source: event.target.value })}
                />
              </label>
              <div className="button-row">
                <button className="primary" type="submit">
                  {editingKnowledgeId ? <Save size={17} /> : <Plus size={17} />}
                  {editingKnowledgeId ? "更新" : "追加"}
                </button>
                {editingKnowledgeId && (
                  <button
                    type="button"
                    onClick={() => {
                      setEditingKnowledgeId(null);
                      setKnowledgeForm(emptyKnowledge);
                    }}
                  >
                    <X size={17} />
                    取消
                  </button>
                )}
              </div>
            </form>

            <section className="item-grid">
              {knowledge.map((item) => (
                <article className="card" key={item.id}>
                  <div className="card-header">
                    <div>
                      <span className="badge">{item.category}</span>
                      <h3>{item.title}</h3>
                    </div>
                    <div className="icon-actions">
                      <button title="編集" onClick={() => editKnowledge(item)}>
                        <Pencil size={16} />
                      </button>
                      <button title="削除" onClick={() => removeKnowledge(item.id)}>
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </div>
                  <p>{item.content}</p>
                  {item.source && <span className="muted">{item.source}</span>}
                </article>
              ))}
              {knowledge.length === 0 && <EmptyState label="ナレッジはまだありません。" />}
            </section>
          </section>
        )}

        {page === "products" && (
          <section className="split-layout wide-form">
            <form className="panel form-panel" onSubmit={saveProduct}>
              <div className="panel-title">
                <h3>{editingProductId ? "商品編集" : "商品登録"}</h3>
                <Package size={18} />
              </div>
              <div className="two-columns">
                <label>
                  name
                  <input
                    value={productForm.name}
                    onChange={(event) => setProductForm({ ...productForm, name: event.target.value })}
                    required
                  />
                </label>
                <label>
                  asp_name
                  <input
                    value={productForm.asp_name ?? ""}
                    onChange={(event) => setProductForm({ ...productForm, asp_name: event.target.value })}
                  />
                </label>
              </div>
              <label>
                affiliate_url
                <input
                  value={productForm.affiliate_url}
                  onChange={(event) => setProductForm({ ...productForm, affiliate_url: event.target.value })}
                  required
                />
              </label>
              <label>
                display_url
                <input
                  value={productForm.display_url ?? ""}
                  onChange={(event) => setProductForm({ ...productForm, display_url: event.target.value })}
                />
              </label>
              <div className="two-columns">
                <label>
                  category
                  <input
                    value={productForm.category ?? ""}
                    onChange={(event) => setProductForm({ ...productForm, category: event.target.value })}
                  />
                </label>
                <label>
                  target_pain
                  <input
                    value={productForm.target_pain ?? ""}
                    onChange={(event) => setProductForm({ ...productForm, target_pain: event.target.value })}
                  />
                </label>
              </div>
              <div className="two-columns">
                <label>
                  commission_type
                  <input
                    value={productForm.commission_type ?? ""}
                    onChange={(event) => setProductForm({ ...productForm, commission_type: event.target.value })}
                  />
                </label>
                <label>
                  commission_amount
                  <input
                    type="number"
                    value={productForm.commission_amount ?? ""}
                    onChange={(event) =>
                      setProductForm({
                        ...productForm,
                        commission_amount: event.target.value ? Number(event.target.value) : null,
                      })
                    }
                  />
                </label>
              </div>
              <label>
                prohibited_claims
                <textarea
                  rows={4}
                  value={productForm.prohibited_claims ?? ""}
                  onChange={(event) => setProductForm({ ...productForm, prohibited_claims: event.target.value })}
                />
              </label>
              <div className="two-columns compact-controls">
                <label>
                  priority
                  <input
                    type="number"
                    value={productForm.priority}
                    onChange={(event) => setProductForm({ ...productForm, priority: Number(event.target.value) })}
                  />
                </label>
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={productForm.is_active}
                    onChange={(event) => setProductForm({ ...productForm, is_active: event.target.checked })}
                  />
                  is_active
                </label>
              </div>
              <div className="button-row">
                <button className="primary" type="submit">
                  {editingProductId ? <Save size={17} /> : <Plus size={17} />}
                  {editingProductId ? "更新" : "追加"}
                </button>
                {editingProductId && (
                  <button
                    type="button"
                    onClick={() => {
                      setEditingProductId(null);
                      setProductForm(emptyProduct);
                    }}
                  >
                    <X size={17} />
                    取消
                  </button>
                )}
              </div>
            </form>

            <section className="item-grid">
              {products.map((product) => (
                <article className="card product-card" key={product.id}>
                  <div className="card-header">
                    <div>
                      <span className={product.is_active ? "badge green" : "badge muted-badge"}>
                        {product.is_active ? "active" : "inactive"}
                      </span>
                      <h3>{product.name}</h3>
                    </div>
                    <div className="icon-actions">
                      <button title="編集" onClick={() => editProduct(product)}>
                        <Pencil size={16} />
                      </button>
                      <button title="削除" onClick={() => removeProduct(product.id)}>
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </div>
                  <dl>
                    <div>
                      <dt>ASP</dt>
                      <dd>{product.asp_name || "-"}</dd>
                    </div>
                    <div>
                      <dt>カテゴリ</dt>
                      <dd>{product.category || "-"}</dd>
                    </div>
                    <div>
                      <dt>悩み</dt>
                      <dd>{product.target_pain || "-"}</dd>
                    </div>
                    <div>
                      <dt>優先度</dt>
                      <dd>{product.priority}</dd>
                    </div>
                  </dl>
                  <p className="url-text">{product.display_url || product.affiliate_url}</p>
                  {product.prohibited_claims && <p className="risk-text">{product.prohibited_claims}</p>}
                </article>
              ))}
              {products.length === 0 && <EmptyState label="商品はまだありません。" />}
            </section>
          </section>
        )}

        {page === "generator" && (
          <section className="generator-layout">
            <form className="panel form-panel" onSubmit={generateContent}>
              <div className="panel-title">
                <h3>Content Generator</h3>
                <Sparkles size={18} />
              </div>
              <label>
                theme
                <input
                  value={generatorForm.theme}
                  onChange={(event) => setGeneratorForm({ ...generatorForm, theme: event.target.value })}
                  required
                />
              </label>
              <label>
                target_reader
                <input
                  value={generatorForm.target_reader}
                  onChange={(event) => setGeneratorForm({ ...generatorForm, target_reader: event.target.value })}
                  required
                />
              </label>
              <div className="two-columns">
                <label>
                  platform
                  <select
                    value={generatorForm.platform}
                    onChange={(event) => setGeneratorForm({ ...generatorForm, platform: event.target.value as Platform })}
                  >
                    <option value="threads">threads</option>
                    <option value="instagram">instagram</option>
                    <option value="both">both</option>
                  </select>
                </label>
                <label>
                  tone
                  <select
                    value={generatorForm.tone}
                    onChange={(event) => setGeneratorForm({ ...generatorForm, tone: event.target.value as Tone })}
                  >
                    <option value="empathy">empathy</option>
                    <option value="practical">practical</option>
                    <option value="story">story</option>
                    <option value="educational">educational</option>
                    <option value="soft_sales">soft_sales</option>
                  </select>
                </label>
              </div>
              <label>
                selected_product_id
                <select
                  value={generatorForm.selected_product_id ?? ""}
                  onChange={(event) =>
                    setGeneratorForm({
                      ...generatorForm,
                      selected_product_id: event.target.value ? Number(event.target.value) : null,
                    })
                  }
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
                  <button className="primary" onClick={saveGeneratedDraft}>
                    <Save size={17} />
                    下書き保存
                  </button>
                </div>
              ) : (
                <EmptyState label="生成結果はここに表示されます。" />
              )}
            </section>
          </section>
        )}

        {page === "drafts" && (
          <section className="panel full-panel">
            <div className="panel-title">
              <h3>投稿下書き</h3>
              <button className="secondary" onClick={() => window.open(`${API_BASE}/api/drafts/export.csv`, "_blank")}>
                <Download size={17} />
                CSV
              </button>
            </div>
            <div className="draft-list">
              {drafts.map((draft) => (
                <DraftCard
                  key={draft.id}
                  draft={draft}
                  onStatusChange={(status) => updateDraftStatus(draft, status)}
                  onScheduleChange={(value) => updateDraftSchedule(draft, value)}
                  onDelete={() => removeDraft(draft.id)}
                />
              ))}
              {drafts.length === 0 && <EmptyState label="下書きはまだありません。" />}
            </div>
          </section>
        )}

        {page === "settings" && (
          <section className="settings-layout">
            <form className="panel form-panel" onSubmit={saveSettings}>
              <div className="panel-title">
                <h3>Settings</h3>
                <SettingsIcon size={18} />
              </div>
              <label>
                OPENAI_API_KEY
                <input
                  type="password"
                  value={settingsForm.openai_api_key}
                  placeholder={settings.openai_api_key_set ? "設定済み" : ""}
                  onChange={(event) => setSettingsForm({ ...settingsForm, openai_api_key: event.target.value })}
                />
              </label>
              <label>
                OPENAI_MODEL
                <input
                  value={settingsForm.openai_model}
                  onChange={(event) => setSettingsForm({ ...settingsForm, openai_model: event.target.value })}
                />
              </label>
              <label>
                default_platform
                <select
                  value={settingsForm.default_platform}
                  onChange={(event) =>
                    setSettingsForm({ ...settingsForm, default_platform: event.target.value as Platform })
                  }
                >
                  <option value="threads">threads</option>
                  <option value="instagram">instagram</option>
                  <option value="both">both</option>
                </select>
              </label>
              <label>
                default_pr_disclosure
                <input
                  value={settingsForm.default_pr_disclosure}
                  onChange={(event) => setSettingsForm({ ...settingsForm, default_pr_disclosure: event.target.value })}
                />
              </label>
              <label>
                brand_voice_summary
                <textarea
                  rows={5}
                  value={settingsForm.brand_voice_summary}
                  onChange={(event) => setSettingsForm({ ...settingsForm, brand_voice_summary: event.target.value })}
                />
              </label>
              <button className="primary" type="submit">
                <Save size={17} />
                保存
              </button>
            </form>
            <section className="panel">
              <div className="panel-title">
                <h3>Runtime</h3>
                <ShieldCheck size={18} />
              </div>
              <dl className="settings-readout">
                <div>
                  <dt>API Key</dt>
                  <dd>{settings.openai_api_key_set ? "set" : "not set"}</dd>
                </div>
                <div>
                  <dt>Model</dt>
                  <dd>{settings.openai_model}</dd>
                </div>
                <div>
                  <dt>PR</dt>
                  <dd>{settings.default_pr_disclosure}</dd>
                </div>
              </dl>
            </section>
          </section>
        )}
      </main>
    </div>
  );
}

function Metric({ label, value, tone = "blue" }: { label: string; value: number; tone?: "blue" | "amber" | "teal" }) {
  return (
    <article className={`metric ${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
    </article>
  );
}

function DraftCard({
  draft,
  onStatusChange,
  onScheduleChange,
  onDelete,
}: {
  draft: Draft;
  onStatusChange: (status: DraftStatus) => void;
  onScheduleChange: (value: string) => void;
  onDelete: () => void;
}) {
  return (
    <article className="draft-card">
      <div className="draft-head">
        <div>
          <span className="badge">{draft.platform}</span>
          <h3>{draft.theme}</h3>
        </div>
        <span className={scoreClass(draft.compliance_score)}>{draft.compliance_score ?? "-"}</span>
      </div>
      <p>{draft.body}</p>
      {draft.caption && <p className="caption-text">{draft.caption}</p>}
      {draft.cta && <p className="cta-text">{draft.cta}</p>}
      {riskLines(draft.risk_notes).length > 0 && (
        <div className="note-list">
          {riskLines(draft.risk_notes).map((note) => (
            <span key={note}>{note}</span>
          ))}
        </div>
      )}
      <div className="draft-controls">
        <select value={draft.status} onChange={(event) => onStatusChange(event.target.value as DraftStatus)}>
          {statusOptions.map((status) => (
            <option key={status} value={status}>
              {status}
            </option>
          ))}
        </select>
        <input
          type="datetime-local"
          value={draft.scheduled_at ? draft.scheduled_at.slice(0, 16) : ""}
          onChange={(event) => onScheduleChange(event.target.value)}
        />
        <span className="muted">{formatDate(draft.created_at)}</span>
        <button title="削除" onClick={onDelete}>
          <Trash2 size={16} />
        </button>
      </div>
    </article>
  );
}

function EmptyState({ label }: { label: string }) {
  return (
    <div className="empty-state">
      <FileText size={22} />
      <span>{label}</span>
    </div>
  );
}

export default App;
