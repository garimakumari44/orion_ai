import { useState } from 'react';
import { Upload, FileText, Search, Check, Loader, AlertCircle, Table, FileText as DocIcon } from 'lucide-react';
import { cn } from '../../components/ui';
import type { KnowledgeDoc } from "@/types";

interface KnowledgeTabProps {
  documents: KnowledgeDoc[];
}

function StatusIcon({ status }: { status: KnowledgeDoc['status'] }) {
  if (status === 'processed') return <Check className="w-3.5 h-3.5 text-success" />;
  if (status === 'processing') return <Loader className="w-3.5 h-3.5 text-warning animate-spin" />;
  return <AlertCircle className="w-3.5 h-3.5 text-danger" />;
}

function statusLabel(status: KnowledgeDoc['status']) {
  if (status === 'processed') return 'Processed';
  if (status === 'processing') return 'Processing...';
  return 'Failed';
}

export function KnowledgeTab({ documents }: KnowledgeTabProps) {
  const [query, setQuery] = useState('');
  const filtered = documents.filter(
    (d) => d.name.toLowerCase().includes(query.toLowerCase()) || (d.type ?? "").toLowerCase().includes(query.toLowerCase()),
  );

  return (
    <div className="max-w-4xl mx-auto px-8 py-6 animate-fade-in">
      <div className="flex items-center justify-between mb-5">
        <p className="text-sm text-text-muted">Project-specific knowledge. Only documents relevant to this research appear here.</p>
        <button className="flex items-center gap-2 px-3 py-1.5 rounded-md bg-accent/10 border border-accent/20 text-accent text-sm font-medium hover:bg-accent/15 transition-colors">
          <Upload className="w-3.5 h-3.5" />
          Upload
        </button>
      </div>

      <div className="flex items-center gap-2 mb-4">
        <div className="flex-1 flex items-center gap-2 bg-bg-surface border border-border rounded-lg px-3 py-2 focus-within:border-border-hover transition-colors">
          <Search className="w-3.5 h-3.5 text-text-faint" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search documents..."
            className="flex-1 bg-transparent text-sm text-text-primary placeholder:text-text-faint outline-none"
          />
        </div>
      </div>

      <div className="space-y-2">
        {filtered.map((doc) => (
          <div
            key={doc.id}
            className="bg-bg-surface border border-border rounded-lg p-4 hover:border-border-hover transition-colors"
          >
            <div className="flex items-start gap-3">
              <div className="w-9 h-9 rounded-lg bg-bg-elevated border border-border flex items-center justify-center shrink-0">
                <DocIcon className="w-4 h-4 text-text-faint" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm text-text-primary truncate">{doc.name}</span>
                </div>
                <div className="flex items-center gap-3 text-xs">
                  <span className="text-text-muted">{doc.type}</span>
                  <span className="text-text-faint">Â·</span>
                  <span className="font-mono text-text-faint">{doc.size}</span>
                  <span className="text-text-faint">Â·</span>
                  <span className="font-mono text-text-faint">{doc.uploadedAt}</span>
                </div>

                <div className="flex items-center gap-2 mt-2">
                  <StatusIcon status={doc.status} />
                  <span
                    className={cn(
                      'text-[10px] uppercase tracking-wider font-mono',
                      doc.status === 'processed' && 'text-success',
                      doc.status === 'processing' && 'text-warning',
                      doc.status === 'failed' && 'text-danger',
                    )}
                  >
                    {statusLabel(doc.status)}
                  </span>
                </div>

                {doc.summary && (
                  <div className="mt-2.5 px-3 py-2 bg-bg-elevated border border-border-subtle rounded text-xs text-text-muted leading-relaxed">
                    {doc.summary}
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}


