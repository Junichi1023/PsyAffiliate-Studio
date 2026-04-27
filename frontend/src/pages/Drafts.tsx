import { useEffect, useState } from "react";
import { Download, FileText } from "lucide-react";
import { API_BASE, api } from "../api/client";
import { SCORE_HELP_TEXT } from "../constants/labels";
import { Draft } from "../types";
import { DraftCard, EmptyState } from "./shared";

export default function Drafts() {
  const [drafts, setDrafts] = useState<Draft[]>([]);

  async function load() {
    setDrafts(await api.listDrafts());
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <section className="panel full-panel">
      <div className="panel-title">
        <h3>下書き・投稿管理</h3>
        <button className="secondary" onClick={() => window.open(`${API_BASE}/api/drafts/export.csv`, "_blank")}>
          <Download size={17} />
          CSV
        </button>
      </div>
      <p className="page-description">
        生成した投稿の安全性、寄り添い度、承認状態、投稿準備状況を確認します。
      </p>
      <div className="score-explainers">
        <p><strong>安全性スコア:</strong> {SCORE_HELP_TEXT.compliance}</p>
        <p><strong>寄り添いスコア:</strong> {SCORE_HELP_TEXT.empathy}</p>
      </div>
      <div className="draft-list">
        {drafts.map((draft) => (
          <DraftCard
            key={draft.id}
            draft={draft}
            onStatusChange={async (status) => {
              await api.updateDraft(draft.id, { status });
              await load();
            }}
            onScheduleChange={async (scheduled_at) => {
              await api.updateDraft(draft.id, { scheduled_at: scheduled_at || null });
              await load();
            }}
            onDelete={async () => {
              await api.deleteDraft(draft.id);
              await load();
            }}
            onMockPublish={async () => {
              await api.mockPublishDraft(draft.id);
              await load();
            }}
          />
        ))}
        {drafts.length === 0 && <EmptyState label="下書きはまだありません。" />}
      </div>
    </section>
  );
}
