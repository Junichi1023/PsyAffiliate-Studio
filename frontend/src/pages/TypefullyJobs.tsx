import { FormEvent, useEffect, useState } from "react";
import { Send } from "lucide-react";
import { api, Draft, ScheduleMode, TypefullyScheduleJob } from "../api/client";
import { mockPublishDisabledReason, platformLabel } from "../constants/labels";
import { EmptyState, formatDate } from "./shared";

export default function TypefullyJobs() {
  const [drafts, setDrafts] = useState<Draft[]>([]);
  const [jobs, setJobs] = useState<TypefullyScheduleJob[]>([]);
  const [draftId, setDraftId] = useState<number | "">("");
  const [scheduleMode, setScheduleMode] = useState<ScheduleMode>("draft_only");
  const [scheduledAt, setScheduledAt] = useState("");
  const [message, setMessage] = useState("");

  async function load() {
    setDrafts(await api.listDrafts());
    setJobs(await api.listTypefullyJobs());
  }

  useEffect(() => { load(); }, []);

  async function schedule(event: FormEvent) {
    event.preventDefault();
    if (!draftId) return;
    try {
      const result = await api.scheduleTypefullyDraft(Number(draftId), {
        schedule_mode: scheduleMode,
        scheduled_at: scheduledAt || null,
      });
      setMessage(result.message);
      await load();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Typefully予約に失敗しました");
    }
  }

  return (
    <section className="page-grid">
      <form className="panel form-panel" onSubmit={schedule}>
        <div className="panel-title"><h3>Typefully予約管理</h3><Send size={18} /></div>
        <p className="page-description compact">
          TypefullyはThreads投稿を予約できる外部サービスです。このアプリでは、承認済みでA8直リンクがなく、プロフィールnote導線がある投稿だけをTypefullyへ送ります。
        </p>
        <label>予約する下書き
          <select value={draftId} onChange={(e) => setDraftId(e.target.value ? Number(e.target.value) : "")}>
            <option value="">選択してください</option>
            {drafts.map((draft) => {
              const reason = mockPublishDisabledReason(draft) || (draft.direct_a8_link_detected ? "A8直リンク検出" : "") || (!draft.note_page_id ? "note未設定" : "") || (!draft.profile_note_cta_included ? "note導線なし" : "");
              return <option key={draft.id} value={draft.id}>{draft.theme} / {reason || "予約可能候補"}</option>;
            })}
          </select>
        </label>
        <label>予約方法
          <select value={scheduleMode} onChange={(e) => setScheduleMode(e.target.value as ScheduleMode)}>
            <option value="draft_only">Typefullyへ下書き作成</option>
            <option value="next_free_slot">次の空き枠で予約</option>
            <option value="scheduled_time">指定日時で予約</option>
          </select>
        </label>
        {scheduleMode === "scheduled_time" && <label>指定日時<input type="datetime-local" value={scheduledAt} onChange={(e) => setScheduledAt(e.target.value)} /></label>}
        <button className="primary" type="submit">Typefullyへ送る</button>
        {message && <p className="field-note">{message}</p>}
        <p className="field-note">Typefully側で予約済みの投稿をキャンセルする場合、Typefullyの画面でも確認してください。</p>
      </form>

      <section className="panel">
        <div className="panel-title"><h3>予約ジョブ</h3></div>
        <div className="draft-list compact">
          {jobs.map((job) => {
            const draft = drafts.find((item) => item.id === job.draft_id);
            return (
              <article className="card" key={job.id}>
                <div className="card-header">
                  <div><span className="badge">{job.status}</span><h3>{draft?.theme || `Draft #${job.draft_id}`}</h3></div>
                  <button className="secondary" onClick={async () => { await api.cancelTypefullyJobLocal(job.id); await load(); }}>ローカル上でキャンセル扱い</button>
                </div>
                <p>{draft?.body?.slice(0, 120)}</p>
                <dl className="settings-readout">
                  <div><dt>投稿先</dt><dd>{draft ? platformLabel(draft.platform) : "-"}</dd></div>
                  <div><dt>予約日時</dt><dd>{formatDate(job.scheduled_at)}</dd></div>
                  <div><dt>schedule_mode</dt><dd>{job.schedule_mode}</dd></div>
                  <div><dt>Typefully draft id</dt><dd>{job.typefully_draft_id || "-"}</dd></div>
                  <div><dt>note導線</dt><dd>{draft?.profile_note_cta_included ? "確認済み" : "未確認"}</dd></div>
                  <div><dt>A8直リンク</dt><dd>{draft?.direct_a8_link_detected ? "検出" : "なし"}</dd></div>
                </dl>
                {job.error_message && <p className="risk-text">{job.error_message}</p>}
              </article>
            );
          })}
          {jobs.length === 0 && <EmptyState label="Typefully予約ジョブはまだありません。" />}
        </div>
      </section>
    </section>
  );
}
