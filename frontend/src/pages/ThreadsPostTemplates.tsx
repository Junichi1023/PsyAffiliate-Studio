import { FormEvent, useEffect, useState } from "react";
import { LayoutTemplate, Plus, Save, Trash2 } from "lucide-react";
import { api, ThreadsPostTemplate, ThreadsPostTemplatePayload } from "../api/client";
import { EmptyState } from "./shared";

const emptyForm: ThreadsPostTemplatePayload = {
  name: "",
  template_type: "empathy",
  target_theme: "",
  structure: "",
  example_post: "",
  cta_style: "soft_profile_note",
  prohibited_patterns: "",
};

export default function ThreadsPostTemplates() {
  const [items, setItems] = useState<ThreadsPostTemplate[]>([]);
  const [form, setForm] = useState<ThreadsPostTemplatePayload>(emptyForm);
  const [editingId, setEditingId] = useState<number | null>(null);

  async function load() { setItems(await api.listThreadsPostTemplates()); }
  useEffect(() => { load(); }, []);

  async function save(event: FormEvent) {
    event.preventDefault();
    if (editingId) await api.updateThreadsPostTemplate(editingId, form);
    else await api.createThreadsPostTemplate(form);
    setForm(emptyForm);
    setEditingId(null);
    await load();
  }

  function edit(item: ThreadsPostTemplate) {
    setEditingId(item.id);
    setForm({ ...emptyForm, ...item });
  }

  return (
    <section className="split-layout wide-form">
      <form className="panel form-panel" onSubmit={save}>
        <div className="panel-title"><h3>{editingId ? "テンプレート編集" : "Threads投稿テンプレート登録"}</h3><LayoutTemplate size={18} /></div>
        <p className="page-description compact">恋愛・復縁・片思いの悩みに寄り添うThreads投稿の型を管理します。A8直リンクや断定復縁表現は入れません。</p>
        <label>テンプレート名<input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></label>
        <div className="two-columns">
          <label>投稿タイプ<input value={form.template_type} onChange={(e) => setForm({ ...form, template_type: e.target.value })} /></label>
          <label>対象テーマ<input value={form.target_theme ?? ""} onChange={(e) => setForm({ ...form, target_theme: e.target.value })} /></label>
        </div>
        <label>投稿構成<textarea required rows={7} value={form.structure} onChange={(e) => setForm({ ...form, structure: e.target.value })} /></label>
        <label>例文<textarea rows={6} value={form.example_post ?? ""} onChange={(e) => setForm({ ...form, example_post: e.target.value })} /></label>
        <label>禁止パターン<textarea rows={3} value={form.prohibited_patterns ?? ""} onChange={(e) => setForm({ ...form, prohibited_patterns: e.target.value })} /></label>
        <button className="primary" type="submit">{editingId ? <Save size={17} /> : <Plus size={17} />}{editingId ? "更新" : "追加"}</button>
      </form>
      <section className="item-grid">
        {items.map((item) => (
          <article className="card" key={item.id}>
            <div className="card-header">
              <div><span className="badge">{item.template_type}</span><h3>{item.name}</h3></div>
              <div className="icon-actions"><button onClick={() => edit(item)}>編集</button><button onClick={async () => { await api.deleteThreadsPostTemplate(item.id); await load(); }}><Trash2 size={16} /></button></div>
            </div>
            <pre>{item.structure}</pre>
            {item.prohibited_patterns && <p className="risk-text">{item.prohibited_patterns}</p>}
          </article>
        ))}
        {items.length === 0 && <EmptyState label="Threads投稿テンプレートはまだありません。" />}
      </section>
    </section>
  );
}
