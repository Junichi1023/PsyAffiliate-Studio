import { FormEvent, useEffect, useState } from "react";
import { Save, Settings as SettingsIcon, ShieldCheck } from "lucide-react";
import { api } from "../api/client";
import { PLATFORM_LABELS } from "../constants/labels";
import { AppSettings, Platform } from "../types";

const emptySettings: AppSettings = {
  openai_api_key_set: false,
  openai_model: "gpt-5.5",
  default_platform: "threads",
  default_pr_disclosure: "#PR",
  brand_voice_summary: "",
  typefully_api_key_set: false,
  typefully_social_set_id: "",
  typefully_default_schedule_mode: "draft_only",
};

export default function Settings() {
  const [settings, setSettings] = useState<AppSettings>(emptySettings);
  const [form, setForm] = useState({
    openai_api_key: "",
    openai_model: "gpt-5.5",
    default_platform: "threads" as Platform,
    default_pr_disclosure: "#PR",
    brand_voice_summary: "",
  });

  async function load() {
    const data = await api.getSettings();
    setSettings(data);
    setForm({
      openai_api_key: "",
      openai_model: data.openai_model,
      default_platform: data.default_platform,
      default_pr_disclosure: data.default_pr_disclosure,
      brand_voice_summary: data.brand_voice_summary,
    });
  }

  useEffect(() => {
    load();
  }, []);

  async function save(event: FormEvent) {
    event.preventDefault();
    const updated = await api.updateSettings(form);
    setSettings(updated);
    setForm((current) => ({ ...current, openai_api_key: "" }));
  }

  return (
    <section className="settings-layout">
      <form className="panel form-panel" onSubmit={save}>
        <div className="panel-title">
          <h3>設定</h3>
          <SettingsIcon size={18} />
        </div>
        <p className="page-description compact">
          AIモデル、PR表記、ブランドボイスなどを設定します。APIキーはGitHubにコミットしないでください。将来的にはOS Keychain管理に移行予定です。
        </p>
        <label>
          OpenAI APIキー
          <input
            type="password"
            value={form.openai_api_key}
            placeholder={settings.openai_api_key_set ? "設定済み" : ""}
            onChange={(event) => setForm({ ...form, openai_api_key: event.target.value })}
          />
        </label>
        <label>
          使用モデル
          <input value={form.openai_model} onChange={(event) => setForm({ ...form, openai_model: event.target.value })} />
        </label>
        <label>
          標準の投稿先
          <select value={form.default_platform} onChange={(event) => setForm({ ...form, default_platform: event.target.value as Platform })}>
            <option value="threads">{PLATFORM_LABELS.threads}</option>
            <option value="instagram">{PLATFORM_LABELS.instagram}</option>
            <option value="both">{PLATFORM_LABELS.both}</option>
          </select>
        </label>
        <label>
          標準PR表記
          <input value={form.default_pr_disclosure} onChange={(event) => setForm({ ...form, default_pr_disclosure: event.target.value })} />
        </label>
        <label>
          ブランドボイス
          <textarea rows={5} value={form.brand_voice_summary} onChange={(event) => setForm({ ...form, brand_voice_summary: event.target.value })} />
        </label>
        <button className="primary" type="submit">
          <Save size={17} />
          保存
        </button>
      </form>
      <section className="panel">
        <div className="panel-title">
          <h3>現在の設定</h3>
          <ShieldCheck size={18} />
        </div>
        <dl className="settings-readout">
          <div><dt>APIキー</dt><dd>{settings.openai_api_key_set ? "設定済み" : "未設定"}</dd></div>
          <div><dt>使用モデル</dt><dd>{settings.openai_model}</dd></div>
          <div><dt>標準PR表記</dt><dd>{settings.default_pr_disclosure}</dd></div>
        </dl>
      </section>
    </section>
  );
}
