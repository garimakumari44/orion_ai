
"use client";

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

import type { ResearchEvidenceItem } from "@/types";

// ============================================================
// Props
// ============================================================

interface EvidencePanelProps {
  /**
   * Evidence returned by the research backend.
   *
   * The backend may temporarily return:
   *
   *   undefined
   *   null
   *   []
   *
   * The UI normalizes all of these to an empty array.
   */
  evidence?: ResearchEvidenceItem[] | null;
}

// ============================================================
// Helpers
// ============================================================

function safeText(value: unknown): string {
  if (typeof value === "string") {
    return value.trim();
  }

  if (
    typeof value === "number" ||
    typeof value === "boolean"
  ) {
    return String(value);
  }

  return "";
}

function formatCategory(value: string): string {
  const normalized = value
    .trim()
    .replace(/[_-]+/g, " ")
    .replace(/\s+/g, " ");

  if (!normalized) {
    return "Uncategorized";
  }

  return normalized.replace(
    /\b\w/g,
    (character) => character.toUpperCase(),
  );
}

function normalizeConfidence(
  value: unknown,
): number {
  const numericValue =
    typeof value === "number"
      ? value
      : Number(value);

  if (!Number.isFinite(numericValue)) {
    return 0;
  }

  /*
   * Confidence is expected to be represented
   * as a percentage between 0 and 100.
   */
  return Math.min(
    100,
    Math.max(0, numericValue),
  );
}

// ============================================================
// Evidence Panel
// ============================================================

export function EvidencePanel({
  evidence,
}: EvidencePanelProps) {
  const [filter, setFilter] =
    useState<string>("all");

  // ==========================================================
  // Normalize evidence
  // ==========================================================

  const safeEvidence = useMemo<ResearchEvidenceItem[]>(
    () =>
      Array.isArray(evidence)
        ? evidence
        : [],
    [evidence],
  );

  // ==========================================================
  // Categories
  // ==========================================================

  const categories = useMemo(() => {
    const uniqueCategories =
      Array.from(
        new Set(
          safeEvidence
            .map((item) =>
              safeText(item?.category),
            )
            .filter(Boolean),
        ),
      );

    return [
      "all",
      ...uniqueCategories,
    ];
  }, [safeEvidence]);

  /*
   * If the backend changes the available categories,
   * make sure the selected filter remains valid.
   */
  const activeFilter =
    filter === "all" ||
    categories.includes(filter)
      ? filter
      : "all";

  // ==========================================================
  // Filtered evidence
  // ==========================================================

  const filteredEvidence =
    activeFilter === "all"
      ? safeEvidence
      : safeEvidence.filter(
          (item) =>
            safeText(
              item?.category,
            ) === activeFilter,
        );

  // ==========================================================
  // Statistics
  // ==========================================================

  const confidenceValues =
    safeEvidence
      .map((item) =>
        normalizeConfidence(
          item?.confidence,
        ),
      )
      .filter(
        (value) =>
          Number.isFinite(value),
      );

  const averageConfidence =
    confidenceValues.length > 0
      ? Math.round(
          confidenceValues.reduce(
            (sum, value) =>
              sum + value,
            0,
          ) /
            confidenceValues.length,
        )
      : null;

  const sourceTypes =
    new Set(
      safeEvidence
        .map((item) =>
          safeText(item?.source),
        )
        .filter(Boolean),
    );

  const sourceTypeCount =
    sourceTypes.size;

  // ==========================================================
  // Empty state
  // ==========================================================

  if (safeEvidence.length === 0) {
    return (
      <div className="max-w-4xl mx-auto px-6 sm:px-8 py-6 animate-fade-in">
        <EmptyState
          icon={
            <FileText className="w-5 h-5" />
          }
          title="No evidence collected yet"
          description="Evidence will appear here as the research system analyzes source material and identifies source-backed findings."
        />
      </div>
    );
  }

  // ==========================================================
  // Main UI
  // ==========================================================

  return (
    <div className="max-w-4xl mx-auto px-6 sm:px-8 py-6 animate-fade-in">
      {/* ======================================================
          Header
          ====================================================== */}

      <div className="mb-6">
        <div className="flex items-center gap-2 mb-1.5">
          <Shield className="w-4 h-4 text-text-faint" />

          <h2 className="text-sm font-medium text-text-primary">
            Research Evidence
          </h2>
        </div>

        <p className="text-xs text-text-muted leading-5 max-w-2xl">
          Source-backed findings collected during the
          research process. Each item connects a
          research claim to the material supporting it.
        </p>
      </div>

      {/* ======================================================
          Filters
          ====================================================== */}

      {categories.length > 1 && (
        <div className="mb-6">
          <div className="flex items-center gap-1.5 overflow-x-auto scrollbar-none pb-1">
            {categories.map(
              (category) => {
                const active =
                  activeFilter ===
                  category;

                return (
                  <button
                    key={category}
                    type="button"
                    onClick={() =>
                      setFilter(
                        category,
                      )
                    }
                    className={cn(
                      "px-2.5 py-1.5 rounded-md text-xs font-medium whitespace-nowrap transition-colors",
                      active
                        ? "bg-bg-hover text-text-primary border border-border"
                        : "text-text-muted hover:text-text-secondary border border-transparent",
                    )}
                  >
                    {category ===
                    "all"
                      ? "All Evidence"
                      : formatCategory(
                          category,
                        )}
                  </button>
                );
              },
            )}
          </div>
        </div>
      )}

      {/* ======================================================
          Evidence list
          ====================================================== */}

      {filteredEvidence.length ===
      0 ? (
        <EmptyState
          icon={
            <FileText className="w-5 h-5" />
          }
          title="No evidence for this category"
          description="No collected evidence matches the selected category."
        />
      ) : (
        <div className="space-y-3">
          {filteredEvidence.map(
            (item, index) => {
              const itemKey =
                item?.id ??
                `${safeText(
                  item?.category,
                ) || "evidence"}-${index}`;

              /*
               * Current canonical field is `claim`.
               *
               * We intentionally do not use `statement`
               * here because ResearchEvidenceItem is the
               * current frontend contract.
               */
              const claim =
                safeText(item?.claim);

              const source =
                safeText(item?.source);

              const filing =
                safeText(
                  item?.filing,
                );

              const date =
                safeText(item?.date);

              const citation =
                safeText(
                  item?.citation,
                );

              const category =
                safeText(
                  item?.category,
                );

              const confidence =
                normalizeConfidence(
                  item?.confidence,
                );

              return (
                <article
                  key={itemKey}
                  className="group rounded-lg border border-border bg-bg-surface p-5 transition-colors hover:border-border-hover"
                >
                  <div className="flex items-start gap-4">
                    {/* Evidence icon */}

                    <div className="w-9 h-9 rounded-lg bg-bg-elevated border border-border flex items-center justify-center shrink-0">
                      <FileText className="w-4 h-4 text-text-faint" />
                    </div>

                    {/* Content */}

                    <div className="flex-1 min-w-0">
                      {/* ==================================================
                          Claim
                          ================================================== */}

                      {claim && (
                        <div className="mb-3">
                          <div className="text-[10px] text-text-faint uppercase tracking-wider font-mono mb-1.5">
                            Finding
                          </div>

                          <p className="text-sm text-text-primary leading-6 whitespace-pre-wrap break-words">
                            {claim}
                          </p>
                        </div>
                      )}

                      {/* ==================================================
                          Source metadata
                          ================================================== */}

                      {(source ||
                        filing ||
                        date) && (
                        <div className="flex flex-wrap items-center gap-x-2 gap-y-1.5 text-xs">
                          {source && (
                            <span className="text-text-muted font-medium">
                              {source}
                            </span>
                          )}

                          {source &&
                            filing && (
                              <span className="text-text-faint">
                                ·
                              </span>
                            )}

                          {filing && (
                            <span className="font-mono text-text-faint">
                              {filing}
                            </span>
                          )}

                          {(source ||
                            filing) &&
                            date && (
                              <span className="text-text-faint">
                                ·
                              </span>
                            )}

                          {date && (
                            <span className="font-mono text-text-faint">
                              {date}
                            </span>
                          )}
                        </div>
                      )}

                      {/* ==================================================
                          Citation
                          ================================================== */}

                      {citation && (
                        <div className="mt-3 rounded-md border border-border-subtle bg-bg-elevated px-3 py-2.5">
                          <div className="text-[10px] text-text-faint uppercase tracking-wider font-mono mb-1">
                            Source reference
                          </div>

                          <p className="text-xs text-text-muted leading-5 whitespace-pre-wrap break-words">
                            {citation}
                          </p>
                        </div>
                      )}

                      {/* ==================================================
                          Metadata
                          ================================================== */}

                      <div className="flex flex-wrap items-center gap-3 mt-4">
                        {/* Confidence */}

                        <div className="flex items-center gap-2">
                          <Shield className="w-3 h-3 text-text-faint shrink-0" />

                          <span className="text-[10px] text-text-faint uppercase tracking-wider font-mono">
                            Confidence
                          </span>

                          <ConfidenceIndicator
                            value={
                              confidence
                            }
                          />

                          <span className="text-[10px] font-mono text-text-muted tabular-nums">
                            {Math.round(
                              confidence,
                            )}
                            %
                          </span>
                        </div>

                        {/* Category */}

                        {category && (
                          <>
                            <span className="text-text-faint">
                              ·
                            </span>

                            <span className="text-[10px] text-text-faint uppercase tracking-wider font-mono px-1.5 py-0.5 bg-bg-elevated border border-border rounded">
                              {formatCategory(
                                category,
                              )}
                            </span>
                          </>
                        )}
                      </div>
                    </div>

                    {/* ==================================================
                        External source action
                        ================================================== */}

                    <button
                      type="button"
                      aria-label="Open evidence source"
                      title="Open source"
                      className="shrink-0 text-text-faint hover:text-text-muted transition-colors opacity-0 group-hover:opacity-100 focus-visible:opacity-100"
                    >
                      <ExternalLink className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </article>
              );
            },
          )}
        </div>
      )}

      {/* ======================================================
          Statistics
          ====================================================== */}

      <Divider className="my-6" />

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        {/* Evidence count */}

        <div className="bg-bg-surface border border-border rounded-lg p-4">
          <div className="text-[10px] text-text-faint uppercase tracking-wider font-mono mb-1">
            Evidence Items
          </div>

          <div className="font-mono text-2xl text-text-primary tabular-nums">
            {safeEvidence.length}
          </div>

          <div className="mt-1 text-[10px] text-text-faint">
            Source-backed findings
          </div>
        </div>

        {/* Source count */}

        <div className="bg-bg-surface border border-border rounded-lg p-4">
          <div className="text-[10px] text-text-faint uppercase tracking-wider font-mono mb-1">
            Source Types
          </div>

          <div className="font-mono text-2xl text-text-primary tabular-nums">
            {sourceTypeCount}
          </div>

          <div className="mt-1 text-[10px] text-text-faint">
            Distinct source types
          </div>
        </div>

        {/* Confidence */}

        <div className="bg-bg-surface border border-border rounded-lg p-4">
          <div className="text-[10px] text-text-faint uppercase tracking-wider font-mono mb-1">
            Avg Confidence
          </div>

          <div className="font-mono text-2xl text-text-primary tabular-nums">
            {averageConfidence !==
            null
              ? `${averageConfidence}%`
              : "—"}
          </div>

          <div className="mt-1 text-[10px] text-text-faint">
            Across collected evidence
          </div>
        </div>
      </div>
    </div>
  );
}

export default EvidencePanel;

