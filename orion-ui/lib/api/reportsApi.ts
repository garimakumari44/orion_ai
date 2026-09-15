import type {
  SavedReport,
  ReportsListResponse,
} from "@/types/report";

/**
 * Canonical FastAPI backend URL.
 *
 * Supports:
 *
 * NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
 *
 * or:
 *
 * NEXT_PUBLIC_API_URL=http://127.0.0.1:8000/api
 */
const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  "http://127.0.0.1:8000";

/**
 * Normalize:
 *
 * http://127.0.0.1:8000
 *
 * and:
 *
 * http://127.0.0.1:8000/api
 *
 * into the same backend origin.
 */
const normalizedApiBaseUrl = API_BASE_URL
  .replace(/\/+$/, "")
  .replace(/\/api$/, "");

/**
 * Build an absolute FastAPI URL.
 */
function buildUrl(path: string): string {
  const normalizedPath = path.startsWith("/")
    ? path
    : `/${path}`;

  return `${normalizedApiBaseUrl}${normalizedPath}`;
}

interface FastAPIErrorResponse {
  detail?: unknown;
  message?: unknown;
  error?: unknown;
}

async function readResponseBody(
  response: Response,
): Promise<unknown> {
  const contentType =
    response.headers.get("content-type") ?? "";

  if (
    contentType
      .toLowerCase()
      .includes("application/json")
  ) {
    try {
      return await response.json();
    } catch {
      return null;
    }
  }

  try {
    return await response.text();
  } catch {
    return null;
  }
}

function extractErrorMessage(
  body: unknown,
  status: number,
  statusText: string,
): string {
  if (
    body &&
    typeof body === "object" &&
    !Array.isArray(body)
  ) {
    const errorBody =
      body as FastAPIErrorResponse;

    if (
      typeof errorBody.detail === "string" &&
      errorBody.detail.trim()
    ) {
      return errorBody.detail;
    }

    if (
      typeof errorBody.message === "string" &&
      errorBody.message.trim()
    ) {
      return errorBody.message;
    }

    if (
      typeof errorBody.error === "string" &&
      errorBody.error.trim()
    ) {
      return errorBody.error;
    }

    if (Array.isArray(errorBody.detail)) {
      const details = errorBody.detail
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
                : null;

            const location =
              Array.isArray(record.loc)
                ? record.loc.join(".")
                : null;

            if (message && location) {
              return `${location}: ${message}`;
            }

            return message;
          }

          return String(item);
        })
        .filter(Boolean)
        .join("; ");

      if (details) {
        return details;
      }
    }
  }

  if (typeof body === "string") {
    const trimmed = body.trim();

    if (trimmed) {
      return trimmed.slice(0, 500);
    }
  }

  return `Request failed with status ${status}${
    statusText
      ? ` (${statusText})`
      : ""
  }`;
}

async function request<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  const url = buildUrl(path);

  const method =
    options?.method ?? "GET";

  console.log("[reportsApi] REQUEST", {
    method,
    path,
    url,
  });

  let response: Response;

  try {
    response = await fetch(url, {
      ...options,
      cache: "no-store",
      headers: {
        Accept: "application/json",
        ...(options?.body
          ? {
              "Content-Type":
                "application/json",
            }
          : {}),
        ...(options?.headers ?? {}),
      },
    });
  } catch (error) {
    console.error(
      "[reportsApi] NETWORK ERROR",
      {
        method,
        path,
        url,
        error,
      },
    );

    throw new Error(
      `Unable to reach the Orion backend at ${url}. ` +
        "Make sure FastAPI is running on port 8000.",
    );
  }

  console.log("[reportsApi] RESPONSE", {
    method,
    url,
    status: response.status,
    statusText: response.statusText,
  });

  if (!response.ok) {
    const body =
      await readResponseBody(response);

    const message =
      extractErrorMessage(
        body,
        response.status,
        response.statusText,
      );

    console.error(
      "[reportsApi] API ERROR",
      {
        method,
        status: response.status,
        statusText: response.statusText,
        url,
        message,
        responseBody: body,
      },
    );

    throw new Error(message);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  const body =
    await readResponseBody(response);

  return body as T;
}

function normalizeReport(
  report: SavedReport,
): SavedReport {
  return {
    ...report,
    destination: "reports",
  };
}

const reportsApi = {
  async list(
    search?: string,
  ): Promise<SavedReport[]> {
    const query = search?.trim()
      ? `?search=${encodeURIComponent(
          search.trim(),
        )}`
      : "";

    const response =
      await request<
        SavedReport[] | ReportsListResponse
      >(`/api/reports${query}`);

    if (Array.isArray(response)) {
      return response.map(normalizeReport);
    }

    return response.items.map(
      normalizeReport,
    );
  },

  async get(
    id: string,
  ): Promise<SavedReport> {
    const response =
      await request<SavedReport>(
        `/api/reports/${encodeURIComponent(id)}`,
      );

    return normalizeReport(response);
  },

  async remove(
    id: string,
  ): Promise<void> {
    await request<void>(
      `/api/reports/${encodeURIComponent(id)}`,
      {
        method: "DELETE",
      },
    );
  },
};

export default reportsApi;