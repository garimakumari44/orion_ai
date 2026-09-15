import { Check, Loader, Clock, Pencil, Download } from 'lucide-react';
import { cn } from '../../components/ui';
import type { DraftSection } from '../type';

interface DraftTabProps {
  title: string;
  sections: DraftSection[];
}

function StatusBadge({ status }: { status: DraftSection['status'] }) {
  if (status === 'complete') {
    return (
      <span className="flex items-center gap-1 text-[10px] uppercase tracking-wider font-mono text-success">
        <Check className="w-3 h-3" /> Complete
      </span>
    );
  }
  if (status === 'in-progress') {
    return (
      <span className="flex items-center gap-1 text-[10px] uppercase tracking-wider font-mono text-accent">
        <Loader className="w-3 h-3 animate-spin" /> Generating...
      </span>
    );
  }
  return (
    <span className="flex items-center gap-1 text-[10px] uppercase tracking-wider font-mono text-text-faint">
      <Clock className="w-3 h-3" /> Waiting
    </span>
  );
}

export function DraftTab({ title, sections }: DraftTabProps) {
  return (
    <div className="max-w-3xl mx-auto px-8 py-6 animate-fade-in">
      <div className="flex items-center justify-between mb-5">
        <div>
          <h2 className="text-lg font-semibold text-text-primary">{title}</h2>
          <p className="text-xs text-text-muted mt-0.5">The draft updates automatically as research progresses. You can edit any section.</p>
        </div>
        <button className="flex items-center gap-2 px-3 py-1.5 rounded-md bg-accent/10 border border-accent/20 text-accent text-sm font-medium hover:bg-accent/15 transition-colors">
          <Download className="w-3.5 h-3.5" />
          Export
        </button>
      </div>

      <div className="space-y-3">
        {sections.map((section) => (
          <div
            key={section.id}
            className={cn(
              'bg-bg-surface border rounded-lg p-5 transition-colors',
              section.status === 'in-progress' ? 'border-accent/30' : 'border-border',
            )}
          >
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-medium text-text-primary">{section.title}</h3>
              <StatusBadge status={section.status} />
            </div>

            {section.content ? (
              <div className="space-y-2">
                {section.content.split('\n').map((line, i) =>
                  line.trim() === '' ? (
                    <div key={i} className="h-1" />
                  ) : (
                    <p key={i} className="text-sm text-text-secondary leading-relaxed">
                      {line}
                    </p>
                  ),
                )}
              </div>
            ) : (
              <div className="py-4 text-center">
                <p className="text-xs text-text-faint italic">This section will be generated when research reaches this stage.</p>
              </div>
            )}

            {section.content && section.status === 'complete' && (
              <div className="flex items-center gap-3 mt-3 pt-3 border-t border-border-subtle">
                <button className="flex items-center gap-1 text-[11px] text-text-faint hover:text-text-muted transition-colors">
                  <Pencil className="w-3 h-3" /> Edit
                </button>
                {section.lastUpdated && (
                  <span className="text-[10px] text-text-faint font-mono ml-auto">Updated {section.lastUpdated}</span>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
