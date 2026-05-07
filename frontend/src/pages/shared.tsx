import { FileText, Trash2 } from "lucide-react";
import {
  complianceStatus,
  DRAFT_STATUS_LABELS,
  empathyStatus,
  mockPublishDisabledReason,
  platformLabel,
  publishReadyLabel,
} from "../constants/labels";
import { Draft, DraftStatus } from "../types";

export const statusOptions: DraftStatus[] = ["draft", "needs_review", "approved", "scheduled", "posted", "failed"];

export function formatDate(value?: string | null) {
  if (!value) return "-";
  return new Intl.DateTimeFormat("ja-JP", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

export function scoreClass(score?: number | null) {
  if (score == null) return "score neutral";
  if (score >= 90) return "score good";
  if (score >= 70) return "score caution";
  if (score >= 40) return "score review";
  return "score danger";
}

export function riskLines(text?: string | null) {
  if (!text) return [];
  return text
    .split(/\n|、/)
    .map((item) => item.trim())
    .filter(Boolean);
}

export function EmptyState({ label }: { label: string }) {
  return (
    <div className="empty-state">
      <FileText size={22} />
      <span>{label}</span>
    </div>
  );
}

export function DraftCard({
  draft,
  onStatusChange,
  onScheduleChange,
  onDelete,
  onMockPublish,
}: {
  draft: Draft;
  onStatusChange: (status: DraftStatus) => void;
  onScheduleChange: (value: string) => void;
  onDelete: () => void;
  onMockPublish?: () => void;
}) {
  const disabledReason = onMockPublish ? mockPublishDisabledReason(draft) : null;
  return (
    <article className="draft-card">
      <div className="draft-head">
        <div>
          <span className="badge">{platformLabel(draft.platform)}</span>
          <h3>{draft.theme}</h3>
        </div>
        <div className="score-stack">
          <span className={scoreClass(draft.compliance_score)}>
            安全性 {draft.compliance_score ?? "-"} / {complianceStatus(draft.compliance_score)}
          </span>
          <span className={scoreClass(draft.empathy_score)}>
            寄り添い {draft.empathy_score ?? "-"} / {empathyStatus(draft.empathy_score)}
          </span>
        </div>
      </div>
      <p>{draft.body}</p>
      {draft.caption && <p className="caption-text">{draft.caption}</p>}
      {draft.cta && <p className="cta-text">{draft.cta}</p>}
      {riskLines(draft.risk_notes).length > 0 && (
        <div className="note-list">
          {riskLines(draft.risk_notes).map((note) => (
            <span key={note}>{note}</span>
          ))}
        </div>
      )}
      {riskLines(draft.empathy_notes).length > 0 && (
        <div className="note-list empathy-notes">
          {riskLines(draft.empathy_notes).map((note) => (
            <span key={note}>{note}</span>
          ))}
        </div>
      )}
      <div className="publish-state">
        <span className={draft.publish_ready ? "badge green" : "badge muted-badge"}>
          {publishReadyLabel(draft.publish_ready)}
        </span>
        <span className={draft.direct_a8_link_detected ? "badge danger-badge" : "badge green"}>
          {draft.direct_a8_link_detected ? "A8直リンク検出" : "A8直リンクなし"}
        </span>
        <span className={draft.profile_note_cta_included ? "badge green" : "badge muted-badge"}>
          {draft.profile_note_cta_included ? "note導線あり" : "note導線なし"}
        </span>
        <span className={draft.note_page_id ? "badge green" : "badge muted-badge"}>
          {draft.note_page_id ? "note設定済み" : "note未設定"}
        </span>
        {disabledReason && <span className="muted">{disabledReason}</span>}
        {!disabledReason && !draft.publish_ready && draft.publish_block_reason && <span className="muted">{draft.publish_block_reason}</span>}
      </div>
      <div className="draft-controls">
        <select value={draft.status} onChange={(event) => onStatusChange(event.target.value as DraftStatus)}>
          {statusOptions.map((status) => (
            <option key={status} value={status}>
              {DRAFT_STATUS_LABELS[status]}
            </option>
          ))}
        </select>
        <input
          type="datetime-local"
          value={draft.scheduled_at ? draft.scheduled_at.slice(0, 16) : ""}
          onChange={(event) => onScheduleChange(event.target.value)}
        />
        <span className="muted">{formatDate(draft.created_at)}</span>
        {onMockPublish && (
          <button className="mock-publish-button" title={disabledReason ?? "mock投稿"} disabled={Boolean(disabledReason)} onClick={onMockPublish}>
            mock投稿
          </button>
        )}
        <button title="削除" onClick={onDelete}>
          <Trash2 size={16} />
        </button>
      </div>
    </article>
  );
}
