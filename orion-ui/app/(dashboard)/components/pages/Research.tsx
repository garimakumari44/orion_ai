"use client";

import {
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react";

import {
  getResearch,
  getResearchStatus,
} from "@/lib/api/researchApi";

import { ResearchWorkspace } from "../../components/research/ResearchWorkspace";

import type {
  ResearchEvidenceItem,
  ResearchInsight,
  ResearchResult,
  ResearchStageInfo,
} from "@/types/research";

/* ========================================================================== */
/* Props                                                                      */
/* ========================================================================== */

interface ResearchPageProps {
  researchId: string | number;
  data?: ResearchResult | null;
}

/* ========================================================================== */
/* Derived domain types                                                       */
/* ========================================================================== */

type ResearchDocumentStatus =
  NonNullable<
    NonNullable<ResearchResult["documents"]>[number]["status"]
  >;

type ReportSection =
  NonNullable<
    NonNullable<ResearchResult["report"]>["sections"]
  >[number];

type ReportSectionStatus =
  NonNullable<ReportSection["status"]>;

type ResearchInsightType =
  ResearchInsight["type"];

type ResearchStageStatus =
  NonNullable<ResearchStageInfo["status"]>;

/* ========================================================================== */
/* Generic helpers                                                            */
/* ========================================================================== */

function isObject(
  value: unknown,
): value is Record<string, unknown> {
  return (
    typeof value === "object" &&
    value !== null &&
    !Array.isArray(value)
  );
}

function safeString(
  value: unknown,
  fallback = "",
): string {
  if (
    typeof value === "string" &&
    value.trim().length > 0
  ) {
    return value.trim();
  }

  if (
    typeof value === "number" ||
    typeof value === "boolean"
  ) {
    return String(value);
  }

  return fallback;
}

function safeNumber(
  value: unknown,
  fallback = 0,
): number {
  const parsed =
    typeof value === "number"
      ? value
      : Number(value);

  return Number.isFinite(parsed)
    ? parsed
    : fallback;
}

function firstString(
  ...values: unknown[]
): string {
  for (const value of values) {
    const result = safeString(value);

    if (result) {
      return result;
    }
  }

  return "";
}

function firstNumber(
  ...values: unknown[]
): number | null {
  for (const value of values) {
    if (
      value === undefined ||
      value === null ||
      value === ""
    ) {
      continue;
    }

    const number =
      typeof value === "number"
        ? value
        : Number(value);

    if (Number.isFinite(number)) {
      return number;
    }
  }

  return null;
}

function firstScalar(
  ...values: unknown[]
): string | number | null {
  for (const value of values) {
    if (
      typeof value === "string" ||
      typeof value === "number"
    ) {
      return value;
    }

    if (typeof value === "boolean") {
      return String(value);
    }
  }

  return null;
}

function firstDefined(
  ...values: unknown[]
): unknown {
  for (const value of values) {
    if (
      value !== undefined &&
      value !== null
    ) {
      return value;
    }
  }

  return undefined;
}

function getObject(
  ...values: unknown[]
): Record<string, unknown> | null {
  for (const value of values) {
    if (isObject(value)) {
      return value;
    }
  }

  return null;
}

/* ========================================================================== */
/* Status helpers                                                             */
/* ========================================================================== */

function normalizeStatus(
  value: unknown,
): string {
  return safeString(value)
    .toLowerCase()
    .replace(/_/g, "-")
    .trim();
}

function isFinishedStatus(
  value: unknown,
): boolean {
  return [
    "completed",
    "complete",
    "finished",
    "success",
    "succeeded",
    "done",
  ].includes(normalizeStatus(value));
}

function isFailedStatus(
  value: unknown,
): boolean {
  return [
    "failed",
    "failure",
    "error",
    "cancelled",
    "canceled",
  ].includes(normalizeStatus(value));
}

function isActiveStatus(
  value: unknown,
): boolean {
  return [
    "pending",
    "queued",
    "running",
    "processing",
    "in-progress",
    "started",
  ].includes(normalizeStatus(value));
}

function normalizeDocumentStatus(
  value: unknown,
): ResearchDocumentStatus | undefined {
  const normalized =
    normalizeStatus(value);

  if (!normalized) {
    return undefined;
  }

  return normalized as ResearchDocumentStatus;
}

function normalizeReportSectionStatus(
  value: unknown,
): ReportSectionStatus {
  const normalized =
    normalizeStatus(value);

  if (!normalized) {
    return "complete" as ReportSectionStatus;
  }

  return normalized as ReportSectionStatus;
}

function normalizeInsightType(
  value: unknown,
): ResearchInsightType {
  const normalized =
    normalizeStatus(value);

  if (
    normalized === "risk" ||
    normalized === "risks"
  ) {
    return "risk" as ResearchInsightType;
  }

  if (
    normalized === "catalyst" ||
    normalized === "catalysts"
  ) {
    return "catalyst" as ResearchInsightType;
  }

  return "insight" as ResearchInsightType;
}

function normalizeStageStatus(
  value: unknown,
): ResearchStageStatus | null {
  const normalized =
    normalizeStatus(value);

  if (!normalized) {
    return null;
  }

  return normalized as ResearchStageStatus;
}

/* ========================================================================== */
/* Research ID                                                                */
/* ========================================================================== */

function resolveResearchId(
  researchId:
    | string
    | number
    | null
    | undefined,
  data?: ResearchResult | null,
): string {
  const direct =
    safeString(researchId);

  if (direct) {
    return direct;
  }

  return firstString(
    data?.researchId,
    data?.id,
  );
}

/* ========================================================================== */
/* Array helpers                                                              */
/* ========================================================================== */

function firstNonEmptyArray(
  ...values: unknown[]
): unknown[] {
  for (const value of values) {
    if (
      Array.isArray(value) &&
      value.length > 0
    ) {
      return value;
    }
  }

  return [];
}

function findArraysByKeys(
  source:
    | Record<string, unknown>
    | null,
  keys: string[],
): unknown[][] {
  if (!source) {
    return [];
  }

  const arrays: unknown[][] = [];

  for (const key of keys) {
    const value = source[key];

    if (Array.isArray(value)) {
      arrays.push(value);
    }
  }

  return arrays;
}

function findFirstNonEmptyArrayByKeys(
  source:
    | Record<string, unknown>
    | null,
  keys: string[],
): unknown[] {
  const arrays =
    findArraysByKeys(
      source,
      keys,
    );

  return firstNonEmptyArray(
    ...arrays,
  );
}

/* ========================================================================== */
/* API response unwrapping                                                    */
/* ========================================================================== */

function unwrapResearchResponse(
  raw: unknown,
): Record<string, unknown> {
  if (!isObject(raw)) {
    return {};
  }

  const nested = [
    raw.data,
    raw.result,
    raw.research,
    raw.research_result,
    raw.researchResult,
  ];

  for (const candidate of nested) {
    if (isObject(candidate)) {
      return candidate;
    }
  }

  return raw;
}

/* ========================================================================== */
/* Evidence normalization                                                     */
/* ========================================================================== */

function normalizeEvidence(
  raw: unknown[],
): ResearchEvidenceItem[] {
  return raw
    .map(
      (
        value,
        index,
      ): ResearchEvidenceItem | null => {
        if (
          typeof value === "string"
        ) {
          const claim =
            value.trim();

          if (!claim) {
            return null;
          }

          return {
            id: `evidence-${index}`,
            claim,
            source: "Unknown",
            confidence: 0,
            date: undefined,
            category: undefined,
            citation: "",
            filing: undefined,
          };
        }

        if (!isObject(value)) {
          return null;
        }

        const claim =
          firstString(
            value.claim,
            value.statement,
            value.text,
            value.description,
            value.finding,
            value.evidence,
          );

        const source =
          firstString(
            value.source,
            value.source_name,
            value.sourceName,
            value.company,
            value.publisher,
            value.document,
            "Unknown",
          );

        const confidence =
          firstNumber(
            value.confidence,
            value.score,
            value.relevance,
          ) ?? 0;

        const id =
          firstString(
            value.id,
            value.evidence_id,
            value.evidenceId,
          ) ||
          `evidence-${index}`;

        const date =
          firstString(
            value.date,
            value.publishedAt,
            value.published_at,
            value.timestamp,
          ) || undefined;

        const category =
          firstString(
            value.category,
            value.type,
          ) || undefined;

        const citation =
          firstString(
            value.citation,
            value.reference,
            value.url,
            value.link,
          );

        const filing =
          firstString(
            value.filing,
            value.filing_type,
            value.filingType,
          ) || undefined;

        if (
          !claim &&
          !source &&
          !citation
        ) {
          return null;
        }

        return {
          ...value,
          id,
          claim:
            claim || "Evidence",
          source:
            source || "Unknown",
          confidence,
          date,
          category,
          citation,
          filing,
        } as ResearchEvidenceItem;
      },
    )
    .filter(
      (
        item,
      ): item is ResearchEvidenceItem =>
        item !== null,
    );
}

/* ========================================================================== */
/* Documents                                                                  */
/* ========================================================================== */

function normalizeDocuments(
  raw: unknown[],
): ResearchResult["documents"] {
  return raw
    .filter(isObject)
    .map((item) => ({
      ...item,

      id:
        firstString(
          item.id,
          item.document_id,
          item.documentId,
        ) || undefined,

      title:
        firstString(
          item.title,
          item.name,
          item.document_title,
          item.documentTitle,
        ) || undefined,

      name:
        firstString(
          item.name,
          item.title,
          item.document_title,
          item.documentTitle,
        ) || undefined,

      type:
        firstString(
          item.type,
          item.document_type,
          item.documentType,
          item.mime_type,
          item.mimeType,
        ) || undefined,

      url:
        firstString(
          item.url,
          item.document_url,
          item.documentUrl,
          item.link,
        ) || undefined,

      source:
        firstString(
          item.source,
          item.source_name,
          item.sourceName,
        ) || undefined,

      status:
        normalizeDocumentStatus(
          firstString(
            item.status,
            item.state,
          ),
        ),

      pages:
        firstNumber(
          item.pages,
          item.page_count,
          item.pageCount,
        ),

      size:
        firstString(
          item.size,
          item.file_size,
          item.fileSize,
        ) || undefined,

      createdAt:
        firstString(
          item.createdAt,
          item.created_at,
        ) || undefined,

      date:
        firstString(
          item.date,
          item.publishedAt,
          item.published_at,
        ) || undefined,
    }));
}

/* ========================================================================== */
/* Insights                                                                   */
/* ========================================================================== */

function normalizeInsights(
  raw: unknown[],
): ResearchInsight[] {
  return raw
    .map(
      (
        value,
        index,
      ): ResearchInsight | null => {
        if (
          typeof value === "string"
        ) {
          const text =
            value.trim();

          if (!text) {
            return null;
          }

          return {
            id: `insight-${index}`,
            title:
              "Research Insight",
            type:
              "insight" as ResearchInsightType,
            description: text,
            summary: text,
            impact: null,
            confidence: 0,
            recommendation: null,
          };
        }

        if (!isObject(value)) {
          return null;
        }

        const title =
          firstString(
            value.title,
            value.name,
            value.heading,
          ) ||
          "Research Insight";

        const description =
          firstString(
            value.description,
            value.text,
            value.insight,
            value.finding,
            value.summary,
          );

        const summary =
          firstString(
            value.summary,
            value.description,
            value.text,
            value.insight,
          ) || description;

        const type =
          normalizeInsightType(
            value.type ??
              value.category ??
              value.kind,
          );

        const impact =
          firstString(
            value.impact,
            value.impact_level,
            value.impactLevel,
          ) || null;

        const confidence =
          firstNumber(
            value.confidence,
            value.score,
          ) ?? 0;

        const recommendation =
          firstString(
            value.recommendation,
            value.action,
            value.next_step,
            value.nextStep,
          ) || null;

        const id =
          firstString(
            value.id,
            value.insight_id,
            value.insightId,
          ) ||
          `insight-${index}`;

        if (!description) {
          return null;
        }

        return {
          ...value,
          id,
          title,
          type,
          description,
          summary:
            summary || null,
          impact,
          confidence,
          recommendation,
        } as ResearchInsight;
      },
    )
    .filter(
      (
        item,
      ): item is ResearchInsight =>
        item !== null,
    );
}

/* ========================================================================== */
/* Stages                                                                     */
/* ========================================================================== */

function normalizeStages(
  raw: unknown[],
): ResearchStageInfo[] {
  return raw
    .filter(isObject)
    .map(
      (
        item,
        index,
      ) =>
        ({
          ...item,

          id:
            firstString(
              item.id,
              item.stage_id,
              item.stageId,
            ) ||
            `stage-${index}`,

          name:
            firstString(
              item.name,
              item.label,
              item.stage,
            ) ||
            `Stage ${index + 1}`,

          label:
            firstString(
              item.label,
              item.name,
              item.stage,
            ) ||
            `Stage ${index + 1}`,

          status:
            normalizeStageStatus(
              firstString(
                item.status,
                item.state,
              ),
            ),

          progress: Math.min(
            100,
            Math.max(
              0,
              safeNumber(
                item.progress,
                0,
              ),
            ),
          ),

          startedAt:
            firstString(
              item.startedAt,
              item.started_at,
            ) || null,

          completedAt:
            firstString(
              item.completedAt,
              item.completed_at,
            ) || null,

          error:
            firstString(
              item.error,
              item.error_message,
              item.errorMessage,
            ) || null,

          detail:
            firstString(
              item.detail,
              item.description,
              item.message,
            ) || undefined,
        }) as ResearchStageInfo,
    );
}

/* ========================================================================== */
/* Report                                                                     */
/* ========================================================================== */

function normalizeReport(
  rawReport: unknown,
  fallback?:
    | ResearchResult["report"]
    | null,
): ResearchResult["report"] {
  const reportObject =
    isObject(rawReport)
      ? rawReport
      : null;

  const sectionsRaw =
    firstNonEmptyArray(
      reportObject?.sections,
      reportObject?.report_sections,
      reportObject?.reportSections,
    );

  const sections: ReportSection[] =
    sectionsRaw
      .map(
        (
          value,
          index,
        ): ReportSection | null => {
          if (
            typeof value === "string"
          ) {
            const text =
              value.trim();

            if (!text) {
              return null;
            }

            return {
              id: `section-${index}`,
              title: `Section ${
                index + 1
              }`,
              content: text,
              status:
                "complete" as ReportSectionStatus,
              lastUpdated:
                undefined,
            };
          }

          if (!isObject(value)) {
            return null;
          }

          const title =
            firstString(
              value.title,
              value.name,
              value.heading,
            ) ||
            `Section ${
              index + 1
            }`;

          const content =
            firstString(
              value.content,
              value.text,
              value.body,
              value.description,
              value.summary,
            );

          if (!content) {
            return null;
          }

          const lastUpdated =
            firstString(
              value.lastUpdated,
              value.last_updated,
              value.updatedAt,
              value.updated_at,
            ) || undefined;

          return {
            ...value,

            id:
              firstString(
                value.id,
                value.section_id,
                value.sectionId,
              ) ||
              `section-${index}`,

            title,

            content,

            status:
              normalizeReportSectionStatus(
                value.status ??
                  value.state,
              ),

            lastUpdated,
          } as ReportSection;
        },
      )
      .filter(
        (
          item,
        ): item is ReportSection =>
          item !== null,
      );

  /* ---------------------------------------------------------------------- */
  /* Single report object containing text                                   */
  /* ---------------------------------------------------------------------- */

  if (
    sections.length === 0 &&
    reportObject
  ) {
    const content =
      firstString(
        reportObject.content,
        reportObject.text,
        reportObject.body,
        reportObject.summary,
        reportObject.description,
      );

    if (content) {
      sections.push({
        id: "section-0",
        title:
          firstString(
            reportObject.title,
            reportObject.name,
          ) ||
          "Research Report",
        content,
        status:
          "complete" as ReportSectionStatus,
        lastUpdated:
          firstString(
            reportObject.lastUpdated,
            reportObject.last_updated,
            reportObject.updatedAt,
            reportObject.updated_at,
          ) || undefined,
      });
    }
  }

  /* ---------------------------------------------------------------------- */
  /* Fallback report                                                        */
  /* ---------------------------------------------------------------------- */

  if (
    sections.length === 0 &&
    fallback?.sections?.length
  ) {
    return fallback;
  }

  return {
    ...(reportObject ?? {}),

    title:
      firstString(
        reportObject?.title,
        reportObject?.name,
      ) ||
      "Research Report",

    sections,
  };
}

/* ========================================================================== */
/* Overview                                                                   */
/* ========================================================================== */

function normalizeOverview(
  raw: unknown,
): ResearchResult["overview"] {
  const root =
    isObject(raw)
      ? raw
      : {};

  const profile =
    getObject(
      root.profile,
      root.company,
      root.company_profile,
      root.companyProfile,
    );

  const market =
    getObject(
      root.market,
      root.market_data,
      root.marketData,
    );

  const financials =
    getObject(
      root.financials,
      root.financial,
      root.financial_data,
      root.financialData,
    );

  const profileResult = {
    ...(profile ?? {}),

    name:
      firstString(
        profile?.name,
        profile?.company_name,
        profile?.companyName,
        root.company_name,
        root.companyName,
      ) || null,

    ticker:
      firstString(
        profile?.ticker,
        profile?.symbol,
        root.ticker,
        root.symbol,
      ) || null,

    sector:
      firstString(
        profile?.sector,
        root.sector,
      ) || null,

    industry:
      firstString(
        profile?.industry,
        root.industry,
      ) || null,

    employees:
      firstScalar(
        profile?.employees,
        profile?.employee_count,
        profile?.employeeCount,
      ),

    founded:
      firstScalar(
        profile?.founded,
        profile?.founded_year,
        profile?.foundedYear,
      ),
  };

  const marketResult = {
    ...(market ?? {}),

    marketCap:
      firstScalar(
        market?.marketCap,
        market?.market_cap,
        market?.marketCapitalization,
      ),

    sharePrice:
      firstScalar(
        market?.sharePrice,
        market?.share_price,
        market?.price,
      ),

    peRatio:
      firstScalar(
        market?.peRatio,
        market?.pe_ratio,
        market?.pe,
      ),

    dividendYield:
      firstScalar(
        market?.dividendYield,
        market?.dividend_yield,
      ),

    beta:
      firstScalar(
        market?.beta,
      ),
  };

  const financialsResult = {
    ...(financials ?? {}),

    revenue:
      firstScalar(
        financials?.revenue,
        financials?.sales,
      ),

    revenueGrowth:
      firstScalar(
        financials?.revenueGrowth,
        financials?.revenue_growth,
      ),

    grossMargin:
      firstScalar(
        financials?.grossMargin,
        financials?.gross_margin,
      ),

    operatingMargin:
      firstScalar(
        financials?.operatingMargin,
        financials?.operating_margin,
      ),

    eps:
      firstScalar(
        financials?.eps,
        financials?.earnings_per_share,
      ),
  };

  return {
    ...(isObject(raw) ? raw : {}),
    profile: profileResult,
    market: marketResult,
    financials: financialsResult,
  } as ResearchResult["overview"];
}

/* ========================================================================== */
/* Research normalization                                                     */
/* ========================================================================== */

function normalizeResearchResult(
  raw: unknown,
  existing?: ResearchResult | null,
  requestedId?: string,
): ResearchResult {
  const root =
    unwrapResearchResponse(raw);

  const nestedResearch =
    getObject(
      root.research,
      root.research_result,
      root.researchResult,
    );

  const analysis =
    getObject(
      root.analysis,
      nestedResearch?.analysis,
    );

  const findings =
    getObject(
      root.findings,
      nestedResearch?.findings,
    );

  const metadata =
    getObject(
      root.metadata,
      nestedResearch?.metadata,
    );

  const summary =
    getObject(
      root.summary,
      nestedResearch?.summary,
    );

  /* ---------------------------------------------------------------------- */
  /* Evidence                                                               */
  /* ---------------------------------------------------------------------- */

  const evidenceRaw =
    firstNonEmptyArray(
      root.evidence,
      root.evidence_items,
      root.evidenceItems,
      analysis?.evidence,
      findings?.evidence,
      nestedResearch?.evidence,
    );

  const evidence =
    normalizeEvidence(
      evidenceRaw,
    );

  const normalizedEvidence =
    evidence.length > 0
      ? evidence
      : existing?.evidence ?? [];

  /* ---------------------------------------------------------------------- */
  /* Documents                                                              */
  /* ---------------------------------------------------------------------- */

  const documentsRaw =
    firstNonEmptyArray(
      root.documents,
      root.docs,
      root.sources,
      nestedResearch?.documents,
      nestedResearch?.docs,
    );

  const documents =
    normalizeDocuments(
      documentsRaw,
    );

  const normalizedDocuments =
    documents.length > 0
      ? documents
      : existing?.documents ?? [];

  /* ---------------------------------------------------------------------- */
  /* Insights                                                               */
  /* ---------------------------------------------------------------------- */

  const insightsRaw =
    firstNonEmptyArray(
      root.insights,
      root.key_insights,
      root.keyInsights,
      analysis?.insights,
      findings?.insights,
      nestedResearch?.insights,
    );

  const insights =
    normalizeInsights(
      insightsRaw,
    );

  const normalizedInsights =
    insights.length > 0
      ? insights
      : existing?.insights ?? [];

  /* ---------------------------------------------------------------------- */
  /* Stages                                                                 */
  /* ---------------------------------------------------------------------- */

  const stagesRaw =
    firstNonEmptyArray(
      root.stages,
      root.pipeline_stages,
      root.pipelineStages,
      root.execution_stages,
      root.executionStages,
      nestedResearch?.stages,
    );

  const stages =
    normalizeStages(
      stagesRaw,
    );

  const normalizedStages =
    stages.length > 0
      ? stages
      : existing?.stages ?? [];

  /* ---------------------------------------------------------------------- */
  /* Overview                                                               */
  /* ---------------------------------------------------------------------- */

  const overviewSource =
    firstDefined(
      root.overview,
      root.company_overview,
      root.companyOverview,
      nestedResearch?.overview,
      existing?.overview,
    );

  const overview =
    overviewSource !== undefined
      ? normalizeOverview(
          overviewSource,
        )
      : existing?.overview ?? null;

  /* ---------------------------------------------------------------------- */
  /* Report                                                                 */
  /* ---------------------------------------------------------------------- */

  const reportSource =
    firstDefined(
      root.report,
      root.researchReport,
      root.research_report,
      nestedResearch?.report,
      nestedResearch?.researchReport,
      nestedResearch?.research_report,
    );

  const report =
    reportSource !== undefined
      ? normalizeReport(
          reportSource,
          existing?.report,
        )
      : existing?.report ?? null;

  /* ---------------------------------------------------------------------- */
  /* Basic fields                                                           */
  /* ---------------------------------------------------------------------- */

  const id =
    firstString(
      root.id,
      root.researchId,
      root.research_id,
      nestedResearch?.id,
      nestedResearch?.researchId,
      existing?.id,
      existing?.researchId,
      requestedId,
    ) ||
    requestedId ||
    "";

  const researchId =
    firstString(
      root.researchId,
      root.research_id,
      nestedResearch?.researchId,
      nestedResearch?.research_id,
      existing?.researchId,
      id,
    ) || null;

  const companyName =
    firstString(
      root.companyName,
      root.company_name,
      nestedResearch?.companyName,
      nestedResearch?.company_name,
      existing?.companyName,
    ) || null;

  const title =
    firstString(
      root.title,
      root.name,
      nestedResearch?.title,
      nestedResearch?.name,
      existing?.title,
    ) || null;

  const status =
    firstString(
      root.status,
      root.state,
      nestedResearch?.status,
      nestedResearch?.state,
      existing?.status,
    ) || "";

  const createdAt =
    firstString(
      root.createdAt,
      root.created_at,
      nestedResearch?.createdAt,
      nestedResearch?.created_at,
      existing?.createdAt,
    ) || null;

  return {
    ...(existing ?? {}),
    ...root,

    id,
    researchId,
    companyName,
    title,
    status,
    createdAt,

    evidence:
      normalizedEvidence,

    documents:
      normalizedDocuments,

    insights:
      normalizedInsights,

    stages:
      normalizedStages,

    overview,

    report,

    metadata:
      metadata ??
      existing?.metadata ??
      null,

    summary:
      summary ??
      existing?.summary ??
      null,
  } as ResearchResult;
}

/* ========================================================================== */
/* Extraction helpers                                                         */
/* ========================================================================== */

function extractStatus(
  raw: unknown,
  result?: ResearchResult | null,
): string {
  const root =
    unwrapResearchResponse(raw);

  return firstString(
    root.status,
    root.state,
    result?.status,
  );
}

function extractProgress(
  raw: unknown,
  result?: ResearchResult | null,
): number {
  const root =
    unwrapResearchResponse(raw);

  const progress =
    firstNumber(
      root.progress,
      root.percent,
      root.percentage,
      root.progress_percent,
      root.progressPercent,
    );

  if (progress !== null) {
    return Math.min(
      100,
      Math.max(0, progress),
    );
  }

  if (
    result?.stages &&
    result.stages.length > 0
  ) {
    return Math.max(
      ...result.stages.map(
        (stage) =>
          safeNumber(
            stage.progress,
            0,
          ),
      ),
    );
  }

  return 0;
}

function extractStages(
  raw: unknown,
  result?: ResearchResult | null,
): ResearchStageInfo[] {
  const root =
    unwrapResearchResponse(raw);

  const stagesRaw =
    firstNonEmptyArray(
      root.stages,
      root.pipeline_stages,
      root.pipelineStages,
      root.execution_stages,
      root.executionStages,
      result?.stages,
    );

  return normalizeStages(
    stagesRaw,
  );
}

function extractCurrentStage(
  raw: unknown,
  result?: ResearchResult | null,
): string {
  const root =
    unwrapResearchResponse(raw);

  return firstString(
    root.currentStage,
    root.current_stage,
    root.activeStage,
    root.active_stage,
    result?.currentStage,
  );
}

function extractCreatedAt(
  raw: unknown,
): string {
  const root =
    unwrapResearchResponse(raw);

  return firstString(
    root.createdAt,
    root.created_at,
  );
}

/* ========================================================================== */
/* Page                                                                       */
/* ========================================================================== */

export function ResearchPage({
  researchId,
  data: initialData = null,
}: ResearchPageProps) {
  const [data, setData] =
    useState<ResearchResult | null>(
      initialData,
    );

  const [loading, setLoading] =
    useState<boolean>(
      !initialData,
    );

  const [error, setError] =
    useState<string | null>(
      null,
    );

  const [status, setStatus] =
    useState<string>(
      initialData?.status ?? "",
    );

  const [progress, setProgress] =
    useState<number>(() => {
      if (
        initialData?.stages &&
        initialData.stages.length > 0
      ) {
        return Math.max(
          ...initialData.stages.map(
            (stage) =>
              safeNumber(
                stage.progress,
                0,
              ),
          ),
        );
      }

      return 0;
    });

  const [currentStage, setCurrentStage] =
    useState<string>("");

  const [stages, setStages] =
    useState<ResearchStageInfo[]>(
      initialData?.stages ?? [],
    );

  const requestInFlight =
    useRef(false);

  const pollTimer =
    useRef<ReturnType<
      typeof setTimeout
    > | null>(null);

  const canonicalResearchId =
    resolveResearchId(
      researchId,
      data ?? initialData,
    );

  /* ---------------------------------------------------------------------- */
  /* Poll timer                                                             */
  /* ---------------------------------------------------------------------- */

  const clearPollTimer =
    useCallback(() => {
      if (pollTimer.current) {
        clearTimeout(
          pollTimer.current,
        );

        pollTimer.current =
          null;
      }
    }, []);

  /* ---------------------------------------------------------------------- */
  /* Load research                                                          */
  /* ---------------------------------------------------------------------- */

  const loadResearch =
    useCallback(
      async (
        silent = false,
      ) => {
        const id =
          resolveResearchId(
            researchId,
            data ?? initialData,
          );

        if (!id) {
          setLoading(false);
          setError(
            "No research ID was provided.",
          );
          return;
        }

        if (
          requestInFlight.current
        ) {
          return;
        }

        requestInFlight.current =
          true;

        if (!silent) {
          setLoading(true);
          setError(null);
        }

        try {
          const raw =
            await getResearch(id);

          const normalized =
            normalizeResearchResult(
              raw,
              data ?? initialData,
              id,
            );

          setData(normalized);

          const resultStatus =
            extractStatus(
              raw,
              normalized,
            );

          const resultProgress =
            extractProgress(
              raw,
              normalized,
            );

          const resultStages =
            extractStages(
              raw,
              normalized,
            );

          const resultCurrentStage =
            extractCurrentStage(
              raw,
              normalized,
            );

          setStatus(
            resultStatus,
          );

          setProgress(
            resultProgress,
          );

          setStages(
            resultStages,
          );

          setCurrentStage(
            resultCurrentStage,
          );

          /* -------------------------------------------------------------- */
          /* Completed                                                       */
          /* -------------------------------------------------------------- */

          if (
            isFinishedStatus(
              resultStatus,
            )
          ) {
            setProgress(100);

            const missingCompletedData =
              normalized.insights
                .length === 0 ||
              normalized.evidence
                .length === 0 ||
              !normalized.report ||
              normalized.report.sections
                .length === 0;

            if (
              missingCompletedData
            ) {
              try {
                const completedRaw =
                  await getResearch(id);

                const completed =
                  normalizeResearchResult(
                    completedRaw,
                    normalized,
                    id,
                  );

                setData(
                  completed,
                );

                setStatus(
                  extractStatus(
                    completedRaw,
                    completed,
                  ) ||
                    resultStatus,
                );

                setProgress(100);

                setStages(
                  extractStages(
                    completedRaw,
                    completed,
                  ),
                );

                setCurrentStage(
                  extractCurrentStage(
                    completedRaw,
                    completed,
                  ),
                );
              } catch {
                // Keep current completed result.
              }
            }

            setLoading(false);
            return;
          }

          /* -------------------------------------------------------------- */
          /* Failed                                                          */
          /* -------------------------------------------------------------- */

          if (
            isFailedStatus(
              resultStatus,
            )
          ) {
            setError(
              firstString(
                normalized.error,
                normalized.errorMessage,
                "Research execution failed.",
              ),
            );

            setLoading(false);
            return;
          }

          /* -------------------------------------------------------------- */
          /* Status endpoint                                                 */
          /* -------------------------------------------------------------- */

          try {
            const statusRaw =
              await getResearchStatus(
                id,
              );

            const statusValue =
              extractStatus(
                statusRaw,
                normalized,
              );

            const statusProgress =
              extractProgress(
                statusRaw,
                normalized,
              );

            const statusStages =
              extractStages(
                statusRaw,
                normalized,
              );

            const statusCurrentStage =
              extractCurrentStage(
                statusRaw,
                normalized,
              );

            setStatus(
              statusValue ||
                resultStatus,
            );

            setProgress(
              Math.min(
                100,
                Math.max(
                  0,
                  statusProgress,
                ),
              ),
            );

            if (
              statusStages.length > 0
            ) {
              setStages(
                statusStages,
              );
            }

            if (
              statusCurrentStage
            ) {
              setCurrentStage(
                statusCurrentStage,
              );
            }

            if (
              isFinishedStatus(
                statusValue,
              )
            ) {
              setProgress(100);

              const missingCompletedData =
                normalized.insights
                  .length === 0 ||
                normalized.evidence
                  .length === 0 ||
                !normalized.report ||
                normalized.report.sections
                  .length === 0;

              if (
                missingCompletedData
              ) {
                try {
                  const completedRaw =
                    await getResearch(
                      id,
                    );

                  const completed =
                    normalizeResearchResult(
                      completedRaw,
                      normalized,
                      id,
                    );

                  setData(
                    completed,
                  );

                  setStages(
                    extractStages(
                      completedRaw,
                      completed,
                    ),
                  );

                  setCurrentStage(
                    extractCurrentStage(
                      completedRaw,
                      completed,
                    ),
                  );
                } catch {
                  // Keep current result.
                }
              }

              setLoading(false);
              return;
            }

            if (
              isFailedStatus(
                statusValue,
              )
            ) {
              setError(
                "Research execution failed.",
              );

              setLoading(false);
              return;
            }

            if (
              isActiveStatus(
                statusValue,
              )
            ) {
              setLoading(true);
            }
          } catch {
            // Status endpoint failure should not discard valid research data.
          }
        } catch (
          requestError
        ) {
          const message =
            requestError instanceof Error
              ? requestError.message
              : "Failed to load research.";

          setError(message);

          if (!silent) {
            setLoading(false);
          }
        } finally {
          requestInFlight.current =
            false;
        }
      },
      [
        researchId,
        data,
        initialData,
      ],
    );

  /* ---------------------------------------------------------------------- */
  /* Reset                                                                  */
  /* ---------------------------------------------------------------------- */

  useEffect(() => {
    clearPollTimer();

    setData(
      initialData,
    );

    setError(null);

    setStatus(
      initialData?.status ?? "",
    );

    setProgress(() => {
      if (
        initialData?.stages &&
        initialData.stages.length > 0
      ) {
        return Math.max(
          ...initialData.stages.map(
            (stage) =>
              safeNumber(
                stage.progress,
                0,
              ),
          ),
        );
      }

      return 0;
    });

    setStages(
      initialData?.stages ?? [],
    );

    setCurrentStage("");

    requestInFlight.current =
      false;
  }, [
    researchId,
    initialData,
    clearPollTimer,
  ]);

  /* ---------------------------------------------------------------------- */
  /* Initial load                                                            */
  /* ---------------------------------------------------------------------- */

  useEffect(() => {
    void loadResearch();
  }, [loadResearch]);

  /* ---------------------------------------------------------------------- */
  /* Polling                                                                 */
  /* ---------------------------------------------------------------------- */

  useEffect(() => {
    clearPollTimer();

    const id =
      canonicalResearchId;

    if (!id) {
      return;
    }

    if (
      isFinishedStatus(status) ||
      isFailedStatus(status)
    ) {
      return;
    }

    pollTimer.current =
      setTimeout(
        async () => {
          try {
            const statusRaw =
              await getResearchStatus(
                id,
              );

            const statusValue =
              extractStatus(
                statusRaw,
              );

            const statusProgress =
              extractProgress(
                statusRaw,
              );

            const statusStages =
              extractStages(
                statusRaw,
              );

            const statusCurrentStage =
              extractCurrentStage(
                statusRaw,
              );

            if (
              statusValue
            ) {
              setStatus(
                statusValue,
              );
            }

            setProgress(
              Math.min(
                100,
                Math.max(
                  0,
                  statusProgress,
                ),
              ),
            );

            if (
              statusStages.length > 0
            ) {
              setStages(
                statusStages,
              );
            }

            if (
              statusCurrentStage
            ) {
              setCurrentStage(
                statusCurrentStage,
              );
            }

            if (
              isFailedStatus(
                statusValue,
              )
            ) {
              setError(
                "Research execution failed.",
              );

              setLoading(false);
              return;
            }

            if (
              isFinishedStatus(
                statusValue,
              )
            ) {
              setProgress(100);

              await loadResearch(
                true,
              );

              setLoading(false);
              return;
            }

            setLoading(true);
          } catch {
            // Continue polling after transient status errors.
          }
        },
        2500,
      );

    return clearPollTimer;
  }, [
    canonicalResearchId,
    status,
    loading,
    clearPollTimer,
    loadResearch,
  ]);

  /* ---------------------------------------------------------------------- */
  /* Workspace values                                                       */
  /* ---------------------------------------------------------------------- */

  const companyName =
    firstString(
      data?.companyName,
      data?.overview?.profile?.name,
      data?.title,
      data?.company_name,
      "Research",
    );

  const createdAt =
    firstString(
      data?.createdAt,
      data?.created_at,
      extractCreatedAt(data),
    );

  const workspaceProgress =
    Math.min(
      100,
      Math.max(
        0,
        safeNumber(
          progress,
          0,
        ),
      ),
    );

  const workspaceStatus =
    firstString(
      status,
      data?.status,
    );

  /* ---------------------------------------------------------------------- */
  /* Error state                                                             */
  /* ---------------------------------------------------------------------- */

  if (
    error &&
    !data
  ) {
    return (
      <div className="min-h-100 flex items-center justify-center px-6">
        <div className="w-full max-w-xl rounded-xl border border-border bg-background p-6 text-center">
          <h2 className="text-lg font-semibold text-text-primary">
            Unable to load research
          </h2>

          <p className="mt-2 text-sm text-text-secondary">
            {error}
          </p>

          <button
            type="button"
            onClick={() => {
              void loadResearch();
            }}
            className="mt-5 rounded-lg bg-primary px-4 py-2 text-sm font-medium text-white transition hover:opacity-90"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  /* ---------------------------------------------------------------------- */
  /* Workspace                                                               */
  /* ---------------------------------------------------------------------- */

  return (
    <ResearchWorkspace
      researchId={
        canonicalResearchId ||
        safeString(researchId)
      }
      data={data}
      loading={loading}
      progress={workspaceProgress}
      status={workspaceStatus}
      currentStage={currentStage}
      stages={stages}
      companyName={companyName}
      createdAt={createdAt}
    />
  );
}

export default ResearchPage;