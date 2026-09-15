
import type {
  ApiCompanySearchResult,
  ApiResearchResult,
  ResearchStatusResponse,
  StartResearchRequest,
  StartResearchResponse,
} from "@/types";

/**
 * Canonical FastAPI backend URL.
 *
 * Supported:
 *
 * NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
 *
 * or:
 *
 * NEXT_PUBLIC_API_URL=http://127.0.0.1:8000/api
 */
const RAW_API_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  "http://127.0.0.1:8000";

/**
 * Normalize the backend origin.
 *
 * This prevents:
 *
 * http://127.0.0.1:8000/api/api/...
 *
 * when NEXT_PUBLIC_API_URL already contains /api.
 */
const API_ORIGIN = RAW_API_URL
  .replace(/\/+$/, "")
  .replace(/\/api$/, "");

/**
 * Build a canonical API URL.
 */
function buildApiUrl(path: string): string {
  const normalizedPath = path.startsWith("/")
    ? path
    : `/${path}`;

  return `${API_ORIGIN}/api${normalizedPath}`;
}

/**
 * Convert FastAPI errors into useful messages.
 */
async function getErrorMessage(
  response: Response,
  fallback: string,
): Promise<string> {
  try {
    const data: unknown = await response.json();

    if (
      data &&
      typeof data === "object" &&
      !Array.isArray(data)
    ) {
      const body = data as {
        detail?: unknown;
        message?: unknown;
        error?: unknown;
      };

      if (
        typeof body.detail === "string" &&
        body.detail.trim()
      ) {
        return body.detail;
      }

      if (
        Array.isArray(body.detail)
      ) {
        const details = body.detail
          .map((item) => {
            if (
              item &&
              typeof item === "object" &&
              !Array.isArray(item)
            ) {
              const error =
                item as {
                  loc?: unknown;
                  msg?: unknown;
                };

              const location =
                Array.isArray(error.loc)
                  ? error.loc.join(".")
                  : "";

              const message =
                typeof error.msg === "string"
                  ? error.msg
                  : "Validation error";

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
        return body.message;
      }

      if (
        typeof body.error === "string" &&
        body.error.trim()
      ) {
        return body.error;
      }
    }
  } catch {
    // Response was not JSON.
  }

  return fallback;
}

/**
 * Validate and encode a research ID.
 */
function assertResearchId(
  researchId: string | number,
): string {
  const id = String(researchId).trim();

  if (!id) {
    throw new Error("Research ID is required");
  }

  return encodeURIComponent(id);
}

// =====================================================
// Company Search
// =====================================================

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
    Math.max(1, limit),
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
        `Company search failed (${response.status})`,
      ),
    );
  }

  const data: unknown = await response.json();

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

// =====================================================
// Start Research
// =====================================================

export async function startResearch(
  payload: StartResearchRequest,
): Promise<StartResearchResponse> {
  const response = await fetch(
    buildApiUrl("/research/start"),
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      cache: "no-store",
      body: JSON.stringify(payload),
    },
  );

  if (!response.ok) {
    throw new Error(
      await getErrorMessage(
        response,
        `Research start failed (${response.status})`,
      ),
    );
  }

  return response.json();
}

// =====================================================
// Research Status
// =====================================================

export async function getResearchStatus(
  researchId: string | number,
): Promise<ResearchStatusResponse> {
  const id = assertResearchId(researchId);

  const response = await fetch(
    buildApiUrl(
      `/research/status/${id}`,
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
        `Failed to fetch research status (${response.status})`,
      ),
    );
  }

  return response.json();
}

// =====================================================
// Research Result
// =====================================================

/**
 * Fetch the persisted research result.
 *
 * GET /api/research/{id}/results
 */
export async function getResearch(
  researchId: string | number,
): Promise<ApiResearchResult> {
  const id = assertResearchId(researchId);

  const response = await fetch(
    buildApiUrl(
      `/research/${id}/results`,
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
        `Failed to load research results (${response.status})`,
      ),
    );
  }

  return response.json();
}



