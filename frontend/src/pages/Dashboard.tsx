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
    <section className="dashboard-page">
      <p className="page-description">
        今日の投稿準備、承認待ち、投稿可能な下書き、リスクのある投稿を確認します。
      </p>
      <div className="dashboard-grid">
        <div className="metrics metrics-grid">
          <StatCard label="ナレッジ件数" value={dashboard?.knowledge_count ?? 0} />
          <StatCard label="登録商品数" value={dashboard?.affiliate_product_count ?? 0} tone="teal" />
          <StatCard label="悩みペルソナ数" value={dashboard?.persona_pain_count ?? 0} />
          <StatCard label="占いテンプレート数" value={dashboard?.fortune_template_count ?? 0} />
          <StatCard label="下書き数" value={dashboard?.draft_count ?? 0} />
          <StatCard label="承認待ち" value={dashboard?.pending_review ?? 0} tone="amber" />
          <StatCard label="投稿準備OK" value={dashboard?.publish_ready_count ?? 0} tone="teal" />
          <StatCard label="リスクあり投稿" value={dashboard?.risky_draft_count ?? 0} tone="amber" />
        </div>
        <section className="panel todo-panel">
          <div className="panel-title">
            <h3>今日やること</h3>
            <FileText size={18} />
          </div>
          <ul className="todo-list">
            <li>要確認の投稿を確認する</li>
            <li>投稿準備OKの下書きを投稿する</li>
            <li>スコアが低い投稿を修正する</li>
            <li>新しい悩みペルソナを追加する</li>
            <li>占いテンプレートを増やす</li>
          </ul>
        </section>
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
