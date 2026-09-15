"use client";

import { useEffect, useMemo, useState } from "react";

import {
Library as LibraryIcon,
ArrowRight,
Search,
Loader2,
Trash2,
} from "lucide-react";

import {
RecommendationBadge,
TickerLogo,
ProgressBar,
} from "../../components/ui";

import libraryApi from "@/lib/api/libraryApi";

import type { LibraryItem } from "@/types/library";

interface LibraryPageProps {
onSelectCompany: (id: string) => void;
}

function normalizeConfidence(value: unknown): number {
if (
typeof value !== "number" ||
!Number.isFinite(value)
) {
return 0;
}

if (value <= 1) {
return Math.max(
0,
Math.min(100, value * 100),
);
}

return Math.max(
0,
Math.min(100, value),
);
}

function displayText(
value: unknown,
fallback = "—",
): string {
if (
value === null ||
value === undefined
) {
return fallback;
}

if (typeof value === "string") {
return value.trim() || fallback;
}

if (
typeof value === "number" ||
typeof value === "boolean"
) {
return String(value);
}

return fallback;
}

function getResearchId(
item: LibraryItem,
): string | null {
const legacyItem = item as LibraryItem & {
research_id?: string | null;
};

const researchId =
item.researchId ??
legacyItem.research_id ??
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

export function LibraryPage({
onSelectCompany,
}: LibraryPageProps) {
const [query, setQuery] =
useState("");

const [items, setItems] =
useState<LibraryItem[]>([]);

const [loading, setLoading] =
useState(true);

const [error, setError] =
useState<string | null>(null);

const [removingId, setRemovingId] =
useState<string | null>(null);

useEffect(() => {
let cancelled = false;


async function loadLibrary() {
  try {
    setLoading(true);
    setError(null);

    const result =
      await libraryApi.list();

    if (!cancelled) {
      setItems(
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
          : "Failed to load library.",
      );
    }
  } finally {
    if (!cancelled) {
      setLoading(false);
    }
  }
}

loadLibrary();

return () => {
  cancelled = true;
};


}, []);

const filtered = useMemo(() => {
const normalized =
query.trim().toLowerCase();


if (!normalized) {
  return items;
}

return items.filter((item) => {
  const company =
    displayText(
      item.companyName,
      "",
    ).toLowerCase();

  const ticker =
    displayText(
      item.ticker,
      "",
    ).toLowerCase();

  const title =
    displayText(
      item.title,
      "",
    ).toLowerCase();

  return (
    company.includes(normalized) ||
    ticker.includes(normalized) ||
    title.includes(normalized)
  );
});


}, [items, query]);

async function handleRemove(
event: React.MouseEvent<HTMLButtonElement>,
id: string,
) {
event.stopPropagation();


try {
  setRemovingId(id);
  setError(null);

  await libraryApi.remove(id);

  setItems((current) =>
    current.filter(
      (item) => item.id !== id,
    ),
  );
} catch (err) {
  setError(
    err instanceof Error
      ? err.message
      : "Failed to remove item.",
  );
} finally {
  setRemovingId(null);
}


}

function handleSelect(
item: LibraryItem,
) {
setError(null);


const researchId =
  getResearchId(item);

/*
 * Research workspace navigation must
 * use the research ID.
 *
 * Legacy library records may not have
 * researchId, so fall back to companyId
 * and finally item.id.
 */
const destination =
  researchId ??
  item.companyId ??
  item.id;

if (
  !destination ||
  destination === "undefined" ||
  destination === "null"
) {
  console.error(
    "Cannot open library item: missing destination.",
    item,
  );

  setError(
    "This saved research is missing its research ID and cannot be opened.",
  );

  return;
}

console.log(
  "Opening library research workspace:",
  destination,
);

onSelectCompany(
  String(destination),
);


}

function handleArrowClick(
event: React.MouseEvent<HTMLButtonElement>,
item: LibraryItem,
) {
event.stopPropagation();


handleSelect(item);


}

return ( <div className="h-full overflow-y-auto"> <div className="max-w-5xl mx-auto px-8 py-8 animate-fade-in">


    {/* Header */}
    <div className="flex items-center gap-2.5 mb-1">
      <LibraryIcon className="w-5 h-5 text-text-faint" />

      <h1 className="text-xl font-semibold text-text-primary">
        Library
      </h1>
    </div>

    <p className="text-sm text-text-muted mb-6">
      Saved research workspaces and analysis.
    </p>

    {/* Search */}
    <div className="relative mb-6">
      <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-faint" />

      <input
        value={query}
        onChange={(event) =>
          setQuery(event.target.value)
        }
        placeholder="Filter by name, ticker, or research..."
        className="w-full bg-bg-surface border border-border rounded-lg pl-9 pr-4 py-2 text-sm text-text-primary placeholder:text-text-faint outline-none focus:border-border-hover transition-colors"
      />
    </div>

    {/* Error */}
    {error && (
      <div className="mb-4 rounded-lg border border-danger/30 bg-danger/5 px-4 py-3 text-sm text-danger">
        {error}
      </div>
    )}

    {/* Library */}
    <div className="bg-bg-surface border border-border rounded-lg overflow-hidden">

      {loading ? (
        <div className="flex items-center justify-center gap-2 py-16 text-sm text-text-muted">
          <Loader2 className="w-4 h-4 animate-spin" />
          Loading library...
        </div>
      ) : filtered.length === 0 ? (
        <div className="py-16 text-center">
          <LibraryIcon className="w-8 h-8 text-text-faint mx-auto mb-3" />

          <div className="text-sm text-text-secondary">
            {query
              ? "No saved research matches your search."
              : "Your library is empty."}
          </div>

          <div className="text-xs text-text-faint mt-1">
            Save a research workspace to see it here.
          </div>
        </div>
      ) : (
        <table className="w-full">
          <thead>
            <tr className="border-b border-border">

              <th className="text-left text-[10px] text-text-faint uppercase tracking-wider font-mono px-5 py-3">
                Research
              </th>

              <th className="text-left text-[10px] text-text-faint uppercase tracking-wider font-mono px-4 py-3">
                Sector
              </th>

              <th className="text-left text-[10px] text-text-faint uppercase tracking-wider font-mono px-4 py-3">
                Recommendation
              </th>

              <th className="text-right text-[10px] text-text-faint uppercase tracking-wider font-mono px-4 py-3">
                Price
              </th>

              <th className="text-right text-[10px] text-text-faint uppercase tracking-wider font-mono px-4 py-3">
                Fair Value
              </th>

              <th className="text-left text-[10px] text-text-faint uppercase tracking-wider font-mono px-4 py-3">
                Confidence
              </th>

              <th className="text-right text-[10px] text-text-faint uppercase tracking-wider font-mono px-5 py-3">
              </th>

            </tr>
          </thead>

          <tbody>
            {filtered.map((item) => {
              const name =
                displayText(
                  item.companyName,
                  displayText(
                    item.title,
                    "Untitled Research",
                  ),
                );

              const ticker =
                displayText(
                  item.ticker,
                  "—",
                );

              const confidence =
                normalizeConfidence(
                  item.confidence,
                );

              const currentPrice =
                typeof item.currentPrice ===
                  "number" &&
                Number.isFinite(
                  item.currentPrice,
                )
                  ? item.currentPrice
                  : null;

              const fairValue =
                typeof item.fairValue ===
                  "number" &&
                Number.isFinite(
                  item.fairValue,
                )
                  ? item.fairValue
                  : null;

              const sector =
                displayText(
                  item.sector,
                  "—",
                );

              const recommendation =
                displayText(
                  item.recommendation,
                  "",
                );

              const researchId =
                getResearchId(item);

              return (
                <tr
                  key={item.id}
                  onClick={() =>
                    handleSelect(item)
                  }
                  onKeyDown={(event) => {
                    if (
                      event.key ===
                        "Enter" ||
                      event.key ===
                        " "
                    ) {
                      event.preventDefault();
                      handleSelect(item);
                    }
                  }}
                  tabIndex={0}
                  className="border-b border-border-subtle last:border-0 hover:bg-bg-hover/30 focus:bg-bg-hover/30 focus:outline-none transition-colors cursor-pointer group"
                >

                  {/* Research */}
                  <td className="px-5 py-3">
                    <div className="flex items-center gap-3">

                      <TickerLogo
                        name={name}
                        color={
                          item.logoColor ??
                          undefined
                        }
                        size={28}
                      />

                      <div>
                        <div className="text-sm text-text-primary">
                          {name}
                        </div>

                        <div className="font-mono text-[11px] text-text-faint">
                          {item.exchange
                            ? `${item.exchange}:`
                            : ""}
                          {ticker}
                        </div>

                        {item.title &&
                          item.title !==
                            name && (
                            <div className="text-[11px] text-text-faint mt-0.5">
                              {item.title}
                            </div>
                          )}
                      </div>
                    </div>
                  </td>

                  {/* Sector */}
                  <td className="px-4 py-3">
                    <span className="text-xs text-text-muted">
                      {sector}
                    </span>
                  </td>

                  {/* Recommendation */}
                  <td className="px-4 py-3">
                    {recommendation ? (
                      <RecommendationBadge
                        value={
                          recommendation
                        }
                      />
                    ) : (
                      <span className="text-xs text-text-faint">
                        —
                      </span>
                    )}
                  </td>

                  {/* Price */}
                  <td className="px-4 py-3 text-right">
                    <span className="font-mono text-xs text-text-secondary tabular-nums">
                      {currentPrice !==
                      null
                        ? `$${currentPrice.toFixed(
                            2,
                          )}`
                        : "—"}
                    </span>
                  </td>

                  {/* Fair Value */}
                  <td className="px-4 py-3 text-right">
                    <span className="font-mono text-xs text-text-secondary tabular-nums">
                      {fairValue !==
                      null
                        ? `$${fairValue.toFixed(
                            2,
                          )}`
                        : "—"}
                    </span>
                  </td>

                  {/* Confidence */}
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <ProgressBar
                        value={
                          confidence
                        }
                        className="w-12"
                      />

                      <span className="font-mono text-[11px] text-text-muted">
                        {confidence
                          ? `${confidence.toFixed(
                              0,
                            )}%`
                          : "—"}
                      </span>
                    </div>
                  </td>

                  {/* Actions */}
                  <td className="px-5 py-3 text-right">
                    <div className="flex items-center justify-end gap-2">

                      {/* Remove */}
                      <button
                        type="button"
                        onClick={(event) =>
                          handleRemove(
                            event,
                            item.id,
                          )
                        }
                        disabled={
                          removingId ===
                          item.id
                        }
                        className="p-1.5 rounded text-text-faint hover:text-danger hover:bg-bg-elevated opacity-0 group-hover:opacity-100 focus:opacity-100 transition-all disabled:opacity-50"
                        aria-label={`Remove ${name} from library`}
                        title={`Remove ${name} from library`}
                      >
                        {removingId ===
                        item.id ? (
                          <Loader2 className="w-3.5 h-3.5 animate-spin" />
                        ) : (
                          <Trash2 className="w-3.5 h-3.5" />
                        )}
                      </button>

                      {/* Open Research */}
                      <button
                        type="button"
                        onClick={(event) =>
                          handleArrowClick(
                            event,
                            item,
                          )
                        }
                        disabled={
                          !researchId &&
                          !item.companyId &&
                          !item.id
                        }
                        className="p-1.5 rounded-md text-text-faint hover:text-text-primary hover:bg-bg-elevated focus:outline-none focus:ring-2 focus:ring-primary transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
                        aria-label={`Open ${name} research workspace`}
                        title="Open research workspace"
                      >
                        <ArrowRight className="w-4 h-4" />
                      </button>

                    </div>
                  </td>

                </tr>
              );
            })}
          </tbody>
        </table>
      )}

    </div>
  </div>
</div>


);
}
