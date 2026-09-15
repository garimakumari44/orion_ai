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

/* -------------------------------------------------------------------------- */
/* Props                                                                      */
/* -------------------------------------------------------------------------- */

interface ResearchPageProps {
  researchId: string | number;
  data?: ResearchResult | null;
}

/* -------------------------------------------------------------------------- */
/* Generic helpers                                                            */
/* -------------------------------------------------------------------------- */

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

/* -------------------------------------------------------------------------- */
/* Array helpers                                                              */
/* -------------------------------------------------------------------------- */

/**
 * Return the first non-empty array.
 *
 * Empty arrays are deliberately ignored when a later location contains
 * actual data.
 */
function firstNonEmptyArray(
  ...values: unknown[]
): unknown[] {
  let firstArray: unknown[] | null = null;

  for (const value of values) {
    if (!Array.isArray(value)) {
      continue;
    }

    if (firstArray === null) {
      firstArray = value;
    }

    if (value.length > 0) {
      return value;
    }
  }

  return firstArray ?? [];
}

/**
 * Recursively search an object tree for arrays belonging to one of the
 * requested keys.
 *
 * This handles backend responses such as:
 *
 * result
 *   -> data
 *      -> research
 *         -> analysis
 *            -> insights
 *
 * and:
 *
 * result
 *   -> research
 *      -> findings
 *         -> items
 */
function findArraysByKeys(
  root: unknown,
  keys: string[],
  maxDepth = 8,
): unknown[][] {
  const results: unknown[][] = [];

  const normalizedKeys = new Set(
    keys.map((key) =>
      key.toLowerCase(),
    ),
  );

  function walk(
    value: unknown,
    depth: number,
  ) {
    if (
      depth > maxDepth ||
      !isObject(value)
    ) {
      return;
    }

    for (const [
      key,
      child,
    ] of Object.entries(value)) {
      const normalizedKey =
        key.toLowerCase();

      if (
        normalizedKeys.has(
          normalizedKey,
        ) &&
        Array.isArray(child)
      ) {
        results.push(child);
      }

      if (isObject(child)) {
        walk(child, depth + 1);
      }
    }
  }

  walk(root, 0);

  return results;
}

/**
 * Get the first useful array from a recursive search.
 */
function findFirstNonEmptyArrayByKeys(
  root: unknown,
  keys: string[],
): unknown[] {
  const arrays =
    findArraysByKeys(
      root,
      keys,
    );

  return firstNonEmptyArray(
    ...arrays,
  );
}

/* -------------------------------------------------------------------------- */
/* Raw response unwrapping                                                    */
/* -------------------------------------------------------------------------- */

/**
 * Unwrap common API envelopes without destroying the original response.
 */
function unwrapResearchResponse(
  value: unknown,
): Record<string, unknown> {
  if (!isObject(value)) {
    return {};
  }

  let current: unknown = value;

  for (let index = 0; index < 8; index += 1) {
    if (!isObject(current)) {
      break;
    }

    const next =
      getObject(
        current.data,
        current.result,
        current.response,
        current.payload,
      );

    if (!next) {
      break;
    }

    current = next;
  }

  return isObject(current)
    ? current
    : {};
}

/* -------------------------------------------------------------------------- */
/* Status helpers                                                             */
/* -------------------------------------------------------------------------- */

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
  ].includes(
    normalizeStatus(value),
  );
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
  ].includes(
    normalizeStatus(value),
  );
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
  ].includes(
    normalizeStatus(value),
  );
}

/* -------------------------------------------------------------------------- */
/* Research ID                                                                */
/* -------------------------------------------------------------------------- */

function resolveResearchId(
  requestedId: string | number,
  data?: ResearchResult | null,
): string {
  return (
    firstString(
      data?.researchId,
      data?.id,
      requestedId,
    ) || ""
  );
}

/* -------------------------------------------------------------------------- */
/* Evidence normalization                                                     */
/* -------------------------------------------------------------------------- */

function normalizeEvidence(
  raw: unknown[],
): ResearchEvidenceItem[] {
  return raw
    .filter(
      (item) =>
        isObject(item) ||
        typeof item === "string",
    )
    .map((item, index) => {
      if (typeof item === "string") {
        const claim =
          item.trim();

        if (!claim) {
          return null;
        }

        return {
          id: `evidence-${index}`,
          claim,
          source: undefined,
          confidence: 0,
          date: undefined,
          category: undefined,
          citation: undefined,
          filing: undefined,
        } as ResearchEvidenceItem;
      }

      const claim =
        firstString(
          item.claim,
          item.statement,
          item.finding,
          item.description,
          item.text,
          item.content,
          item.summary,
        );

      const source =
        firstString(
          item.source,
          item.source_name,
          item.sourceName,
          item.source_type,
          item.sourceType,
        );

      const confidence =
        firstNumber(
          item.confidence,
          item.confidence_score,
          item.confidenceScore,
        );

      const id =
        firstString(
          item.id,
          item.evidence_id,
          item.evidenceId,
        );

      return {
        ...item,

        id:
          id ||
          `evidence-${index}`,

        claim,

        source:
          source || undefined,

        confidence:
          confidence ?? 0,

        date:
          firstString(
            item.date,
            item.publishedAt,
            item.published_at,
          ) || undefined,

        category:
          firstString(
            item.category,
            item.type,
            item.evidence_type,
            item.evidenceType,
          ) || undefined,

        citation:
          firstString(
            item.citation,
            item.reference,
            item.source_reference,
            item.sourceReference,
            item.url,
          ) || undefined,

        filing:
          firstString(
            item.filing,
            item.filing_name,
            item.filingName,
          ) || undefined,
      } as ResearchEvidenceItem;
    })
    .filter(
      (
        item,
      ): item is ResearchEvidenceItem =>
        item !== null &&
        Boolean(
          item.claim ||
          item.source ||
          item.citation,
        ),
    );
}

/* -------------------------------------------------------------------------- */
/* Document normalization                                                     */
/* -------------------------------------------------------------------------- */

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
        firstString(
          item.status,
          item.state,
        ) || undefined,

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

/* -------------------------------------------------------------------------- */
/* Insight normalization                                                      */
/* -------------------------------------------------------------------------- */

function normalizeInsights(
  raw: unknown[],
): ResearchInsight[] {
  return raw
    .filter(
      (item) =>
        isObject(item) ||
        typeof item === "string",
    )
    .map((item, index) => {
      if (typeof item === "string") {
        const text =
          item.trim();

        if (!text) {
          return null;
        }

        return {
          id: `insight-${index}`,
          title: "Research Insight",
          type: "insight",
          description: text,
          summary: text,
          impact: null,
          confidence: null,
          recommendation: null,
        } as ResearchInsight;
      }

      const description =
        firstString(
          item.description,
          item.content,
          item.text,
          item.finding,
          item.statement,
          item.summary,
          item.details,
          item.body,
        );

      const title =
        firstString(
          item.title,
          item.name,
          item.heading,
          item.label,
          item.insight,
        );

      let type =
        firstString(
          item.type,
          item.category,
          item.insight_type,
          item.insightType,
        )
          .toLowerCase()
          .trim();

      if (
        ![
          "insight",
          "risk",
          "catalyst",
        ].includes(type)
      ) {
        type = "insight";
      }

      const id =
        firstString(
          item.id,
          item.insight_id,
          item.insightId,
        );

      const summary =
        firstString(
          item.summary,
          item.description,
          item.content,
        );

      return {
        ...item,

        id:
          id ||
          `insight-${index}`,

        title:
          title ||
          "Research Insight",

        type,

        description:
          description ||
          null,

        summary:
          summary ||
          null,

        impact:
          firstString(
            item.impact,
            item.impact_level,
            item.impactLevel,
          ) || null,

        confidence:
          firstNumber(
            item.confidence,
            item.confidence_score,
            item.confidenceScore,
          ),

        recommendation:
          firstString(
            item.recommendation,
            item.action,
            item.recommended_action,
            item.recommendedAction,
          ) || null,
      } as ResearchInsight;
    })
    .filter(
      (
        item,
      ): item is ResearchInsight =>
        item !== null &&
        Boolean(
          item.description ||
          item.summary ||
          item.title,
        ),
    );
}

/* -------------------------------------------------------------------------- */
/* Stage normalization                                                        */
/* -------------------------------------------------------------------------- */

function normalizeStages(
  raw: unknown[],
): ResearchStageInfo[] {
  return raw
    .filter(isObject)
    .map((item, index) => {
      const stageStatus =
        firstString(
          item.status,
          item.state,
        )
          .toLowerCase()
          .trim();

      return {
        id:
          firstString(
            item.id,
            item.stage_id,
            item.stageId,
            item.key,
          ) ||
          `stage-${index}`,

        name:
          firstString(
            item.name,
            item.stage,
            item.key,
            item.label,
            item.id,
          ) ||
          `Stage ${index + 1}`,

        label:
          firstString(
            item.label,
            item.name,
            item.stage,
          ) || undefined,

        status:
          stageStatus || null,

        progress:
          firstNumber(
            item.progress,
            item.percent,
            item.percentage,
            item.progress_percent,
            item.progressPercent,
          ) ?? 0,

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
            item.message,
            item.description,
          ) || undefined,
      };
    });
}

/* -------------------------------------------------------------------------- */
/* Report normalization                                                       */
/* -------------------------------------------------------------------------- */

function normalizeReport(
  rawReport: unknown,
  root: Record<string, unknown>,
): ResearchResult["report"] {
  let reportObject =
    isObject(rawReport)
      ? rawReport
      : {};

  /*
   * Sometimes report is nested one level deeper.
   */
  if (
    isObject(reportObject.data)
  ) {
    reportObject =
      reportObject.data;
  }

  if (
    isObject(reportObject.report)
  ) {
    reportObject =
      reportObject.report;
  }

  const rawSections =
    firstNonEmptyArray(
      reportObject.sections,
      reportObject.reportSections,
      reportObject.report_sections,
      reportObject.items,
      root.reportSections,
      root.report_sections,

      findFirstNonEmptyArrayByKeys(
        root,
        [
          "sections",
          "reportSections",
          "report_sections",
        ],
      ),
    );

  /*
   * Some APIs return report sections directly as:
   *
   * report: [...]
   */
  const directReportArray =
    Array.isArray(rawReport)
      ? rawReport
      : [];

  const sectionSource =
    rawSections.length > 0
      ? rawSections
      : directReportArray;

  const sections =
    sectionSource
      .filter(
        (section) =>
          isObject(section) ||
          typeof section === "string",
      )
      .map(
        (section, index) => {
          if (
            typeof section ===
            "string"
          ) {
            return {
              id: `section-${index}`,
              title: `Section ${index + 1}`,
              status: "complete",
              content:
                section.trim(),
              lastUpdated:
                undefined,
            };
          }

          return {
            ...section,

            id:
              firstString(
                section.id,
                section.section_id,
                section.sectionId,
              ) ||
              `section-${index}`,

            title:
              firstString(
                section.title,
                section.name,
                section.heading,
                section.label,
              ) ||
              `Section ${index + 1}`,

            status:
              firstString(
                section.status,
                section.state,
              ) ||
              "complete",

            content:
              firstString(
                section.content,
                section.text,
                section.body,
                section.description,
                section.summary,
              ),

            lastUpdated:
              firstString(
                section.lastUpdated,
                section.last_updated,
                section.updatedAt,
                section.updated_at,
              ) || undefined,
          };
        },
      );

  /*
   * If there are no explicit sections but report itself contains text,
   * expose that text as a single report section instead of losing it.
   */
  if (
    sections.length === 0 &&
    isObject(rawReport)
  ) {
    const reportContent =
      firstString(
        reportObject.content,
        reportObject.text,
        reportObject.body,
        reportObject.summary,
        reportObject.description,
      );

    if (reportContent) {
      sections.push({
        id: "section-0",
        title:
          firstString(
            reportObject.title,
            reportObject.name,
            "Research Report",
          ),
        status: "complete",
        content: reportContent,
        lastUpdated:
          firstString(
            reportObject.updatedAt,
            reportObject.updated_at,
          ) || undefined,
      });
    }
  }

  return {
    title:
      firstString(
        reportObject.title,
        reportObject.name,
        root.reportTitle,
        root.report_title,
      ) || null,

    sections,
  };
}

/* -------------------------------------------------------------------------- */
/* Overview normalization                                                     */
/* -------------------------------------------------------------------------- */

function normalizeOverview(
  root: Record<string, unknown>,
): ResearchResult["overview"] {
  const overview =
    getObject(
      root.overview,
      root.companyProfile,
      root.company_profile,
    ) ?? {};

  const profile =
    getObject(
      overview.profile,
      root.profile,
      root.company,
      root.companyProfile,
      root.company_profile,
    );

  const market =
    getObject(
      overview.market,
      root.market,
      root.marketData,
      root.market_data,
    );

  const financials =
    getObject(
      overview.financials,
      root.financials,
      root.financial,
      root.financialData,
      root.financial_data,
    );

  return {
    profile: profile
      ? {
          ...profile,

          name:
            firstString(
              profile.name,
              root.companyName,
              root.company_name,
            ) || null,

          ticker:
            firstString(
              profile.ticker,
              root.ticker,
              root.symbol,
            ) || null,

          description:
            firstString(
              profile.description,
              profile.summary,
              profile.about,
            ) || null,

          sector:
            firstString(
              profile.sector,
            ) || null,

          industry:
            firstString(
              profile.industry,
            ) || null,

          headquarters:
            firstString(
              profile.headquarters,
              profile.location,
            ) || null,

          ceo:
            firstString(
              profile.ceo,
              profile.chief_executive,
              profile.chiefExecutive,
            ) || null,

          employees:
            firstDefined(
              profile.employees,
              profile.employeeCount,
              profile.employee_count,
            ) ?? null,

          founded:
            firstDefined(
              profile.founded,
              profile.foundedYear,
              profile.founded_year,
            ) ?? null,

          website:
            firstString(
              profile.website,
              profile.url,
            ) || null,
        }
      : null,

    market: market
      ? {
          ...market,

          marketCap:
            firstDefined(
              market.marketCap,
              market.market_cap,
            ) ?? null,

          sharePrice:
            firstDefined(
              market.sharePrice,
              market.share_price,
              market.currentPrice,
              market.current_price,
            ) ?? null,

          peRatio:
            firstDefined(
              market.peRatio,
              market.pe_ratio,
              market.pe,
            ) ?? null,

          weekRange52:
            firstString(
              market.weekRange52,
              market.week_range_52,
              market.fiftyTwoWeekRange,
              market.fifty_two_week_range,
            ) || null,

          dividendYield:
            firstDefined(
              market.dividendYield,
              market.dividend_yield,
            ) ?? null,

          beta:
            firstDefined(
              market.beta,
            ) ?? null,
        }
      : null,

    financials: financials
      ? {
          ...financials,

          revenue:
            firstDefined(
              financials.revenue,
            ) ?? null,

          revenueGrowth:
            firstDefined(
              financials.revenueGrowth,
              financials.revenue_growth,
            ) ?? null,

          grossMargin:
            firstDefined(
              financials.grossMargin,
              financials.gross_margin,
            ) ?? null,

          operatingMargin:
            firstDefined(
              financials.operatingMargin,
              financials.operating_margin,
            ) ?? null,

          eps:
            firstDefined(
              financials.eps,
            ) ?? null,
        }
      : null,
  };
}

/* -------------------------------------------------------------------------- */
/* Research normalization                                                     */
/* -------------------------------------------------------------------------- */

function normalizeResearchResult(
  raw: unknown,
  fallback?: ResearchResult | null,
  requestedId?: string | number,
): ResearchResult {
  const root =
    unwrapResearchResponse(raw);

  const existing =
    fallback ?? null;

  /*
   * These objects are intentionally collected from several possible
   * backend locations.
   */
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
      root.analyses,
    );

  const findings =
    getObject(
      root.findings,
      nestedResearch?.findings,
      analysis?.findings,
    );

  const metadata =
    getObject(
      root.metadata,
      nestedResearch?.metadata,
    );

  const summaryObject =
    getObject(
      root.summary,
      nestedResearch?.summary,
    );

  /* ------------------------------------------------------------------------ */
  /* Evidence                                                                 */
  /* ------------------------------------------------------------------------ */

  const explicitEvidence =
    firstNonEmptyArray(
      root.evidence,
      root.evidenceItems,
      root.evidence_items,

      nestedResearch?.evidence,
      nestedResearch?.evidenceItems,
      nestedResearch?.evidence_items,

      analysis?.evidence,
      analysis?.evidenceItems,
      analysis?.evidence_items,

      findings?.evidence,
      findings?.evidenceItems,
      findings?.evidence_items,

      metadata?.evidence,
    );

  const recursiveEvidence =
    findFirstNonEmptyArrayByKeys(
      root,
      [
        "evidence",
        "evidenceItems",
        "evidence_items",
      ],
    );

  const rawEvidence =
    explicitEvidence.length > 0
      ? explicitEvidence
      : recursiveEvidence;

  const normalizedEvidence =
    normalizeEvidence(
      rawEvidence,
    );

  const evidence =
    normalizedEvidence.length > 0
      ? normalizedEvidence
      : existing?.evidence ?? [];

  /* ------------------------------------------------------------------------ */
  /* Documents                                                                */
  /* ------------------------------------------------------------------------ */

  const explicitDocuments =
    firstNonEmptyArray(
      root.documents,
      root.sourceDocuments,
      root.source_documents,
      root.sources,

      nestedResearch?.documents,
      nestedResearch?.sourceDocuments,
      nestedResearch?.source_documents,

      metadata?.documents,
    );

  const recursiveDocuments =
    findFirstNonEmptyArrayByKeys(
      root,
      [
        "documents",
        "sourceDocuments",
        "source_documents",
      ],
    );

  const rawDocuments =
    explicitDocuments.length > 0
      ? explicitDocuments
      : recursiveDocuments;

  const normalizedDocuments =
    normalizeDocuments(
      rawDocuments,
    );

  const documents =
    normalizedDocuments.length > 0
      ? normalizedDocuments
      : existing?.documents ?? [];

  /* ------------------------------------------------------------------------ */
  /* Insights                                                                 */
  /* ------------------------------------------------------------------------ */

  /*
   * This is intentionally much broader than the previous implementation.
   *
   * Supported shapes include:
   *
   * analysis.insights
   * analysis.keyFindings
   * analysis.findings
   * findings.insights
   * findings.items
   * summary.insights
   * research.insights
   * root.insights
   *
   * and recursive equivalents.
   */
  const explicitInsights =
    firstNonEmptyArray(
      root.insights,
      root.insightItems,
      root.insight_items,
      root.keyInsights,
      root.key_insights,
      root.keyFindings,
      root.key_findings,

      nestedResearch?.insights,
      nestedResearch?.insightItems,
      nestedResearch?.insight_items,
      nestedResearch?.keyInsights,
      nestedResearch?.key_insights,
      nestedResearch?.keyFindings,
      nestedResearch?.key_findings,

      analysis?.insights,
      analysis?.insightsItems,
      analysis?.insight_items,
      analysis?.keyFindings,
      analysis?.key_findings,
      analysis?.keyInsights,
      analysis?.key_insights,
      analysis?.findings,
      analysis?.items,
      analysis?.results,

      findings?.insights,
      findings?.keyFindings,
      findings?.key_findings,
      findings?.keyInsights,
      findings?.key_insights,
      findings?.items,
      findings?.results,

      summaryObject?.insights,
      summaryObject?.keyFindings,
      summaryObject?.key_findings,
      summaryObject?.keyInsights,
      summaryObject?.key_insights,

      metadata?.insights,
    );

  const recursiveInsights =
    findFirstNonEmptyArrayByKeys(
      root,
      [
        "insights",
        "insightItems",
        "insight_items",
        "keyInsights",
        "key_insights",
        "keyFindings",
        "key_findings",
      ],
    );

  /*
   * If an explicit location contains an empty array but another nested
   * location has real insights, use the nested location.
   */
  const rawInsights =
    explicitInsights.length > 0
      ? explicitInsights
      : recursiveInsights;

  const normalizedInsights =
    normalizeInsights(
      rawInsights,
    );

  const insights =
    normalizedInsights.length > 0
      ? normalizedInsights
      : existing?.insights ?? [];

  /* ------------------------------------------------------------------------ */
  /* Stages                                                                   */
  /* ------------------------------------------------------------------------ */

  const explicitStages =
    firstNonEmptyArray(
      root.stages,
      root.steps,
      root.pipeline,

      nestedResearch?.stages,
      nestedResearch?.steps,
      nestedResearch?.pipeline,

      metadata?.stages,
    );

  const recursiveStages =
    findFirstNonEmptyArrayByKeys(
      root,
      [
        "stages",
        "steps",
        "pipeline",
      ],
    );

  const rawStages =
    explicitStages.length > 0
      ? explicitStages
      : recursiveStages;

  const normalizedStages =
    normalizeStages(
      rawStages,
    );

  const stages =
    normalizedStages.length > 0
      ? normalizedStages
      : existing?.stages ?? [];

  /* ------------------------------------------------------------------------ */
  /* IDs                                                                      */
  /* ------------------------------------------------------------------------ */

  const id =
    firstString(
      root.id,
      root.researchId,
      root.research_id,

      nestedResearch?.id,
      nestedResearch?.researchId,
      nestedResearch?.research_id,

      existing?.id,
      existing?.researchId,

      requestedId,
    ) || null;

  const canonicalResearchId =
    firstString(
      root.researchId,
      root.research_id,

      nestedResearch?.researchId,
      nestedResearch?.research_id,

      root.id,
      nestedResearch?.id,

      existing?.researchId,
      existing?.id,

      requestedId,
    ) || null;

  /* ------------------------------------------------------------------------ */
  /* Basic fields                                                             */
  /* ------------------------------------------------------------------------ */

  const title =
    firstString(
      root.title,
      root.name,

      nestedResearch?.title,
      nestedResearch?.name,

      existing?.title,
    ) || null;

  const companyName =
    firstString(
      root.companyName,
      root.company_name,

      nestedResearch?.companyName,
      nestedResearch?.company_name,

      root.company,

      existing?.companyName,
    ) || null;

  const ticker =
    firstString(
      root.ticker,
      root.symbol,

      nestedResearch?.ticker,
      nestedResearch?.symbol,

      existing?.ticker,
    ) || null;

  const status =
    firstString(
      root.status,
      root.state,

      nestedResearch?.status,
      nestedResearch?.state,

      existing?.status,
    ) || null;

  const summary =
    firstString(
      typeof root.summary ===
      "string"
        ? root.summary
        : undefined,

      root.description,

      nestedResearch?.summary,

      nestedResearch?.description,

      summaryObject?.text,
      summaryObject?.content,
      summaryObject?.description,

      existing?.summary,
    ) || null;

  const createdAt =
    firstString(
      root.createdAt,
      root.created_at,

      nestedResearch?.createdAt,
      nestedResearch?.created_at,

      existing?.createdAt,
    ) || null;

  const updatedAt =
    firstString(
      root.updatedAt,
      root.updated_at,

      nestedResearch?.updatedAt,
      nestedResearch?.updated_at,

      existing?.updatedAt,
    ) || null;

  /* ------------------------------------------------------------------------ */
  /* Overview                                                                 */
  /* ------------------------------------------------------------------------ */

  const hasOverviewData =
    Boolean(
      root.overview ||
      root.profile ||
      root.company ||
      root.companyProfile ||
      root.company_profile ||
      root.market ||
      root.marketData ||
      root.market_data ||
      root.financials ||
      root.financial ||
      root.financialData ||
      root.financial_data,
    );

  const overview =
    hasOverviewData
      ? normalizeOverview(root)
      : existing?.overview ?? {
          profile: null,
          market: null,
          financials: null,
        };

  /* ------------------------------------------------------------------------ */
  /* Report                                                                   */
  /* ------------------------------------------------------------------------ */

  const reportSource =
    firstDefined(
      root.report,
      root.researchReport,
      root.research_report,
      nestedResearch?.report,
      nestedResearch?.researchReport,
      nestedResearch?.research_report,
    );

  const normalizedReport =
    normalizeReport(
      reportSource,
      root,
    );

  const report = {
    title:
      normalizedReport.title ??
      existing?.report?.title ??
      null,

    sections:
      normalizedReport.sections
        .length > 0
        ? normalizedReport.sections
        : existing?.report?.sections ??
          [],
  };

  /* ------------------------------------------------------------------------ */
  /* Metadata                                                                 */
  /* ------------------------------------------------------------------------ */

  const normalizedMetadata =
    metadata ??
    existing?.metadata ??
    null;

  /* ------------------------------------------------------------------------ */
  /* Return                                                                   */
  /* ------------------------------------------------------------------------ */

  return {
    /*
     * Keep all backend fields.
     */
    ...root,

    /*
     * Keep existing workspace fields.
     */
    ...(existing ?? {}),

    /*
     * Canonical normalized fields.
     */
    id,

    researchId:
      canonicalResearchId,

    title,

    companyName,

    ticker,

    status,

    summary,

    overview,

    stages,

    evidence,

    documents,

    insights,

    report,

    createdAt,

    updatedAt,

    metadata:
      normalizedMetadata,
  };
}

/* -------------------------------------------------------------------------- */
/* Status extraction                                                          */
/* -------------------------------------------------------------------------- */

function extractStatus(
  value: unknown,
): string {
  if (!isObject(value)) {
    return "";
  }

  const result =
    isObject(value.result)
      ? value.result
      : null;

  const data =
    isObject(value.data)
      ? value.data
      : null;

  const research =
    isObject(value.research)
      ? value.research
      : null;

  return firstString(
    value.status,
    value.state,
    value.researchStatus,
    value.research_status,

    result?.status,
    result?.state,

    data?.status,
    data?.state,

    research?.status,
    research?.state,
  );
}

/* -------------------------------------------------------------------------- */
/* Progress extraction                                                        */
/* -------------------------------------------------------------------------- */

function extractProgress(
  value: unknown,
): number {
  if (!isObject(value)) {
    return 0;
  }

  const result =
    isObject(value.result)
      ? value.result
      : null;

  const data =
    isObject(value.data)
      ? value.data
      : null;

  const research =
    isObject(value.research)
      ? value.research
      : null;

  const progress =
    firstNumber(
      value.progress,
      value.progressPercent,
      value.progress_percent,
      value.percentage,
      value.percent,

      result?.progress,
      result?.progressPercent,
      result?.progress_percent,

      data?.progress,
      data?.progressPercent,
      data?.progress_percent,

      research?.progress,
      research?.progressPercent,
      research?.progress_percent,
    );

  return Math.min(
    100,
    Math.max(
      0,
      progress ?? 0,
    ),
  );
}

/* -------------------------------------------------------------------------- */
/* Stage extraction                                                           */
/* -------------------------------------------------------------------------- */

function extractStages(
  value: unknown,
): ResearchStageInfo[] {
  if (!isObject(value)) {
    return [];
  }

  const raw =
    findFirstNonEmptyArrayByKeys(
      value,
      [
        "stages",
        "steps",
        "pipeline",
      ],
    );

  return normalizeStages(
    raw,
  );
}

/* -------------------------------------------------------------------------- */
/* Current stage extraction                                                   */
/* -------------------------------------------------------------------------- */

function extractCurrentStage(
  value: unknown,
): string {
  if (!isObject(value)) {
    return "";
  }

  const result =
    isObject(value.result)
      ? value.result
      : null;

  const data =
    isObject(value.data)
      ? value.data
      : null;

  const research =
    isObject(value.research)
      ? value.research
      : null;

  return firstString(
    value.currentStage,
    value.current_stage,
    value.stage,
    value.currentStep,
    value.current_step,

    result?.currentStage,
    result?.current_stage,
    result?.stage,

    data?.currentStage,
    data?.current_stage,
    data?.stage,

    research?.currentStage,
    research?.current_stage,
    research?.stage,
  );
}

/* -------------------------------------------------------------------------- */
/* Created-at extraction                                                      */
/* -------------------------------------------------------------------------- */

function extractCreatedAt(
  value: unknown,
): string {
  if (!isObject(value)) {
    return "";
  }

  const research =
    isObject(value.research)
      ? value.research
      : null;

  const result =
    isObject(value.result)
      ? value.result
      : null;

  const data =
    isObject(value.data)
      ? value.data
      : null;

  return firstString(
    value.createdAt,
    value.created_at,

    research?.createdAt,
    research?.created_at,

    result?.createdAt,
    result?.created_at,

    data?.createdAt,
    data?.created_at,
  );
}

/* -------------------------------------------------------------------------- */
/* Research Page                                                              */
/* -------------------------------------------------------------------------- */

function ResearchPage({
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
    useState<string | null>(null);

  const [status, setStatus] =
    useState<string>(
      initialData?.status ?? "",
    );

  const [progress, setProgress] =
    useState<number>(
      initialData?.stages?.length
        ? Math.max(
            ...initialData.stages.map(
              (stage) =>
                safeNumber(
                  stage.progress,
                  0,
                ),
            ),
          )
        : 0,
    );

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

  /* ------------------------------------------------------------------------ */
  /* Canonical ID                                                             */
  /* ------------------------------------------------------------------------ */

  const canonicalResearchId =
    resolveResearchId(
      researchId,
      data,
    );

  /* ------------------------------------------------------------------------ */
  /* Poll cleanup                                                             */
  /* ------------------------------------------------------------------------ */

  const clearPollTimer =
    useCallback(() => {
      if (pollTimer.current) {
        clearTimeout(
          pollTimer.current,
        );

        pollTimer.current = null;
      }
    }, []);

  /* ------------------------------------------------------------------------ */
  /* Load research                                                            */
  /* ------------------------------------------------------------------------ */

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
          setError(
            "A valid research ID is required.",
          );

          setLoading(false);

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
        }

        setError(null);

        try {
          const raw =
            await getResearch(id);

          const previousData =
            data ?? initialData;

          const normalized =
            normalizeResearchResult(
              raw,
              previousData,
              id,
            );

          setData(
            normalized,
          );

          const resultStatus =
            extractStatus(raw);

          const resultProgress =
            extractProgress(raw);

          const resultStages =
            extractStages(raw);

          const resultCurrentStage =
            extractCurrentStage(raw);

          if (resultStatus) {
            setStatus(
              resultStatus,
            );
          }

          if (
            resultProgress > 0
          ) {
            setProgress(
              resultProgress,
            );
          }

          if (
            resultStages.length > 0
          ) {
            setStages(
              resultStages,
            );
          }

          if (
            resultCurrentStage
          ) {
            setCurrentStage(
              resultCurrentStage,
            );
          }

          /*
           * If the actual result is already complete,
           * don't perform another status request.
           */
          if (
            isFinishedStatus(
              resultStatus,
            )
          ) {
            setProgress(100);
            setLoading(false);

            return;
          }

          if (
            isFailedStatus(
              resultStatus,
            )
          ) {
            setLoading(false);

            setError(
              firstString(
                isObject(raw)
                  ? raw.error
                  : undefined,

                isObject(raw)
                  ? raw.message
                  : undefined,

                "Research failed.",
              ),
            );

            return;
          }

          /*
           * Status endpoint is supplementary.
           */
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

            if (statusValue) {
              setStatus(
                statusValue,
              );
            }

            setProgress(
              Math.max(
                resultProgress,
                statusProgress,
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

              /*
               * Fetch the completed research again so that
               * insights, evidence and report are available.
               */
              if (
                normalized.insights
                  ?.length === 0 ||
                normalized.evidence
                  ?.length === 0 ||
                normalized.report
                  ?.sections?.length === 0
              ) {
                await loadResearch(
                  true,
                );
              }
            }

            if (
              isFailedStatus(
                statusValue,
              )
            ) {
              setError(
                firstString(
                  isObject(
                    statusRaw,
                  )
                    ? statusRaw.error
                    : undefined,

                  isObject(
                    statusRaw,
                  )
                    ? statusRaw.message
                    : undefined,

                  "Research failed.",
                ),
              );
            }
          } catch {
            /*
             * Status failure must never destroy the actual
             * research result.
             */
          }

          setLoading(false);
        } catch (requestError) {
          setLoading(false);

          if (
            data ||
            initialData
          ) {
            setError(
              firstString(
                requestError instanceof
                Error
                  ? requestError.message
                  : undefined,

                "Unable to refresh research data.",
              ),
            );
          } else {
            setError(
              firstString(
                requestError instanceof
                Error
                  ? requestError.message
                  : undefined,

                "Unable to load research.",
              ),
            );
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

  /* ------------------------------------------------------------------------ */
  /* Reset when research ID changes                                           */
  /* ------------------------------------------------------------------------ */

  useEffect(() => {
    clearPollTimer();

    setData(
      initialData,
    );

    setStatus(
      initialData?.status ?? "",
    );

    setProgress(
      initialData?.stages?.length
        ? Math.max(
            ...initialData.stages.map(
              (stage) =>
                safeNumber(
                  stage.progress,
                  0,
                ),
            ),
          )
        : 0,
    );

    setCurrentStage("");

    setStages(
      initialData?.stages ?? [],
    );

    setError(null);

    setLoading(
      !initialData,
    );

    requestInFlight.current =
      false;
  }, [
    researchId,
    initialData,
    clearPollTimer,
  ]);

  /* ------------------------------------------------------------------------ */
  /* Initial load                                                             */
  /* ------------------------------------------------------------------------ */

  useEffect(() => {
    void loadResearch();
  }, [loadResearch]);

  /* ------------------------------------------------------------------------ */
  /* Poll research status                                                     */
  /* ------------------------------------------------------------------------ */

  useEffect(() => {
    clearPollTimer();

    if (
      !canonicalResearchId
    ) {
      return;
    }

    if (
      isFinishedStatus(status) ||
      isFailedStatus(status)
    ) {
      return;
    }

    const shouldPoll =
      loading ||
      isActiveStatus(status) ||
      !status;

    if (!shouldPoll) {
      return;
    }

    pollTimer.current =
      setTimeout(
        async () => {
          const id =
            canonicalResearchId;

          try {
            const statusRaw =
              await getResearchStatus(
                id,
              );

            const nextStatus =
              extractStatus(
                statusRaw,
              );

            const nextProgress =
              extractProgress(
                statusRaw,
              );

            const nextStages =
              extractStages(
                statusRaw,
              );

            const nextCurrentStage =
              extractCurrentStage(
                statusRaw,
              );

            if (nextStatus) {
              setStatus(
                nextStatus,
              );
            }

            if (
              nextProgress > 0
            ) {
              setProgress(
                nextProgress,
              );
            }

            if (
              nextStages.length > 0
            ) {
              setStages(
                nextStages,
              );
            }

            if (
              nextCurrentStage
            ) {
              setCurrentStage(
                nextCurrentStage,
              );
            }

            if (
              isFailedStatus(
                nextStatus,
              )
            ) {
              setLoading(false);

              setError(
                firstString(
                  isObject(
                    statusRaw,
                  )
                    ? statusRaw.error
                    : undefined,

                  isObject(
                    statusRaw,
                  )
                    ? statusRaw.message
                    : undefined,

                  "Research failed.",
                ),
              );

              return;
            }

            if (
              isFinishedStatus(
                nextStatus,
              )
            ) {
              setProgress(100);

              /*
               * Critical:
               *
               * When the status endpoint reports completion,
               * fetch the complete research payload.
               */
              await loadResearch(
                true,
              );

              setLoading(false);

              return;
            }

            setLoading(true);
          } catch {
            /*
             * Polling failures are intentionally ignored.
             */
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

  /* ------------------------------------------------------------------------ */
  /* Derived workspace values                                                 */
  /* ------------------------------------------------------------------------ */

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

  /* ------------------------------------------------------------------------ */
  /* Error state                                                              */
  /* ------------------------------------------------------------------------ */

  if (
    error &&
    !data &&
    !loading
  ) {
    return (
      <div className="min-h-[400px] flex items-center justify-center px-6">
        <div className="max-w-lg w-full rounded-lg border border-border bg-bg-surface p-6">
          <div className="text-sm font-medium text-text-primary">
            Unable to load research
          </div>

          <p className="mt-2 text-xs leading-5 text-text-muted">
            {error}
          </p>

          <button
            type="button"
            onClick={() => {
              void loadResearch();
            }}
            className="mt-4 rounded-md border border-border bg-bg-elevated px-3 py-2 text-xs font-medium text-text-primary hover:bg-bg-hover transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  /* ------------------------------------------------------------------------ */
  /* Research Workspace                                                       */
  /* ------------------------------------------------------------------------ */

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

/* -------------------------------------------------------------------------- */
/* Exports                                                                    */
/* -------------------------------------------------------------------------- */

export { ResearchPage };

export default ResearchPage;