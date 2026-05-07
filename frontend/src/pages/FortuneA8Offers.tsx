import { FormEvent, useEffect, useState } from "react";
import { Package, Plus, Save, Trash2 } from "lucide-react";
import { api, FortuneA8Offer, FortuneA8OfferPayload } from "../api/client";
import { EmptyState } from "./shared";

const emptyForm: FortuneA8OfferPayload = {
  offer_name: "",
  advertiser_name: "",
  service_type: "phone_fortune",
  affiliate_url: "",
  lp_url: "",
  reward_amount: null,
  conversion_condition: "",
  rejection_conditions: "",
  first_time_bonus: "",
  consultation_genres: "",
  lp_impression: "",
  approval_rate: "",
  recommended_use: "",
  prohibited_claims: "",
  is_active: true,
};

export default function FortuneA8Offers() {
  const [items, setItems] = useState<FortuneA8Offer[]>([]);
  const [form, setForm] = useState<FortuneA8OfferPayload>(emptyForm);
  const [editingId, setEditingId] = useState<number | null>(null);

  async function load() {
    setItems(await api.listFortuneA8Offers());
  }

  useEffect(() => { load(); }, []);

  async function save(event: FormEvent) {
    event.preventDefault();
    if (editingId) await api.updateFortuneA8Offer(editingId, form);
    else await api.createFortuneA8Offer(form);
    setForm(emptyForm);
    setEditingId(null);
    await load();
  }

  function edit(item: FortuneA8Offer) {
    setEditingId(item.id);
    setForm({ ...emptyForm, ...item });
  }

  return (
    <section className="split-layout wide-form">
      <form className="panel form-panel" onSubmit={save}>
        <div className="panel-title"><h3>{editingId ? "A8占い案件を編集" : "A8占い案件を登録"}</h3><Package size={18} /></div>
        <p className="page-description compact">Threads本文にはこのURLを直接貼らず、note記事内で使用してください。成果条件、否認条件、禁止訴求を必ず残します。</p>
        <label>案件名<input required value={form.offer_name} onChange={(e) => setForm({ ...form, offer_name: e.target.value })} /></label>
        <div className="two-columns">
          <label>広告主<input value={form.advertiser_name ?? ""} onChange={(e) => setForm({ ...form, advertiser_name: e.target.value })} /></label>
          <label>サービス種別<input value={form.service_type ?? ""} onChange={(e) => setForm({ ...form, service_type: e.target.value })} /></label>
        </div>
        <label>A8広告URL（note内のみ）<input value={form.affiliate_url ?? ""} onChange={(e) => setForm({ ...form, affiliate_url: e.target.value })} /></label>
        <label>LP URL<input value={form.lp_url ?? ""} onChange={(e) => setForm({ ...form, lp_url: e.target.value })} /></label>
        <div className="two-columns">
          <label>報酬額<input type="number" value={form.reward_amount ?? ""} onChange={(e) => setForm({ ...form, reward_amount: e.target.value ? Number(e.target.value) : null })} /></label>
          <label className="checkbox-label"><input type="checkbox" checked={form.is_active} onChange={(e) => setForm({ ...form, is_active: e.target.checked })} />有効</label>
        </div>
        <label>成果条件<textarea rows={3} value={form.conversion_condition ?? ""} onChange={(e) => setForm({ ...form, conversion_condition: e.target.value })} /></label>
        <label>否認条件<textarea rows={3} value={form.rejection_conditions ?? ""} onChange={(e) => setForm({ ...form, rejection_conditions: e.target.value })} /></label>
        <label>禁止訴求<textarea rows={3} value={form.prohibited_claims ?? ""} onChange={(e) => setForm({ ...form, prohibited_claims: e.target.value })} /></label>
        <button className="primary" type="submit">{editingId ? <Save size={17} /> : <Plus size={17} />}{editingId ? "更新" : "追加"}</button>
      </form>

      <section className="item-grid">
        {items.map((item) => (
          <article className="card product-card" key={item.id}>
            <div className="card-header">
              <div><span className={item.is_active ? "badge green" : "badge muted-badge"}>{item.is_active ? "有効" : "無効"}</span><h3>{item.offer_name}</h3></div>
              <div className="icon-actions"><button onClick={() => edit(item)}>編集</button><button onClick={async () => { await api.deleteFortuneA8Offer(item.id); await load(); }}><Trash2 size={16} /></button></div>
            </div>
            <dl>
              <div><dt>サービス種別</dt><dd>{item.service_type || "-"}</dd></div>
              <div><dt>報酬額</dt><dd>{item.reward_amount ?? "-"}</dd></div>
              <div><dt>相談ジャンル</dt><dd>{item.consultation_genres || "-"}</dd></div>
            </dl>
            {item.prohibited_claims && <p className="risk-text">{item.prohibited_claims}</p>}
          </article>
        ))}
        {items.length === 0 && <EmptyState label="A8占い案件はまだありません。" />}
      </section>
    </section>
  );
}
