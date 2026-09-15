"use client";

import {
  FileText,
  Download,
  ExternalLink,
} from "lucide-react";

import {
  cn,
  EmptyState,
} from "../../components/ui";

import type { ResearchDocument } from "@/types";

interface DocumentPanelProps {
  documents?: ResearchDocument[] | null;
}

function StatusBadge({
  status,
}: {
  status: ResearchDocument["status"];
}) {
  const styles: Record<
    ResearchDocument["status"],
    string
  > = {
    processed: "text-success",
    processing: "text-warning",
    failed: "text-danger",
  };

  const labels: Record<
    ResearchDocument["status"],
    string
  > = {
    processed: "Processed",
    processing: "Processing",
    failed: "Failed",
  };

  return (
    <span
      className={cn(
        "text-[10px] uppercase tracking-wider font-mono",
        styles[status]
      )}
    >
      {labels[status]}
    </span>
  );
}

export function DocumentPanel({
  documents,
}: DocumentPanelProps) {
  const safeDocuments = Array.isArray(documents)
    ? documents
    : [];

  if (safeDocuments.length === 0) {
    return (
      <div className="max-w-4xl mx-auto px-8 py-6 animate-fade-in">
        <EmptyState
          icon={
            <FileText className="w-5 h-5" />
          }
          title="No documents retrieved yet"
          description="Source documents will appear here as the AI collects filings, transcripts, reports, and other research materials."
        />
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-8 py-6 animate-fade-in">

      <div className="mb-5">
        <p className="text-sm text-text-muted">
          Research materials retrieved and processed by
          the AI.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">

        {safeDocuments.map((doc) => (
          <div
            key={String(doc.id)}
            className="bg-bg-surface border border-border rounded-lg p-4 hover:border-border-hover transition-colors group"
          >
            <div className="flex items-start gap-3">

              {/* Icon */}
              <div className="w-9 h-9 rounded-lg bg-bg-elevated border border-border flex items-center justify-center shrink-0">
                <FileText className="w-4 h-4 text-text-faint" />
              </div>

              {/* Main information */}
              <div className="flex-1 min-w-0">

                <div className="text-sm text-text-primary truncate">
                  {doc.title || "Untitled document"}
                </div>

                <div className="flex items-center gap-2 mt-1 text-xs min-w-0">

                  {doc.source && (
                    <>
                      <span className="text-text-muted truncate">
                        {doc.source}
                      </span>

                      {doc.date && (
                        <span className="text-text-faint shrink-0">
                          ·
                        </span>
                      )}
                    </>
                  )}

                  {doc.date && (
                    <span className="font-mono text-text-faint shrink-0">
                      {doc.date}
                    </span>
                  )}

                </div>

                <div className="flex items-center gap-3 mt-2 flex-wrap">

                  <StatusBadge
                    status={doc.status}
                  />

                  {doc.type && (
                    <span className="text-[10px] text-text-faint font-mono">
                      {doc.type}
                    </span>
                  )}

                  {doc.size && (
                    <>
                      <span className="text-text-faint">
                        ·
                      </span>

                      <span className="text-[10px] text-text-faint font-mono">
                        {doc.size}
                      </span>
                    </>
                  )}

                </div>
              </div>

              {/* Actions */}
              <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">

                <button
                  type="button"
                  disabled
                  title="Download unavailable"
                  aria-label="Download document"
                  className="w-7 h-7 flex items-center justify-center rounded-md text-text-faint/40 cursor-not-allowed"
                >
                  <Download className="w-3.5 h-3.5" />
                </button>

                <button
                  type="button"
                  disabled
                  title="Source link unavailable"
                  aria-label="Open document"
                  className="w-7 h-7 flex items-center justify-center rounded-md text-text-faint/40 cursor-not-allowed"
                >
                  <ExternalLink className="w-3.5 h-3.5" />
                </button>

              </div>

            </div>
          </div>
        ))}

      </div>
    </div>
  );
}