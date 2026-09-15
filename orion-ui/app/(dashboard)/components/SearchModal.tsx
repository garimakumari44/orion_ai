"use client";

import {
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  Search,
  X,
  TrendingUp,
  FileText,
  Newspaper,
  Clock,
  Bot,
} from "lucide-react";

import { TickerLogo } from "./ui";

import {
  searchCompanies,
} from "@/lib/api/research";

import savedArtifactsApi from "@/lib/api/savedArtifactsApi";

import type {
  ApiCompanySearchResult,
} from "@/types/api";

import type {
  SavedArtifact,
} from "@/types/savedArtifact";

/* -------------------------------------------------------------------------- */
/* Props                                                                      */
/* -------------------------------------------------------------------------- */

interface SearchModalProps {
  open: boolean;

  onClose: () => void;

  onSelectCompany: (id: string) => void;

  onNavigate: (page: string) => void;
}

/* -------------------------------------------------------------------------- */
/* Navigation                                                                 */
/* -------------------------------------------------------------------------- */

interface NavDestination {
  id: string;

  label: string;

  description: string;

  page: string;
}

const navDestinations: NavDestination[] = [
  {
    id: "nav-workspace",
    label: "AI Workplace",
    description:
      "AI-powered research workspace dashboard",
    page: "workspace",
  },

  {
    id: "nav-research",
    label: "Research",
    description:
      "Company equity research and analysis",
    page: "research",
  },

  {
    id: "nav-library",
    label: "Library",
    description:
      "Browse saved research reports",
    page: "library",
  },

  {
    id: "nav-reports",
    label: "Reports",
    description:
      "View completed research reports",
    page: "reports",
  },
];

/* -------------------------------------------------------------------------- */
/* Recent searches                                                            */
/* -------------------------------------------------------------------------- */

/**
 * These are navigation/search suggestions, not research data.
 *
 * They are safe to keep as UI suggestions.
 */
const recentSearches = [
  "AAPL",
  "Microsoft",
  "NVDA earnings",
];

/* -------------------------------------------------------------------------- */
/* Helpers                                                                    */
/* -------------------------------------------------------------------------- */

function getArtifactSearchText(
  artifact: SavedArtifact,
): string {
  const title =
    typeof artifact.title === "string"
      ? artifact.title
      : "";

  const description =
    typeof artifact.description === "string"
      ? artifact.description
      : "";

  return `${title} ${description}`.toLowerCase();
}

function getArtifactTitle(
  artifact: SavedArtifact,
): string {
  if (
    typeof artifact.title === "string" &&
    artifact.title.trim()
  ) {
    return artifact.title;
  }

  return "Saved research";
}

/* -------------------------------------------------------------------------- */
/* Component                                                                  */
/* -------------------------------------------------------------------------- */

export function SearchModal({
  open,
  onClose,
  onSelectCompany,
  onNavigate,
}: SearchModalProps) {
  const [query, setQuery] =
    useState("");

  const [
    companyResults,
    setCompanyResults,
  ] = useState<ApiCompanySearchResult[]>(
    [],
  );

  const [
    savedReports,
    setSavedReports,
  ] = useState<SavedArtifact[]>(
    [],
  );

  const [
    loadingCompanies,
    setLoadingCompanies,
  ] = useState(false);

  const [
    loadingReports,
    setLoadingReports,
  ] = useState(false);

  const [
    companySearchError,
    setCompanySearchError,
  ] = useState<string | null>(null);

  const [
    reportSearchError,
    setReportSearchError,
  ] = useState<string | null>(null);

  /* ------------------------------------------------------------------------ */
  /* Reset                                                                    */
  /* ------------------------------------------------------------------------ */

  useEffect(() => {
    if (!open) {
      setQuery("");

      setCompanyResults([]);

      setCompanySearchError(null);

      setReportSearchError(null);
    }
  }, [open]);

  /* ------------------------------------------------------------------------ */
  /* Escape                                                                   */
  /* ------------------------------------------------------------------------ */

  useEffect(() => {
    if (!open) {
      return;
    }

    const handler = (
      event: KeyboardEvent,
    ) => {
      if (event.key === "Escape") {
        onClose();
      }
    };

    window.addEventListener(
      "keydown",
      handler,
    );

    return () => {
      window.removeEventListener(
        "keydown",
        handler,
      );
    };
  }, [open, onClose]);

  /* ------------------------------------------------------------------------ */
  /* Company search                                                           */
  /* ------------------------------------------------------------------------ */

  useEffect(() => {
    const normalizedQuery =
      query.trim();

    if (!normalizedQuery) {
      setCompanyResults([]);

      setCompanySearchError(null);

      setLoadingCompanies(false);

      return;
    }

    let cancelled = false;

    const timer = setTimeout(
      async () => {
        try {
          setLoadingCompanies(true);

          setCompanySearchError(null);

          const results =
            await searchCompanies(
              normalizedQuery,
              10,
            );

          if (!cancelled) {
            setCompanyResults(
              results,
            );
          }
        } catch (error) {
          if (cancelled) {
            return;
          }

          console.error(
            "[SearchModal] Company search failed:",
            error,
          );

          setCompanyResults([]);

          setCompanySearchError(
            error instanceof Error
              ? error.message
              : "Company search failed.",
          );
        } finally {
          if (!cancelled) {
            setLoadingCompanies(false);
          }
        }
      },
      300,
    );

    return () => {
      cancelled = true;

      clearTimeout(timer);
    };
  }, [query]);

  /* ------------------------------------------------------------------------ */
  /* Saved reports                                                            */
  /* ------------------------------------------------------------------------ */

  useEffect(() => {
    if (!open) {
      return;
    }

    let cancelled = false;

    async function loadReports() {
      try {
        setLoadingReports(true);

        setReportSearchError(null);

        /**
         * Load persisted saved artifacts from FastAPI.
         *
         * We intentionally do not use mock report data.
         */
        const artifacts =
          await savedArtifactsApi.list();

        if (!cancelled) {
          setSavedReports(
            Array.isArray(artifacts)
              ? artifacts
              : [],
          );
        }
      } catch (error) {
        if (cancelled) {
          return;
        }

        console.error(
          "[SearchModal] Failed to load saved reports:",
          error,
        );

        setSavedReports([]);

        setReportSearchError(
          error instanceof Error
            ? error.message
            : "Failed to load reports.",
        );
      } finally {
        if (!cancelled) {
          setLoadingReports(false);
        }
      }
    }

    void loadReports();

    return () => {
      cancelled = true;
    };
  }, [open]);

  /* ------------------------------------------------------------------------ */
  /* Search results                                                           */
  /* ------------------------------------------------------------------------ */

  const results = useMemo(() => {
    const normalizedQuery =
      query.trim();

    if (!normalizedQuery) {
      return {
        companies:
          [] as ApiCompanySearchResult[],

        reports:
          [] as SavedArtifact[],

        destinations:
          [] as NavDestination[],
      };
    }

    const q =
      normalizedQuery.toLowerCase();

    const reports =
      savedReports.filter(
        (report) =>
          getArtifactSearchText(
            report,
          ).includes(q),
      );

    const destinations =
      navDestinations.filter(
        (destination) =>
          destination.label
            .toLowerCase()
            .includes(q) ||
          destination.description
            .toLowerCase()
            .includes(q),
      );

    return {
      companies: companyResults,

      reports,

      destinations,
    };
  }, [
    query,
    companyResults,
    savedReports,
  ]);

  const aiWorkplace =
    navDestinations[0];

  /* ------------------------------------------------------------------------ */
  /* Closed                                                                   */
  /* ------------------------------------------------------------------------ */

  if (!open) {
    return null;
  }

  /* ------------------------------------------------------------------------ */
  /* Render                                                                   */
  /* ------------------------------------------------------------------------ */

  return (
    <div
      className="
        fixed inset-0
        z-50
        flex
        items-start
        justify-center
        pt-[15vh]
        px-4
        animate-fade-in
      "
    >
      {/* Backdrop */}

      <div
        className="
          absolute
          inset-0
          bg-black/70
          backdrop-blur-sm
        "
        onClick={onClose}
      />

      {/* Modal */}

      <div
        className="
          relative
          w-full
          max-w-xl
          bg-bg-surface
          border
          border-border
          rounded-lg
          shadow-2xl
          overflow-hidden
          animate-slide-up
        "
      >
        {/* Search input */}

        <div
          className="
            flex
            items-center
            gap-3
            px-4
            py-3
            border-b
            border-border
          "
        >
          <Search
            className="
              w-4
              h-4
              text-text-faint
            "
          />

          <input
            autoFocus
            value={query}
            onChange={(event) =>
              setQuery(
                event.target.value,
              )
            }
            placeholder="
              Search companies, tickers, reports...
            "
            className="
              flex-1
              bg-transparent
              text-sm
              text-text-primary
              placeholder:text-text-faint
              outline-none
            "
          />

          <button
            type="button"
            onClick={onClose}
            className="
              text-text-faint
              hover:text-text-muted
            "
            aria-label="Close search"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Results */}

        <div
          className="
            max-h-[55vh]
            overflow-y-auto
          "
        >
          {!query.trim() ? (
            <div className="p-4">
              <div
                className="
                  flex
                  items-center
                  gap-2
                  text-[10px]
                  text-text-faint
                  uppercase
                  tracking-widest
                  font-mono
                  mb-2
                "
              >
                <Clock className="w-3 h-3" />

                Recent Searches
              </div>

              {recentSearches.map(
                (item) => (
                  <button
                    key={item}
                    type="button"
                    onClick={() =>
                      setQuery(item)
                    }
                    className="
                      w-full
                      flex
                      items-center
                      gap-2.5
                      px-2.5
                      py-1.5
                      rounded-md
                      text-sm
                      text-left
                      hover:bg-bg-hover
                    "
                  >
                    <Clock
                      className="
                        w-3.5
                        h-3.5
                        text-text-faint
                      "
                    />

                    {item}
                  </button>
                ),
              )}
            </div>
          ) : (
            <div
              className="
                p-4
                space-y-4
              "
            >
              {/* ---------------------------------------------------------------- */}
              {/* AI WORKPLACE                                                     */}
              {/* ---------------------------------------------------------------- */}

              <div>
                <div
                  className="
                    flex
                    items-center
                    gap-2
                    text-[10px]
                    text-text-faint
                    uppercase
                    tracking-widest
                    font-mono
                    mb-2
                  "
                >
                  <Bot className="w-3 h-3" />

                  AI Workplace
                </div>

                <button
                  type="button"
                  onClick={() => {
                    onNavigate(
                      aiWorkplace.page,
                    );

                    onClose();
                  }}
                  className="
                    w-full
                    flex
                    items-center
                    gap-2.5
                    px-2.5
                    py-1.5
                    rounded-md
                    hover:bg-bg-hover
                  "
                >
                  <Bot
                    className="
                      w-4
                      h-4
                      text-accent
                    "
                  />

                  <div className="text-left">
                    <div>
                      {aiWorkplace.label}
                    </div>

                    <div
                      className="
                        text-xs
                        text-text-faint
                      "
                    >
                      {
                        aiWorkplace.description
                      }
                    </div>
                  </div>
                </button>
              </div>

              {/* ---------------------------------------------------------------- */}
              {/* COMPANIES                                                        */}
              {/* ---------------------------------------------------------------- */}

              {loadingCompanies && (
                <p
                  className="
                    text-sm
                    text-text-faint
                  "
                >
                  Searching companies...
                </p>
              )}

              {companySearchError && (
                <p
                  className="
                    text-sm
                    text-red-400
                  "
                >
                  {companySearchError}
                </p>
              )}

              {results.companies.length >
                0 && (
                <div>
                  <div
                    className="
                      flex
                      items-center
                      gap-2
                      text-[10px]
                      text-text-faint
                      uppercase
                      tracking-widest
                      font-mono
                      mb-2
                    "
                  >
                    <TrendingUp className="w-3 h-3" />

                    Companies
                  </div>

                  {results.companies.map(
                    (company) => (
                      <button
                        key={String(
                          company.id,
                        )}
                        type="button"
                        onClick={() => {
                          onSelectCompany(
                            String(
                              company.id,
                            ),
                          );

                          onClose();
                        }}
                        className="
                          w-full
                          flex
                          items-center
                          gap-2.5
                          px-2.5
                          py-1.5
                          rounded-md
                          hover:bg-bg-hover
                        "
                      >
                        <TickerLogo
                          name={
                            company.name
                          }
                          logoUrl={
                            company.logo_url
                          }
                          size={24}
                        />

                        <div
                          className="
                            flex-1
                            text-left
                          "
                        >
                          <div
                            className="
                              text-text-secondary
                            "
                          >
                            {
                              company.name
                            }
                          </div>

                          <div
                            className="
                              text-[11px]
                              text-text-faint
                              font-mono
                            "
                          >
                            {company.exchange ??
                              ""}

                            {company.exchange
                              ? " : "
                              : ""}

                            {company.ticker ??
                              "--"}
                          </div>
                        </div>
                      </button>
                    ),
                  )}
                </div>
              )}

              {/* ---------------------------------------------------------------- */}
              {/* SAVED REPORTS                                                   */}
              {/* ---------------------------------------------------------------- */}

              {loadingReports && (
                <p
                  className="
                    text-sm
                    text-text-faint
                  "
                >
                  Searching saved reports...
                </p>
              )}

              {reportSearchError && (
                <p
                  className="
                    text-sm
                    text-red-400
                  "
                >
                  {reportSearchError}
                </p>
              )}

              {results.reports.length >
                0 && (
                <div>
                  <div
                    className="
                      flex
                      items-center
                      gap-2
                      text-[10px]
                      text-text-faint
                      uppercase
                      tracking-widest
                      font-mono
                      mb-2
                    "
                  >
                    <FileText className="w-3 h-3" />

                    Reports
                  </div>

                  {results.reports.map(
                    (report) => (
                      <button
                        key={String(
                          report.id,
                        )}
                        type="button"
                        onClick={() => {
                          onNavigate(
                            "reports",
                          );

                          onClose();
                        }}
                        className="
                          w-full
                          flex
                          items-center
                          gap-2.5
                          px-2.5
                          py-1.5
                          rounded-md
                          hover:bg-bg-hover
                        "
                      >
                        <FileText
                          className="
                            w-4
                            h-4
                            text-text-faint
                          "
                        />

                        <div className="text-left">
                          <div>
                            {getArtifactTitle(
                              report,
                            )}
                          </div>

                          {typeof report.description ===
                            "string" &&
                            report.description.trim() && (
                              <div
                                className="
                                  text-xs
                                  text-text-faint
                                  truncate
                                  max-w-[400px]
                                "
                              >
                                {
                                  report.description
                                }
                              </div>
                            )}
                        </div>
                      </button>
                    ),
                  )}
                </div>
              )}

              {/* ---------------------------------------------------------------- */}
              {/* NAVIGATION                                                       */}
              {/* ---------------------------------------------------------------- */}

              {results.destinations
                .length > 0 && (
                <div>
                  <div
                    className="
                      flex
                      items-center
                      gap-2
                      text-[10px]
                      text-text-faint
                      uppercase
                      tracking-widest
                      font-mono
                      mb-2
                    "
                  >
                    <Newspaper className="w-3 h-3" />

                    Navigation
                  </div>

                  {results.destinations.map(
                    (destination) => (
                      <button
                        key={
                          destination.id
                        }
                        type="button"
                        onClick={() => {
                          onNavigate(
                            destination.page,
                          );

                          onClose();
                        }}
                        className="
                          w-full
                          flex
                          items-center
                          gap-2.5
                          px-2.5
                          py-1.5
                          rounded-md
                          hover:bg-bg-hover
                        "
                      >
                        <Newspaper
                          className="
                            w-4
                            h-4
                            text-text-faint
                          "
                        />

                        <div className="text-left">
                          <div>
                            {
                              destination.label
                            }
                          </div>

                          <div
                            className="
                              text-xs
                              text-text-faint
                            "
                          >
                            {
                              destination.description
                            }
                          </div>
                        </div>
                      </button>
                    ),
                  )}
                </div>
              )}

              {/* ---------------------------------------------------------------- */}
              {/* EMPTY                                                            */}
              {/* ---------------------------------------------------------------- */}

              {!loadingCompanies &&
                !loadingReports &&
                !companySearchError &&
                !reportSearchError &&
                results.companies.length ===
                  0 &&
                results.reports.length ===
                  0 &&
                results.destinations.length ===
                  0 && (
                  <div
                    className="
                      py-8
                      text-center
                      text-sm
                      text-text-faint
                    "
                  >
                    No results found.
                  </div>
                )}
            </div>
          )}
        </div>

        {/* Footer */}

        <div
          className="
            px-4
            py-2.5
            border-t
            border-border
            flex
            justify-between
            text-[11px]
            text-text-faint
          "
        >
          <span>
            ↵ Open
          </span>

          <span
            className="
              flex
              items-center
              gap-1
            "
          >
            <Newspaper className="w-3 h-3" />

            Powered by Research Canvas
          </span>
        </div>
      </div>
    </div>
  );
}