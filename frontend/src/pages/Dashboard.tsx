import { useEffect, useState } from "react";
import { FileText } from "lucide-react";
import { api } from "../api/client";
import StatCard from "../components/StatCard";
import { DashboardStats } from "../types";
import { DraftCard, EmptyState } from "./shared";

export default function Dashboard() {
  const [dashboard, setDashboard] = useState<DashboardStats | null>(null);

  async function load() {
    setDashboard(await api.getDashboard());
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <section className="page-grid">
      <div className="metrics">
        <StatCard label="ナレッジ件数" value={dashboard?.knowledge_count ?? 0} />
        <StatCard label="商品件数" value={dashboard?.affiliate_product_count ?? 0} tone="teal" />
        <StatCard label="下書き件数" value={dashboard?.draft_count ?? 0} />
        <StatCard label="承認待ち" value={dashboard?.pending_review ?? 0} tone="amber" />
      </div>
      <section className="panel">
        <div className="panel-title">
          <h3>最近生成した投稿</h3>
          <FileText size={18} />
        </div>
        <div className="draft-list compact">
          {(dashboard?.recent_drafts ?? []).map((draft) => (
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
            />
          ))}
          {(dashboard?.recent_drafts ?? []).length === 0 && <EmptyState label="下書きはまだありません。" />}
        </div>
      </section>
    </section>
  );
}
