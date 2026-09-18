"use client";

import { useEffect, useState } from "react";

import {
FileText,
Download,
ChevronRight,
Loader2,
Trash2,
} from "lucide-react";

import {
RecommendationBadge,
Divider,
} from "../../components/ui";

import reportsApi from "@/lib/api/reportsApi";

import type { SavedReport } from "@/types/report";
import { normalizeRecommendation } from "@/models/company";

interface ReportsPageProps {
onSelectCompany: (id: string) => void;
}

function getResearchId(
report: SavedReport,
): string | null {
const legacyReport =
report as SavedReport & {
research_id?: string | null;
};

const researchId =
report.researchId ??
legacyReport.research_id ??
null;

if (
!researchId ||
researchId === "undefined" ||
researchId === "null"
) {
return null;
}

return String(researchId);
}

export function ReportsPage({
onSelectCompany,
}: ReportsPageProps) {
const [reports, setReports] =
useState<SavedReport[]>([]);

const [loading, setLoading] =
useState(true);

const [error, setError] =
useState<string | null>(null);

const [removingId, setRemovingId] =
useState<string | null>(null);

useEffect(() => {
let cancelled = false;


async function loadReports() {
  try {
    setLoading(true);
    setError(null);

    const result =
      await reportsApi.list();

    if (!cancelled) {
      setReports(
        Array.isArray(result)
          ? result
          : [],
      );
    }
  } catch (err) {
    if (!cancelled) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to load reports.",
      );
    }
  } finally {
    if (!cancelled) {
      setLoading(false);
    }
  }
}

loadReports();

return () => {
  cancelled = true;
};


}, []);

function handleSelect(
report: SavedReport,
) {
setError(null);


const researchId =
  getResearchId(report);

if (!researchId) {
  console.error(
    "Cannot open report: missing research ID.",
    report,
  );

  setError(
    "This report is missing its research ID and cannot be opened.",
  );

  return;
}

console.log(
  "Opening report research workspace:",
  researchId,
);

onSelectCompany(researchId);


}

function handleArrowClick(
event: React.MouseEvent<HTMLButtonElement>,
report: SavedReport,
) {
event.stopPropagation();


handleSelect(report);


}

async function handleRemove(
event: React.MouseEvent<HTMLButtonElement>,
id: string,
) {
event.stopPropagation();


try {
  setRemovingId(id);
  setError(null);

  await reportsApi.remove(id);

  setReports((current) =>
    current.filter(
      (report) =>
        report.id !== id,
    ),
  );
} catch (err) {
  setError(
    err instanceof Error
      ? err.message
      : "Failed to remove report.",
  );
} finally {
  setRemovingId(null);
}


}

function handleDownload(
event: React.MouseEvent<HTMLButtonElement>,
report: SavedReport,
) {
event.stopPropagation();

setError(null);

if (!report.downloadUrl) {
  setError(
    "This report does not have a downloadable file yet.",
  );
  return;
}

const filename = (
  report.companyName ??
  report.title ??
  "research-report"
)
  .replace(
    /[^a-z0-9]+/gi,
    "-",
  )
  .replace(
    /^-+|-+$/g,
    "",
  )
  .toLowerCase();

const link =
  document.createElement(
    "a",
  );

link.href =
  report.downloadUrl;

link.download =
  `${filename || "research-report"}.pdf`;

link.target = "_blank";

link.rel =
  "noopener noreferrer";

document.body.appendChild(
  link,
);

link.click();

document.body.removeChild(
  link,
);


}

return ( <div className="h-full overflow-y-auto"> <div className="max-w-4xl mx-auto px-8 py-8 animate-fade-in">


    {/* Header */}
    <div className="flex items-center gap-2.5 mb-1">
      <FileText className="w-5 h-5 text-text-faint" />

      <h1 className="text-xl font-semibold text-text-primary">
        Reports
      </h1>
    </div>

    <p className="text-sm text-text-muted mb-6">
      Generated equity research reports across your saved research.
    </p>

    {/* Error */}
    {error && (
      <div className="mb-4 rounded-lg border border-danger/30 bg-danger/5 px-4 py-3 text-sm text-danger">
        {error}
      </div>
    )}

    {/* Reports */}
    <div className="bg-bg-surface border border-border rounded-lg overflow-hidden">

      {/* Loading */}
      {loading ? (
        <div className="flex items-center justify-center gap-2 py-16 text-sm text-text-muted">
          <Loader2 className="w-4 h-4 animate-spin" />
          Loading reports...
        </div>
      ) : reports.length === 0 ? (
        <div className="py-16 text-center">
          <FileText className="w-8 h-8 text-text-faint mx-auto mb-3" />

          <div className="text-sm text-text-secondary">
            No saved reports yet.
          </div>

          <div className="text-xs text-text-faint mt-1">
            Save a research workspace to Reports to see it here.
          </div>
        </div>
      ) : (
        reports.map(
          (
            report,
            index,
          ) => {
            const company =
              report.companyName ??
              report.title ??
              "Untitled Report";

            const researchId =
              getResearchId(
                report,
              );

            const canOpen =
              Boolean(
                researchId,
              );

            return (
              <div
                key={report.id}
              >

                {/* Report row */}
                <div
                  role="button"
                  tabIndex={
                    canOpen
                      ? 0
                      : -1
                  }
                  aria-disabled={
                    !canOpen
                  }
                  onClick={() => {
                    if (
                      canOpen
                    ) {
                      handleSelect(
                        report,
                      );
                    }
                  }}
                  onKeyDown={(
                    event,
                  ) => {
                    if (
                      event.key ===
                        "Enter" ||
                      event.key ===
                        " "
                    ) {
                      event.preventDefault();

                      if (
                        canOpen
                      ) {
                        handleSelect(
                          report,
                        );
                      }
                    }
                  }}
                  className={`w-full flex items-center gap-4 px-5 py-4 transition-colors group text-left ${
                    canOpen
                      ? "hover:bg-bg-hover/30 cursor-pointer focus:outline-none focus:ring-2 focus:ring-primary"
                      : "opacity-75"
                  }`}
                >

                  {/* Icon */}
                  <div className="w-10 h-10 rounded-lg bg-bg-elevated border border-border flex items-center justify-center shrink-0">
                    <FileText className="w-4 h-4 text-text-faint" />
                  </div>

                  {/* Report information */}
                  <div className="flex-1 min-w-0">

                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-text-primary truncate">
                        {company}
                      </span>

                      {report.ticker && (
                        <span className="font-mono text-xs text-text-faint">
                          {report.ticker}
                        </span>
                      )}
                    </div>

                    <div className="flex items-center gap-3 mt-0.5">

                      <span className="text-xs text-text-muted">
                        {report.reportType ??
                          report.title}
                      </span>

                      {report.date && (
                        <>
                          <span className="text-xs text-text-faint">
                            ·
                          </span>

                          <span className="text-xs text-text-faint font-mono">
                            {report.date}
                          </span>
                        </>
                      )}

                      {typeof report.confidence ===
                        "number" && (
                        <>
                          <span className="text-xs text-text-faint">
                            ·
                          </span>

                          <span className="text-xs text-text-muted">
                            {report.confidence}% confidence
                          </span>
                        </>
                      )}

                    </div>

                    {/* Missing research ID */}
                    {!canOpen && (
                      <div className="text-[10px] text-danger mt-1">
                        Research workspace unavailable
                      </div>
                    )}

                  </div>

                  {/* Recommendation */}
                  {report.recommendation && (
                    <RecommendationBadge
  value={normalizeRecommendation(report.recommendation)}
/>
                  )}

                  {/* Download */}
                  {report.downloadUrl && (
                    <button
                      type="button"
                      onClick={(
                        event,
                      ) =>
                        handleDownload(
                          event,
                          report,
                        )
                      }
                      className="flex items-center gap-1.5 px-2.5 py-1.5 text-xs text-text-secondary border border-border rounded-md hover:bg-bg-elevated hover:text-text-primary transition-colors shrink-0"
                      aria-label={`Download ${company} report`}
                      title={`Download ${company} report`}
                    >
                      <Download className="w-3.5 h-3.5" />
                      <span>
                        Download
                      </span>
                    </button>
                  )}

                  {/* Remove */}
                  <button
                    type="button"
                    onClick={(
                      event,
                    ) =>
                      handleRemove(
                        event,
                        report.id,
                      )
                    }
                    disabled={
                      removingId ===
                      report.id
                    }
                    className="text-text-faint hover:text-danger transition-colors p-1.5 rounded hover:bg-bg-elevated opacity-0 group-hover:opacity-100 focus:opacity-100 disabled:opacity-50 shrink-0"
                    aria-label={`Remove ${company} report`}
                    title={`Remove ${company} report`}
                  >
                    {removingId ===
                    report.id ? (
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    ) : (
                      <Trash2 className="w-3.5 h-3.5" />
                    )}
                  </button>

                  {/* Explicit Arrow Button */}
                  <button
                    type="button"
                    disabled={
                      !canOpen
                    }
                    onClick={(
                      event,
                    ) =>
                      handleArrowClick(
                        event,
                        report,
                      )
                    }
                    className={`p-1.5 rounded-md shrink-0 transition-colors focus:outline-none focus:ring-2 focus:ring-primary ${
                      canOpen
                        ? "text-text-faint hover:text-text-primary hover:bg-bg-elevated cursor-pointer"
                        : "text-text-faint/40 cursor-not-allowed"
                    }`}
                    aria-label={
                      canOpen
                        ? `Open ${company} research workspace`
                        : `Research workspace unavailable for ${company}`
                    }
                    title={
                      canOpen
                        ? "Open research workspace"
                        : "Research workspace unavailable"
                    }
                  >
                    <ChevronRight className="w-4 h-4" />
                  </button>

                </div>

                {/* Divider */}
                {index <
                  reports.length -
                    1 && (
                  <Divider />
                )}

              </div>
            );
          },
        )
      )}

    </div>
  </div>
</div>


);
}
