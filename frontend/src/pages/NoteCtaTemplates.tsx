import { FormEvent, useEffect, useState } from "react";
import { ListChecks, Plus, Save, Trash2 } from "lucide-react";
import { api, NoteCtaTemplate, NoteCtaTemplatePayload, NoteFunnelPage } from "../api/client";
import { EmptyState } from "./shared";

const emptyForm: NoteCtaTemplatePayload = {
  name: "",
  cta_type: "profile_note",
  text: "",
  target_note_page_id: null,
  use_pr_disclosure: true,
};

export default function NoteCtaTemplates() {
  const [items, setItems] = useState<NoteCtaTemplate[]>([]);
  const [pages, setPages] = useState<NoteFunnelPage[]>([]);
  const [form, setForm] = useState<NoteCtaTemplatePayload>(emptyForm);
  const [editingId, setEditingId] = useState<number | null>(null);

  async function load() {
    setItems(await api.listNoteCtaTemplates());
    setPages(await api.listNoteFunnelPages());
  }
  useEffect(() => { load(); }, []);

  async function save(event: FormEvent) {
    event.preventDefault();
    if (editingId) await api.updateNoteCtaTemplate(editingId, form);
    else await api.createNoteCtaTemplate(form);
    setForm(emptyForm);
    setEditingId(null);
    await load();
  }

  function edit(item: NoteCtaTemplate) {
    setEditingId(item.id);
    setForm({ ...emptyForm, ...item });
  }

  return (
    <section className="split-layout">
      <form className="panel form-panel" onSubmit={save}>
        <div className="panel-title"><h3>{editingId ? "CTA編集" : "CTA登録"}</h3><ListChecks size={18} /></div>
        <p className="page-description compact">Threadsから直接A8へ送らず、プロフィールのnoteへ自然に誘導する言い回しを管理します。</p>
        <label>CTA名<input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></label>
        <label>CTAタイプ<input value={form.cta_type} onChange={(e) => setForm({ ...form, cta_type: e.target.value })} /></label>
        <label>本文<textarea required rows={4} value={form.text} onChange={(e) => setForm({ ...form, text: e.target.value })} /></label>
        <label>誘導先note
          <select value={form.target_note_page_id ?? ""} onChange={(e) => setForm({ ...form, target_note_page_id: e.target.value ? Number(e.target.value) : null })}>
            <option value="">指定なし</option>
            {pages.map((page) => <option key={page.id} value={page.id}>{page.title}</option>)}
          </select>
        </label>
        <label className="checkbox-label"><input type="checkbox" checked={form.use_pr_disclosure} onChange={(e) => setForm({ ...form, use_pr_disclosure: e.target.checked })} />PR表記を使う</label>
        <button className="primary" type="submit">{editingId ? <Save size={17} /> : <Plus size={17} />}{editingId ? "更新" : "追加"}</button>
      </form>
      <section className="item-grid">
        {items.map((item) => (
          <article className="card" key={item.id}>
            <div className="card-header">
              <div><span className="badge">{item.cta_type}</span><h3>{item.name}</h3></div>
              <div className="icon-actions"><button onClick={() => edit(item)}>編集</button><button onClick={async () => { await api.deleteNoteCtaTemplate(item.id); await load(); }}><Trash2 size={16} /></button></div>
            </div>
            <p>{item.text}</p>
          </article>
        ))}
        {items.length === 0 && <EmptyState label="CTAはまだありません。" />}
      </section>
    </section>
  );
}
