import { ReactNode } from "react";
import { RefreshCw } from "lucide-react";
import { Page } from "../types";
import Sidebar, { pageLabel } from "./Sidebar";

export default function Layout({
  page,
  onPageChange,
  onRefresh,
  children,
}: {
  page: Page;
  onPageChange: (page: Page) => void;
  onRefresh?: () => void;
  children: ReactNode;
}) {
  return (
    <div className="app-shell">
      <Sidebar page={page} onPageChange={onPageChange} />
      <main className="workspace">
        <header className="topbar">
          <div>
            <p className="eyebrow">悩みに寄り添う占い投稿・アフィリエイト運用OS</p>
            <h2>{pageLabel(page)}</h2>
          </div>
          {onRefresh && (
            <button className="icon-button" title="再読み込み" onClick={onRefresh}>
              <RefreshCw size={18} />
            </button>
          )}
        </header>
        {children}
      </main>
    </div>
  );
}
