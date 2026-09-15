import type {
  SaveArtifactRequest,
  SaveArtifactResponse,
  SavedArtifact,
  SaveDestination,
} from "@/types/savedArtifact";

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
const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  "http://127.0.0.1:8000";

/**
 * Normalize backend URL.
 */
const normalizedApiBaseUrl =
  API_BASE_URL
    .replace(/\/+$/, "")
    .replace(/\/api$/, "");

/**
 * Build complete backend URL.
 */
function buildUrl(path: string): string {
  const normalizedPath =
    path.startsWith("/")
      ? path
      : `/${path}`;

  return `${normalizedApiBaseUrl}${normalizedPath}`;
}

interface SavedArtifactListResponse {
  items: SavedArtifact[];
  total: number;
}

interface FastAPIValidationError {
  loc?: Array<string | number>;
  msg?: string;
  type?: string;
  input?: unknown;
}

interface FastAPIErrorResponse {
  detail?:
    | string
    | FastAPIValidationError[]
    | unknown;
  message?: string;
}

/**
 * Runtime-compatible save payload.
 *
 * Research IDs are intentionally string-compatible because
 * the research backend uses UUID identifiers.
 */
type SaveArtifactPayload =
  Partial<SaveArtifactRequest> & {
    researchId?: string | number;
    research_id?: string | number;
    destination?:
      | SaveDestination
      | string;
    title?: string;
    description?: string;
  };

/**
 * Payload accepted by saveResearch().
 */
interface SaveResearchPayload {
  researchId?: string | number;
  research_id?: string | number;
  destination:
    | SaveDestination
    | string;
  title?: string;
  description?: string;
}

/**
 * Convert FastAPI errors into a useful message.
 */
function formatApiError(
  body: FastAPIErrorResponse | null,
  status: number,
): string {
  const fallback =
    `Request failed with status ${status}`;

  if (!body) {
    return fallback;
  }

  if (
    typeof body.detail ===
    "string"
  ) {
    return body.detail;
  }

  if (
    Array.isArray(
      body.detail,
    )
  ) {
    const validationMessages =
      body.detail
        .map((error) => {
          if (
            error &&
            typeof error ===
              "object"
          ) {
            const validationError =
              error as FastAPIValidationError;

            const location =
              validationError.loc
                ?.map(String)
                .join(".");

            const message =
              validationError.msg ??
              "Validation error";

            return location
              ? `${location}: ${message}`
              : message;
          }

          return String(error);
        })
        .filter(Boolean);

    if (
      validationMessages.length >
      0
    ) {
      return validationMessages.join(
        "; ",
      );
    }
  }

  if (
    typeof body.message ===
      "string" &&
    body.message.trim()
  ) {
    return body.message;
  }

  return fallback;
}

/**
 * Generic API request helper.
 */
async function request<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  const url =
    buildUrl(path);

  console.log(
    "[savedArtifactsApi] REQUEST",
    {
      method:
        options?.method ??
        "GET",
      path,
      url,
      body:
        options?.body,
    },
  );

  let response: Response;

  try {
    response =
      await fetch(
        url,
        {
          ...options,

          headers: {
            Accept:
              "application/json",

            "Content-Type":
              "application/json",

            ...(options?.headers ??
              {}),
          },
        },
      );
  } catch (error) {
    console.error(
      "[savedArtifactsApi] NETWORK ERROR",
      {
        method:
          options?.method ??
          "GET",
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

  console.log(
    "[savedArtifactsApi] RESPONSE",
    {
      method:
        options?.method ??
        "GET",
      url,
      status:
        response.status,
      statusText:
        response.statusText,
    },
  );

  if (!response.ok) {
    let errorBody:
      | FastAPIErrorResponse
      | null = null;

    try {
      errorBody =
        (await response.json()) as FastAPIErrorResponse;
    } catch {
      // Non-JSON response.
    }

    console.error(
      "[savedArtifactsApi] API ERROR",
      {
        status:
          response.status,
        statusText:
          response.statusText,
        url,
        body:
          errorBody,
      },
    );

    throw new Error(
      formatApiError(
        errorBody,
        response.status,
      ),
    );
  }

  /**
   * DELETE endpoints may return 204.
   */
  if (
    response.status ===
    204
  ) {
    return undefined as T;
  }

  const contentType =
    response.headers.get(
      "content-type",
    );

  if (
    !contentType ||
    !contentType.includes(
      "application/json",
    )
  ) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

/**
 * Normalize destination names.
 */
function normalizeDestination(
  destination: string,
): SaveDestination {
  const normalized =
    destination
      .trim()
      .toLowerCase();

  switch (normalized) {
    case "library":
    case "saved":
      return "library" as SaveDestination;

    case "research":
      return "research" as SaveDestination;

    case "report":
    case "reports":
      return "reports" as SaveDestination;

    case "favorite":
    case "favorites":
      return "library" as SaveDestination;

    default:
      throw new Error(
        `Invalid save destination: ${destination}. ` +
          "Expected library, research, or reports.",
      );
  }
}

/**
 * Normalize a research ID.
 *
 * IMPORTANT:
 *
 * Research IDs are not assumed to be numeric.
 *
 * UUID:
 *
 * 8f9de065-ea11-453d-b703-22c9e4758ac4
 *
 * is preserved exactly.
 */
function normalizeResearchId(
  value: unknown,
): string {
  if (
    typeof value ===
    "number"
  ) {
    if (
      !Number.isSafeInteger(
        value,
      ) ||
      value <= 0
    ) {
      throw new Error(
        "Research ID is invalid.",
      );
    }

    return String(value);
  }

  if (
    typeof value ===
    "string"
  ) {
    const normalized =
      value.trim();

    if (!normalized) {
      throw new Error(
        "Research ID is required.",
      );
    }

    return normalized;
  }

  throw new Error(
    "Research ID is required.",
  );
}

/**
 * Convert any supported payload into the canonical
 * FastAPI request body.
 *
 * IMPORTANT:
 *
 * SaveArtifactRequest must support a string research_id
 * if the backend research primary key is UUID.
 */
function normalizeSaveArtifactPayload(
  payload: SaveArtifactPayload,
): SaveArtifactRequest {
  const rawResearchId =
    payload.research_id ??
    payload.researchId;

  const normalizedResearchId =
    normalizeResearchId(
      rawResearchId,
    );

  if (
    !payload.destination
  ) {
    throw new Error(
      "Save destination is required.",
    );
  }

  if (
    !payload.title?.trim()
  ) {
    throw new Error(
      "Artifact title is required.",
    );
  }

  return {
    research_id:
      normalizedResearchId,

    destination:
      normalizeDestination(
        String(
          payload.destination,
        ),
      ),

    title:
      payload.title.trim(),

    description:
      payload.description?.trim() ??
      "",
  } as SaveArtifactRequest;
}

/**
 * Saved Artifacts API.
 *
 * Backend:
 *
 * POST   /api/saved-artifacts
 * GET    /api/saved-artifacts
 * GET    /api/saved-artifacts/{artifact_id}
 * DELETE /api/saved-artifacts/{artifact_id}
 */
const savedArtifactsApi = {
  /**
   * Canonical create method.
   */
  async create(
    payload: SaveArtifactPayload,
  ): Promise<SaveArtifactResponse> {
    const normalizedPayload =
      normalizeSaveArtifactPayload(
        payload,
      );

    console.log(
      "[savedArtifactsApi] CREATE ARTIFACT",
      {
        originalPayload:
          payload,

        normalizedPayload,
      },
    );

    return request<SaveArtifactResponse>(
      "/api/saved-artifacts",
      {
        method: "POST",

        body:
          JSON.stringify(
            normalizedPayload,
          ),
      },
    );
  },

  /**
   * Save research.
   *
   * Supports both UUID and numeric research IDs.
   */
  async saveResearch(
    payload: SaveResearchPayload,
  ): Promise<SaveArtifactResponse> {
    const researchId =
      payload.research_id ??
      payload.researchId;

    const title =
      payload.title?.trim() ||
      "Equity Research";

    const description =
      payload.description?.trim() ||
      "Saved research artifact.";

    return this.create({
      research_id:
        researchId,

      destination:
        normalizeDestination(
          String(
            payload.destination,
          ),
        ),

      title,

      description,
    });
  },

  /**
   * List saved artifacts.
   *
   * Supports UUID or numeric research IDs.
   */
  async list(
    destination?: SaveDestination,
    researchId?: string | number,
  ): Promise<SavedArtifact[]> {
    const params =
      new URLSearchParams();

    if (destination) {
      params.set(
        "destination",
        String(destination),
      );
    }

    if (
      researchId !==
      undefined
    ) {
      const normalizedResearchId =
        normalizeResearchId(
          researchId,
        );

      params.set(
        "research_id",
        normalizedResearchId,
      );
    }

    const queryString =
      params.toString();

    const response =
      await request<SavedArtifactListResponse>(
        `/api/saved-artifacts${
          queryString
            ? `?${queryString}`
            : ""
        }`,
      );

    return response.items;
  },

  /**
   * Get one saved artifact.
   */
  async get(
    artifactId: string,
  ): Promise<SavedArtifact> {
    return request<SavedArtifact>(
      `/api/saved-artifacts/${encodeURIComponent(
        artifactId,
      )}`,
    );
  },

  /**
   * Delete one saved artifact.
   */
  async remove(
    artifactId: string,
  ): Promise<void> {
    await request<void>(
      `/api/saved-artifacts/${encodeURIComponent(
        artifactId,
      )}`,
      {
        method:
          "DELETE",
      },
    );
  },
};

export default savedArtifactsApi;