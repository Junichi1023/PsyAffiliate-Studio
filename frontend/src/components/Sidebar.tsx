import {
  BarChart3,
  BookOpen,
  CalendarDays,
  FileText,
  Import,
  LayoutTemplate,
  Link,
  ListChecks,
  Package,
  Settings,
  Sparkles,
  Users,
} from "lucide-react";
import { PAGE_LABELS } from "../constants/labels";
import { Page } from "../types";

type NavItem = {
  id: Page;
  label: string;
  icon: typeof BarChart3;
};

const navGroups: Array<{ label: string; items: NavItem[] }> = [
  {
    label: "運用",
    items: [
      { id: "dashboard", label: PAGE_LABELS.dashboard, icon: BarChart3 },
      { id: "thirty-day-plan", label: PAGE_LABELS["thirty-day-plan"], icon: CalendarDays },
      { id: "typefully-jobs", label: PAGE_LABELS["typefully-jobs"], icon: ListChecks },
    ],
  },
  {
    label: "投稿作成",
    items: [
      { id: "generator", label: "Threads投稿作成", icon: Sparkles },
      { id: "drafts", label: PAGE_LABELS.drafts, icon: FileText },
      { id: "threads-templates", label: PAGE_LABELS["threads-templates"], icon: LayoutTemplate },
    ],
  },
  {
    label: "導線設計",
    items: [
      { id: "note-funnel", label: PAGE_LABELS["note-funnel"], icon: Link },
      { id: "fortune-a8-offers", label: PAGE_LABELS["fortune-a8-offers"], icon: Package },
      { id: "note-ctas", label: PAGE_LABELS["note-ctas"], icon: ListChecks },
    ],
  },
  {
    label: "ナレッジ",
    items: [
      { id: "knowledge", label: PAGE_LABELS.knowledge, icon: BookOpen },
      { id: "facebook-import", label: PAGE_LABELS["facebook-import"], icon: Import },
      { id: "persona-pains", label: PAGE_LABELS["persona-pains"], icon: Users },
      { id: "fortune-templates", label: PAGE_LABELS["fortune-templates"], icon: LayoutTemplate },
    ],
  },
  {
    label: "設定",
    items: [
      { id: "typefully-settings", label: PAGE_LABELS["typefully-settings"], icon: Settings },
      { id: "settings", label: PAGE_LABELS.settings, icon: Settings },
    ],
  },
] ;

const navItems = navGroups.flatMap((group) => group.items);

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
        {navGroups.map((group) => (
          <div className="nav-group" key={group.label}>
            <span className="nav-group-label">{group.label}</span>
            {group.items.map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.id}
                  className={page === item.id ? "nav-item active" : "nav-item"}
                  onClick={() => onPageChange(item.id as Page)}
                >
                  <Icon size={18} />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </div>
        ))}
      </nav>
    </aside>
  );
}
