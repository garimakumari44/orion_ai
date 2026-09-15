"use client";

import {
  ArrowRight,
  TrendingUp,
  FileText,
  Search,
  Plus,
  Clock,
  Bot,
} from "lucide-react";
import { useEffect, useState } from "react";

import { cn } from "../../components/ui";
import { searchCompanies } from "@/lib/api/research";
import savedArtifactsApi from "@/lib/api/savedArtifactsApi";

import type { ApiCompanySearchResult } from "@/types/api";
import type { SavedArtifact } from "@/types/savedArtifact";

interface HomePageProps {
  onSelectCompany: (id: string) => void;
  onNavigate: (page: string) => void;
  onOpenSearch: () => void;
}

export function HomePage({
  onSelectCompany,
  onNavigate,
  onOpenSearch,
}: HomePageProps) {
  const [recentResearch, setRecentResearch] = useState<SavedArtifact[]>([]);
  const [recentLoading, setRecentLoading] = useState(true);
  const [recentError, setRecentError] = useState<string | null>(null);

  const [watchlist, setWatchlist] = useState<ApiCompanySearchResult[]>([]);
  const [watchlistLoading, setWatchlistLoading] = useState(false);

  /**
   * Load persisted research artifacts from the backend.
   *
   * No mock companies, fake dates, fake prices, or synthetic research
   * records are created here.
   */
  useEffect(() => {
    let cancelled = false;

    async function loadRecentResearch() {
      setRecentLoading(true);
      setRecentError(null);

      try {
        const artifacts = await savedArtifactsApi.list();

        if (cancelled) return;

        const reports = Array.isArray(artifacts)
          ? artifacts
              .filter((artifact) => {
                const destination = artifact.destination;

                return (
                  destination === "reports" ||
                  destination === "report" ||
                  destination === "research"
                );
              })
              .slice(0, 3)
          : [];

        setRecentResearch(reports);
      } catch (error) {
        if (cancelled) return;

        const message =
          error instanceof Error
            ? error.message
            : "Failed to load recent research.";

        setRecentError(message);
        setRecentResearch([]);
      } finally {
        if (!cancelled) {
          setRecentLoading(false);
        }
      }
    }

    void loadRecentResearch();

    return () => {
      cancelled = true;
    };
  }, []);

  /**
   * The backend currently exposes company search rather than a dedicated
   * watchlist endpoint in the API used by this page.
   *
   * We therefore do not manufacture a watchlist.
   *
   * This state is intentionally empty until a real watchlist API is wired in.
   */
  useEffect(() => {
    setWatchlist([]);
    setWatchlistLoading(false);
  }, []);

  return (
    <div className="h-full overflow-y-auto">
      <div className="mx-auto max-w-4xl px-8 py-10 animate-fade-in">
        {/* Header */}
        <div className="mb-10">
          <h1 className="text-2xl font-semibold tracking-tight text-text-primary">
            Welcome back
          </h1>

          <p className="mt-1 text-sm text-text-muted">
            Pick up where you left off, or start a new research project.
          </p>
        </div>

        {/* Primary actions */}
        <div className="mb-10 grid grid-cols-2 gap-3">
          <button
            type="button"
            onClick={onOpenSearch}
            className="group rounded-lg border border-border bg-bg-surface p-5 text-left transition-colors hover:border-border-hover"
          >
            <div className="mb-2 flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg border border-accent/20 bg-accent/10">
                <Search className="h-4 w-4 text-accent" />
              </div>

              <div>
                <div className="text-sm font-medium text-text-primary">
                  Quick Search
                </div>

                <div className="text-xs text-text-muted">
                  Find any company or ticker
                </div>
              </div>
            </div>
          </button>

          <button
            type="button"
            onClick={() => onNavigate("workspace")}
            className="group rounded-lg border border-border bg-bg-surface p-5 text-left transition-colors hover:border-border-hover"
          >
            <div className="mb-2 flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg border border-accent/20 bg-accent/10">
                <Bot className="h-4 w-4 text-accent" />
              </div>

              <div>
                <div className="text-sm font-medium text-text-primary">
                  AI Workspace
                </div>

                <div className="text-xs text-text-muted">
                  Collaborate with the AI Analyst
                </div>
              </div>
            </div>
          </button>

          <button
            type="button"
            onClick={() => onNavigate("new-research")}
            className="group rounded-lg border border-border bg-bg-surface p-5 text-left transition-colors hover:border-border-hover"
          >
            <div className="mb-2 flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg border border-success/20 bg-success/10">
                <Plus className="h-4 w-4 text-success" />
              </div>

              <div>
                <div className="text-sm font-medium text-text-primary">
                  New Research
                </div>

                <div className="text-xs text-text-muted">
                  Start analyzing a new company
                </div>
              </div>
            </div>
          </button>
        </div>

        {/* Continue Research */}
        <section className="mb-10">
          <div className="mb-3 flex items-center justify-between">
            <h2 className="flex items-center gap-2 text-sm font-medium text-text-primary">
              <Clock className="h-3.5 w-3.5 text-text-faint" />
              Continue Research
            </h2>
          </div>

          {recentLoading ? (
            <div className="rounded-lg border border-border bg-bg-surface p-5">
              <div className="flex items-center gap-3">
                <div className="h-9 w-9 animate-pulse rounded-lg bg-bg-hover" />

                <div className="flex-1 space-y-2">
                  <div className="h-3 w-48 animate-pulse rounded bg-bg-hover" />
                  <div className="h-2.5 w-32 animate-pulse rounded bg-bg-hover" />
                </div>
              </div>
            </div>
          ) : recentError ? (
            <div className="rounded-lg border border-border bg-bg-surface p-5">
              <div className="text-sm text-text-primary">
                Unable to load recent research.
              </div>

              <div className="mt-1 text-xs text-text-muted">
                {recentError}
              </div>

              <button
                type="button"
                onClick={() => onNavigate("reports")}
                className="mt-3 text-xs text-accent hover:underline"
              >
                Open reports
              </button>
            </div>
          ) : recentResearch.length === 0 ? (
            <div className="rounded-lg border border-border bg-bg-surface p-6 text-center">
              <Clock className="mx-auto h-5 w-5 text-text-faint" />

              <div className="mt-2 text-sm text-text-primary">
                No recent research
              </div>

              <div className="mt-1 text-xs text-text-muted">
                Start a research project to see it here.
              </div>

              <button
                type="button"
                onClick={() => onNavigate("new-research")}
                className="mt-4 inline-flex items-center gap-1.5 rounded-md border border-border px-3 py-2 text-xs text-text-secondary transition-colors hover:border-border-hover hover:text-text-primary"
              >
                <Plus className="h-3.5 w-3.5" />
                Start research
              </button>
            </div>
          ) : (
            <div className="space-y-2">
              {recentResearch.map((research) => {
                const researchId =
                  research.research_id ??
                  research.researchId ??
                  null;

                const title =
                  typeof research.title === "string"
                    ? research.title.trim()
                    : "";

                const description =
                  typeof research.description === "string"
                    ? research.description.trim()
                    : "";

                /**
                 * Never create a synthetic ID.
                 * If the persisted artifact does not contain a research ID,
                 * it cannot be opened as a research workspace.
                 */
                if (!researchId) {
                  return (
                    <div
                      key={String(research.id)}
                      className="w-full rounded-lg border border-border bg-bg-surface p-4"
                    >
                      <div className="text-sm font-medium text-text-primary">
                        {title || "Saved artifact"}
                      </div>

                      {description && (
                        <div className="mt-1 truncate text-xs text-text-muted">
                          {description}
                        </div>
                      )}
                    </div>
                  );
                }

                return (
                  <button
                    key={String(research.id)}
                    type="button"
                    onClick={() => onSelectCompany(String(researchId))}
                    className="group flex w-full items-center gap-4 rounded-lg border border-border bg-bg-surface p-4 text-left transition-colors hover:border-border-hover"
                  >
                    <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-accent/20 bg-accent/10">
                      <FileText className="h-4 w-4 text-accent" />
                    </div>

                    <div className="min-w-0 flex-1">
                      <div className="truncate text-sm font-medium text-text-primary">
                        {title || "Research"}
                      </div>

                      {description && (
                        <div className="mt-0.5 truncate text-xs text-text-muted">
                          {description}
                        </div>
                      )}
                    </div>

                    <ArrowRight className="h-4 w-4 shrink-0 text-text-faint transition-colors group-hover:text-text-muted" />
                  </button>
                );
              })}
            </div>
          )}
        </section>

        {/* Watchlist */}
        <section className="mb-10">
          <h2 className="mb-3 flex items-center gap-2 text-sm font-medium text-text-primary">
            <TrendingUp className="h-3.5 w-3.5 text-text-faint" />
            Watchlist
          </h2>

          {watchlistLoading ? (
            <div className="rounded-lg border border-border bg-bg-surface p-5 text-xs text-text-muted">
              Loading watchlist…
            </div>
          ) : watchlist.length === 0 ? (
            <div className="rounded-lg border border-border bg-bg-surface p-6 text-center">
              <TrendingUp className="mx-auto h-5 w-5 text-text-faint" />

              <div className="mt-2 text-sm text-text-primary">
                No watchlist data
              </div>

              <div className="mt-1 text-xs text-text-muted">
                Connect the watchlist endpoint to display live companies here.
              </div>

              <button
                type="button"
                onClick={onOpenSearch}
                className={cn(
                  "mt-4 inline-flex items-center gap-1.5",
                  "rounded-md border border-border px-3 py-2",
                  "text-xs text-text-secondary",
                  "transition-colors hover:border-border-hover",
                  "hover:text-text-primary",
                )}
              >
                <Search className="h-3.5 w-3.5" />
                Search companies
              </button>
            </div>
          ) : (
            <div className="overflow-hidden rounded-lg border border-border bg-bg-surface">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-border">
                    <th className="px-4 py-2.5 text-left font-mono text-[10px] uppercase tracking-wider text-text-faint">
                      Company
                    </th>

                    <th className="px-4 py-2.5 text-right font-mono text-[10px] uppercase tracking-wider text-text-faint">
                      Ticker
                    </th>
                  </tr>
                </thead>

                <tbody>
                  {watchlist.map((company) => {
                    const id = String(company.id ?? "").trim();

                    if (!id) return null;

                    return (
                      <tr
                        key={id}
                        className="border-b border-border-subtle last:border-0"
                      >
                        <td className="px-4 py-2.5">
                          <span className="text-xs text-text-primary">
                            {company.name}
                          </span>
                        </td>

                        <td className="px-4 py-2.5 text-right">
                          <button
                            type="button"
                            onClick={() => onSelectCompany(id)}
                            className="font-mono text-xs text-text-secondary hover:text-text-primary"
                          >
                            {company.ticker ?? "—"}
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </section>

        {/* Recent Reports */}
        <section>
          <div className="mb-3 flex items-center justify-between">
            <h2 className="flex items-center gap-2 text-sm font-medium text-text-primary">
              <FileText className="h-3.5 w-3.5 text-text-faint" />
              Recent Reports
            </h2>

            <button
              type="button"
              onClick={() => onNavigate("reports")}
              className="flex items-center gap-1 text-xs text-text-muted transition-colors hover:text-text-primary"
            >
              View all
              <ArrowRight className="h-3 w-3" />
            </button>
          </div>

          {recentLoading ? (
            <div className="grid grid-cols-2 gap-2">
              {[0, 1].map((item) => (
                <div
                  key={item}
                  className="rounded-lg border border-border bg-bg-surface p-4"
                >
                  <div className="h-3 w-24 animate-pulse rounded bg-bg-hover" />
                  <div className="mt-3 h-3 w-40 animate-pulse rounded bg-bg-hover" />
                  <div className="mt-2 h-2.5 w-20 animate-pulse rounded bg-bg-hover" />
                </div>
              ))}
            </div>
          ) : recentResearch.length === 0 ? (
            <div className="rounded-lg border border-border bg-bg-surface p-6 text-center">
              <FileText className="mx-auto h-5 w-5 text-text-faint" />

              <div className="mt-2 text-sm text-text-primary">
                No reports yet
              </div>

              <div className="mt-1 text-xs text-text-muted">
                Completed research reports will appear here.
              </div>

              <button
                type="button"
                onClick={() => onNavigate("new-research")}
                className="mt-4 inline-flex items-center gap-1.5 rounded-md border border-border px-3 py-2 text-xs text-text-secondary transition-colors hover:border-border-hover hover:text-text-primary"
              >
                <Plus className="h-3.5 w-3.5" />
                Start research
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-2 gap-2">
              {recentResearch.slice(0, 4).map((report) => {
                const researchId =
                  report.research_id ??
                  report.researchId ??
                  null;

                const title =
                  typeof report.title === "string"
                    ? report.title.trim()
                    : "";

                const description =
                  typeof report.description === "string"
                    ? report.description.trim()
                    : "";

                return (
                  <button
                    key={String(report.id)}
                    type="button"
                    disabled={!researchId}
                    onClick={() => {
                      if (!researchId) return;

                      onSelectCompany(String(researchId));
                    }}
                    className={cn(
                      "group rounded-lg border border-border bg-bg-surface p-4 text-left transition-colors",
                      researchId
                        ? "hover:border-border-hover"
                        : "cursor-default opacity-70",
                    )}
                  >
                    <div className="mb-1.5 flex items-center justify-between gap-2">
                      <span className="font-mono text-xs text-text-faint">
                        {report.destination ?? "research"}
                      </span>

                      <FileText className="h-3.5 w-3.5 text-text-faint" />
                    </div>

                    <div className="truncate text-sm text-text-primary">
                      {title || "Research"}
                    </div>

                    {description && (
                      <div className="mt-0.5 truncate text-xs text-text-muted">
                        {description}
                      </div>
                    )}
                  </button>
                );
              })}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}