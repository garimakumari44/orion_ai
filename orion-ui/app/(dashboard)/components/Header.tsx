import { Search, Bell, ChevronDown } from 'lucide-react';

interface HeaderProps {
  onOpenSearch: () => void;
}

export function Header({ onOpenSearch }: HeaderProps) {
  return (
    <header className="h-12 shrink-0 bg-bg-base border-b border-border flex items-center justify-between px-4 z-20">
      <button
        onClick={onOpenSearch}
        className="flex items-center gap-2.5 px-3 py-1.5 rounded-md bg-bg-surface border border-border hover:border-border-hover transition-colors group min-w-[320px]"
      >
        <Search className="w-3.5 h-3.5 text-text-faint group-hover:text-text-muted transition-colors" />
        <span className="text-sm text-text-faint">Search companies, tickers, reports...</span>
        <kbd className="ml-auto font-mono text-[10px] text-text-faint bg-bg-elevated border border-border px-1.5 py-0.5 rounded">
          Ctrl K
        </kbd>
      </button>

      <div className="flex items-center gap-1">
        <button className="w-8 h-8 flex items-center justify-center rounded-md text-text-muted hover:text-text-primary hover:bg-bg-hover transition-colors relative">
          <Bell className="w-4 h-4" />
          <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full bg-accent" />
        </button>
        <button className="flex items-center gap-2 px-2 py-1 rounded-md hover:bg-bg-hover transition-colors">
          <div className="w-7 h-7 rounded-full bg-accent/15 border border-accent/30 flex items-center justify-center text-xs font-medium text-accent">
            JD
          </div>
          <ChevronDown className="w-3.5 h-3.5 text-text-faint" />
        </button>
      </div>
    </header>
  );
}
