"use client";

import {
  useState,
  type ReactNode,
} from "react";

import {
  Building2,
  BarChart3,
  TrendingUp,
  FileText,
  CheckCircle2,
  Loader,
  Clock,
  Save,
  ChevronDown,
  AlertCircle,
  Globe,
  MapPin,
  UserRound,
  Users,
  CalendarDays,
  DollarSign,
  Percent,
  Activity,
  Library,
  FolderOpen,
} from "lucide-react";

import {
  cn,
  Skeleton,
  EmptyState,
} from "../../components/ui";

import { ResearchProgress } from "./ResearchProgress";
import { EvidencePanel } from "./EvidencePanel";
import { DocumentPanel } from "./DocumentPanel";
import { InsightPanel } from "./InsightPanel";
import { ReportViewer } from "./ReportViewer";

import savedArtifactsApi from "@/lib/api/savedArtifactsApi";

import type {
  ResearchResult,
  ResearchStageInfo,
  OverviewData,
} from "@/types/research";

// ============================================================
// Props
// ============================================================

interface ResearchWorkspaceProps {
  /**
   * Canonical research identifier.
   *
   * The backend currently returns research IDs as UUID strings,
   * for example:
   *
   * 8f9de065-ea11-453d-b703-22c9e4758ac4
   *
   * Numeric IDs are also accepted for compatibility with older
   * research records.
   */
  researchId: string | number;

  data: ResearchResult | null;
  loading: boolean;
  progress: number;
  status: string;
  currentStage: string;
  stages: ResearchStageInfo[];
  companyName: string;
  createdAt: string;
}

// ============================================================
// Tabs
// ============================================================

type WorkspaceTab =
  | "overview"
  | "progress"
  | "evidence"
  | "documents"
  | "insights"
  | "report";

// ============================================================
// Save destinations
// ============================================================

type WorkspaceSaveDestination =
  | "research"
  | "library"
  | "reports";

// ============================================================
// Safe helpers
// ============================================================

function safeString(value: unknown): string {
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

// ============================================================
// Research ID resolver
// ============================================================

/**
 * Resolve the canonical research ID without assuming that
 * research IDs are numeric.
 *
 * The backend currently returns UUID research IDs.
 *
 * Resolution order:
 *
 * 1. researchId prop
 * 2. data.id
 * 3. data.research_id
 * 4. data.researchId
 * 5. data.research.id
 * 6. data.research.research_id
 * 7. data.research.researchId
 */
function getResearchId(
  researchId: unknown,
  data: ResearchResult | null,
): string | null {
  const record =
    data as
      | (ResearchResult & {
          id?: unknown;
          research_id?: unknown;
          researchId?: unknown;
          research?: {
            id?: unknown;
            research_id?: unknown;
            researchId?: unknown;
          } | null;
        })
      | null;

  const candidates: unknown[] = [
    researchId,

    record?.id,
    record?.research_id,
    record?.researchId,

    record?.research?.id,
    record?.research?.research_id,
    record?.research?.researchId,
  ];

  for (const candidate of candidates) {
    const normalized = safeString(candidate);

    if (normalized) {
      return normalized;
    }
  }

  return null;
}

// ============================================================
// Status helpers
// ============================================================

function normalizeStatus(
  value: unknown,
): string {
  return safeString(value).toLowerCase();
}

function getStatusLabel(
  status: string,
): string {
  switch (normalizeStatus(status)) {
    case "completed":
    case "complete":
    case "success":
    case "succeeded":
      return "Completed";

    case "running":
    case "in_progress":
    case "in-progress":
      return "Running";

    case "failed":
    case "error":
      return "Failed";

    case "pending":
    case "queued":
      return "Pending";

    default:
      return status || "Unknown";
  }
}

function formatCreatedAt(
  value: unknown,
): string {
  const raw = safeString(value);

  if (!raw) {
    return "";
  }

  const date = new Date(raw);

  if (Number.isNaN(date.getTime())) {
    return raw;
  }

  return date.toLocaleString(
    undefined,
    {
      dateStyle: "medium",
      timeStyle: "short",
    },
  );
}

function getStatusIcon(
  status: string,
): ReactNode {
  switch (normalizeStatus(status)) {
    case "completed":
    case "complete":
    case "success":
    case "succeeded":
      return (
        <CheckCircle2 className="w-3.5 h-3.5 text-success" />
      );

    case "running":
    case "in_progress":
    case "in-progress":
      return (
        <Loader className="w-3.5 h-3.5 text-warning animate-spin" />
      );

    case "failed":
    case "error":
      return (
        <AlertCircle className="w-3.5 h-3.5 text-danger" />
      );

    default:
      return (
        <Clock className="w-3.5 h-3.5 text-text-faint" />
      );
  }
}

// ============================================================
// Save helpers
// ============================================================

function getSaveDestinationLabel(
  destination: WorkspaceSaveDestination,
): string {
  switch (destination) {
    case "research":
      return "Research";

    case "library":
      return "Library";

    case "reports":
      return "Reports";

    default:
      return "Research";
  }
}

function getSaveDestinationIcon(
  destination: WorkspaceSaveDestination,
): ReactNode {
  switch (destination) {
    case "research":
      return (
        <FolderOpen className="w-3.5 h-3.5" />
      );

    case "library":
      return (
        <Library className="w-3.5 h-3.5" />
      );

    case "reports":
      return (
        <FileText className="w-3.5 h-3.5" />
      );

    default:
      return (
        <Save className="w-3.5 h-3.5" />
      );
  }
}

// ============================================================
// Overview helpers
// ============================================================

function hasOverviewSection(
  section:
    | OverviewData["profile"]
    | OverviewData["market"]
    | OverviewData["financials"]
    | null
    | undefined,
): boolean {
  if (!section) {
    return false;
  }

  return Object.values(section).some(
    (value) =>
      safeString(value).length > 0,
  );
}

interface OverviewFieldProps {
  label: string;
  value: unknown;
  icon?: ReactNode;
  mono?: boolean;
}

function OverviewField({
  label,
  value,
  icon,
  mono = false,
}: OverviewFieldProps) {
  const displayValue =
    safeString(value);

  if (!displayValue) {
    return null;
  }

  return (
    <div className="min-w-0">
      <div className="flex items-center gap-1.5 mb-1">
        {icon && (
          <span className="text-text-faint">
            {icon}
          </span>
        )}

        <span className="text-[10px] text-text-faint uppercase tracking-wider font-mono">
          {label}
        </span>
      </div>

      <div
        className={cn(
          "text-sm text-text-primary break-words",
          mono &&
            "font-mono tabular-nums",
        )}
      >
        {displayValue}
      </div>
    </div>
  );
}

// ============================================================
// Overview section
// ============================================================

function OverviewContent({
  overview,
  summary,
  companyName,
  statusLabel,
  normalizedStatus,
}: {
  overview: OverviewData | null;
  summary: string;
  companyName: string;
  status: string;
  statusLabel: string;
  normalizedStatus: string;
}) {
  const profile =
    overview?.profile ?? null;

  const market =
    overview?.market ?? null;

  const financials =
    overview?.financials ?? null;

  const hasProfile =
    hasOverviewSection(profile);

  const hasMarket =
    hasOverviewSection(market);

  const hasFinancials =
    hasOverviewSection(financials);

  const hasAnyOverview =
    hasProfile ||
    hasMarket ||
    hasFinancials;

  if (!overview && !summary) {
    return (
      <EmptyState
        icon={
          <BarChart3 className="w-5 h-5" />
        }
        title="No overview data available yet"
        description="Overview information will appear as the research agents complete their analysis."
      />
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-6 sm:px-8 py-6 animate-fade-in">
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-1.5">
          <BarChart3 className="w-4 h-4 text-text-faint" />

          <h2 className="text-sm font-medium text-text-primary">
            Research Overview
          </h2>
        </div>

        <p className="text-xs text-text-muted leading-5">
          Structured company, market, and financial
          analysis returned by the research backend.
        </p>
      </div>

      {summary && (
        <section className="mb-5 rounded-lg border border-border bg-bg-surface">
          <div className="px-5 py-4 border-b border-border">
            <div className="flex items-center gap-2">
              <FileText className="w-4 h-4 text-text-faint" />

              <h3 className="text-sm font-medium text-text-primary">
                Executive Summary
              </h3>
            </div>
          </div>

          <div className="px-5 py-5">
            <p className="text-sm leading-6 text-text-secondary whitespace-pre-wrap break-words">
              {summary}
            </p>
          </div>
        </section>
      )}

      {hasProfile &&
        profile && (
          <section className="mb-5 rounded-lg border border-border bg-bg-surface overflow-hidden">
            <div className="px-5 py-4 border-b border-border">
              <div className="flex items-center gap-2">
                <Building2 className="w-4 h-4 text-text-faint" />

                <h3 className="text-sm font-medium text-text-primary">
                  Company Profile
                </h3>
              </div>
            </div>

            <div className="p-5">
              {profile.description && (
                <div className="mb-6">
                  <div className="text-[10px] text-text-faint uppercase tracking-wider font-mono mb-2">
                    Description
                  </div>

                  <p className="text-sm text-text-secondary leading-6 whitespace-pre-wrap break-words">
                    {safeString(
                      profile.description,
                    )}
                  </p>
                </div>
              )}

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-x-6 gap-y-5">
                <OverviewField
                  label="Sector"
                  value={profile.sector}
                />

                <OverviewField
                  label="Industry"
                  value={profile.industry}
                />

                <OverviewField
                  label="Headquarters"
                  value={profile.headquarters}
                  icon={
                    <MapPin className="w-3 h-3" />
                  }
                />

                <OverviewField
                  label="CEO"
                  value={profile.ceo}
                  icon={
                    <UserRound className="w-3 h-3" />
                  }
                />

                <OverviewField
                  label="Employees"
                  value={profile.employees}
                  icon={
                    <Users className="w-3 h-3" />
                  }
                />

                <OverviewField
                  label="Founded"
                  value={profile.founded}
                  icon={
                    <CalendarDays className="w-3 h-3" />
                  }
                />

                <OverviewField
                  label="Website"
                  value={profile.website}
                  icon={
                    <Globe className="w-3 h-3" />
                  }
                />
              </div>
            </div>
          </section>
        )}

      {hasMarket &&
        market && (
          <section className="mb-5 rounded-lg border border-border bg-bg-surface overflow-hidden">
            <div className="px-5 py-4 border-b border-border">
              <div className="flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-text-faint" />

                <h3 className="text-sm font-medium text-text-primary">
                  Market Data
                </h3>
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 divide-x-0 md:divide-x md:divide-border">
              {[
                {
                  label: "Market Cap",
                  value:
                    market.marketCap,
                  icon: (
                    <DollarSign className="w-3 h-3" />
                  ),
                },
                {
                  label: "Share Price",
                  value:
                    market.sharePrice,
                  icon: (
                    <Activity className="w-3 h-3" />
                  ),
                },
                {
                  label: "P/E Ratio",
                  value:
                    market.peRatio,
                  icon: (
                    <BarChart3 className="w-3 h-3" />
                  ),
                },
                {
                  label: "52W Range",
                  value:
                    market.weekRange52,
                  icon: (
                    <TrendingUp className="w-3 h-3" />
                  ),
                },
                {
                  label:
                    "Dividend Yield",
                  value:
                    market.dividendYield,
                  icon: (
                    <Percent className="w-3 h-3" />
                  ),
                },
                {
                  label: "Beta",
                  value:
                    market.beta,
                  icon: (
                    <Activity className="w-3 h-3" />
                  ),
                },
              ].map((item) => {
                const value =
                  safeString(
                    item.value,
                  );

                if (!value) {
                  return null;
                }

                return (
                  <div
                    key={item.label}
                    className="px-5 py-4 border-b md:border-b-0 border-border last:border-b-0"
                  >
                    <div className="flex items-center gap-1.5 mb-2">
                      <span className="text-text-faint">
                        {item.icon}
                      </span>

                      <span className="text-[10px] text-text-faint uppercase tracking-wider font-mono">
                        {item.label}
                      </span>
                    </div>

                    <div className="font-mono text-base text-text-primary tabular-nums break-words">
                      {value}
                    </div>
                  </div>
                );
              })}
            </div>
          </section>
        )}

      {hasFinancials &&
        financials && (
          <section className="mb-5 rounded-lg border border-border bg-bg-surface overflow-hidden">
            <div className="px-5 py-4 border-b border-border">
              <div className="flex items-center gap-2">
                <DollarSign className="w-4 h-4 text-text-faint" />

                <h3 className="text-sm font-medium text-text-primary">
                  Financials
                </h3>
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 divide-x-0 md:divide-x md:divide-border">
              {[
                {
                  label: "Revenue",
                  value:
                    financials.revenue,
                },
                {
                  label:
                    "Revenue Growth",
                  value:
                    financials.revenueGrowth,
                },
                {
                  label:
                    "Gross Margin",
                  value:
                    financials.grossMargin,
                },
                {
                  label:
                    "Operating Margin",
                  value:
                    financials.operatingMargin,
                },
                {
                  label: "EPS",
                  value:
                    financials.eps,
                },
              ].map((item) => {
                const value =
                  safeString(
                    item.value,
                  );

                if (!value) {
                  return null;
                }

                return (
                  <div
                    key={item.label}
                    className="px-5 py-4 border-b md:border-b-0 border-border"
                  >
                    <div className="text-[10px] text-text-faint uppercase tracking-wider font-mono mb-2">
                      {item.label}
                    </div>

                    <div className="font-mono text-base text-text-primary tabular-nums break-words">
                      {value}
                    </div>
                  </div>
                );
              })}
            </div>
          </section>
        )}

      <section className="rounded-lg border border-border bg-bg-surface p-5">
        <div className="text-[10px] text-text-faint uppercase tracking-wider font-mono mb-2">
          Research Status
        </div>

        <div className="flex items-center gap-2">
          {getStatusIcon(
            normalizedStatus,
          )}

          <span className="text-sm text-text-primary">
            {statusLabel}
          </span>
        </div>

        {companyName && (
          <div className="mt-3 text-xs text-text-faint">
            {companyName}
          </div>
        )}

        {!hasAnyOverview &&
          summary && (
            <div className="mt-4 pt-4 border-t border-border">
              <p className="text-xs text-text-muted">
                Structured company and market fields
                were not returned by the backend, but
                an executive summary is available.
              </p>
            </div>
          )}
      </section>
    </div>
  );
}

// ============================================================
// Research Workspace
// ============================================================

export function ResearchWorkspace({
  researchId,
  data,
  loading,
  progress,
  status,
  currentStage,
  stages,
  companyName,
  createdAt,
}: ResearchWorkspaceProps) {
  const [activeTab, setActiveTab] =
    useState<WorkspaceTab>(
      "overview",
    );

  const [saveOpen, setSaveOpen] =
    useState(false);

  const [saving, setSaving] =
    useState(false);

  const [saveMessage, setSaveMessage] =
    useState("");

  const [
    savingDestination,
    setSavingDestination,
  ] =
    useState<WorkspaceSaveDestination | null>(
      null,
    );

  // ==========================================================
  // Normalize values
  // ==========================================================

  const resolvedResearchId =
    getResearchId(
      researchId,
      data,
    );

  const safeCompanyName =
    safeString(companyName) ||
    safeString(data?.title) ||
    "Equity Research";

  const effectiveStatus =
    safeString(data?.status) ||
    safeString(status);

  const normalizedStatus =
    normalizeStatus(
      effectiveStatus,
    );

  const statusLabel =
    getStatusLabel(
      effectiveStatus,
    );

  const safeProgress =
    Number.isFinite(progress)
      ? Math.min(
          100,
          Math.max(
            0,
            progress,
          ),
        )
      : 0;

  // ==========================================================
  // Debug research ID
  // ==========================================================

  console.log(
    "[ResearchWorkspace] Research ID resolution",
    {
      researchId,
      researchIdType:
        typeof researchId,
      resolvedResearchId,

      dataId:
        (
          data as
            | (ResearchResult & {
                id?: unknown;
              })
            | null
        )?.id,

      dataResearchId:
        (
          data as
            | (ResearchResult & {
                research_id?: unknown;
              })
            | null
        )?.research_id,

      dataResearchIdCamel:
        (
          data as
            | (ResearchResult & {
                researchId?: unknown;
              })
            | null
        )?.researchId,
    },
  );

  // ==========================================================
  // Canonical collections
  // ==========================================================

  const evidence =
    Array.isArray(data?.evidence)
      ? data.evidence
      : [];

  const documents =
    Array.isArray(data?.documents)
      ? data.documents
      : [];

  const insights =
    Array.isArray(data?.insights)
      ? data.insights
      : [];

  const safeStages =
    Array.isArray(stages)
      ? stages
      : [];

  // ==========================================================
  // Overview
  // ==========================================================

  const summary =
    safeString(
      data?.summary,
    );

  const overview =
    data?.overview ?? null;

  // ==========================================================
  // Report
  // ==========================================================

  const reportTitle =
    safeString(
      data?.report?.title,
    ) ||
    safeString(
      data?.title,
    ) ||
    `${safeCompanyName} Equity Research`;

  const reportSections =
    Array.isArray(
      data?.report?.sections,
    )
      ? data.report.sections
      : [];

  // ==========================================================
  // Counts
  // ==========================================================

  const evidenceCount =
    evidence.length;

  const documentCount =
    documents.length;

  const insightCount =
    insights.length;

  const reportSectionCount =
    reportSections.length;

  // ==========================================================
  // Save
  // ==========================================================

  async function handleSave(
    destination: WorkspaceSaveDestination,
  ) {
    if (saving) {
      return;
    }

    /**
     * Resolve the ID again at save time.
     *
     * IMPORTANT:
     * Do NOT convert this value to Number().
     *
     * Research IDs may be UUIDs.
     */
    const saveResearchId =
      getResearchId(
        researchId,
        data,
      );

    if (!saveResearchId) {
      console.error(
        "[ResearchWorkspace] Cannot save: invalid research ID",
        {
          researchId,
          researchIdType:
            typeof researchId,
          data,
        },
      );

      setSaveMessage(
        "Unable to save research because a valid research ID was not found.",
      );

      return;
    }

    try {
      setSaving(true);

      setSavingDestination(
        destination,
      );

      setSaveMessage("");

      console.log(
        "[ResearchWorkspace] Saving research",
        {
          researchId:
            saveResearchId,
          destination,
          title:
            reportTitle,
        },
      );

      const response =
        await savedArtifactsApi.saveResearch(
          {
            researchId:
              saveResearchId,

            destination,

            title:
              reportTitle,

            description:
              summary ||
              `Equity research report for ${safeCompanyName}.`,
          },
        );

      console.log(
        "[ResearchWorkspace] Save successful",
        response,
      );

      setSaveMessage(
        `Saved to ${getSaveDestinationLabel(
          destination,
        )}`,
      );

      setSaveOpen(false);
    } catch (error) {
      console.error(
        "[ResearchWorkspace] Failed to save research:",
        error,
      );

      if (error instanceof Error) {
        setSaveMessage(
          error.message ||
            "Unable to save research.",
        );
      } else {
        setSaveMessage(
          "Unable to save research.",
        );
      }
    } finally {
      setSaving(false);

      setSavingDestination(
        null,
      );
    }
  }

  // ==========================================================
  // Loading
  // ==========================================================

  if (
    loading &&
    !data
  ) {
    return (
      <div className="w-full h-[calc(100vh-7rem)] overflow-y-auto overflow-x-hidden">
        <div className="border-b border-border bg-bg-surface">
          <div className="max-w-7xl mx-auto px-6 py-5">
            <div className="flex items-start justify-between gap-6">
              <div className="flex items-start gap-3 min-w-0">
                <div className="w-10 h-10 rounded-lg bg-bg-elevated border border-border flex items-center justify-center shrink-0">
                  <Skeleton className="w-5 h-5 rounded" />
                </div>

                <div className="min-w-0">
                  <Skeleton className="h-5 w-72 mb-2" />
                  <Skeleton className="h-3 w-56" />
                </div>
              </div>

              <Skeleton className="h-8 w-24" />
            </div>
          </div>
        </div>

        <div className="border-b border-border bg-bg-surface">
          <div className="max-w-7xl mx-auto px-6">
            <div className="flex gap-6 py-3">
              {Array.from(
                {
                  length: 6,
                },
              ).map(
                (_, index) => (
                  <Skeleton
                    key={index}
                    className="h-4 w-20"
                  />
                ),
              )}
            </div>
          </div>
        </div>

        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {Array.from(
              {
                length: 6,
              },
            ).map(
              (_, index) => (
                <div
                  key={index}
                  className="border border-border rounded-lg p-5"
                >
                  <Skeleton className="h-4 w-32 mb-4" />
                  <Skeleton className="h-8 w-44 mb-2" />
                  <Skeleton className="h-3 w-24" />
                </div>
              ),
            )}
          </div>
        </div>
      </div>
    );
  }

  // ==========================================================
  // Main workspace
  // ==========================================================

  return (
    <div className="w-full h-[calc(100vh-7rem)] overflow-y-auto overflow-x-hidden scroll-smooth">
      {/* Header */}

      <div className="border-b border-border bg-bg-surface">
        <div className="max-w-7xl mx-auto px-6 py-5">
          <div className="flex items-start justify-between gap-6">
            <div className="flex items-start gap-3 min-w-0">
              <div className="w-10 h-10 rounded-lg bg-bg-elevated border border-border flex items-center justify-center shrink-0">
                <Building2 className="w-5 h-5 text-text-muted" />
              </div>

              <div className="min-w-0">
                <h1 className="text-lg font-medium text-text-primary truncate">
                  {safeCompanyName}
                </h1>

                <div className="flex items-center gap-3 mt-1 flex-wrap">
                  <div className="flex items-center gap-1.5">
                    {getStatusIcon(
                      normalizedStatus,
                    )}

                    <span className="text-xs text-text-muted">
                      {statusLabel}
                    </span>
                  </div>

                  <span className="text-text-faint">
                    Â·
                  </span>

                  <span className="text-xs text-text-muted">
                    Progress:{" "}
                    {Math.round(
                      safeProgress,
                    )}
                    %
                  </span>

                  {createdAt && (
                    <>
                      <span className="text-text-faint">
                        Â·
                      </span>

                      <span className="text-xs text-text-faint">
                        Created:{" "}
                        {formatCreatedAt(
                          createdAt,
                        )}
                      </span>
                    </>
                  )}

                  {currentStage && (
                    <>
                      <span className="text-text-faint">
                        Â·
                      </span>

                      <span className="text-xs text-text-faint">
                        {currentStage}
                      </span>
                    </>
                  )}
                </div>
              </div>
            </div>

            {/* Save menu */}

            <div className="relative shrink-0">
              <button
                type="button"
                onClick={() =>
                  setSaveOpen(
                    (value) =>
                      !value,
                  )
                }
                disabled={saving}
                className={cn(
                  "inline-flex items-center gap-2 px-3 py-2 rounded-md border text-xs transition-colors",
                  "border-border bg-bg-surface text-text-muted",
                  "hover:border-border-hover hover:text-text-primary",
                  "disabled:opacity-50 disabled:cursor-not-allowed",
                )}
              >
                <Save className="w-3.5 h-3.5" />

                {saving
                  ? savingDestination
                    ? `Saving to ${getSaveDestinationLabel(
                        savingDestination,
                      )}...`
                    : "Saving..."
                  : "Save"}

                <ChevronDown
                  className={cn(
                    "w-3.5 h-3.5 transition-transform",
                    saveOpen &&
                      "rotate-180",
                  )}
                />
              </button>

              {saveOpen && (
                <div className="absolute right-0 top-full mt-2 w-60 rounded-lg border border-border bg-bg-surface shadow-xl z-30 overflow-hidden">
                  <div className="px-3 py-3 border-b border-border">
                    <p className="text-xs font-medium text-text-primary">
                      Save research
                    </p>

                    <p className="mt-0.5 text-[10px] text-text-faint">
                      Choose where to store this research.
                    </p>
                  </div>

                  {(
                    [
                      {
                        destination:
                          "research" as const,
                        title:
                          "Save to Research",
                        description:
                          "Keep it with your research workspace.",
                      },
                      {
                        destination:
                          "library" as const,
                        title:
                          "Save to Library",
                        description:
                          "Add it to your saved research library.",
                      },
                      {
                        destination:
                          "reports" as const,
                        title:
                          "Save to Reports",
                        description:
                          "Store the completed report artifact.",
                      },
                    ]
                  ).map(
                    ({
                      destination,
                      title,
                      description,
                    }) => (
                      <button
                        key={destination}
                        type="button"
                        disabled={saving}
                        onClick={() =>
                          handleSave(
                            destination,
                          )
                        }
                        className={cn(
                          "w-full px-3 py-3 text-left transition-colors",
                          "hover:bg-bg-elevated",
                          "disabled:opacity-50 disabled:cursor-not-allowed",
                        )}
                      >
                        <div className="flex items-center gap-3">
                          <span className="w-7 h-7 rounded-md border border-border bg-bg-elevated flex items-center justify-center text-text-muted">
                            {getSaveDestinationIcon(
                              destination,
                            )}
                          </span>

                          <span className="min-w-0">
                            <span className="block text-xs font-medium text-text-primary">
                              {title}
                            </span>

                            <span className="block mt-0.5 text-[10px] text-text-faint">
                              {description}
                            </span>
                          </span>
                        </div>
                      </button>
                    ),
                  )}
                </div>
              )}
            </div>
          </div>

          {saveMessage && (
            <div
              className={cn(
                "mt-3 text-xs",
                saveMessage.startsWith(
                  "Saved to",
                )
                  ? "text-success"
                  : "text-danger",
              )}
            >
              {saveMessage}
            </div>
          )}
        </div>
      </div>

      {/* Navigation tabs */}

      <div className="sticky top-0 z-20 border-b border-border bg-bg-surface/95 backdrop-blur">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex items-center gap-1 overflow-x-auto scrollbar-none">
            {[
              {
                id: "overview" as const,
                label: "Overview",
                icon: BarChart3,
              },
              {
                id: "progress" as const,
                label: "Progress",
                icon: TrendingUp,
              },
              {
                id: "evidence" as const,
                label: "Evidence",
                icon: CheckCircle2,
                count:
                  evidenceCount,
              },
              {
                id: "documents" as const,
                label: "Documents",
                icon: FileText,
                count:
                  documentCount,
              },
              {
                id: "insights" as const,
                label: "Insights",
                icon: TrendingUp,
                count:
                  insightCount,
              },
              {
                id: "report" as const,
                label: "Report",
                icon: FileText,
                count:
                  reportSectionCount,
              },
            ].map(
              ({
                id,
                label,
                icon: Icon,
                count,
              }) => {
                const active =
                  activeTab === id;

                return (
                  <button
                    key={id}
                    type="button"
                    onClick={() =>
                      setActiveTab(id)
                    }
                    className={cn(
                      "relative flex items-center gap-2 px-3 py-3 text-xs whitespace-nowrap transition-colors shrink-0",
                      active
                        ? "text-text-primary"
                        : "text-text-muted hover:text-text-primary",
                    )}
                  >
                    <Icon className="w-3.5 h-3.5" />

                    <span>
                      {label}
                    </span>

                    {typeof count ===
                      "number" && (
                      <span
                        className={cn(
                          "font-mono text-[10px]",
                          active
                            ? "text-text-muted"
                            : "text-text-faint",
                        )}
                      >
                        {count}
                      </span>
                    )}

                    {active && (
                      <span className="absolute left-2 right-2 bottom-0 h-px bg-text-primary" />
                    )}
                  </button>
                );
              },
            )}
          </div>
        </div>
      </div>

      {/* Content */}

      <main className="min-h-[500px] overflow-x-hidden">
        {activeTab ===
          "overview" && (
          <OverviewContent
            overview={
              overview
            }
            summary={
              summary
            }
            companyName={
              safeCompanyName
            }
            status={
              effectiveStatus
            }
            statusLabel={
              statusLabel
            }
            normalizedStatus={
              normalizedStatus
            }
          />
        )}

        {activeTab ===
          "progress" && (
          <div className="p-6">
            <ResearchProgress
              progress={
                safeProgress
              }
              status={
                effectiveStatus
              }
              currentStage={
                currentStage
              }
              stages={
                safeStages
              }
            />
          </div>
        )}

        {activeTab ===
          "evidence" && (
          <div className="p-6">
            <EvidencePanel
              evidence={
                evidence
              }
            />
          </div>
        )}

        {activeTab ===
          "documents" && (
          <div className="p-6">
            <DocumentPanel
              documents={
                documents
              }
            />
          </div>
        )}

        {activeTab ===
          "insights" && (
          <div className="p-6">
            <InsightPanel
              insights={
                insights
              }
            />
          </div>
        )}

        {activeTab ===
          "report" && (
          <div className="p-6">
            <ReportViewer
              title={
                reportTitle
              }
              sections={
                reportSections
              }
            />
          </div>
        )}
      </main>
    </div>
  );
}

export default ResearchWorkspace;

