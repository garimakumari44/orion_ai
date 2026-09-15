import { useState } from 'react';
import { FileText, ExternalLink, Shield } from 'lucide-react';
import { cn, ConfidenceIndicator, Divider } from '../../components/ui';
import type { WorkspaceEvidence } from '../type';

interface EvidenceTabProps {
  evidence: WorkspaceEvidence[];
}

export function EvidenceTab({ evidence }: EvidenceTabProps) {
  const [filter, setFilter] = useState<string>('all');
  const categories = ['all', ...Array.from(new Set(evidence.map((e) => e.docType)))];
  const filtered = filter === 'all' ? evidence : evidence.filter((e) => e.docType === filter);

  return (
    <div className="max-w-4xl mx-auto px-8 py-6 animate-fade-in">
      <div className="mb-5">
        <p className="text-sm text-text-muted">
          Every AI-generated conclusion is traceable to its source. Inspect the evidence behind any finding below.
        </p>
      </div>

      <div className="flex items-center gap-1.5 mb-5 overflow-x-auto scrollbar-none">
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setFilter(cat)}
            className={cn(
              'px-2.5 py-1 rounded text-xs font-medium whitespace-nowrap transition-colors',
              filter === cat
                ? 'bg-bg-hover text-text-primary border border-border'
                : 'text-text-muted hover:text-text-secondary border border-transparent',
            )}
          >
            {cat === 'all' ? 'All Evidence' : cat}
          </button>
        ))}
      </div>

      <div className="space-y-3">
        {filtered.map((e) => (
          <div
            key={e.id}
            className="bg-bg-surface border border-border rounded-lg p-5 hover:border-border-hover transition-colors group"
          >
            <div className="flex items-start gap-4">
              <div className="w-9 h-9 rounded-lg bg-bg-elevated border border-border flex items-center justify-center shrink-0">
                <FileText className="w-4 h-4 text-text-faint" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-text-primary leading-relaxed mb-2.5">{e.statement}</p>
                <div className="flex items-center gap-3 text-xs">
                  <span className="text-text-muted">{e.source}</span>
                  <span className="text-text-faint">·</span>
                  <span className="font-mono text-text-faint">{e.docType}</span>
                  <span className="text-text-faint">·</span>
                  <span className="font-mono text-text-faint">{e.date}</span>
                </div>
                <div className="mt-2 px-3 py-2 bg-bg-elevated border border-border-subtle rounded text-xs text-text-muted italic">
                  {e.citation}
                </div>
                <div className="flex items-center gap-4 mt-3">
                  <div className="flex items-center gap-2">
                    <Shield className="w-3 h-3 text-text-faint" />
                    <span className="text-[10px] text-text-faint uppercase tracking-wider font-mono">Confidence</span>
                    <ConfidenceIndicator value={e.confidence} />
                  </div>
                </div>
              </div>
              <button className="text-text-faint hover:text-text-muted transition-colors opacity-0 group-hover:opacity-100">
                <ExternalLink className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        ))}
      </div>

      <Divider className="my-6" />

      <div className="grid grid-cols-3 gap-3">
        <div className="bg-bg-surface border border-border rounded-lg p-4">
          <div className="text-[10px] text-text-faint uppercase tracking-wider font-mono mb-1">Evidence Items</div>
          <div className="font-mono text-2xl text-text-primary tabular-nums">{evidence.length}</div>
        </div>
        <div className="bg-bg-surface border border-border rounded-lg p-4">
          <div className="text-[10px] text-text-faint uppercase tracking-wider font-mono mb-1">Source Types</div>
          <div className="font-mono text-2xl text-text-primary tabular-nums">{categories.length - 1}</div>
        </div>
        <div className="bg-bg-surface border border-border rounded-lg p-4">
          <div className="text-[10px] text-text-faint uppercase tracking-wider font-mono mb-1">Avg Confidence</div>
          <div className="font-mono text-2xl text-text-primary tabular-nums">
            {Math.round(evidence.reduce((a, e) => a + e.confidence, 0) / evidence.length)}%
          </div>
        </div>
      </div>
    </div>
  );
}
