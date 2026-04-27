import { BarChart3, BookOpen, FileText, LayoutTemplate, Package, Settings, Sparkles, Users } from "lucide-react";
import { PAGE_LABELS } from "../constants/labels";
import { Page } from "../types";

const navItems = [
  { id: "dashboard", label: PAGE_LABELS.dashboard, icon: BarChart3 },
  { id: "knowledge", label: PAGE_LABELS.knowledge, icon: BookOpen },
  { id: "products", label: PAGE_LABELS.products, icon: Package },
  { id: "persona-pains", label: PAGE_LABELS["persona-pains"], icon: Users },
  { id: "fortune-templates", label: PAGE_LABELS["fortune-templates"], icon: LayoutTemplate },
  { id: "generator", label: PAGE_LABELS.generator, icon: Sparkles },
  { id: "drafts", label: PAGE_LABELS.drafts, icon: FileText },
  { id: "settings", label: PAGE_LABELS.settings, icon: Settings },
] as const;

export function pageLabel(page: Page) {
  return navItems.find((item) => item.id === page)?.label ?? PAGE_LABELS.dashboard;
}

export default function Sidebar({ page, onPageChange }: { page: Page; onPageChange: (page: Page) => void }) {
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-mark">PS</div>
        <div>
          <h1>PsyAffiliate Studio</h1>
          <span>占い × 心理学 × AI × アフィリエイト</span>
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
