"use client";

import {
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";

import { getResearch } from "@/lib/api/research";
import { mapApiResearchResult } from "@/types/mappers";

import type { ResearchResult } from "@/models/research";

// ============================================================
// Types
// ============================================================

interface UseResearchResultsReturn {
  data: ResearchResult | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

// ============================================================
// Status Helpers
// ============================================================

const TERMINAL_STATUSES =
  new Set([
    "completed",
    "complete",
    "success",
    "succeeded",
    "failed",
    "cancelled",
    "canceled",
    "error",
  ]);

function normalizeStatus(
  value: unknown,
): string {
  return String(value ?? "")
    .trim()
    .toLowerCase()
    .replace(/_/g, "-");
}

function isTerminalStatus(
  value: unknown,
): boolean {
  return TERMINAL_STATUSES.has(
    normalizeStatus(value),
  );
}

// ============================================================
// Hook
// ============================================================

export function useResearchResults(
  researchId: string | null,
  _progress?: number,
): UseResearchResultsReturn {
  const [data, setData] =
    useState<ResearchResult | null>(
      null,
    );

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState<string | null>(
      null,
    );

  const requestInFlight =
    useRef(false);

  const latestStatus =
    useRef<string | null>(
      null,
    );

  const loadResearch =
    useCallback(
      async () => {
        if (!researchId) {
          setData(null);
          setLoading(false);
          setError(null);

          latestStatus.current =
            null;

          return;
        }

        if (
          requestInFlight.current
        ) {
          return;
        }

        requestInFlight.current =
          true;

        setLoading(true);
        setError(null);

        try {
          const apiResult =
            await getResearch(
              researchId,
            );

          const rawStatus =
            apiResult &&
            typeof apiResult ===
              "object"
              ? (
                  apiResult as {
                    status?: unknown;
                  }
                ).status
              : undefined;

          latestStatus.current =
            normalizeStatus(
              rawStatus,
            );

          const result =
            mapApiResearchResult(
              apiResult,
            );

          setData(result);
        } catch (err) {
          const message =
            err instanceof Error
              ? err.message
              : "Failed to load research results";

          setError(message);
        } finally {
          requestInFlight.current =
            false;

          setLoading(false);
        }
      },
      [researchId],
    );

  // ==========================================================
  // Initial Load
  // ==========================================================

  useEffect(() => {
    latestStatus.current =
      null;

    if (!researchId) {
      setData(null);
      setLoading(false);
      setError(null);
      return;
    }

    void loadResearch();
  }, [
    researchId,
    loadResearch,
  ]);

  // ==========================================================
  // Polling
  // ==========================================================

  useEffect(() => {
    if (!researchId) {
      return;
    }

    if (
      latestStatus.current &&
      isTerminalStatus(
        latestStatus.current,
      )
    ) {
      return;
    }

    const interval =
      window.setInterval(
        () => {
          void loadResearch();
        },
        3000,
      );

    return () => {
      window.clearInterval(
        interval,
      );
    };
  }, [
    researchId,
    loadResearch,
  ]);

  return {
    data,
    loading,
    error,
    refetch: loadResearch,
  };
}