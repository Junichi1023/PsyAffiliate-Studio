import { useEffect, useState } from "react";
import { CalendarDays } from "lucide-react";
import { api, Threads30DayPlan } from "../api/client";
import { EmptyState } from "./shared";

export default function ThirtyDayPlan() {
  const [plan, setPlan] = useState<Threads30DayPlan | null>(null);

  async function load() {
    setPlan(await api.getThreads30DayPlan());
  }

  useEffect(() => { load(); }, []);

  async function setStatus(id: number, status: string) {
    await api.updateThreads30DayPlanTask(id, { status });
    await load();
  }

  return (
    <section className="dashboard-page">
      <p className="page-description">Facebookナレッジ、note導線、Threads投稿、Typefully予約を30日で回すための運用計画です。</p>
      <section className="panel">
        <div className="panel-title"><h3>投稿ジャンル配分</h3><CalendarDays size={18} /></div>
        <div className="metrics metrics-grid">
          {Object.entries(plan?.post_type_distribution ?? {}).map(([label, value]) => (
            <article className="metric teal" key={label}><span>{label}</span><strong>{value}%</strong></article>
          ))}
        </div>
      </section>
      <section className="item-grid">
        {plan?.tasks.map((task) => (
          <article className="card" key={task.id}>
            <div className="card-header">
              <div><span className="badge">{task.day_number}日目〜</span><h3>{task.title}</h3></div>
              <select value={task.status} onChange={(e) => setStatus(task.id, e.target.value)}>
                <option value="todo">未着手</option>
                <option value="doing">作業中</option>
                <option value="done">完了</option>
              </select>
            </div>
            <p>{task.description}</p>
          </article>
        ))}
        {!plan?.tasks.length && <EmptyState label="30日運用プランを読み込み中です。" />}
      </section>
    </section>
  );
}
