"use client";

import {
  Target,
  TrendingUp,
  AlertTriangle,
  Calendar,
  DollarSign,
  Building2,
  BarChart3,
} from "lucide-react";

import {
  cn,
  SectionCard,
  RecommendationBadge,
  ConfidenceIndicator,
  Divider,
  EmptyState,
} from "../../components/ui";

import type {
  CompanyData,
  CompanyEvidence,
} from "@/types/company";
import { normalizeRecommendation } from "@/models/company";

interface OverviewTabProps {
  data: CompanyData;
}

function isFiniteNumber(value: unknown): value is number {
  return (
    typeof value === "number" &&
    Number.isFinite(value)
  );
}

function formatNumber(value: unknown): string {
  if (!isFiniteNumber(value)) {
    return "—";
  }

  return new Intl.NumberFormat("en-US", {
    maximumFractionDigits: 2,
  }).format(value);
}

function formatCurrency(value: unknown): string {
  if (!isFiniteNumber(value)) {
    return "—";
  }

  const absolute = Math.abs(value);

  if (absolute >= 1_000_000_000_000) {
    return `$${(value / 1_000_000_000_000).toFixed(2)}T`;
  }

  if (absolute >= 1_000_000_000) {
    return `$${(value / 1_000_000_000).toFixed(2)}B`;
  }

  if (absolute >= 1_000_000) {
    return `$${(value / 1_000_000).toFixed(2)}M`;
  }

  return `$${value.toFixed(2)}`;
}

function formatPercentage(
  value: unknown,
  decimals = 1
): string {
  if (!isFiniteNumber(value)) {
    return "—";
  }

  return `${value >= 0 ? "+" : ""}${value.toFixed(
    decimals
  )}%`;
}

function normalizeConfidence(
  value: unknown
): number {
  if (!isFiniteNumber(value)) {
    return 0;
  }

  if (value > 1) {
    return Math.min(1, value / 100);
  }

  return Math.max(0, Math.min(1, value));
}

function getEvidenceText(
  evidence: CompanyEvidence
): string {
  if (typeof evidence.claim === "string") {
    return evidence.claim;
  }

  if (typeof evidence.source === "string") {
    return evidence.source;
  }

  return "Verified research evidence.";
}

function EmptySection({
  title,
  description,
  icon,
}: {
  title: string;
  description: string;
  icon: React.ReactNode;
}) {
  return (
    <EmptyState
      icon={icon}
      title={title}
      description={description}
    />
  );
}

export function OverviewTab({
  data,
}: OverviewTabProps) {
  const summary = data.summary;

  const companyName =
    typeof summary?.name === "string"
      ? summary.name
      : "Company";

  const ticker =
    typeof summary?.ticker === "string"
      ? summary.ticker
      : "—";

  const recommendation =
    typeof summary?.recommendation === "string"
      ? summary.recommendation
      : "Not available";

  const currentPrice = isFiniteNumber(
    summary?.currentPrice
  )
    ? summary.currentPrice
    : null;

  const fairValue = isFiniteNumber(
    summary?.fairValue
  )
    ? summary.fairValue
    : null;

  const upside = isFiniteNumber(summary?.upside)
    ? summary.upside
    : currentPrice !== null &&
        fairValue !== null &&
        currentPrice !== 0
      ? ((fairValue - currentPrice) /
          currentPrice) *
        100
      : null;

  const confidence = normalizeConfidence(
    summary?.confidence
  );

  const thesis =
    typeof data.thesis === "string"
      ? data.thesis.trim()
      : "";

  const analysisSections =
    Array.isArray(data.analysisSections)
      ? data.analysisSections
      : [];

  const incomeStatement =
    Array.isArray(data.incomeStatement)
      ? data.incomeStatement
      : [];

  const evidence =
    Array.isArray(data.evidence)
      ? data.evidence
      : [];

  /*
   * We deliberately do not render data.summary directly.
   *
   * data.summary is an object:
   *
   * {
   *   name,
   *   ticker,
   *   recommendation,
   *   fairValue,
   *   currentPrice,
   *   upside,
   *   confidence,
   *   lastResearched
   * }
   *
   * React cannot render that object as a child.
   */

  const businessSection =
    analysisSections[0];

  const financialSection =
    analysisSections[1];

  const industrySection =
    analysisSections[2];

  const valuationSection =
    analysisSections[6];

  return (
    <div className="max-w-4xl mx-auto px-8 py-6 space-y-6 animate-fade-in">

      {/* ============================================================
          COMPANY OVERVIEW
          ============================================================ */}

      <SectionCard title="Company Overview">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">

          <div className="flex items-start gap-3">
            <div className="w-9 h-9 rounded-lg bg-bg-elevated border border-border flex items-center justify-center shrink-0">
              <Building2 className="w-4 h-4 text-text-faint" />
            </div>

            <div>
              <div className="text-[10px] text-text-faint uppercase tracking-wider font-mono mb-1">
                Company
              </div>

              <div className="text-sm text-text-primary font-medium">
                {companyName}
              </div>

              <div className="text-xs text-text-muted font-mono mt-0.5">
                {ticker}
              </div>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <div className="w-9 h-9 rounded-lg bg-bg-elevated border border-border flex items-center justify-center shrink-0">
              <Target className="w-4 h-4 text-text-faint" />
            </div>

            <div>
              <div className="text-[10px] text-text-faint uppercase tracking-wider font-mono mb-1">
                Research Status
              </div>

              <div className="text-sm text-text-primary font-medium">
                {data.status ?? "Research available"}
              </div>

              {summary?.lastResearched && (
                <div className="text-xs text-text-muted mt-0.5">
                  Last researched{" "}
                  {summary.lastResearched}
                </div>
              )}
            </div>
          </div>

        </div>
      </SectionCard>

      {/* ============================================================
          INVESTMENT THESIS
          ============================================================ */}

      <SectionCard title="Investment Thesis">

        {thesis ? (
          <p className="text-sm text-text-secondary leading-relaxed whitespace-pre-wrap">
            {thesis}
          </p>
        ) : (
          <p className="text-sm text-text-muted leading-relaxed">
            A complete investment thesis has not
            been generated yet. The available
            research data can still be reviewed
            below.
          </p>
        )}

        <div className="flex flex-wrap items-center gap-6 mt-5 pt-5 border-t border-border">

          {/* Recommendation */}
          <div>
            <div className="text-[10px] text-text-faint uppercase tracking-wider font-mono mb-1">
              Recommendation
            </div>

            {recommendation !==
            "Not available" ? (
             <RecommendationBadge
  value={normalizeRecommendation(recommendation)}
  size="md"
/>
            ) : (
              <span className="text-sm text-text-muted">
                Not available
              </span>
            )}
          </div>

          {/* Fair Value */}
          <div>
            <div className="text-[10px] text-text-faint uppercase tracking-wider font-mono mb-1">
              Fair Value
            </div>

            <div className="font-mono text-lg text-text-primary tabular-nums">
              {fairValue !== null
                ? `$${fairValue.toFixed(2)}`
                : "—"}
            </div>
          </div>

          {/* Current Price */}
          <div>
            <div className="text-[10px] text-text-faint uppercase tracking-wider font-mono mb-1">
              Current Price
            </div>

            <div className="font-mono text-lg text-text-primary tabular-nums">
              {currentPrice !== null
                ? `$${currentPrice.toFixed(2)}`
                : "—"}
            </div>
          </div>

          {/* Upside */}
          <div>
            <div className="text-[10px] text-text-faint uppercase tracking-wider font-mono mb-1">
              Upside
            </div>

            <div
              className={cn(
                "font-mono text-lg tabular-nums",
                upside === null
                  ? "text-text-muted"
                  : upside >= 0
                    ? "text-success"
                    : "text-danger"
              )}
            >
              {formatPercentage(upside)}
            </div>
          </div>

          {/* Confidence */}
          <div>
            <div className="text-[10px] text-text-faint uppercase tracking-wider font-mono mb-1">
              Confidence
            </div>

            {confidence > 0 ? (
              <ConfidenceIndicator
                value={confidence}
              />
            ) : (
              <span className="text-sm text-text-muted">
                Not available
              </span>
            )}
          </div>

        </div>
      </SectionCard>

      {/* ============================================================
          RESEARCH HIGHLIGHTS
          ============================================================ */}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

        <SectionCard
          title="Business Analysis"
          action={
            <TrendingUp className="w-3.5 h-3.5 text-text-faint" />
          }
        >
          {businessSection ? (
            <div className="space-y-3">
              <div className="text-sm text-text-primary font-medium">
                {businessSection.title}
              </div>

              {Array.isArray(
                businessSection.content
              ) &&
                businessSection.content.length >
                  0 && (
                  <div className="space-y-2">
                    {businessSection.content.map(
                      (item, index) => (
                        <div
                          key={`${businessSection.id ?? "business"}-${index}`}
                          className="flex items-start gap-2.5"
                        >
                          <div className="mt-1.5 w-1 h-1 rounded-full bg-accent shrink-0" />

                          <p className="text-xs text-text-muted leading-relaxed">
                            {item}
                          </p>
                        </div>
                      )
                    )}
                  </div>
                )}
            </div>
          ) : (
            <EmptySection
              icon={
                <TrendingUp className="w-5 h-5" />
              }
              title="No business analysis"
              description="The research pipeline has not produced a business analysis section yet."
            />
          )}
        </SectionCard>

        <SectionCard
          title="Risk & Industry Analysis"
          action={
            <AlertTriangle className="w-3.5 h-3.5 text-text-faint" />
          }
        >
          {industrySection ? (
            <div className="space-y-3">
              <div className="text-sm text-text-primary font-medium">
                {industrySection.title}
              </div>

              {Array.isArray(
                industrySection.content
              ) &&
                industrySection.content.length >
                  0 && (
                  <div className="space-y-2">
                    {industrySection.content.map(
                      (item, index) => (
                        <div
                          key={`${industrySection.id ?? "industry"}-${index}`}
                          className="flex items-start gap-2.5"
                        >
                          <div className="mt-1.5 w-1 h-1 rounded-full bg-danger shrink-0" />

                          <p className="text-xs text-text-muted leading-relaxed">
                            {item}
                          </p>
                        </div>
                      )
                    )}
                  </div>
                )}
            </div>
          ) : (
            <EmptySection
              icon={
                <AlertTriangle className="w-5 h-5" />
              }
              title="No industry analysis"
              description="Industry and risk analysis has not been returned yet."
            />
          )}
        </SectionCard>

      </div>

      {/* ============================================================
          FINANCIAL METRICS
          ============================================================ */}

      <SectionCard
        title="Key Financial Metrics"
        action={
          <DollarSign className="w-3.5 h-3.5 text-text-faint" />
        }
      >
        {incomeStatement.length === 0 ? (
          <EmptySection
            icon={
              <DollarSign className="w-5 h-5" />
            }
            title="Financial data not available"
            description="The financial research data has not been returned yet."
          />
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">

            <div className="bg-bg-elevated border border-border-subtle rounded-lg p-3">
              <div className="text-[10px] text-text-faint uppercase tracking-wide mb-1">
                Current Price
              </div>

              <div className="font-mono text-sm text-text-primary tabular-nums">
                {formatCurrency(currentPrice)}
              </div>
            </div>

            <div className="bg-bg-elevated border border-border-subtle rounded-lg p-3">
              <div className="text-[10px] text-text-faint uppercase tracking-wide mb-1">
                Fair Value
              </div>

              <div className="font-mono text-sm text-text-primary tabular-nums">
                {formatCurrency(fairValue)}
              </div>
            </div>

            <div className="bg-bg-elevated border border-border-subtle rounded-lg p-3">
              <div className="text-[10px] text-text-faint uppercase tracking-wide mb-1">
                Upside
              </div>

              <div
                className={cn(
                  "font-mono text-sm tabular-nums",
                  upside === null
                    ? "text-text-muted"
                    : upside >= 0
                      ? "text-success"
                      : "text-danger"
                )}
              >
                {formatPercentage(upside)}
              </div>
            </div>

            <div className="bg-bg-elevated border border-border-subtle rounded-lg p-3">
              <div className="text-[10px] text-text-faint uppercase tracking-wide mb-1">
                Confidence
              </div>

              <div className="font-mono text-sm text-text-primary tabular-nums">
                {confidence > 0
                  ? `${Math.round(
                      confidence * 100
                    )}%`
                  : "—"}
              </div>
            </div>

          </div>
        )}
      </SectionCard>

      {/* ============================================================
          VALUATION
          ============================================================ */}

      <SectionCard
        title="Valuation"
        action={
          <BarChart3 className="w-3.5 h-3.5 text-text-faint" />
        }
      >
        {valuationSection ? (
          <div className="space-y-3">
            <div className="text-sm text-text-primary font-medium">
              {valuationSection.title}
            </div>

            {valuationSection.content.map(
              (item, index) => (
                <div key={index}>
                  <p className="text-xs text-text-muted leading-relaxed">
                    {item}
                  </p>
                </div>
              )
            )}
          </div>
        ) : data.dcf ? (
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">

            <div className="bg-bg-elevated border border-border-subtle rounded-lg p-3">
              <div className="text-[10px] text-text-faint uppercase tracking-wide mb-1">
                DCF Fair Value
              </div>

              <div className="font-mono text-sm text-text-primary">
                {formatCurrency(
                  data.dcf.fairValue
                )}
              </div>
            </div>

            <div className="bg-bg-elevated border border-border-subtle rounded-lg p-3 md:col-span-2">
              <div className="text-[10px] text-text-faint uppercase tracking-wide mb-1">
                Assumptions
              </div>

              <div className="space-y-1">
                {data.dcf.assumptions.map(
                  (assumption, index) => (
                    <div
                      key={`${assumption.label}-${index}`}
                      className="flex justify-between gap-4 text-xs"
                    >
                      <span className="text-text-muted">
                        {assumption.label}
                      </span>

                      <span className="font-mono text-text-primary">
                        {assumption.value}
                      </span>
                    </div>
                  )
                )}
              </div>
            </div>

          </div>
        ) : (
          <EmptySection
            icon={
              <BarChart3 className="w-5 h-5" />
            }
            title="Valuation not available"
            description="No valuation analysis has been returned yet."
          />
        )}
      </SectionCard>

      {/* ============================================================
          EVIDENCE
          ============================================================ */}

      {evidence.length > 0 && (
        <SectionCard
          title="Research Evidence"
          action={
            <BarChart3 className="w-3.5 h-3.5 text-text-faint" />
          }
        >
          <div className="space-y-3">
            {evidence
              .slice(0, 8)
              .map((item, index) => (
                <div key={String(item.id ?? index)}>
                  <div className="py-3">
                    <div className="flex items-start gap-3">

                      <div className="w-6 h-6 rounded-md bg-bg-elevated border border-border flex items-center justify-center shrink-0">
                        <span className="text-[10px] font-mono text-text-faint">
                          {index + 1}
                        </span>
                      </div>

                      <div className="flex-1 min-w-0">

                        <div className="text-sm text-text-primary font-medium mb-1">
                          {getEvidenceText(item)}
                        </div>

                        {item.source && (
                          <p className="text-xs text-text-muted">
                            Source: {item.source}
                          </p>
                        )}

                        {isFiniteNumber(
                          item.confidence
                        ) && (
                          <p className="text-[11px] text-text-faint mt-1 font-mono">
                            Confidence:{" "}
                            {Math.round(
                              normalizeConfidence(
                                item.confidence
                              ) * 100
                            )}
                            %
                          </p>
                        )}

                      </div>

                    </div>
                  </div>

                  {index <
                    Math.min(
                      evidence.length,
                      8
                    ) -
                      1 && <Divider />}
                </div>
              ))}
          </div>
        </SectionCard>
      )}

      {/* ============================================================
          LATEST EVENTS
          ============================================================ */}

      <SectionCard
        title="Latest Events"
        action={
          <Calendar className="w-3.5 h-3.5 text-text-faint" />
        }
      >
        <EmptyState
          icon={
            <Calendar className="w-5 h-5" />
          }
          title="No events retrieved yet"
          description="Events will appear here when the research pipeline retrieves news, filings, earnings, or other dated sources."
        />
      </SectionCard>

    </div>
  );
}