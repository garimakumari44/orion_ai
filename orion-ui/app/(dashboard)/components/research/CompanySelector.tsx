import { useState, useEffect, useRef } from "react";
import { Search, X, ChevronRight } from "lucide-react";

import { TickerLogo } from "../../components/ui";

import { searchCompanies } from "@/lib/api/research";

import { CompanySearchResult } from "@/types";

interface CompanySelectorProps {
  label?: string;
  selected: CompanySearchResult | null;
  onSelect: (company: CompanySearchResult | null) => void;
  placeholder?: string;
}

export function CompanySelector({
  label = "Company Selection",
  selected,
  onSelect,
  placeholder = "Search company...",
}: CompanySelectorProps) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<CompanySearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);

  const containerRef = useRef<HTMLDivElement>(null);

  /*
   * Company search
   *
   * Backend requires q to contain at least 2 characters.
   * Therefore, we do not make an API request for:
   * - empty string
   * - whitespace
   * - one-character queries
   *
   * Search is also debounced by 300ms to avoid making
   * a request for every keystroke.
   */
  useEffect(() => {
    const trimmedQuery = query.trim();

    // Do not search until at least 2 characters are entered.
    if (trimmedQuery.length < 2) {
      setResults([]);
      setLoading(false);
      return;
    }

    const timer = setTimeout(async () => {
      try {
        setLoading(true);

        const companies = await searchCompanies(trimmedQuery);

        console.log("API returned:", companies);

        setResults(companies);
      } catch (err) {
        console.error("Company search failed:", err);
        setResults([]);
      } finally {
        setLoading(false);
      }
    }, 300);

    return () => {
      clearTimeout(timer);
    };
  }, [query]);

  /*
   * Close dropdown when clicking outside the component.
   */
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (
        containerRef.current &&
        !containerRef.current.contains(e.target as Node)
      ) {
        setOpen(false);
      }
    };

    document.addEventListener("mousedown", handler);

    return () => {
      document.removeEventListener("mousedown", handler);
    };
  }, []);

  return (
    <div ref={containerRef} className="relative">
      {/* Label */}
      <div className="text-[10px] text-text-faint uppercase tracking-widest font-mono mb-2">
        {label}
      </div>

      {selected ? (
        /*
         * Selected company
         */
        <div className="flex items-center gap-3 bg-bg-surface border border-border rounded-lg p-3.5">
          <TickerLogo
            name={selected.name}
            logoUrl={selected.logoUrl}
            size={36}
          />

          <div className="flex-1 min-w-0">
            <div className="text-sm font-medium text-text-primary">
              {selected.name}
            </div>

            <div className="flex items-center gap-2 mt-1 text-xs text-text-muted">
              <span className="font-mono">
                {selected.ticker ?? "--"}
              </span>

              <span>•</span>

              <span>{selected.exchange ?? "--"}</span>

              <span>•</span>

              <span>{selected.country ?? "--"}</span>
            </div>
          </div>

          <button
            type="button"
            onClick={() => {
              onSelect(null);
              setQuery("");
              setResults([]);
              setOpen(false);
            }}
            className="text-text-faint hover:text-text-primary"
            aria-label="Remove selected company"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      ) : (
        /*
         * Company search input
         */
        <div className="relative">
          <div className="flex items-center gap-2 bg-bg-surface border border-border rounded-lg px-3 py-2.5">
            <Search className="w-4 h-4 text-text-faint" />

            <input
              value={query}
              placeholder={placeholder}
              onFocus={() => setOpen(true)}
              onChange={(e) => {
                setQuery(e.target.value);
                setOpen(true);
              }}
              className="flex-1 bg-transparent outline-none text-sm"
              aria-label={label}
            />

            {loading && (
              <span className="text-xs font-mono text-text-muted">
                Searching...
              </span>
            )}
          </div>

          {open && (
            <div className="absolute top-full left-0 right-0 mt-2 bg-bg-surface border border-border rounded-lg shadow-xl max-h-72 overflow-y-auto z-50">
              {results.length > 0 ? (
                /*
                 * Search results
                 */
                results.map((company) => (
                  <button
                    type="button"
                    key={company.id}
                    onClick={() => {
                      onSelect(company);
                      setOpen(false);
                      setQuery("");
                      setResults([]);
                    }}
                    className="w-full flex items-center gap-3 px-3 py-3 hover:bg-bg-hover text-left"
                  >
                    <TickerLogo
                      name={company.name}
                      logoUrl={company.logoUrl}
                      size={28}
                    />

                    <div className="flex-1 min-w-0">
                      <div className="text-sm text-text-primary truncate">
                        {company.name}
                      </div>

                      <div className="text-xs text-text-faint">
                        {company.exchange ?? "--"} •{" "}
                        {company.ticker ?? "--"}
                      </div>
                    </div>

                    <ChevronRight className="w-4 h-4 text-text-faint" />
                  </button>
                ))
              ) : (
                /*
                 * Only show "No companies found" after
                 * a valid search has actually been performed.
                 */
                !loading &&
                query.trim().length >= 2 && (
                  <div className="p-4 text-center text-sm text-text-muted">
                    No companies found.
                  </div>
                )
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}