import { FormEvent, useEffect, useState } from "react";
import { BookOpen, Pencil, Plus, Save, Trash2, X } from "lucide-react";
import { api } from "../api/client";
import { KnowledgeItem, KnowledgePayload } from "../types";
import { EmptyState } from "./shared";

const categories = [
  "profile",
  "brand_voice",
  "psychology",
  "ai_prompt",
  "prohibited_expression",
  "past_post",
  "note_article",
  "fortune_telling_method",
  "tarot_reading",
  "astrology",
  "numerology",
  "oracle_card",
  "money_luck",
  "love_luck",
  "work_luck",
  "relationship_worry",
  "spiritual_expression",
  "fortune_disclaimer",
  "affiliate_offer",
  "cta_template",
  "persona_pain",
  "threads_hook",
];
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
        <label>
          タイトル
          <input value={form.title} onChange={(event) => setForm({ ...form, title: event.target.value })} required />
        </label>
        <label>
          カテゴリ
          <select value={form.category} onChange={(event) => setForm({ ...form, category: event.target.value })}>
            {categories.map((category) => (
              <option key={category} value={category}>
                {category}
              </option>
            ))}
          </select>
        </label>
        <label>
          内容
          <textarea rows={8} value={form.content} onChange={(event) => setForm({ ...form, content: event.target.value })} required />
        </label>
        <label>
          source
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
                <span className="badge">{item.category}</span>
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
