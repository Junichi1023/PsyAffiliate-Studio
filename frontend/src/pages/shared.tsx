import { FileText, Trash2 } from "lucide-react";
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
}: {
  draft: Draft;
  onStatusChange: (status: DraftStatus) => void;
  onScheduleChange: (value: string) => void;
  onDelete: () => void;
}) {
  return (
    <article className="draft-card">
      <div className="draft-head">
        <div>
          <span className="badge">{draft.platform}</span>
          <h3>{draft.theme}</h3>
        </div>
        <span className={scoreClass(draft.compliance_score)}>{draft.compliance_score ?? "-"}</span>
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
      <div className="draft-controls">
        <select value={draft.status} onChange={(event) => onStatusChange(event.target.value as DraftStatus)}>
          {statusOptions.map((status) => (
            <option key={status} value={status}>
              {status}
            </option>
          ))}
        </select>
        <input
          type="datetime-local"
          value={draft.scheduled_at ? draft.scheduled_at.slice(0, 16) : ""}
          onChange={(event) => onScheduleChange(event.target.value)}
        />
        <span className="muted">{formatDate(draft.created_at)}</span>
        <button title="削除" onClick={onDelete}>
          <Trash2 size={16} />
        </button>
      </div>
    </article>
  );
}
