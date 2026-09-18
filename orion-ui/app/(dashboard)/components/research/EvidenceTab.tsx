import { useMemo, useState } from "react";
import {
  FileText,
  ExternalLink,
  Shield,
} from "lucide-react";

import {
  cn,
  ConfidenceIndicator,
  Divider,
  EmptyState,
} from "../../components/ui";

import type { CompanyData } from "../../../../types";

interface EvidenceTabProps {
  data: CompanyData;
}

export function EvidenceTab({
  data,
}: EvidenceTabProps) {
  const [filter, setFilter] = useState<string>("all");

  const evidence = Array.isArray(data.evidence)
    ? data.evidence
    : [];

  const sources = Array.isArray(data.sources)
    ? data.sources
    : [];

  const categories = useMemo(
    () => [
      "all",
      ...Array.from(
        new Set(
          evidence
            .map((item) => item.category)
            .filter(Boolean),
        ),
      ),
    ],
    [evidence],
  );

  const filtered =
    filter === "all"
      ? evidence
      : evidence.filter(
          (item) => item.category === filter,
        );

  const averageConfidence =
    evidence.length > 0
      ? Math.round(
          evidence.reduce(
            (total, item) =>
              total + (Number(item.confidence) || 0),
            0,
          ) / evidence.length,
        )
      : null;

  const totalSources = sources.reduce(
    (total, source) =>
      total + (Number(source.count) || 0),
    0,
  );

  if (evidence.length === 0) {
    return (
      <div className="max-w-4xl mx-auto px-8 py-6 animate-fade-in">
        <EmptyState
          icon={<FileText className="w-5 h-5" />}
          title="No evidence collected"
          description="The evidence agent completed successfully, but no source-backed claims were returned for this research yet."
        />

        <Divider className="my-6" />

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <div className="bg-bg-surface border border-border rounded-lg p-4">
            <div className="text-[10px] text-text-faint uppercase tracking-wider font-mono mb-1">
              Total Sources
            </div>

            <div className="font-mono text-2xl text-text-primary tabular-nums">
              {totalSources}
            </div>
          </div>

          <div className="bg-bg-surface border border-border rounded-lg p-4">
            <div className="text-[10px] text-text-faint uppercase tracking-wider font-mono mb-1">
              Evidence Items
            </div>

            <div className="font-mono text-2xl text-text-primary tabular-nums">
              0
            </div>
          </div>

          <div className="bg-bg-surface border border-border rounded-lg p-4">
            <div className="text-[10px] text-text-faint uppercase tracking-wider font-mono mb-1">
              Avg Confidence
            </div>

            <div className="font-mono text-2xl text-text-muted tabular-nums">
              â€”
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-8 py-6 animate-fade-in">
      <div className="mb-5">
        <p className="text-sm text-text-muted">
          Every conclusion in this research is backed by
          source material. Each evidence item traces a
          statement to its origin.
        </p>
      </div>

      <div className="flex items-center gap-1.5 mb-5 overflow-x-auto scrollbar-none">
        {categories.map((category) => (
          <button
            key={category}
            onClick={() => category && setFilter(category)}
            className={cn(
              "px-2.5 py-1 rounded text-xs font-medium whitespace-nowrap transition-colors",
              filter === category
                ? "bg-bg-hover text-text-primary border border-border"
                : "text-text-muted hover:text-text-secondary border border-transparent",
            )}
          >
            {category === "all"
              ? "All Evidence"
              : category}
          </button>
        ))}
      </div>

      <div className="space-y-3">
        {filtered.map((item) => (
          <div
            key={item.id}
            className="bg-bg-surface border border-border rounded-lg p-5 hover:border-border-hover transition-colors group"
          >
            <div className="flex items-start gap-4">
              <div className="w-9 h-9 rounded-lg bg-bg-elevated border border-border flex items-center justify-center shrink-0">
                <FileText className="w-4 h-4 text-text-faint" />
              </div>

              <div className="flex-1 min-w-0">
                <p className="text-sm text-text-primary leading-relaxed mb-2.5">
                  {item.statement}
                </p>

                <div className="flex items-center gap-4 text-xs">
                  <span className="text-text-muted">
                    {item.source}
                  </span>

                  {item.filing && (
                    <>
                      <span className="text-text-faint">
                        Â·
                      </span>

                      <span className="font-mono text-text-faint">
                        {item.filing}
                      </span>
                    </>
                  )}

                  {item.date && (
                    <>
                      <span className="text-text-faint">
                        Â·
                      </span>

                      <span className="font-mono text-text-faint">
                        {item.date}
                      </span>
                    </>
                  )}
                </div>

                {item.citation && (
                  <div className="mt-2 px-3 py-2 bg-bg-elevated border border-border-subtle rounded text-xs text-text-muted italic">
                    {item.citation}
                  </div>
                )}

                <div className="flex items-center gap-4 mt-3">
                  <div className="flex items-center gap-2">
                    <Shield className="w-3 h-3 text-text-faint" />

                    <span className="text-[10px] text-text-faint uppercase tracking-wider font-mono">
                      Confidence
                    </span>

                    <ConfidenceIndicator
                      value={Number(item.confidence) || 0}
                    />
                  </div>

                  {item.category && (
                    <span className="text-[10px] text-text-faint uppercase tracking-wider font-mono px-1.5 py-0.5 bg-bg-elevated border border-border rounded">
                      {item.category}
                    </span>
                  )}
                </div>
              </div>

              <button
                type="button"
                aria-label="Open evidence source"
                className="text-text-faint hover:text-text-muted transition-colors opacity-0 group-hover:opacity-100"
              >
                <ExternalLink className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        ))}
      </div>

      <Divider className="my-6" />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <div className="bg-bg-surface border border-border rounded-lg p-4">
          <div className="text-[10px] text-text-faint uppercase tracking-wider font-mono mb-1">
            Total Sources
          </div>

          <div className="font-mono text-2xl text-text-primary tabular-nums">
            {totalSources}
          </div>
        </div>

        <div className="bg-bg-surface border border-border rounded-lg p-4">
          <div className="text-[10px] text-text-faint uppercase tracking-wider font-mono mb-1">
            Evidence Items
          </div>

          <div className="font-mono text-2xl text-text-primary tabular-nums">
            {evidence.length}
          </div>
        </div>

        <div className="bg-bg-surface border border-border rounded-lg p-4">
          <div className="text-[10px] text-text-faint uppercase tracking-wider font-mono mb-1">
            Avg Confidence
          </div>

          <div className="font-mono text-2xl text-text-primary tabular-nums">
            {averageConfidence !== null
              ? `${averageConfidence}%`
              : "â€”"}
          </div>
        </div>
      </div>
    </div>
  );
}
