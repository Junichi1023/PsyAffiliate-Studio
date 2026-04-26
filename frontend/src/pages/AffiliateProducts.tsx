import { FormEvent, useEffect, useState } from "react";
import { Package, Pencil, Plus, Save, Trash2, X } from "lucide-react";
import { api } from "../api/client";
import { AffiliateProduct, AffiliateProductPayload } from "../types";
import { EmptyState } from "./shared";

const emptyForm: AffiliateProductPayload = {
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

export default function AffiliateProducts() {
  const [products, setProducts] = useState<AffiliateProduct[]>([]);
  const [form, setForm] = useState<AffiliateProductPayload>(emptyForm);
  const [editingId, setEditingId] = useState<number | null>(null);

  async function load() {
    setProducts(await api.listProducts());
  }

  useEffect(() => {
    load();
  }, []);

  async function save(event: FormEvent) {
    event.preventDefault();
    if (editingId) {
      await api.updateProduct(editingId, form);
    } else {
      await api.createProduct(form);
    }
    setForm(emptyForm);
    setEditingId(null);
    await load();
  }

  function edit(product: AffiliateProduct) {
    setEditingId(product.id);
    setForm({
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

  return (
    <section className="split-layout wide-form">
      <form className="panel form-panel" onSubmit={save}>
        <div className="panel-title">
          <h3>{editingId ? "商品編集" : "商品登録"}</h3>
          <Package size={18} />
        </div>
        <div className="two-columns">
          <label>
            商品名
            <input value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} required />
          </label>
          <label>
            ASP
            <input value={form.asp_name ?? ""} onChange={(event) => setForm({ ...form, asp_name: event.target.value })} />
          </label>
        </div>
        <label>
          アフィリエイトURL
          <input value={form.affiliate_url} onChange={(event) => setForm({ ...form, affiliate_url: event.target.value })} required />
        </label>
        <label>
          表示URL
          <input value={form.display_url ?? ""} onChange={(event) => setForm({ ...form, display_url: event.target.value })} />
        </label>
        <div className="two-columns">
          <label>
            カテゴリ
            <input value={form.category ?? ""} onChange={(event) => setForm({ ...form, category: event.target.value })} />
          </label>
          <label>
            悩み
            <input value={form.target_pain ?? ""} onChange={(event) => setForm({ ...form, target_pain: event.target.value })} />
          </label>
        </div>
        <div className="two-columns">
          <label>
            報酬タイプ
            <input value={form.commission_type ?? ""} onChange={(event) => setForm({ ...form, commission_type: event.target.value })} />
          </label>
          <label>
            報酬額
            <input
              type="number"
              value={form.commission_amount ?? ""}
              onChange={(event) => setForm({ ...form, commission_amount: event.target.value ? Number(event.target.value) : null })}
            />
          </label>
        </div>
        <label>
          禁止訴求
          <textarea rows={4} value={form.prohibited_claims ?? ""} onChange={(event) => setForm({ ...form, prohibited_claims: event.target.value })} />
        </label>
        <div className="two-columns compact-controls">
          <label>
            優先度
            <input type="number" value={form.priority} onChange={(event) => setForm({ ...form, priority: Number(event.target.value) })} />
          </label>
          <label className="checkbox-label">
            <input type="checkbox" checked={form.is_active} onChange={(event) => setForm({ ...form, is_active: event.target.checked })} />
            active
          </label>
        </div>
        <div className="button-row">
          <button className="primary" type="submit">
            {editingId ? <Save size={17} /> : <Plus size={17} />}
            {editingId ? "更新" : "追加"}
          </button>
          {editingId && (
            <button type="button" onClick={() => { setEditingId(null); setForm(emptyForm); }}>
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
                <span className={product.is_active ? "badge green" : "badge muted-badge"}>{product.is_active ? "active" : "inactive"}</span>
                <h3>{product.name}</h3>
              </div>
              <div className="icon-actions">
                <button title="編集" onClick={() => edit(product)}>
                  <Pencil size={16} />
                </button>
                <button title="削除" onClick={async () => { await api.deleteProduct(product.id); await load(); }}>
                  <Trash2 size={16} />
                </button>
              </div>
            </div>
            <dl>
              <div><dt>ASP</dt><dd>{product.asp_name || "-"}</dd></div>
              <div><dt>カテゴリ</dt><dd>{product.category || "-"}</dd></div>
              <div><dt>悩み</dt><dd>{product.target_pain || "-"}</dd></div>
              <div><dt>優先度</dt><dd>{product.priority}</dd></div>
            </dl>
            <p className="url-text">{product.display_url || product.affiliate_url}</p>
            {product.prohibited_claims && <p className="risk-text">{product.prohibited_claims}</p>}
          </article>
        ))}
        {products.length === 0 && <EmptyState label="商品はまだありません。" />}
      </section>
    </section>
  );
}
