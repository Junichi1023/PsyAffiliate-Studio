import { FormEvent, useEffect, useState } from "react";
import { LayoutTemplate, Pencil, Plus, Save, Trash2, X } from "lucide-react";
import { api } from "../api/client";
import { FORTUNE_TYPE_LABELS, genericLabel, PERSONA_CATEGORY_LABELS } from "../constants/labels";
import { FortuneTemplate, FortuneTemplatePayload } from "../types";
import { EmptyState } from "./shared";

const fortuneTypes = Object.entries(FORTUNE_TYPE_LABELS);
const personaCategories = Object.entries(PERSONA_CATEGORY_LABELS);
const emptyForm: FortuneTemplatePayload = {
  name: "",
  fortune_type: "tarot",
  target_pain_category: "",
  structure: "",
  example_output: "",
  prohibited_patterns: "",
};

export default function FortuneTemplates() {
  const [items, setItems] = useState<FortuneTemplate[]>([]);
  const [form, setForm] = useState<FortuneTemplatePayload>(emptyForm);
  const [editingId, setEditingId] = useState<number | null>(null);

  async function load() {
    setItems(await api.listFortuneTemplates());
  }

  useEffect(() => {
    load();
  }, []);

  async function save(event: FormEvent) {
    event.preventDefault();
    if (editingId) {
      await api.updateFortuneTemplate(editingId, form);
    } else {
      await api.createFortuneTemplate(form);
    }
    setForm(emptyForm);
    setEditingId(null);
    await load();
  }

  function edit(item: FortuneTemplate) {
    setEditingId(item.id);
    setForm({
      name: item.name,
      fortune_type: item.fortune_type,
      target_pain_category: item.target_pain_category ?? "",
      structure: item.structure,
      example_output: item.example_output ?? "",
      prohibited_patterns: item.prohibited_patterns ?? "",
    });
  }

  return (
    <section className="split-layout wide-form">
      <form className="panel form-panel" onSubmit={save}>
        <div className="panel-title">
          <h3>{editingId ? "テンプレート編集" : "占いテンプレート登録"}</h3>
          <LayoutTemplate size={18} />
        </div>
        <p className="page-description compact">
          金運、恋愛、仕事運など、投稿の型を登録します。断定予言ではなく、自己理解と小さな行動につながる構成にしてください。
        </p>
        <label>
          テンプレート名
          <input value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} required />
        </label>
        <div className="two-columns">
          <label>
            占いタイプ
            <select value={form.fortune_type} onChange={(event) => setForm({ ...form, fortune_type: event.target.value })}>
              {fortuneTypes.map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </label>
          <label>
            対象の悩みカテゴリ
            <select value={form.target_pain_category ?? ""} onChange={(event) => setForm({ ...form, target_pain_category: event.target.value })}>
              <option value="">指定なし</option>
              {personaCategories.map(([value, label]) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </label>
        </div>
        <label>
          投稿構成
          <textarea rows={8} value={form.structure} onChange={(event) => setForm({ ...form, structure: event.target.value })} required />
        </label>
        <label>
          出力例
          <textarea rows={4} value={form.example_output ?? ""} onChange={(event) => setForm({ ...form, example_output: event.target.value })} />
        </label>
        <label>
          禁止パターン
          <textarea rows={4} value={form.prohibited_patterns ?? ""} onChange={(event) => setForm({ ...form, prohibited_patterns: event.target.value })} />
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
                <span className="badge">{genericLabel(FORTUNE_TYPE_LABELS, item.fortune_type)}</span>
                <h3>{item.name}</h3>
              </div>
              <div className="icon-actions">
                <button title="編集" onClick={() => edit(item)}>
                  <Pencil size={16} />
                </button>
                <button title="削除" onClick={async () => { await api.deleteFortuneTemplate(item.id); await load(); }}>
                  <Trash2 size={16} />
                </button>
              </div>
            </div>
            <pre>{item.structure}</pre>
            {item.prohibited_patterns && <p className="risk-text">{item.prohibited_patterns}</p>}
          </article>
        ))}
        {items.length === 0 && <EmptyState label="占いテンプレートはまだありません。" />}
      </section>
    </section>
  );
}
