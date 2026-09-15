import type {
  ApiCompanySearchResult,
  ApiResearchResult,
  ResearchStatusResponse,
  StartResearchRequest,
  StartResearchResponse,
} from "@/types";

/**
 * ============================================================
 * Research API Client
 * ============================================================
 *
 * Canonical backend:
 *
 *   http://127.0.0.1:8000
 *
 * Supported environment values:
 *
 *   NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
 *
 * or:
 *
 *   NEXT_PUBLIC_API_URL=http://127.0.0.1:8000/api
 *
 * All endpoints are normalized to:
 *
 *   /api/...
 *
 * ============================================================
 */

// ------------------------------------------------------------
// API origin
// ------------------------------------------------------------

const RAW_API_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  "http://127.0.0.1:8000";

const API_ORIGIN = RAW_API_URL
  .replace(/\/+$/, "")
  .replace(/\/api$/, "");

// ------------------------------------------------------------
// URL builder
// ------------------------------------------------------------

function buildApiUrl(path: string): string {
  const normalizedPath = path.startsWith("/")
    ? path
    : `/${path}`;

  return `${API_ORIGIN}/api${normalizedPath}`;
}

// ------------------------------------------------------------
// Error handling
// ------------------------------------------------------------

async function getErrorMessage(
  response: Response,
  fallback: string,
): Promise<string> {
  try {
    const data: unknown = await response.json();

    if (
      !data ||
      typeof data !== "object" ||
      Array.isArray(data)
    ) {
      return fallback;
    }

    const body = data as {
      detail?: unknown;
      message?: unknown;
      error?: unknown;
    };

    // FastAPI string detail
    if (
      typeof body.detail === "string" &&
      body.detail.trim()
    ) {
      return body.detail.trim();
    }

    // FastAPI validation errors
    if (Array.isArray(body.detail)) {
      const details = body.detail
        .map((item) => {
          if (
            item &&
            typeof item === "object" &&
            !Array.isArray(item)
          ) {
            const record =
              item as Record<string, unknown>;

            const message =
              typeof record.msg === "string"
                ? record.msg
                : "Validation error";

            const location =
              Array.isArray(record.loc)
                ? record.loc
                    .map(String)
                    .join(".")
                : "";

            return location
              ? `${location}: ${message}`
              : message;
          }

          return String(item);
        })
        .filter(Boolean)
        .join("; ");

      if (details) {
        return details;
      }
    }

    if (
      typeof body.message === "string" &&
      body.message.trim()
    ) {
      return body.message.trim();
    }

    if (
      typeof body.error === "string" &&
      body.error.trim()
    ) {
      return body.error.trim();
    }
  } catch {
    // Non-JSON response.
  }

  return fallback;
}

// ------------------------------------------------------------
// Research ID validation
// ------------------------------------------------------------

function assertResearchId(
  researchId: string | number,
): string {
  const id = String(researchId).trim();

  if (!id) {
    throw new Error("Research ID is required.");
  }

  return encodeURIComponent(id);
}

// ============================================================
// Company Search
// ============================================================

export async function searchCompanies(
  query: string,
  limit = 10,
): Promise<ApiCompanySearchResult[]> {
  const normalizedQuery = query.trim();

  if (!normalizedQuery) {
    return [];
  }

  const safeLimit = Math.min(
    50,
    Math.max(1, Math.floor(limit)),
  );

  const response = await fetch(
    buildApiUrl(
      `/research/companies/search?q=${encodeURIComponent(
        normalizedQuery,
      )}&limit=${safeLimit}`,
    ),
    {
      method: "GET",
      cache: "no-store",
      headers: {
        Accept: "application/json",
      },
    },
  );

  if (!response.ok) {
    throw new Error(
      await getErrorMessage(
        response,
        `Company search failed (${response.status}).`,
      ),
    );
  }

  const data: unknown =
    await response.json();

  if (
    !data ||
    typeof data !== "object" ||
    Array.isArray(data)
  ) {
    return [];
  }

  const body = data as {
    results?: unknown;
  };

  return Array.isArray(body.results)
    ? (body.results as ApiCompanySearchResult[])
    : [];
}

// ============================================================
// Start Research
// ============================================================

export async function startResearch(
  payload: StartResearchRequest,
): Promise<StartResearchResponse> {
  const response = await fetch(
    buildApiUrl("/research/start"),
    {
      method: "POST",
      cache: "no-store",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify(payload),
    },
  );

  if (!response.ok) {
    throw new Error(
      await getErrorMessage(
        response,
        `Research start failed (${response.status}).`,
      ),
    );
  }

  return response.json();
}

// ============================================================
// Research Status
// ============================================================

export async function getResearchStatus(
  researchId: string | number,
): Promise<ResearchStatusResponse> {
  const id = assertResearchId(researchId);

  const response = await fetch(
    buildApiUrl(`/research/status/${id}`),
    {
      method: "GET",
      cache: "no-store",
      headers: {
        Accept: "application/json",
      },
    },
  );

  if (!response.ok) {
    throw new Error(
      await getErrorMessage(
        response,
        `Failed to fetch research status (${response.status}).`,
      ),
    );
  }

  return response.json();
}

// ============================================================
// Research Result
// ============================================================

/**
 * Fetch the persisted research result.
 *
 * GET /api/research/{research_id}/results
 *
 * This function intentionally returns the backend response
 * without transforming it.
 *
 * Transformation belongs to ResearchPage because that is the
 * boundary between the API contract and the UI contract.
 */
export async function getResearch(
  researchId: string | number,
): Promise<ApiResearchResult> {
  const id = assertResearchId(researchId);

  const response = await fetch(
    buildApiUrl(`/research/${id}/results`),
    {
      method: "GET",
      cache: "no-store",
      headers: {
        Accept: "application/json",
      },
    },
  );

  if (!response.ok) {
    throw new Error(
      await getErrorMessage(
        response,
        `Failed to load research results (${response.status}).`,
      ),
    );
  }

  return response.json();
}