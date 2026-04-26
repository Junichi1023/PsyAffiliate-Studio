import { FormEvent, useEffect, useState } from "react";
import { Pencil, Plus, Save, Trash2, Users, X } from "lucide-react";
import { api } from "../api/client";
import { PersonaPain, PersonaPainPayload } from "../types";
import { EmptyState } from "./shared";

const categories = ["money", "love", "work", "relationship", "future", "self_confidence"];
const emptyForm: PersonaPainPayload = {
  name: "",
  category: "money",
  pain_summary: "",
  emotional_state: "",
  desired_future: "",
  forbidden_approach: "",
  recommended_tone: "",
};

export default function PersonaPains() {
  const [items, setItems] = useState<PersonaPain[]>([]);
  const [form, setForm] = useState<PersonaPainPayload>(emptyForm);
  const [editingId, setEditingId] = useState<number | null>(null);

  async function load() {
    setItems(await api.listPersonaPains());
  }

  useEffect(() => {
    load();
  }, []);

  async function save(event: FormEvent) {
    event.preventDefault();
    if (editingId) {
      await api.updatePersonaPain(editingId, form);
    } else {
      await api.createPersonaPain(form);
    }
    setForm(emptyForm);
    setEditingId(null);
    await load();
  }

  function edit(item: PersonaPain) {
    setEditingId(item.id);
    setForm({
      name: item.name,
      category: item.category,
      pain_summary: item.pain_summary,
      emotional_state: item.emotional_state ?? "",
      desired_future: item.desired_future ?? "",
      forbidden_approach: item.forbidden_approach ?? "",
      recommended_tone: item.recommended_tone ?? "",
    });
  }

  return (
    <section className="split-layout">
      <form className="panel form-panel" onSubmit={save}>
        <div className="panel-title">
          <h3>{editingId ? "ペルソナ編集" : "悩みペルソナ登録"}</h3>
          <Users size={18} />
        </div>
        <label>
          名前
          <input value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} required />
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
          悩みの概要
          <textarea rows={4} value={form.pain_summary} onChange={(event) => setForm({ ...form, pain_summary: event.target.value })} required />
        </label>
        <label>
          感情状態
          <input value={form.emotional_state ?? ""} onChange={(event) => setForm({ ...form, emotional_state: event.target.value })} />
        </label>
        <label>
          望む未来
          <input value={form.desired_future ?? ""} onChange={(event) => setForm({ ...form, desired_future: event.target.value })} />
        </label>
        <label>
          避ける接し方
          <textarea rows={3} value={form.forbidden_approach ?? ""} onChange={(event) => setForm({ ...form, forbidden_approach: event.target.value })} />
        </label>
        <label>
          推奨トーン
          <input value={form.recommended_tone ?? ""} onChange={(event) => setForm({ ...form, recommended_tone: event.target.value })} />
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
                <h3>{item.name}</h3>
              </div>
              <div className="icon-actions">
                <button title="編集" onClick={() => edit(item)}>
                  <Pencil size={16} />
                </button>
                <button title="削除" onClick={async () => { await api.deletePersonaPain(item.id); await load(); }}>
                  <Trash2 size={16} />
                </button>
              </div>
            </div>
            <p>{item.pain_summary}</p>
            {item.emotional_state && <p className="caption-text">{item.emotional_state}</p>}
            {item.forbidden_approach && <p className="risk-text">{item.forbidden_approach}</p>}
          </article>
        ))}
        {items.length === 0 && <EmptyState label="悩みペルソナはまだありません。" />}
      </section>
    </section>
  );
}
