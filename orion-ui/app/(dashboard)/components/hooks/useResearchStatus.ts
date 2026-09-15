import {
  useCallback,
  useEffect,
  useState,
} from "react";

import { getResearchStatus } from "@/lib/api/research";

import type { ResearchStatusResponse } from "@/types";

interface UseResearchStatusReturn {
  status: ResearchStatusResponse | null;
  isLoading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
}

const TERMINAL_STATUSES = new Set([
  "completed",
  "failed",
  "cancelled",
]);

export function useResearchStatus(
  researchId: string | null,
  poll = true,
  interval = 3000,
): UseResearchStatusReturn {
  const [status, setStatus] =
    useState<ResearchStatusResponse | null>(null);

  const [isLoading, setIsLoading] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);

  const refresh = useCallback(async () => {
    if (!researchId) {
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const result =
        await getResearchStatus(researchId);

      setStatus(result);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to load research status",
      );
    } finally {
      setIsLoading(false);
    }
  }, [researchId]);

  useEffect(() => {
    if (!researchId) {
      setStatus(null);
      setError(null);
      return;
    }

    void refresh();
  }, [researchId, refresh]);

  useEffect(() => {
    if (!poll || !researchId) {
      return;
    }

    if (
      status?.status &&
      TERMINAL_STATUSES.has(status.status)
    ) {
      return;
    }

    const timer = window.setInterval(() => {
      void refresh();
    }, interval);

    return () => {
      window.clearInterval(timer);
    };
  }, [
    poll,
    researchId,
    interval,
    status?.status,
    refresh,
  ]);

  return {
    status,
    isLoading,
    error,
    refresh,
  };
}