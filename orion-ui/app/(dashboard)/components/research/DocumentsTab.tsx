
'use client';

import { useMemo, useState } from 'react';
import {
  FileText,
  Download,
  ChevronRight,
} from 'lucide-react';

import { cn, Divider, EmptyState } from '../ui';
import type { CompanyData, DocumentItem } from '@/types';

interface DocumentsTabProps {
  data: CompanyData;
}

const typeColors: Partial<Record<DocumentItem['type'], string>> = {
  '10-K': 'text-accent',
  '10-Q': 'text-accent',
  'Earnings Call': 'text-warning',
  'Investor Presentation': 'text-success',
  News: 'text-text-muted',
  'Annual Report': 'text-accent',
};

export function DocumentsTab({ data }: DocumentsTabProps) {
  const [filter, setFilter] = useState<'all' | DocumentItem['type']>('all');

  const types = useMemo(
    () => [
      'all' as const,
      ...Array.from(
        new Set(data.documents.map((document) => document.type))
      ),
    ],
    [data.documents]
  );

  const filteredDocuments = useMemo(() => {
    if (filter === 'all') {
      return data.documents;
    }

    return data.documents.filter(
      (document) => document.type === filter
    );
  }, [data.documents, filter]);

  const handleOpenDocument = (document: DocumentItem) => {
    console.log('Open document:', document);

    // TODO:
    // router.push(`/research/documents/${document.id}`)
    // or open a document preview modal
  };

  const handleDownload = (document: DocumentItem) => {
    console.log('Download:', document);

    // TODO:
    // window.open(document.url, '_blank')
    // or trigger a download endpoint
  };

  return (
    <div className="space-y-5">
      {/* Description */}
      <div>
        <p className="text-sm text-text-secondary leading-relaxed">
          Primary source documents used in this research. All filings are
          sourced from SEC EDGAR and company investor relations.
        </p>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-1.5 overflow-x-auto scrollbar-none">
        {types.map((type) => (
          <button
            key={type}
            type="button"
            onClick={() => setFilter(type)}
            className={cn(
              'px-2.5 py-1 rounded text-xs font-medium',
              'whitespace-nowrap transition-colors',
              filter === type
                ? 'bg-bg-hover text-text-primary border border-border'
                : 'text-text-muted hover:text-text-secondary border border-transparent'
            )}
          >
            {type === 'all' ? 'All Documents' : type}
          </button>
        ))}
      </div>

      {/* Documents */}
      {filteredDocuments.length === 0 ? (
        <EmptyState
          icon={<FileText className="w-5 h-5" />}
          title="No documents found"
          description="No documents match this filter. Try selecting a different document type."
        />
      ) : (
        <div className="bg-bg-surface border border-border rounded-lg overflow-hidden">
          {filteredDocuments.map((document, index) => {
            const colorClass =
              typeColors[document.type] ?? 'text-text-faint';

            return (
              <div key={document.id}>
                <div
                  role="button"
                  tabIndex={0}
                  onClick={() => handleOpenDocument(document)}
                  onKeyDown={(event) => {
                    if (
                      event.key === 'Enter' ||
                      event.key === ' '
                    ) {
                      event.preventDefault();
                      handleOpenDocument(document);
                    }
                  }}
                  className={cn(
                    'w-full flex items-center gap-4 px-5 py-3.5',
                    'hover:bg-bg-hover/30 transition-colors',
                    'group text-left cursor-pointer',
                    'focus:outline-none focus:bg-bg-hover/30'
                  )}
                >
                  {/* Document Icon */}
                  <div className="w-9 h-9 rounded-lg bg-bg-elevated border border-border flex items-center justify-center shrink-0">
                    <FileText
                      className={cn('w-4 h-4', colorClass)}
                    />
                  </div>

                  {/* Document Information */}
                  <div className="flex-1 min-w-0">
                    <div className="text-sm text-text-primary truncate">
                      {document.title}
                    </div>

                    <div className="flex items-center gap-3 mt-0.5 flex-wrap">
                      <span
                        className={cn(
                          'text-[10px] font-mono uppercase tracking-wider',
                          colorClass
                        )}
                      >
                        {document.type}
                      </span>

                      <span className="text-xs text-text-faint font-mono">
                        {document.date}
                      </span>

                      <span className="text-xs text-text-faint">
                        ·
                      </span>

                      <span className="text-xs text-text-faint">
                        {document.pages} pages
                      </span>

                      <span className="text-xs text-text-faint">
                        ·
                      </span>

                      <span className="text-xs text-text-faint">
                        {document.source}
                      </span>
                    </div>
                  </div>

                  {/* Download */}
                  <button
                    type="button"
                    aria-label={`Download ${document.title}`}
                    onClick={(event) => {
                      event.stopPropagation();
                      handleDownload(document);
                    }}
                    className={cn(
                      'text-text-faint hover:text-text-muted',
                      'transition-colors p-1.5 rounded',
                      'hover:bg-bg-elevated'
                    )}
                  >
                    <Download className="w-3.5 h-3.5" />
                  </button>

                  {/* Open */}
                  <ChevronRight
                    className={cn(
                      'w-4 h-4 text-text-faint',
                      'group-hover:text-text-muted',
                      'transition-colors shrink-0'
                    )}
                  />
                </div>

                {index < filteredDocuments.length - 1 && <Divider />}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

