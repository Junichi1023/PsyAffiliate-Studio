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
        FacebookナレッジからThreads投稿を作り、Typefully予約、プロフィールnote、A8占い案件へつなぐ運用状況を確認します。
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
          <StatCard label="今日の予約予定" value={dashboard?.today_scheduled_count ?? 0} tone="teal" />
          <StatCard label="Typefully予約待ち" value={dashboard?.typefully_waiting_count ?? 0} />
          <StatCard label="note導線未設定" value={dashboard?.note_missing_draft_count ?? 0} tone="amber" />
          <StatCard label="A8直リンク検出" value={dashboard?.a8_link_detected_count ?? 0} tone="amber" />
          <StatCard label="Facebook候補" value={dashboard?.facebook_candidate_count ?? 0} />
          <StatCard label="30日プラン進捗" value={dashboard?.plan_total_count ? Math.round(((dashboard?.plan_done_count ?? 0) / dashboard.plan_total_count) * 100) : 0} tone="teal" />
        </div>
        <section className="panel todo-panel">
          <div className="panel-title">
            <h3>今日やること</h3>
            <FileText size={18} />
          </div>
          <ul className="todo-list">
            <li>Facebookデータを取り込む</li>
            <li>note導線URLを設定する</li>
            <li>Threads投稿を3本作成する</li>
            <li>承認済み投稿をTypefullyへ予約する</li>
            <li>A8直リンクが入っていないか確認する</li>
          </ul>
        </section>
      </div>
      <section className="panel">
        <div className="panel-title"><h3>今週の投稿タイプ配分</h3></div>
        <div className="hashtag-row">
          {Object.entries(dashboard?.weekly_post_type_distribution ?? {}).map(([label, value]) => (
            <span key={label}>{label}: {value}%</span>
          ))}
        </div>
      </section>
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
