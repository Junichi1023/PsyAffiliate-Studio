import { FormEvent, useEffect, useState } from "react";
import { BookOpen, Pencil, Plus, Save, Trash2, X } from "lucide-react";
import { api } from "../api/client";
import { genericLabel, KNOWLEDGE_CATEGORY_LABELS } from "../constants/labels";
import { KnowledgeItem, KnowledgePayload } from "../types";
import { EmptyState } from "./shared";

const categories = Object.entries(KNOWLEDGE_CATEGORY_LABELS);
const emptyForm: KnowledgePayload = { title: "", category: "psychology", content: "", source: "" };

export default function Knowledge() {
  const [items, setItems] = useState<KnowledgeItem[]>([]);
  const [form, setForm] = useState<KnowledgePayload>(emptyForm);
  const [editingId, setEditingId] = useState<number | null>(null);

  async function load() {
    setItems(await api.listKnowledge());
  }

  useEffect(() => {
    load();
  }, []);

  async function save(event: FormEvent) {
    event.preventDefault();
    if (editingId) {
      await api.updateKnowledge(editingId, form);
    } else {
      await api.createKnowledge(form);
    }
    setForm(emptyForm);
    setEditingId(null);
    await load();
  }

  return (
    <section className="split-layout">
      <form className="panel form-panel" onSubmit={save}>
        <div className="panel-title">
          <h3>{editingId ? "ナレッジ編集" : "ナレッジ登録"}</h3>
          <BookOpen size={18} />
        </div>
        <p className="page-description compact">
          占いノウハウ、投稿の口調、禁止表現、過去の反応が良かった投稿などを登録します。
          占いの知識だけでなく、読者の悩み、投稿の冒頭フック、商品紹介の言い回しもナレッジとして登録してください。
        </p>
        <label>
          タイトル
          <input value={form.title} onChange={(event) => setForm({ ...form, title: event.target.value })} required />
        </label>
        <label>
          カテゴリ
          <select value={form.category} onChange={(event) => setForm({ ...form, category: event.target.value })}>
            {categories.map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </label>
        <label>
          内容
          <textarea rows={8} value={form.content} onChange={(event) => setForm({ ...form, content: event.target.value })} required />
        </label>
        <label>
          情報元
          <input value={form.source ?? ""} onChange={(event) => setForm({ ...form, source: event.target.value })} />
        </label>
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
        {items.map((item) => (
          <article className="card" key={item.id}>
            <div className="card-header">
              <div>
                <span className="badge">{genericLabel(KNOWLEDGE_CATEGORY_LABELS, item.category)}</span>
                <h3>{item.title}</h3>
              </div>
              <div className="icon-actions">
                <button title="編集" onClick={() => { setEditingId(item.id); setForm({ title: item.title, category: item.category, content: item.content, source: item.source ?? "" }); }}>
                  <Pencil size={16} />
                </button>
                <button title="削除" onClick={async () => { await api.deleteKnowledge(item.id); await load(); }}>
                  <Trash2 size={16} />
                </button>
              </div>
            </div>
            <p>{item.content}</p>
            {item.source && <span className="muted">{item.source}</span>}
          </article>
        ))}
        {items.length === 0 && <EmptyState label="ナレッジはまだありません。" />}
      </section>
    </section>
  );
}
