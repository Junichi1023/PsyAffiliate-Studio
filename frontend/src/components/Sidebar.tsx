import { BarChart3, BookOpen, FileText, Package, Settings, Sparkles } from "lucide-react";
import { Page } from "../types";

const navItems = [
  { id: "dashboard", label: "Dashboard", icon: BarChart3 },
  { id: "knowledge", label: "Knowledge", icon: BookOpen },
  { id: "products", label: "Products", icon: Package },
  { id: "generator", label: "Generator", icon: Sparkles },
  { id: "drafts", label: "Drafts", icon: FileText },
  { id: "settings", label: "Settings", icon: Settings },
] as const;

export function pageLabel(page: Page) {
  return navItems.find((item) => item.id === page)?.label ?? "Dashboard";
}

export default function Sidebar({ page, onPageChange }: { page: Page; onPageChange: (page: Page) => void }) {
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-mark">PS</div>
        <div>
          <h1>PsyAffiliate Studio</h1>
          <span>Phase 1 MVP</span>
        </div>
      </div>
      <nav>
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <button
              key={item.id}
              className={page === item.id ? "nav-item active" : "nav-item"}
              onClick={() => onPageChange(item.id)}
            >
              <Icon size={18} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>
    </aside>
  );
}
