import { FormEvent, useEffect, useState } from "react";
import { Link, Plus, Save, Trash2 } from "lucide-react";
import { api, NoteFunnelPage, NoteFunnelPagePayload } from "../api/client";
import { EmptyState } from "./shared";

const emptyForm: NoteFunnelPagePayload = {
  title: "",
  note_url: "",
  purpose: "",
  target_theme: "",
  target_reader: "",
  article_type: "first_time_guide",
  pr_disclosure: "【PR】",
  status: "idea",
  memo: "",
};

export default function NoteFunnelPages() {
  const [items, setItems] = useState<NoteFunnelPage[]>([]);
  const [form, setForm] = useState<NoteFunnelPagePayload>(emptyForm);
  const [editingId, setEditingId] = useState<number | null>(null);

  async function load() {
    setItems(await api.listNoteFunnelPages());
  }

  useEffect(() => {
    load();
  }, []);

  async function save(event: FormEvent) {
    event.preventDefault();
    if (editingId) await api.updateNoteFunnelPage(editingId, form);
    else await api.createNoteFunnelPage(form);
    setForm(emptyForm);
    setEditingId(null);
    await load();
  }

  function edit(item: NoteFunnelPage) {
    setEditingId(item.id);
    setForm({ ...emptyForm, ...item });
  }

  return (
    <section className="split-layout wide-form">
      <form className="panel form-panel" onSubmit={save}>
        <div className="panel-title">
          <h3>{editingId ? "note記事を編集" : "note導線を登録"}</h3>
          <Link size={18} />
        </div>
        <p className="page-description compact">
          Threads投稿はA8リンクに直接送らず、このnote記事へ誘導します。note記事内で電話占い・占いアプリ案件を注意点や質問例と一緒に紹介してください。
        </p>
        <label>note記事タイトル<input required value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} /></label>
        <label>note URL<input required value={form.note_url} onChange={(e) => setForm({ ...form, note_url: e.target.value })} /></label>
        <div className="two-columns">
          <label>記事タイプ<input value={form.article_type ?? ""} onChange={(e) => setForm({ ...form, article_type: e.target.value })} /></label>
          <label>status<input value={form.status ?? ""} onChange={(e) => setForm({ ...form, status: e.target.value })} /></label>
        </div>
        <label>対象悩み<input value={form.target_theme ?? ""} onChange={(e) => setForm({ ...form, target_theme: e.target.value })} /></label>
        <label>PR表記<input value={form.pr_disclosure ?? ""} onChange={(e) => setForm({ ...form, pr_disclosure: e.target.value })} /></label>
        <label>目的<textarea rows={3} value={form.purpose ?? ""} onChange={(e) => setForm({ ...form, purpose: e.target.value })} /></label>
        <button className="primary" type="submit">{editingId ? <Save size={17} /> : <Plus size={17} />}{editingId ? "更新" : "追加"}</button>
      </form>

      <section className="item-grid">
        {items.map((item) => (
          <article className="card" key={item.id}>
            <div className="card-header">
              <div><span className="badge">{item.status}</span><h3>{item.title}</h3></div>
              <div className="icon-actions">
                <button onClick={() => edit(item)}>編集</button>
                <button onClick={async () => { await api.deleteNoteFunnelPage(item.id); await load(); }}><Trash2 size={16} /></button>
              </div>
            </div>
            <p className="url-text">{item.note_url}</p>
            <p>{item.purpose}</p>
          </article>
        ))}
        {items.length === 0 && <EmptyState label="note導線はまだありません。" />}
      </section>
    </section>
  );
}
