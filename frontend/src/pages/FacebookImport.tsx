import { ChangeEvent, FormEvent, useEffect, useMemo, useState } from "react";
import { CheckCircle2, Import, Save } from "lucide-react";
import { api, ImportCandidate, ImportSession } from "../api/client";
import { KNOWLEDGE_CATEGORY_LABELS, genericLabel } from "../constants/labels";
import { Page } from "../types";
import { EmptyState } from "./shared";

const MAX_ITEM_OPTIONS = [500, 1000, 2000, 5000];
const CATEGORY_OPTIONS = Object.entries(KNOWLEDGE_CATEGORY_LABELS);

const REDACTION_LABELS: Record<string, string> = {
  email_removed: "メール削除",
  phone_removed: "電話番号削除",
  url_removed: "URL削除",
  facebook_url_removed: "Facebook URL削除",
  instagram_url_removed: "Instagram URL削除",
  x_url_removed: "X/Twitter URL削除",
  postal_code_removed: "郵便番号削除",
  long_id_removed: "長いID削除",
  credit_card_like_removed: "カード番号風数字削除",
  username_removed: "@ユーザー名削除",
  line_id_removed: "LINE ID削除",
  address_like_removed: "住所らしき表記削除",
  name_like_warning: "名前らしき表現の確認",
  skipped_message_files: "Messenger除外ファイル",
  message_files_processed: "Messenger処理ファイル",
  skipped_json_files: "壊れたJSONなどでスキップ",
  skipped_html_files: "壊れたHTMLなどでスキップ",
  json_files_processed: "JSON処理ファイル",
  html_files_processed: "HTML処理ファイル",
  duplicate_texts_skipped: "重複テキスト除外",
  sanitized_text_fragments: "候補生成に使った断片",
};

function parseSummary(summary?: string | null) {
  if (!summary) return {};
  try {
    return JSON.parse(summary) as Record<string, unknown>;
  } catch {
    return { summary };
  }
}

function cloneCandidate(candidate: ImportCandidate): ImportCandidate {
  return { ...candidate };
}

export default function FacebookImport({ onNavigate }: { onNavigate?: (page: Page) => void }) {
  const [sessions, setSessions] = useState<ImportSession[]>([]);
  const [selectedSession, setSelectedSession] = useState<ImportSession | null>(null);
  const [candidates, setCandidates] = useState<ImportCandidate[]>([]);
  const [draftEdits, setDraftEdits] = useState<Record<number, ImportCandidate>>({});
  const [busy, setBusy] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [useAiSummary, setUseAiSummary] = useState(false);
  const [includeMessages, setIncludeMessages] = useState(false);
  const [maxItems, setMaxItems] = useState(2000);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [privacyConfirmed, setPrivacyConfirmed] = useState(false);

  const redactionSummary = useMemo(() => parseSummary(selectedSession?.redaction_summary), [selectedSession?.redaction_summary]);

  async function loadSessions() {
    const data = await api.listImportSessions();
    setSessions(data);
    if (!selectedSession && data[0]) setSelectedSession(data[0]);
  }

  async function loadCandidates(session: ImportSession | null) {
    if (!session) return;
    const loaded = await api.listImportCandidates(session.id);
    setCandidates(loaded);
    setDraftEdits(Object.fromEntries(loaded.map((candidate) => [candidate.id, cloneCandidate(candidate)])));
  }

  useEffect(() => { loadSessions(); }, []);
  useEffect(() => { loadCandidates(selectedSession); }, [selectedSession?.id]);

  function onFileChange(event: ChangeEvent<HTMLInputElement>) {
    setFile(event.target.files?.[0] ?? null);
    setError("");
    setMessage("");
  }

  async function upload(event: FormEvent) {
    event.preventDefault();
    if (!file) {
      setError("Facebook ZIPファイルを選択してください。");
      return;
    }
    setBusy(true);
    setError("");
    setMessage("");
    try {
      const session = await api.uploadFacebookZipPreview(file, {
        use_ai_summary: useAiSummary,
        include_messages: includeMessages,
        max_items: maxItems,
      });
      setSelectedSession(session);
      await loadSessions();
      await loadCandidates(session);
      setPrivacyConfirmed(false);
      setMessage("解析が完了しました。候補を確認・編集してからナレッジ登録してください。");
    } catch (uploadError) {
      setError(uploadError instanceof Error ? uploadError.message : "Facebook ZIPの解析に失敗しました。");
    } finally {
      setBusy(false);
    }
  }

  function updateLocal(candidateId: number, patch: Partial<ImportCandidate>) {
    setDraftEdits((current) => ({
      ...current,
      [candidateId]: { ...(current[candidateId] ?? candidates.find((item) => item.id === candidateId)!), ...patch },
    }));
  }

  async function saveCandidate(candidateId: number) {
    const draft = draftEdits[candidateId];
    if (!draft) return;
    const updated = await api.updateImportCandidate(candidateId, {
      title: draft.title,
      category: draft.category,
      content: draft.content,
      selected: draft.selected,
    });
    setCandidates((items) => items.map((item) => item.id === updated.id ? updated : item));
    setDraftEdits((items) => ({ ...items, [updated.id]: cloneCandidate(updated) }));
  }

  async function commit() {
    if (!selectedSession || !privacyConfirmed) return;
    const ok = window.confirm("選択した候補をナレッジに登録します。個人名・連絡先・具体的なプライベート情報が残っていないことを確認しましたか？");
    if (!ok) return;
    setBusy(true);
    setError("");
    setMessage("");
    try {
      const result = await api.commitImportSession(selectedSession.id);
      await loadSessions();
      setMessage(`${result.committed_count}件のナレッジを登録しました。次はThreads投稿作成で口調を反映できます。`);
    } catch (commitError) {
      setError(commitError instanceof Error ? commitError.message : "ナレッジ登録に失敗しました。");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="page-grid">
      <section className="panel form-panel">
        <div className="panel-title"><h3>Facebook取り込み</h3><Import size={18} /></div>
        <p className="page-description compact">
          FacebookからダウンロードしたZIPを選択してください。JSON形式だけでなくHTML形式のエクスポートにも対応しています。このアプリは生データを保存せず、個人情報を除去したうえで「自分らしい口調・価値観・投稿傾向」だけをナレッジ候補にします。
        </p>
        <div className="step-list">
          <span>Step 1: ZIPを選ぶ</span>
          <span>Step 2: 解析結果を確認</span>
          <span>Step 3: 候補を編集</span>
          <span>Step 4: ナレッジ登録</span>
        </div>
        <form onSubmit={upload}>
          <label>Facebook ZIPファイル<input type="file" accept=".zip" onChange={onFileChange} disabled={busy} /></label>
          <label>AI要約を使う
            <select value={String(useAiSummary)} onChange={(event) => setUseAiSummary(event.target.value === "true")}>
              <option value="false">OFF（安定・APIキー不要）</option>
              <option value="true">ON（将来拡張用。現在は安全な要約ルールで処理）</option>
            </select>
          </label>
          <label>Messengerも取り込む
            <select value={String(includeMessages)} onChange={(event) => setIncludeMessages(event.target.value === "true")}>
              <option value="false">OFF（推奨。他人の発言や個人情報を除外）</option>
              <option value="true">ON（確認メモ付きで処理）</option>
            </select>
          </label>
          <label>最大解析件数
            <select value={maxItems} onChange={(event) => setMaxItems(Number(event.target.value))}>
              {MAX_ITEM_OPTIONS.map((value) => <option key={value} value={value}>{value}件</option>)}
            </select>
          </label>
          <button className="primary" type="submit" disabled={busy}>解析してプレビュー作成</button>
        </form>
        <p className="field-note">
          Messengerには他人の発言や個人情報が多く含まれるため、通常はOFFのままにしてください。ZIPは解凍せず、そのままアップロードします。
        </p>
        {error && <div className="error-box">{error}</div>}
        {message && <div className="success-box">{message}</div>}
        <div className="settings-readout">
          {sessions.map((session) => (
            <button className="secondary" key={session.id} onClick={() => setSelectedSession(session)}>
              #{session.id} {session.source_name || "Facebook ZIP"} / 候補 {session.candidate_count}件
            </button>
          ))}
        </div>
      </section>

      <section className="panel">
        <div className="panel-title"><h3>解析結果と候補編集</h3></div>
        {selectedSession && (
          <>
            <div className="summary-grid">
              <div><strong>抽出件数</strong><span>{selectedSession.total_items}</span></div>
              <div><strong>sanitize済み件数</strong><span>{selectedSession.sanitized_items}</span></div>
              <div><strong>候補数</strong><span>{selectedSession.candidate_count}</span></div>
              <div><strong>ステータス</strong><span>{selectedSession.status}</span></div>
            </div>
            <div className="summary-grid">
              {Object.entries(redactionSummary)
                .filter(([key]) => key !== "skipped_files")
                .map(([key, value]) => (
                  <div key={key}><strong>{REDACTION_LABELS[key] ?? key}</strong><span>{String(value)}</span></div>
                ))}
            </div>
            {Array.isArray(redactionSummary.skipped_files) && redactionSummary.skipped_files.length > 0 && (
              <details className="field-note">
                <summary>スキップされたJSONファイル</summary>
                <ul>{redactionSummary.skipped_files.map((name: string) => <li key={name}>{name}</li>)}</ul>
              </details>
            )}
          </>
        )}
        <div className="button-row">
          <label className="checkbox-row">
            <input type="checkbox" checked={privacyConfirmed} onChange={(event) => setPrivacyConfirmed(event.target.checked)} />
            候補内に個人名・連絡先・具体的なプライベート情報が残っていないことを確認しました
          </label>
          <button className="primary" disabled={!selectedSession || busy || !privacyConfirmed} onClick={commit}>
            <Save size={17} />選択した候補をナレッジに登録
          </button>
        </div>
        {message.includes("登録しました") && (
          <div className="button-row">
            <button className="secondary" onClick={() => onNavigate?.("knowledge")}>ナレッジ画面へ</button>
            <button className="secondary" onClick={() => onNavigate?.("generator")}>Threads投稿作成へ</button>
          </div>
        )}
        <div className="draft-list compact">
          {candidates.map((candidate) => {
            const edit = draftEdits[candidate.id] ?? candidate;
            return (
              <article className="card candidate-editor" key={candidate.id}>
                <div className="card-header">
                  <label className="checkbox-row">
                    <input
                      type="checkbox"
                      checked={Boolean(edit.selected)}
                      onChange={(event) => updateLocal(candidate.id, { selected: event.target.checked })}
                    />
                    {edit.selected ? "登録対象" : "除外"}
                  </label>
                  <button className="secondary" onClick={() => saveCandidate(candidate.id)}><CheckCircle2 size={16} />候補を保存</button>
                </div>
                <label>タイトル<input value={edit.title} onChange={(event) => updateLocal(candidate.id, { title: event.target.value })} /></label>
                <label>カテゴリ
                  <select value={edit.category} onChange={(event) => updateLocal(candidate.id, { category: event.target.value })}>
                    {CATEGORY_OPTIONS.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
                  </select>
                </label>
                <label>内容<textarea rows={8} value={edit.content} onChange={(event) => updateLocal(candidate.id, { content: event.target.value })} /></label>
                <div className="publish-state">
                  <span className="badge">{genericLabel(KNOWLEDGE_CATEGORY_LABELS, edit.category)}</span>
                  <span className="muted">信頼度 {edit.confidence_score}</span>
                </div>
                <p className="field-note">{edit.redaction_notes}</p>
              </article>
            );
          })}
          {candidates.length === 0 && <EmptyState label="まだ候補はありません。Facebook ZIPをアップロードしてください。" />}
        </div>
      </section>
    </section>
  );
}
