import type {
  LibraryItem,
  LibraryListResponse,
} from "@/types/library";

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
 * Normalize the base URL.
 *
 * We always add `/api` explicitly in endpoint paths.
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

interface GenericListResponse {
  items?: unknown;
  data?: unknown;
  results?: unknown;
}

type RawLibraryItem =
  Partial<LibraryItem> &
  Record<string, unknown>;

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

  console.log("[libraryApi] REQUEST", {
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
      "[libraryApi] NETWORK ERROR",
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

  console.log("[libraryApi] RESPONSE", {
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
      "[libraryApi] API ERROR",
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

/**
 * Read a field from either camelCase or snake_case.
 */
function readField<T>(
  item: RawLibraryItem,
  camelCase: string,
  snakeCase: string,
): T | undefined {
  const camelValue =
    item[camelCase];

  if (
    camelValue !== undefined &&
    camelValue !== null
  ) {
    return camelValue as T;
  }

  const snakeValue =
    item[snakeCase];

  if (
    snakeValue !== undefined &&
    snakeValue !== null
  ) {
    return snakeValue as T;
  }

  return undefined;
}

/**
 * Normalize backend Library records.
 *
 * FastAPI/Pydantic responses may use snake_case
 * while the frontend uses camelCase.
 *
 * We explicitly normalize both forms here so
 * the rest of the frontend has one canonical shape.
 */
function normalizeLibraryItem(
  raw: LibraryItem | RawLibraryItem,
): LibraryItem {
  const item =
    raw as RawLibraryItem;

  return {
    ...(item as LibraryItem),

    id:
      readField<string>(
        item,
        "id",
        "id",
      ) ?? "",

    researchId:
      readField<string>(
        item,
        "researchId",
        "research_id",
      ),

    companyId:
      readField<string>(
        item,
        "companyId",
        "company_id",
      ),

    companyName:
      readField<string>(
        item,
        "companyName",
        "company_name",
      ),

    ticker:
      readField<string>(
        item,
        "ticker",
        "ticker",
      ),

    title:
      readField<string>(
        item,
        "title",
        "title",
      ),

    description:
      readField<string>(
        item,
        "description",
        "description",
      ),

    sector:
      readField<string>(
        item,
        "sector",
        "sector",
      ),

    exchange:
      readField<string>(
        item,
        "exchange",
        "exchange",
      ),

    recommendation:
      readField<string>(
        item,
        "recommendation",
        "recommendation",
      ),

    confidence:
      readField<number>(
        item,
        "confidence",
        "confidence",
      ),

    currentPrice:
      readField<number>(
        item,
        "currentPrice",
        "current_price",
      ),

    fairValue:
      readField<number>(
        item,
        "fairValue",
        "fair_value",
      ),

    logoColor:
      readField<string>(
        item,
        "logoColor",
        "logo_color",
      ),

    createdAt:
      readField<string>(
        item,
        "createdAt",
        "created_at",
      ),

    updatedAt:
      readField<string>(
        item,
        "updatedAt",
        "updated_at",
      ),

    destination: "library",
  };
}

function extractLibraryItems(
  response:
    | LibraryItem[]
    | LibraryListResponse
    | GenericListResponse
    | null
    | undefined,
): LibraryItem[] {
  if (Array.isArray(response)) {
    return response.map(
      normalizeLibraryItem,
    );
  }

  if (
    !response ||
    typeof response !== "object"
  ) {
    return [];
  }

  const objectResponse =
    response as GenericListResponse;

  if (Array.isArray(objectResponse.items)) {
    return objectResponse.items.map(
      (item) =>
        normalizeLibraryItem(
          item as RawLibraryItem,
        ),
    );
  }

  if (Array.isArray(objectResponse.data)) {
    return objectResponse.data.map(
      (item) =>
        normalizeLibraryItem(
          item as RawLibraryItem,
        ),
    );
  }

  if (
    Array.isArray(objectResponse.results)
  ) {
    return objectResponse.results.map(
      (item) =>
        normalizeLibraryItem(
          item as RawLibraryItem,
        ),
    );
  }

  console.warn(
    "[libraryApi] Unexpected list response shape",
    response,
  );

  return [];
}

const libraryApi = {
  async list(
    search?: string,
  ): Promise<LibraryItem[]> {
    const query = search?.trim()
      ? `?search=${encodeURIComponent(
          search.trim(),
        )}`
      : "";

    const response =
      await request<
        | LibraryItem[]
        | LibraryListResponse
        | GenericListResponse
      >(`/api/library${query}`);

    const items =
      extractLibraryItems(response);

    console.log(
      "[libraryApi] NORMALIZED LIBRARY ITEMS",
      items.map((item) => ({
        id: item.id,
        researchId: item.researchId,
        companyId: item.companyId,
        title: item.title,
      })),
    );

    return items;
  },

  async get(
    id: string,
  ): Promise<LibraryItem> {
    const response =
      await request<
        LibraryItem | RawLibraryItem
      >(
        `/api/library/${encodeURIComponent(id)}`,
      );

    if (
      !response ||
      typeof response !== "object" ||
      Array.isArray(response)
    ) {
      throw new Error(
        "Library API returned an invalid library item.",
      );
    }

    return normalizeLibraryItem(
      response as RawLibraryItem,
    );
  },

  async remove(
    id: string,
  ): Promise<void> {
    await request<void>(
      `/api/library/${encodeURIComponent(id)}`,
      {
        method: "DELETE",
      },
    );
  },
};

export default libraryApi;