import { ChangeEvent, useEffect, useState } from "react";
import { Import, Save } from "lucide-react";
import { api, ImportCandidate, ImportSession } from "../api/client";
import { EmptyState } from "./shared";

export default function FacebookImport() {
  const [sessions, setSessions] = useState<ImportSession[]>([]);
  const [selectedSession, setSelectedSession] = useState<ImportSession | null>(null);
  const [candidates, setCandidates] = useState<ImportCandidate[]>([]);
  const [busy, setBusy] = useState(false);

  async function loadSessions() {
    const data = await api.listImportSessions();
    setSessions(data);
    if (!selectedSession && data[0]) setSelectedSession(data[0]);
  }

  async function loadCandidates(session: ImportSession | null) {
    if (!session) return;
    setCandidates(await api.listImportCandidates(session.id));
  }

  useEffect(() => { loadSessions(); }, []);
  useEffect(() => { loadCandidates(selectedSession); }, [selectedSession?.id]);

  async function upload(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    setBusy(true);
    try {
      const session = await api.uploadFacebookZipPreview(file);
      setSelectedSession(session);
      await loadSessions();
      setCandidates(await api.listImportCandidates(session.id));
    } finally {
      setBusy(false);
    }
  }

  async function toggle(candidate: ImportCandidate) {
    const updated = await api.updateImportCandidate(candidate.id, { selected: !candidate.selected });
    setCandidates((items) => items.map((item) => item.id === updated.id ? updated : item));
  }

  async function commit() {
    if (!selectedSession) return;
    setBusy(true);
    try {
      await api.commitImportSession(selectedSession.id);
      await loadSessions();
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="page-grid">
      <section className="panel form-panel">
        <div className="panel-title"><h3>Facebook取り込み</h3><Import size={18} /></div>
        <p className="page-description compact">
          Facebook ZIPからMessengerを除外し、メール・電話番号・URLを削除したうえで、自分らしい口調や価値観だけをナレッジ候補にします。生データは保存せず、必ずプレビュー後に登録します。
        </p>
        <label>Facebook ZIPファイル<input type="file" accept=".zip" onChange={upload} disabled={busy} /></label>
        <div className="button-row">
          <button className="primary" disabled={!selectedSession || busy} onClick={commit}><Save size={17} />選択候補をナレッジ登録</button>
        </div>
        <div className="settings-readout">
          {sessions.map((session) => (
            <button className="secondary" key={session.id} onClick={() => setSelectedSession(session)}>
              #{session.id} {session.source_name || "Facebook ZIP"} / {session.candidate_count}件
            </button>
          ))}
        </div>
      </section>
      <section className="panel">
        <div className="panel-title"><h3>ナレッジ候補</h3></div>
        {selectedSession && <p className="muted">PII処理: {selectedSession.redaction_summary}</p>}
        <div className="draft-list compact">
          {candidates.map((candidate) => (
            <article className="card" key={candidate.id}>
              <div className="card-header">
                <div><span className={candidate.selected ? "badge green" : "badge muted-badge"}>{candidate.selected ? "登録対象" : "除外"}</span><h3>{candidate.title}</h3></div>
                <button className="secondary" onClick={() => toggle(candidate)}>{candidate.selected ? "除外する" : "登録対象に戻す"}</button>
              </div>
              <span className="badge">{candidate.category}</span>
              <p>{candidate.content}</p>
              <span className="muted">{candidate.redaction_notes}</span>
            </article>
          ))}
          {candidates.length === 0 && <EmptyState label="まだ候補はありません。Facebook ZIPをアップロードしてください。" />}
        </div>
      </section>
    </section>
  );
}
