"use client";

import { useCallback, useState } from "react";

import { startResearch as startResearchApi } from "@/lib/api/research";
import type { StartResearchRequest } from "@/types";

interface UseResearchReturn {
  researchId: string | null;
  isCreating: boolean;
  error: string | null;

  startResearch: (
    request: StartResearchRequest,
  ) => Promise<string | null>;

  reset: () => void;
}

function extractResearchId(
  response: Awaited<
    ReturnType<typeof startResearchApi>
  >,
): string | null {
  const candidates: unknown[] = [
    response.research?.id,
    response.research?.research_id,
    response.research_id,
    response.id,
  ];

  for (const candidate of candidates) {
    if (
      candidate === null ||
      candidate === undefined
    ) {
      continue;
    }

    const value =
      String(candidate).trim();

    if (value) {
      return value;
    }
  }

  return null;
}

export function useResearch(): UseResearchReturn {
  const [researchId, setResearchId] =
    useState<string | null>(null);

  const [isCreating, setIsCreating] =
    useState(false);

  const [error, setError] =
    useState<string | null>(null);

  const startResearchHandler =
    useCallback(
      async (
        request: StartResearchRequest,
      ): Promise<string | null> => {
        setIsCreating(true);
        setError(null);

        try {
          const response =
            await startResearchApi(
              request,
            );

          const id =
            extractResearchId(
              response,
            );

          if (!id) {
            throw new Error(
              "Research started but the backend did not return a research ID.",
            );
          }

          setResearchId(id);

          return id;
        } catch (err) {
          const message =
            err instanceof Error
              ? err.message
              : "Failed to start research";

          setError(message);

          return null;
        } finally {
          setIsCreating(false);
        }
      },
      [],
    );

  const reset =
    useCallback(() => {
      setResearchId(null);
      setIsCreating(false);
      setError(null);
    }, []);

  return {
    researchId,
    isCreating,
    error,
    startResearch:
      startResearchHandler,
    reset,
  };
}