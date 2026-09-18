"use client";

import {
  useCallback,
  useState,
} from "react";

import { ArrowRight } from "lucide-react";

import { cn } from "../ui";

import { ResearchTypeSelector } from "./ResearchTypeSelector";
import { ResearchConfiguration } from "./ResearchConfiguration";
import { ResearchReview } from "./ResearchReview";
import { ResearchWorkspace } from "./ResearchWorkspace";

import { useResearch } from "../hooks/useResearch";
import { useResearchStatus } from "../hooks/useResearchStatus";
import { useResearchResults } from "../hooks/useResearchResults";

import type {
  ApiCompanySearchResult,
  ApiResearchType,
  StartResearchRequest,
} from "@/types";
import type { ResearchResult as UiResearchResult } from "@/types/research";

// ============================================================
// Wizard Steps
// ============================================================

type Step =
  | "type"
  | "config"
  | "review"
  | "workspace";

const steps: {
  id: Step;
  label: string;
}[] = [
  {
    id: "type",
    label: "Research Type",
  },
  {
    id: "config",
    label: "Configuration",
  },
  {
    id: "review",
    label: "Review",
  },
  {
    id: "workspace",
    label: "Workspace",
  },
];

// ============================================================
// Props
// ============================================================

interface ResearchWizardProps {
  onExit: () => void;
  onCreated?: (researchId: string | number) => void;
}

// ============================================================
// Configuration
// ============================================================

interface ConfigData {
  company: ApiCompanySearchResult | null;

  comparisonCompanies: ApiCompanySearchResult[];

  industry: string;

  theme: string;

  objective:
    | "full"
    | "earnings"
    | "valuation"
    | "competitive"
    | "risk"
    | "memo";

  depth:
    | "quick"
    | "standard"
    | "comprehensive";

  horizon:
    | "short"
    | "medium"
    | "long";

  dataSources: string[];

  outputFormats: (
    | "report"
    | "summary"
    | "memo"
    | "dashboard"
    | "presentation"
  )[];
}

// ============================================================
// Default Configuration
// ============================================================

const defaultConfig: ConfigData = {
  company: null,

  comparisonCompanies: [],

  industry: "",

  theme: "",

  objective: "full",

  depth: "comprehensive",

  horizon: "medium",

  dataSources: [
    "SEC Filings",
    "Earnings Reports",
    "Earnings Transcripts",
    "Financial Statements",
    "Market Data",
    "News",
    "Analyst Estimates",
    "Industry Data",
  ],

  outputFormats: [
    "report",
    "dashboard",
    "memo",
  ],
};

// ============================================================
// Research Wizard
// ============================================================

export function ResearchWizard({
  onExit,
}: ResearchWizardProps) {
  const [step, setStep] =
    useState<Step>("type");

  const [researchType, setResearchType] =
    useState<ApiResearchType | null>(null);

  const [config, setConfig] =
    useState<ConfigData>(defaultConfig);

  // ==========================================================
  // Created At
  // ==========================================================

  const [createdAt] =
    useState(() => {
      const now = new Date();

      return `Today ${now.toLocaleTimeString(
        "en-US",
        {
          hour: "numeric",
          minute: "2-digit",
          hour12: true,
        },
      )}`;
    });

  // ==========================================================
  // Research Creation
  // ==========================================================

  const {
    startResearch,
    isCreating,
    researchId,
    error: researchError,
  } = useResearch();

  // ==========================================================
  // Research Status
  // ==========================================================

  const {
    status,
  } = useResearchStatus(
    researchId,
  );

  // ==========================================================
  // Research Results
  // ==========================================================

  const {
    data,
    loading,
    error: resultsError,
  } = useResearchResults(
    researchId,
    status?.progress ?? undefined,
  );

  // ==========================================================
  // Determine Whether Company Is Required
  // ==========================================================

  const requiresCompany = useCallback(
    (type: ApiResearchType): boolean => {
      return (
        type === "company_research" ||
        type === "company_comparison"
      );
    },
    [],
  );

  // ==========================================================
  // Configuration Validation
  // ==========================================================

  const canProceedFromConfig =
    useCallback(() => {
      if (!researchType) {
        return false;
      }

      // ------------------------------------------------------
      // Company research
      // ------------------------------------------------------

      if (
        researchType ===
          "company_research" &&
        !config.company
      ) {
        return false;
      }

      // ------------------------------------------------------
      // Company comparison
      // ------------------------------------------------------

      if (
        researchType ===
          "company_comparison"
      ) {
        if (!config.company) {
          return false;
        }

        if (
          config.comparisonCompanies
            .length === 0
        ) {
          return false;
        }
      }

      // ------------------------------------------------------
      // Industry research
      // ------------------------------------------------------

      if (
        researchType ===
          "industry_research" &&
        !config.industry.trim()
      ) {
        return false;
      }

      // ------------------------------------------------------
      // Theme research
      // ------------------------------------------------------

      if (
        researchType ===
          "theme_research" &&
        !config.theme.trim()
      ) {
        return false;
      }

      return true;
    }, [
      researchType,
      config,
    ]);

  // ==========================================================
  // Start Research
  // ==========================================================

  const handleStart =
    useCallback(
      async () => {
        if (!researchType) {
          return;
        }

        // ----------------------------------------------------
        // Validate required company
        // ----------------------------------------------------

        if (
          requiresCompany(
            researchType,
          ) &&
          !config.company
        ) {
          return;
        }

        // ----------------------------------------------------
        // Validate industry
        // ----------------------------------------------------

        if (
          researchType ===
            "industry_research" &&
          !config.industry.trim()
        ) {
          return;
        }

        // ----------------------------------------------------
        // Validate theme
        // ----------------------------------------------------

        if (
          researchType ===
            "theme_research" &&
          !config.theme.trim()
        ) {
          return;
        }

        // ----------------------------------------------------
        // Build query
        // ----------------------------------------------------

        const queryParts = [
          `Research objective: ${config.objective}`,
          `Depth: ${config.depth}`,
          `Investment horizon: ${config.horizon}`,
          `Required sources: ${config.dataSources.join(", ")}`,
          `Output: ${config.outputFormats.join(", ")}`,
        ];

        if (config.industry.trim()) {
          queryParts.push(
            `Industry: ${config.industry.trim()}`,
          );
        }

        if (config.theme.trim()) {
          queryParts.push(
            `Theme: ${config.theme.trim()}`,
          );
        }

        if (
          config.comparisonCompanies
            .length > 0
        ) {
          queryParts.push(
            `Comparison companies: ${config.comparisonCompanies
              .map((company) => company.name)
              .join(", ")}`,
          );
        }

        const payload: StartResearchRequest = {
          company_id:
            config.company?.id ?? undefined,

          research_type:
            researchType,

          query:
            queryParts.join("\n"),
        };

        // ----------------------------------------------------
        // Create research
        // ----------------------------------------------------

        const id =
          await startResearch(
            payload,
          );

        // ----------------------------------------------------
        // IMPORTANT
        //
        // Only move to Workspace after
        // the backend has returned a real ID.
        // ----------------------------------------------------

        if (!id) {
          return;
        }

        setStep("workspace");
      },
      [
        researchType,
        config,
        requiresCompany,
        startResearch,
      ],
    );

  // ==========================================================
  // Workspace Name
  // ==========================================================

  const companyName =
    config.company?.name ??
    config.industry ??
    config.theme ??
    "New Research";

  // ==========================================================
  // Current Step
  // ==========================================================

  const currentStepIndex =
    steps.findIndex(
      (item) =>
        item.id === step,
    );

  // ==========================================================
  // Workspace
  // ==========================================================

  if (
    step === "workspace" &&
    researchId
  ) {
    return (
      <ResearchWorkspace
        researchId={researchId}
      data={
        data
          ? ({
              ...data,
              id: data.id == null ? "" : String(data.id),
              researchId:
                data.researchId == null ? null : String(data.researchId),
            } as UiResearchResult)
          : null
      }
        loading={loading}
        progress={
          status?.progress ?? 0
        }
        status={
          status?.status ??
          "queued"
        }
        currentStage={
        typeof status?.current_stage === "string"
          ? status.current_stage
          : "Planning"
      }
        stages={[]}
        companyName={companyName}
        createdAt={createdAt}
      />
    );
  }

  // ==========================================================
  // Wizard UI
  // ==========================================================

  return (
    <div className="flex flex-col h-full">

      {/* ====================================================
          Progress Header
          ==================================================== */}

      <div className="flex items-center gap-3 p-4 border-b">

        {steps
          .slice(0, 3)
          .map(
            (item, index) => {
              const active =
                step === item.id;

              const past =
                currentStepIndex >
                index;

              return (
                <div
                  key={item.id}
                  className={cn(
                    "flex items-center gap-2 text-xs",
                    active &&
                      "text-primary",
                    past &&
                      "text-muted",
                  )}
                >
                  <span>
                    {past
                      ? "âœ“"
                      : index + 1}
                  </span>

                  {item.label}
                </div>
              );
            },
          )}

        <button
          onClick={onExit}
          className="ml-auto text-xs"
          type="button"
        >
          Cancel
        </button>

      </div>

      {/* ====================================================
          Errors
          ==================================================== */}

      {(researchError ||
        resultsError) && (
        <div className="mx-6 mt-4 rounded-md border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-400">
          {researchError ??
            resultsError}
        </div>
      )}

      {/* ====================================================
          Content
          ==================================================== */}

      <div className="flex-1 overflow-y-auto">

        {/* ==================================================
            Research Type
            ================================================== */}

        {step === "type" && (
          <ResearchTypeSelector
            selected={
              researchType
            }
            onSelect={(type) => {
              setResearchType(
                type,
              );

              setStep(
                "config",
              );
            }}
          />
        )}

        {/* ==================================================
            Configuration
            ================================================== */}

        {step === "config" &&
          researchType && (
            <>
              <ResearchConfiguration
                type={
                  researchType
                }
                config={
                  config
                }
                onChange={(
                  partial,
                ) =>
                  setConfig(
                    (
                      previous,
                    ) => ({
                      ...previous,
                      ...partial,
                    }),
                  )
                }
              />

              <button
                disabled={
                  !canProceedFromConfig()
                }
                onClick={() =>
                  setStep(
                    "review",
                  )
                }
                type="button"
                className="m-8 px-4 py-2 rounded bg-accent text-white disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Continue to Review

                <ArrowRight className="inline ml-2 w-4 h-4" />
              </button>
            </>
          )}

        {/* ==================================================
            Review
            ================================================== */}

        {step === "review" &&
          researchType && (
            <ResearchReview
              config={{
                type:
                  researchType,
                ...config,
              }}
              onStart={
                handleStart
              }
              isStarting={
                isCreating
              }
            />
          )}

      </div>
    </div>
  );
}












