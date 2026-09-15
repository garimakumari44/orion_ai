"use client";

import { useCallback, useEffect, useState } from "react";

import {
AlertCircle,
ArrowLeft,
ArrowRight,
Building2,
CheckCircle2,
Clock3,
FileText,
Loader2,
RefreshCw,
Sparkles,
} from "lucide-react";

import {
getResearch,
getResearchStatus,
} from "@/lib/api/researchApi";

import type { ResearchResult } from "@/types/research";

interface NewResearchResultProps {
researchId: string | number;
onOpenResearch: () => void;
onBack: () => void;
}

type ResearchStatus =
| "queued"
| "pending"
| "running"
| "processing"
| "completed"
| "failed"
| "unknown";

function isObject(value: unknown): value is Record<string, unknown> {
return typeof value === "object" && value !== null;
}

function safeString(
value: unknown,
fallback = ""
): string {
if (typeof value === "string") {
return value.trim();
}

if (
typeof value === "number" ||
typeof value === "boolean"
) {
return String(value);
}

return fallback;
}

function safeNumber(
value: unknown,
fallback = 0
): number {
if (
typeof value === "number" &&
Number.isFinite(value)
) {
return value;
}

if (typeof value === "string") {
const parsed = Number(value);


if (Number.isFinite(parsed)) {
  return parsed;
}


}

return fallback;
}

function normalizeStatus(
value: unknown
): ResearchStatus {
const status = safeString(value).toLowerCase();

if (!status) {
return "unknown";
}

if (
status === "complete" ||
status === "completed" ||
status === "done" ||
status === "success" ||
status === "succeeded"
) {
return "completed";
}

if (
status === "failed" ||
status === "failure" ||
status === "error"
) {
return "failed";
}

if (
status === "running" ||
status === "processing" ||
status === "in_progress" ||
status === "in-progress"
) {
return "running";
}

if (
status === "queued" ||
status === "pending" ||
status === "created"
) {
return "queued";
}

return "unknown";
}

function unwrapResearchResponse(
response: unknown
): Record<string, unknown> {
if (!isObject(response)) {
return {};
}

if (isObject(response.data)) {
return response.data;
}

if (isObject(response.result)) {
return response.result;
}

if (isObject(response.research)) {
return response.research;
}

return response;
}

function extractStatus(
response: unknown
): ResearchStatus {
const root = unwrapResearchResponse(response);

return normalizeStatus(
root.status ??
root.state ??
root.research_status ??
root.researchStatus
);
}

function extractProgress(
response: unknown
): number {
const root = unwrapResearchResponse(response);

const progress = safeNumber(
root.progress ??
root.progress_percent ??
root.progressPercentage ??
root.completion ??
0
);

return Math.max(
0,
Math.min(100, progress)
);
}

function extractCompanyName(
response: unknown
): string {
const root = unwrapResearchResponse(response);

const directName =
safeString(root.company_name) ||
safeString(root.companyName);

if (directName) {
return directName;
}

if (isObject(root.company)) {
return (
safeString(root.company.name) ||
safeString(root.company.company_name) ||
safeString(root.company.companyName) ||
"Research"
);
}

if (isObject(root.company_data)) {
return (
safeString(root.company_data.name) ||
safeString(root.company_data.company_name) ||
"Research"
);
}

return "Research";
}

function extractTitle(
response: unknown
): string {
const root = unwrapResearchResponse(response);

return (
safeString(root.title) ||
safeString(root.name) ||
safeString(root.research_title) ||
safeString(root.researchTitle) ||
"New Research"
);
}

function extractSummary(
response: unknown
): string {
const root = unwrapResearchResponse(response);

return (
safeString(root.summary) ||
safeString(root.description) ||
safeString(root.objective) ||
"Your research has been created successfully."
);
}

function isFinished(
status: ResearchStatus
): boolean {
return status === "completed";
}

function isFailed(
status: ResearchStatus
): boolean {
return status === "failed";
}

function isActive(
status: ResearchStatus
): boolean {
return (
status === "queued" ||
status === "pending" ||
status === "running" ||
status === "processing" ||
status === "unknown"
);
}

export function NewResearchResult({
researchId,
onOpenResearch,
onBack,
}: NewResearchResultProps) {
const [data, setData] =
useState<ResearchResult | null>(null);

const [rawData, setRawData] =
useState<unknown>(null);

const [status, setStatus] =
useState<ResearchStatus>("queued");

const [progress, setProgress] =
useState(0);

const [loading, setLoading] =
useState(true);

const [refreshing, setRefreshing] =
useState(false);

const [error, setError] =
useState<string | null>(null);

const loadResearch = useCallback(
async (manual = false) => {
const id = String(researchId).trim();


  if (!id) {
    setError("Invalid research ID.");
    setLoading(false);
    return;
  }

  if (manual) {
    setRefreshing(true);
  } else {
    setLoading(true);
  }

  setError(null);

  try {
    /*
     * Load the actual research.
     *
     * IMPORTANT:
     * id must be the research ID returned by
     * the create/start research API.
     */
    const response =
      await getResearch(id);

    setRawData(response);

    const nextStatus =
      extractStatus(response);

    const nextProgress =
      extractProgress(response);

    setStatus(nextStatus);
    setProgress(nextProgress);

    if (isObject(response)) {
      const normalized =
        unwrapResearchResponse(
          response
        ) as ResearchResult;

      setData(normalized);
    }

    /*
     * Load the execution status separately.
     *
     * The research record can exist while the
     * background research pipeline is still running.
     */
    try {
      const statusResponse =
        await getResearchStatus(id);

      const statusValue =
        extractStatus(statusResponse);

      const statusProgress =
        extractProgress(statusResponse);

      if (
        statusValue !== "unknown"
      ) {
        setStatus(statusValue);
      }

      if (
        statusProgress > 0 ||
        statusValue === "completed"
      ) {
        setProgress(statusProgress);
      }
    } catch (statusError) {
      /*
       * Status failure should not remove the
       * research data already loaded.
       */
      console.warn(
        "Unable to load research status:",
        statusError
      );
    }
  } catch (err) {
    console.error(
      "Failed to load research:",
      err
    );

    setError(
      err instanceof Error
        ? err.message
        : "Unable to load the research."
    );
  } finally {
    setLoading(false);
    setRefreshing(false);
  }
},
[researchId]


);

/*

* Initial load.
  */
  useEffect(() => {
  loadResearch();
  }, [loadResearch]);

/*

* Poll while the research is active.
  */
  useEffect(() => {
  if (!isActive(status)) {
  return;
  }


const timer =



  window.setInterval(() => {
    void loadResearch();
  }, 2500);

return () => {
  window.clearInterval(timer);
};


}, [status, loadResearch]);

const companyName =
extractCompanyName(rawData);

const title =
extractTitle(rawData);

const summary =
extractSummary(rawData);

const finished =
isFinished(status);

const failed =
isFailed(status);

const statusLabel = finished
? "Research completed"
: failed
? "Research failed"
: status === "running" ||
status === "processing"
? "Research in progress"
: "Research queued";

return ( <div className="min-h-full bg-[#050505] text-white">
{/* =====================================================
HEADER
===================================================== */}

```
  <header className="border-b border-white/[0.08] bg-[#080808]">
    <div className="mx-auto max-w-6xl px-6 py-5">
      <div className="flex items-center justify-between gap-4">
        <button
          type="button"
          onClick={onBack}
          className="inline-flex items-center gap-2 text-sm text-zinc-400 transition-colors hover:text-white"
        >
          <ArrowLeft className="h-4 w-4" />
          Back
        </button>

        <div className="text-xs text-zinc-500">
          Research ID{" "}
          <span className="font-mono text-zinc-300">
            {String(researchId)}
          </span>
        </div>
      </div>
    </div>
  </header>

  {/* =====================================================
      MAIN
      ===================================================== */}

  <main className="mx-auto max-w-6xl px-6 py-10">
    {/* ===================================================
        INITIAL LOADING
        =================================================== */}

    {loading && !data ? (
      <div className="flex min-h-[500px] items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-7 w-7 animate-spin text-blue-400" />

          <p className="text-sm text-zinc-400">
            Loading research...
          </p>
        </div>
      </div>
    ) : error && !data ? (
      /* =================================================
         ERROR
         ================================================= */

      <div className="mx-auto max-w-xl rounded-xl border border-red-500/20 bg-red-500/[0.05] p-8 text-center">
        <AlertCircle className="mx-auto mb-4 h-8 w-8 text-red-400" />

        <h2 className="text-lg font-medium text-white">
          Unable to load research
        </h2>

        <p className="mt-2 text-sm text-zinc-400">
          {error}
        </p>

        <button
          type="button"
          onClick={() => {
            void loadResearch(true);
          }}
          className="mt-6 inline-flex items-center gap-2 rounded-lg border border-white/[0.1] bg-white/[0.05] px-4 py-2 text-sm text-white transition-colors hover:bg-white/[0.08]"
        >
          <RefreshCw className="h-4 w-4" />
          Retry
        </button>
      </div>
    ) : (
      /* =================================================
         CONTENT
         ================================================= */

      <div className="space-y-8">
        {/* =================================================
            STATUS BANNER
            ================================================= */}

        <section
          className={[
            "rounded-xl border p-5",
            finished
              ? "border-emerald-500/20 bg-emerald-500/[0.05]"
              : failed
                ? "border-red-500/20 bg-red-500/[0.05]"
                : "border-blue-500/20 bg-blue-500/[0.05]",
          ].join(" ")}
        >
          <div className="flex items-start gap-4">
            <div className="mt-0.5">
              {finished ? (
                <CheckCircle2 className="h-6 w-6 text-emerald-400" />
              ) : failed ? (
                <AlertCircle className="h-6 w-6 text-red-400" />
              ) : (
                <Clock3 className="h-6 w-6 text-blue-400" />
              )}
            </div>

            <div className="min-w-0 flex-1">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <div>
                  <h1 className="text-lg font-semibold text-white">
                    {statusLabel}
                  </h1>

                  <p className="mt-1 text-sm text-zinc-400">
                    {finished
                      ? "Your research is ready to explore."
                      : failed
                        ? "Something went wrong while processing this research."
                        : "The research engine is processing your request."}
                  </p>
                </div>

                {!finished && !failed && (
                  <div className="font-mono text-sm font-medium text-blue-300">
                    {Math.round(progress)}%
                  </div>
                )}
              </div>

              {!finished && !failed && (
                <div className="mt-4 h-1.5 overflow-hidden rounded-full bg-white/[0.08]">
                  <div
                    className="h-full rounded-full bg-blue-500 transition-all duration-500"
                    style={{
                      width: `${Math.max(
                        0,
                        Math.min(
                          100,
                          progress
                        )
                      )}%`,
                    }}
                  />
                </div>
              )}
            </div>
          </div>
        </section>

        {/* =================================================
            RESEARCH HEADER
            ================================================= */}

        <section>
          <div className="mb-5">
            <div className="mb-2 flex items-center gap-2 text-xs uppercase tracking-[0.18em] text-zinc-500">
              <Sparkles className="h-3.5 w-3.5" />
              New Research
            </div>

            <h2 className="text-3xl font-semibold tracking-tight text-white">
              {title}
            </h2>

            <p className="mt-2 max-w-2xl text-sm leading-6 text-zinc-400">
              {summary}
            </p>
          </div>

          <div className="grid gap-4 md:grid-cols-3">
            {/* Company */}

            <div className="rounded-xl border border-white/[0.08] bg-white/[0.02] p-5">
              <div className="mb-3 flex items-center gap-2 text-xs uppercase tracking-wider text-zinc-500">
                <Building2 className="h-4 w-4" />
                Company
              </div>

              <div className="text-sm font-medium text-white">
                {companyName}
              </div>
            </div>

            {/* Research ID */}

            <div className="rounded-xl border border-white/[0.08] bg-white/[0.02] p-5">
              <div className="mb-3 text-xs uppercase tracking-wider text-zinc-500">
                Research ID
              </div>

              <div className="font-mono text-sm text-white">
                {String(researchId)}
              </div>
            </div>

            {/* Status */}

            <div className="rounded-xl border border-white/[0.08] bg-white/[0.02] p-5">
              <div className="mb-3 text-xs uppercase tracking-wider text-zinc-500">
                Status
              </div>

              <div className="text-sm font-medium capitalize text-white">
                {status === "completed"
                  ? "Completed"
                  : status}
              </div>
            </div>
          </div>
        </section>

        {/* =================================================
            RESULT
            ================================================= */}

        <section className="rounded-xl border border-white/[0.08] bg-[#080808]">
          <div className="flex items-center justify-between border-b border-white/[0.08] px-6 py-5">
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-blue-500/10">
                <FileText className="h-4 w-4 text-blue-400" />
              </div>

              <div>
                <h3 className="text-sm font-medium text-white">
                  Research Result
                </h3>

                <p className="mt-0.5 text-xs text-zinc-500">
                  {finished
                    ? "Analysis generated successfully."
                    : failed
                      ? "Research processing failed."
                      : "Analysis is being generated."}
                </p>
              </div>
            </div>

            <button
              type="button"
              onClick={() => {
                void loadResearch(true);
              }}
              disabled={refreshing}
              className="inline-flex items-center gap-2 rounded-lg border border-white/[0.08] px-3 py-2 text-xs text-zinc-400 transition-colors hover:bg-white/[0.04] hover:text-white disabled:cursor-not-allowed disabled:opacity-50"
            >
              <RefreshCw
                className={[
                  "h-3.5 w-3.5",
                  refreshing
                    ? "animate-spin"
                    : "",
                ].join(" ")}
              />

              Refresh
            </button>
          </div>

          <div className="p-6">
            {failed ? (
              <div className="py-12 text-center">
                <AlertCircle className="mx-auto mb-3 h-7 w-7 text-red-400" />

                <div className="text-sm font-medium text-white">
                  Research processing failed
                </div>

                <div className="mt-1 text-xs text-zinc-500">
                  Please refresh or return and
                  create the research again.
                </div>
              </div>
            ) : finished ? (
              <div className="rounded-lg border border-emerald-500/10 bg-emerald-500/[0.03] p-6">
                <div className="flex items-start gap-3">
                  <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-emerald-400" />

                  <div>
                    <div className="text-sm font-medium text-white">
                      Analysis is ready
                    </div>

                    <p className="mt-1 text-sm leading-6 text-zinc-400">
                      Your research has finished
                      processing. Open the research
                      workspace to view the complete
                      analysis, evidence, documents,
                      insights, and report.
                    </p>
                  </div>
                </div>
              </div>
            ) : (
              <div className="py-12 text-center">
                <Loader2 className="mx-auto mb-4 h-7 w-7 animate-spin text-blue-400" />

                <div className="text-sm font-medium text-white">
                  Building your research
                </div>

                <p className="mx-auto mt-2 max-w-md text-xs leading-5 text-zinc-500">
                  The research engine is collecting
                  information, analyzing evidence,
                  and preparing the final result.
                </p>
              </div>
            )}
          </div>
        </section>

        {/* =================================================
            ACTIONS
            ================================================= */}

        <div className="flex flex-col-reverse justify-between gap-3 border-t border-white/[0.08] pt-6 sm:flex-row">
          <button
            type="button"
            onClick={onBack}
            className="inline-flex items-center justify-center gap-2 rounded-lg border border-white/[0.08] bg-white/[0.02] px-5 py-3 text-sm text-zinc-300 transition-colors hover:bg-white/[0.05] hover:text-white"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Dashboard
          </button>

          <button
            type="button"
            onClick={onOpenResearch}
            disabled={!finished}
            className="inline-flex items-center justify-center gap-2 rounded-lg bg-blue-600 px-5 py-3 text-sm font-medium text-white transition-colors hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-40"
          >
            Open Research
            <ArrowRight className="h-4 w-4" />
          </button>
        </div>
      </div>
    )}
  </main>
</div>


);
}

export default NewResearchResult;
