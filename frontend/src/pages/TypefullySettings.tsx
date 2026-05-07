import { FormEvent, useEffect, useState } from "react";
import { Save, Settings } from "lucide-react";
import { api, AppSettings, ScheduleMode } from "../api/client";

export default function TypefullySettings() {
  const [settings, setSettings] = useState<AppSettings | null>(null);
  const [form, setForm] = useState({
    typefully_api_key: "",
    typefully_social_set_id: "",
    typefully_default_schedule_mode: "draft_only" as ScheduleMode,
  });

  async function load() {
    const data = await api.getSettings();
    setSettings(data);
    setForm({
      typefully_api_key: "",
      typefully_social_set_id: data.typefully_social_set_id ?? "",
      typefully_default_schedule_mode: data.typefully_default_schedule_mode,
    });
  }

  useEffect(() => { load(); }, []);

  async function save(event: FormEvent) {
    event.preventDefault();
    const updated = await api.updateSettings(form);
    setSettings(updated);
    setForm((current) => ({ ...current, typefully_api_key: "" }));
  }

  return (
    <section className="settings-layout">
      <form className="panel form-panel" onSubmit={save}>
        <div className="panel-title"><h3>Typefully設定</h3><Settings size={18} /></div>
        <p className="page-description compact">
          TypefullyはThreads投稿を予約できる外部サービスです。APIキーは全文表示せず、承認済み投稿だけを送信します。
        </p>
        <label>TYPEFULLY_API_KEY
          <input type="password" value={form.typefully_api_key} placeholder={settings?.typefully_api_key_set ? "設定済み" : "未設定"} onChange={(e) => setForm({ ...form, typefully_api_key: e.target.value })} />
        </label>
        <label>TYPEFULLY_SOCIAL_SET_ID
          <input value={form.typefully_social_set_id} onChange={(e) => setForm({ ...form, typefully_social_set_id: e.target.value })} />
        </label>
        <label>標準予約方法
          <select value={form.typefully_default_schedule_mode} onChange={(e) => setForm({ ...form, typefully_default_schedule_mode: e.target.value as ScheduleMode })}>
            <option value="draft_only">下書きのみ</option>
            <option value="next_free_slot">次の空き枠</option>
            <option value="scheduled_time">指定日時</option>
          </select>
        </label>
        <button className="primary" type="submit"><Save size={17} />保存</button>
      </form>
      <section className="panel">
        <div className="panel-title"><h3>現在の状態</h3></div>
        <dl className="settings-readout">
          <div><dt>APIキー</dt><dd>{settings?.typefully_api_key_set ? "設定済み" : "未設定"}</dd></div>
          <div><dt>Social Set ID</dt><dd>{settings?.typefully_social_set_id || "-"}</dd></div>
          <div><dt>標準予約方法</dt><dd>{settings?.typefully_default_schedule_mode}</dd></div>
        </dl>
      </section>
    </section>
  );
}
