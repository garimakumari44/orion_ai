import { Home, Bot, TrendingUp, Library, FileText, Settings, Plus, Layers } from 'lucide-react';
import { cn } from '../components/ui';
import { Page } from '../dashboard/page';

interface SidebarProps {
  currentPage: Page;
  onNavigate: (page: Page) => void;
  onSelectCompany: (id: string) => void;
  recentCompanies: { id: string; name: string; ticker: string }[];
}

const navItems: { id: Page; label: string; icon: typeof Home }[] = [
  { id: 'home', label: 'Home', icon: Home },
  { id: 'workspace', label: 'AI Workspace', icon: Bot },
  { id: 'research', label: 'Research', icon: TrendingUp },
  { id: 'library', label: 'Library', icon: Library },
  { id: 'reports', label: 'Reports', icon: FileText },
  { id: 'settings', label: 'Settings', icon: Settings },
];

export function Sidebar({ currentPage, onNavigate, onSelectCompany, recentCompanies }: SidebarProps) {
  return (
    <aside className="w-56 shrink-0 bg-bg-base border-r border-border flex flex-col h-full">
      <div className="px-5 py-4 flex items-center gap-2.5">
        <div className="w-7 h-7 rounded-lg bg-accent/15 border border-accent/30 flex items-center justify-center">
          <Layers className="w-4 h-4 text-accent" />
        </div>
        <span className="text-sm font-semibold text-text-primary tracking-tight">Research Canvas</span>
      </div>

      <nav className="px-3 mt-2 space-y-0.5">
        {navItems.map((item) => {
          const Icon = item.icon;
          const active = currentPage === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              className={cn(
                'w-full flex items-center gap-2.5 px-2.5 py-1.5 rounded-md text-sm transition-colors',
                active
                  ? 'bg-bg-hover text-text-primary'
                  : 'text-text-muted hover:text-text-secondary hover:bg-bg-hover/50',
              )}
            >
              <Icon className={cn('w-4 h-4', active ? 'text-accent' : 'text-text-faint')} />
              {item.label}
            </button>
          );
        })}
      </nav>

      <div className="px-5 mt-6 mb-2 flex items-center justify-between">
        <span className="text-[10px] text-text-faint uppercase tracking-widest font-mono">Recent</span>
      </div>

      <div className="px-3 flex-1 overflow-y-auto scrollbar-none">
        <div className="space-y-0.5">
          {recentCompanies.map((c) => (
            <button
              key={c.id}
              onClick={() => onSelectCompany(c.id)}
              className={cn(
                'w-full flex items-center gap-2.5 px-2.5 py-1.5 rounded-md text-sm transition-colors group',
                currentPage === 'research'
                  ? 'text-text-secondary hover:text-text-primary hover:bg-bg-hover/50'
                  : 'text-text-muted hover:text-text-secondary hover:bg-bg-hover/50',
              )}
            >
              <span className="font-mono text-[11px] text-text-faint w-10">{c.ticker}</span>
              <span className="truncate flex-1 text-left">{c.name}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="p-3 border-t border-border">
        <button
          onClick={() => onNavigate('new-research')}
          className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-md bg-accent/10 border border-accent/20 text-accent text-sm font-medium hover:bg-accent/15 transition-colors"
        >
          <Plus className="w-4 h-4" />
          New Research
        </button>
      </div>
    </aside>
  );
}
