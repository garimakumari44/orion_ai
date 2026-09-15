import {
  startResearch,
  getResearch,
  getResearchStatus,
} from "@/lib/api/research";

import type {
  StartResearchRequest,
  ResearchStatusResponse,
  ApiResearchResult,
} from "@/types";

// ============================================================
// Constants
// ============================================================

const DEFAULT_POLL_INTERVAL = 3000;

const TERMINAL_STATUSES = new Set([
  "completed",
  "complete",
  "failed",
  "cancelled",
  "error",
]);

// ============================================================
// Helpers
// ============================================================

function normalizeStatus(
  value: unknown,
): string {
  return String(value ?? "")
    .trim()
    .toLowerCase();
}

function isTerminalStatus(
  value: unknown,
): boolean {
  return TERMINAL_STATUSES.has(
    normalizeStatus(value),
  );
}

function isSuccessfulStatus(
  value: unknown,
): boolean {
  const status =
    normalizeStatus(value);

  return (
    status === "completed" ||
    status === "complete"
  );
}

function wait(
  milliseconds: number,
  signal?: AbortSignal,
): Promise<void> {
  return new Promise(
    (resolve, reject) => {
      if (signal?.aborted) {
        reject(
          new DOMException(
            "Research was cancelled",
            "AbortError",
          ),
        );

        return;
      }

      const timer =
        window.setTimeout(
          resolve,
          milliseconds,
        );

      const handleAbort = () => {
        window.clearTimeout(timer);

        reject(
          new DOMException(
            "Research was cancelled",
            "AbortError",
          ),
        );
      };

      signal?.addEventListener(
        "abort",
        handleAbort,
        {
          once: true,
        },
      );
    },
  );
}

// ============================================================
// Research Service
// ============================================================

/**
 * Client-side orchestration service for research workflows.
 *
 * This service intentionally does NOT contain research
 * business logic.
 *
 * Backend remains responsible for:
 *
 * - Research planning
 * - Agent orchestration
 * - Retrieval
 * - Evidence collection
 * - Analysis
 * - Verification
 * - Report generation
 *
 * Frontend responsibilities:
 *
 * - Start research
 * - Read research
 * - Read execution status
 * - Poll while running
 */
export const researchService = {
  // ==========================================================
  // Start
  // ==========================================================

  async start(
    request: StartResearchRequest,
  ): Promise<string> {
    const response =
      await startResearch(request);

    /*
     * Current backend response may expose the ID in
     * either:
     *
     *   response.research.id
     *
     * or directly as:
     *
     *   response.id
     *
     * Support both shapes.
     */
    const nestedId =
      response?.research?.id;

    const directId =
      (
        response as {
          id?: string | number;
        }
      )?.id;

    const researchId =
      nestedId ??
      directId;

    if (
      researchId === undefined ||
      researchId === null ||
      String(researchId).trim() === ""
    ) {
      throw new Error(
        "Research start response did not contain a research ID",
      );
    }

    return String(researchId);
  },

  // ==========================================================
  // Get Research
  // ==========================================================

  async get(
    researchId: string,
  ): Promise<ApiResearchResult> {
    if (!researchId?.trim()) {
      throw new Error(
        "Research ID is required",
      );
    }

    return getResearch(
      researchId,
    );
  },

  // ==========================================================
  // Get Status
  // ==========================================================

  async getStatus(
    researchId: string,
  ): Promise<ResearchStatusResponse> {
    if (!researchId?.trim()) {
      throw new Error(
        "Research ID is required",
      );
    }

    return getResearchStatus(
      researchId,
    );
  },

  // ==========================================================
  // Run
  // ==========================================================

  /**
   * Start a research workflow and wait until it reaches
   * a terminal state.
   */
  async run(
    request: StartResearchRequest,
    options?: {
      interval?: number;
      signal?: AbortSignal;
      onStatus?: (
        status: ResearchStatusResponse,
      ) => void;
    },
  ): Promise<ApiResearchResult> {
    const interval =
      Math.max(
        500,
        options?.interval ??
          DEFAULT_POLL_INTERVAL,
      );

    // --------------------------------------------------------
    // Start
    // --------------------------------------------------------

    const researchId =
      await this.start(request);

    // --------------------------------------------------------
    // Poll
    // --------------------------------------------------------

    while (true) {
      // ------------------------------------------------------
      // Cancellation
      // ------------------------------------------------------

      if (
        options?.signal?.aborted
      ) {
        throw new DOMException(
          "Research was cancelled",
          "AbortError",
        );
      }

      // ------------------------------------------------------
      // Fetch status
      // ------------------------------------------------------

      const status =
        await this.getStatus(
          researchId,
        );

      options?.onStatus?.(
        status,
      );

      const normalized =
        normalizeStatus(
          status?.status,
        );

      // ------------------------------------------------------
      // Terminal state
      // ------------------------------------------------------

      if (
        isTerminalStatus(
          normalized,
        )
      ) {
        if (
          !isSuccessfulStatus(
            normalized,
          )
        ) {
          throw new Error(
            `Research ${normalized}`,
          );
        }

        /*
         * IMPORTANT:
         *
         * Always make one final request to:
         *
         *   GET /api/research/{id}
         *
         * after status becomes completed.
         *
         * This guarantees that the frontend receives
         * the persisted research results rather than
         * relying on the status response alone.
         */
        return this.get(
          researchId,
        );
      }

      // ------------------------------------------------------
      // Wait
      // ------------------------------------------------------

      await wait(
        interval,
        options?.signal,
      );
    }
  },
};