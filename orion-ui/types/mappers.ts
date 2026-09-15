/**
 * API → Frontend Type Mappers
 *
 * Converts RAW backend research responses into the canonical
 * ResearchResult model consumed by the Research Workspace.
 *
 * IMPORTANT:
 * - Never invent research content.
 * - Never create fake timestamps.
 * - Never create fake evidence/documents/insights.
 * - Never create synthetic research IDs.
 * - Only expose data that exists in the backend response.
 *
 * Supported backend shapes:
 *
 *   GET /api/research/{id}/results
 *
 * Possible execution containers:
 *
 *   agent_results[]
 *   results[]
 *   executions[]
 */

import type { ApiResearchResult } from "./api";

import type {
  ResearchResult,
  ResearchStageInfo,
  ResearchEvidenceItem,
  ResearchDocument,
  ResearchInsight,
  ResearchReport,
  ReportSection,
  OverviewData,
} from "./research";

// ============================================================
// Generic Types
// ============================================================

type UnknownRecord = Record<string, unknown>;

interface BackendResearchExecution {
  task_id?: unknown;
  task_name?: unknown;
  task_type?: unknown;

  agent?: unknown;
  agent_name?: unknown;

  success?: unknown;

  execution_id?: unknown;
  trace_id?: unknown;

  output?: unknown;
  result?: unknown;

  error?: unknown;

  started_at?: unknown;
  completed_at?: unknown;

  metadata?: unknown;

  status?: unknown;
  progress?: unknown;
  current_step?: unknown;
}

interface BackendCitation {
  id?: unknown;
  source?: unknown;
  source_name?: unknown;
  title?: unknown;
  url?: unknown;
  citation?: unknown;
  date?: unknown;
  published_at?: unknown;
  confidence?: unknown;
}

// ============================================================
// Generic Helpers
// ============================================================

function isRecord(
  value: unknown,
): value is UnknownRecord {
  return (
    typeof value === "object" &&
    value !== null &&
    !Array.isArray(value)
  );
}

function asString(
  value: unknown,
): string {
  if (typeof value === "string") {
    return value.trim();
  }

  if (
    typeof value === "number" ||
    typeof value === "boolean"
  ) {
    return String(value);
  }

  return "";
}

function asNullableString(
  value: unknown,
): string | null {
  const result = asString(value);

  return result || null;
}

function asNullableNumber(
  value: unknown,
): number | null {
  if (
    typeof value === "number" &&
    Number.isFinite(value)
  ) {
    return value;
  }

  if (
    typeof value === "string" &&
    value.trim()
  ) {
    const parsed = Number(value);

    return Number.isFinite(parsed)
      ? parsed
      : null;
  }

  return null;
}

function asArray<T = unknown>(
  value: unknown,
): T[] {
  return Array.isArray(value)
    ? (value as T[])
    : [];
}

function firstNonEmpty(
  ...values: unknown[]
): string {
  for (const value of values) {
    const result = asString(value);

    if (result) {
      return result;
    }
  }

  return "";
}

function clamp(
  value: number,
  min: number,
  max: number,
): number {
  return Math.min(
    max,
    Math.max(min, value),
  );
}

function normalizeConfidence(
  value: unknown,
): number {
  const number =
    asNullableNumber(value);

  if (number === null) {
    return 0;
  }

  return clamp(
    Math.abs(number) <= 1
      ? number * 100
      : number,
    0,
    100,
  );
}

// ============================================================
// Date / Timestamp Helpers
// ============================================================

function getTimestamp(
  value: unknown,
): string | null {
  return asNullableString(value);
}

function getExecutionTimestamp(
  execution: BackendResearchExecution,
): string | null {
  return (
    getTimestamp(
      execution.completed_at,
    ) ??
    getTimestamp(
      execution.started_at,
    )
  );
}

// ============================================================
// Financial Value Extraction
// ============================================================

function getLatestNumericValue(
  value: unknown,
): number | null {
  const direct =
    asNullableNumber(value);

  if (direct !== null) {
    return direct;
  }

  if (!isRecord(value)) {
    return null;
  }

  const candidates: Array<{
    key: string;
    value: number;
    sortValue: number;
  }> = [];

  for (const [key, rawValue] of Object.entries(
    value,
  )) {
    const numeric =
      asNullableNumber(rawValue);

    if (numeric === null) {
      continue;
    }

    const yearMatch =
      key.match(/\d{4}/)?.[0];

    const year =
      yearMatch
        ? Number(yearMatch)
        : Number(
            key.replace(/\D/g, ""),
          );

    candidates.push({
      key,
      value: numeric,
      sortValue: Number.isFinite(year)
        ? year
        : 0,
    });
  }

  if (candidates.length === 0) {
    return null;
  }

  candidates.sort(
    (a, b) => {
      if (
        a.sortValue !==
        b.sortValue
      ) {
        return (
          b.sortValue -
          a.sortValue
        );
      }

      return b.key.localeCompare(
        a.key,
      );
    },
  );

  return candidates[0]?.value ?? null;
}

function getLatestFinancialValue(
  record: UnknownRecord,
  ...keys: string[]
): number | null {
  for (const key of keys) {
    if (!(key in record)) {
      continue;
    }

    const value =
      getLatestNumericValue(
        record[key],
      );

    if (value !== null) {
      return value;
    }
  }

  return null;
}

// ============================================================
// Financial Statement Extraction
// ============================================================

function getFinancialData(
  financial: UnknownRecord,
): UnknownRecord {
  return isRecord(
    financial.financial_data,
  )
    ? financial.financial_data
    : isRecord(
        financial.financialData,
      )
      ? financial.financialData
      : financial;
}

function findStatementMetric(
  statement: unknown,
  aliases: string[],
): number | null {
  const normalizedAliases =
    aliases.map(
      (alias) =>
        alias
          .toLowerCase()
          .replace(
            /[^a-z0-9]/g,
            "",
          ),
    );

  const rows =
    asArray<unknown>(
      statement,
    );

  for (const row of rows) {
    if (!isRecord(row)) {
      continue;
    }

    for (const [
      key,
      value,
    ] of Object.entries(row)) {
      const normalizedKey =
        key
          .toLowerCase()
          .replace(
            /[^a-z0-9]/g,
            "",
          );

      const matches =
        normalizedAliases.some(
          (alias) =>
            normalizedKey ===
              alias ||
            normalizedKey.includes(
              alias,
            ) ||
            alias.includes(
              normalizedKey,
            ),
        );

      if (!matches) {
        continue;
      }

      const numeric =
        getLatestNumericValue(
          value,
        );

      if (numeric !== null) {
        return numeric;
      }
    }
  }

  return null;
}

function getIncomeStatement(
  financial: UnknownRecord,
): unknown[] {
  const data =
    getFinancialData(financial);

  return asArray(
    data.income_statement ??
      data.incomeStatement,
  );
}

function getCashFlowStatement(
  financial: UnknownRecord,
): unknown[] {
  const data =
    getFinancialData(financial);

  return asArray(
    data.cash_flow_statement ??
      data.cashFlowStatement ??
      data.cashflow_statement,
  );
}

function getFinancialMetric(
  financial: UnknownRecord,
  aliases: string[],
): number | null {
  const direct =
    getLatestFinancialValue(
      financial,
      ...aliases,
    );

  if (direct !== null) {
    return direct;
  }

  const financialData =
    getFinancialData(
      financial,
    );

  const nested =
    getLatestFinancialValue(
      financialData,
      ...aliases,
    );

  if (nested !== null) {
    return nested;
  }

  const incomeStatement =
    getIncomeStatement(
      financial,
    );

  const incomeValue =
    findStatementMetric(
      incomeStatement,
      aliases,
    );

  if (incomeValue !== null) {
    return incomeValue;
  }

  const cashFlow =
    getCashFlowStatement(
      financial,
    );

  return findStatementMetric(
    cashFlow,
    aliases,
  );
}

// ============================================================
// Formatting
// ============================================================

function formatCurrency(
  value: unknown,
): string | null {
  const number =
    getLatestNumericValue(
      value,
    );

  if (number === null) {
    return null;
  }

  return new Intl.NumberFormat(
    "en-US",
    {
      style: "currency",
      currency: "USD",
      maximumFractionDigits: 2,
    },
  ).format(number);
}

function formatPercent(
  value: unknown,
): string | null {
  const number =
    getLatestNumericValue(
      value,
    );

  if (number === null) {
    return null;
  }

  const percent =
    Math.abs(number) <= 1
      ? number * 100
      : number;

  return `${percent.toFixed(1)}%`;
}

// ============================================================
// Output Unwrapping
// ============================================================

/**
 * Research execution outputs can be nested:
 *
 * output
 *   → data
 *      → result
 *         → output
 *            → actual payload
 *
 * Unwrap repeatedly rather than assuming
 * a single nesting level.
 */
function unwrapOutput(
  output: unknown,
): UnknownRecord {
  let current = output;

  for (let depth = 0; depth < 8; depth++) {
    if (!isRecord(current)) {
      return {};
    }

    if (isRecord(current.data)) {
      current = current.data;
      continue;
    }

    if (isRecord(current.result)) {
      current = current.result;
      continue;
    }

    if (isRecord(current.output)) {
      current = current.output;
      continue;
    }

    return current;
  }

  return isRecord(current)
    ? current
    : {};
}

// ============================================================
// Backend Execution Extraction
// ============================================================

function getExecutions(
  api: ApiResearchResult,
): BackendResearchExecution[] {
  const source =
    api as unknown as UnknownRecord;

  const containers: UnknownRecord[] = [
    source,

    isRecord(source.data)
      ? source.data
      : {},

    isRecord(source.result)
      ? source.result
      : {},

    isRecord(source.output)
      ? source.output
      : {},
  ];

  for (const container of containers) {
    const candidates = [
      container.agent_results,
      container.agentResults,

      container.results,

      container.executions,

      container.execution_results,
      container.executionResults,
    ];

    for (const candidate of candidates) {
      const executions =
        asArray<BackendResearchExecution>(
          candidate,
        );

      if (executions.length > 0) {
        return executions;
      }
    }
  }

  return [];
}

// ============================================================
// Execution Helpers
// ============================================================

function getOutput(
  execution: BackendResearchExecution,
): UnknownRecord {
  return unwrapOutput(
    execution.output ??
      execution.result,
  );
}

function getExecutionName(
  execution: BackendResearchExecution,
): string {
  const metadata =
    isRecord(execution.metadata)
      ? execution.metadata
      : {};

  const output =
    getOutput(execution);

  const agentName =
    isRecord(execution.agent)
      ? firstNonEmpty(
          execution.agent.name,
          execution.agent.agent_name,
          execution.agent.type,
          execution.agent.id,
        )
      : asString(
          execution.agent,
        );

  const outputAgent =
    isRecord(output.agent)
      ? firstNonEmpty(
          output.agent.name,
          output.agent.agent_name,
          output.agent.type,
          output.agent.id,
        )
      : asString(
          output.agent,
        );

  return firstNonEmpty(
    execution.agent_name,

    agentName,

    execution.task_type,
    execution.task_name,

    metadata.agent_name,
    metadata.agent,
    metadata.assigned_executor,
    metadata.executor,
    metadata.task_type,
    metadata.name,

    output.agent_name,

    outputAgent,

    output.type,
    output.task_type,
    output.executor,
  ).toLowerCase();
}

function findExecution(
  executions: BackendResearchExecution[],
  names: string[],
): BackendResearchExecution | null {
  const normalized =
    names.map(
      (name) =>
        name
          .toLowerCase()
          .replace(
            /[\s_-]/g,
            "",
          ),
    );

  return (
    executions.find(
      (execution) => {
        const executionName =
          getExecutionName(
            execution,
          ).replace(
            /[\s_-]/g,
            "",
          );

        if (!executionName) {
          return false;
        }

        return normalized.some(
          (candidate) =>
            executionName ===
              candidate ||
            executionName.includes(
              candidate,
            ) ||
            candidate.includes(
              executionName,
            ),
        );
      },
    ) ?? null
  );
}

function getAgentOutput(
  executions: BackendResearchExecution[],
  names: string[],
): UnknownRecord {
  const execution =
    findExecution(
      executions,
      names,
    );

  return execution
    ? getOutput(execution)
    : {};
}

// ============================================================
// Overview
// ============================================================

function mapOverview(
  api: ApiResearchResult,
  executions: BackendResearchExecution[],
): OverviewData {
  const apiRecord =
    api as unknown as UnknownRecord;

  const financial =
    getAgentOutput(
      executions,
      [
        "financial",
        "financial_agent",
        "financial_analysis",
        "financialanalysis",
      ],
    );

  const industry =
    getAgentOutput(
      executions,
      [
        "industry",
        "industry_agent",
        "industry_analysis",
        "industryanalysis",
      ],
    );

  const companyName =
    firstNonEmpty(
      financial.company,
      financial.company_name,
      industry.company,
      industry.company_name,
      apiRecord.company,
    );

  const description =
    firstNonEmpty(
      financial.description,
      financial.business_description,
      financial.company_description,
      industry.description,
    );

  const sector =
    firstNonEmpty(
      financial.sector,
      industry.sector,
      apiRecord.sector,
    );

  const industryName =
    firstNonEmpty(
      financial.industry,
      industry.industry,
      apiRecord.industry,
    );

  const currentPrice =
    getFinancialMetric(
      financial,
      [
        "current_price",
        "share_price",
        "price",
        "currentPrice",
      ],
    );

  const marketCap =
    getFinancialMetric(
      financial,
      [
        "market_cap",
        "marketCap",
      ],
    );

  const pe =
    getFinancialMetric(
      financial,
      [
        "trailing_pe",
        "pe_ratio",
        "pe",
        "trailingPE",
      ],
    );

  const beta =
    getFinancialMetric(
      financial,
      ["beta"],
    );

  const dividendYield =
    getFinancialMetric(
      financial,
      [
        "dividend_yield",
        "dividendYield",
      ],
    );

  const weekHigh =
    getFinancialMetric(
      financial,
      [
        "52_week_high",
        "fifty_two_week_high",
        "week_52_high",
      ],
    );

  const weekLow =
    getFinancialMetric(
      financial,
      [
        "52_week_low",
        "fifty_two_week_low",
        "week_52_low",
      ],
    );

  const revenue =
    getFinancialMetric(
      financial,
      [
        "revenue",
        "total_revenue",
        "totalRevenue",
      ],
    );

  const revenueGrowth =
    getFinancialMetric(
      financial,
      [
        "revenue_growth",
        "revenueGrowth",
      ],
    );

  const operatingIncome =
    getFinancialMetric(
      financial,
      [
        "operating_income",
        "operatingIncome",
      ],
    );

  let operatingMargin =
    getFinancialMetric(
      financial,
      [
        "operating_margin",
        "operatingMargin",
      ],
    );

  if (
    operatingMargin === null &&
    revenue !== null &&
    operatingIncome !== null &&
    revenue !== 0
  ) {
    operatingMargin =
      operatingIncome /
      revenue;
  }

  const grossMargin =
    getFinancialMetric(
      financial,
      [
        "gross_margin",
        "grossMargin",
      ],
    );

  const eps =
    getFinancialMetric(
      financial,
      [
        "eps",
        "trailing_eps",
        "trailingEps",
      ],
    );

  const headquarters =
    firstNonEmpty(
      financial.headquarters,
      financial.location,

      financial.city &&
        financial.state
        ? `${asString(
            financial.city,
          )}, ${asString(
            financial.state,
          )}`
        : "",
    );

  const website =
    firstNonEmpty(
      financial.website,
      industry.website,
    );

  const hasProfileData =
    Boolean(
      companyName ||
      description ||
      sector ||
      industryName ||
      headquarters ||
      asString(
        financial.ceo,
      ) ||
      asString(
        financial.employees,
      ) ||
      asString(
        financial.founded,
      ) ||
      website,
    );

  const explicitWeekRange =
    firstNonEmpty(
      financial.fifty_two_week_range,
      financial.week_range_52,
      financial.weekRange52,
    );

  const computedWeekRange =
    weekHigh !== null &&
    weekLow !== null
      ? `${formatCurrency(
          weekLow,
        )} - ${formatCurrency(
          weekHigh,
        )}`
      : "";

  const hasMarketData =
    currentPrice !== null ||
    marketCap !== null ||
    pe !== null ||
    beta !== null ||
    dividendYield !== null ||
    weekHigh !== null ||
    weekLow !== null ||
    Boolean(explicitWeekRange);

  const hasFinancialData =
    revenue !== null ||
    revenueGrowth !== null ||
    grossMargin !== null ||
    operatingMargin !== null ||
    eps !== null;

  return {
    profile: hasProfileData
      ? {
          description:
            asNullableString(
              description,
            ),

          sector:
            asNullableString(
              sector,
            ),

          industry:
            asNullableString(
              industryName,
            ),

          headquarters:
            asNullableString(
              headquarters,
            ),

          ceo:
            asNullableString(
              financial.ceo,
            ),

          employees:
            asNullableString(
              financial.employees,
            ),

          founded:
            asNullableString(
              financial.founded,
            ),

          website:
            asNullableString(
              website,
            ),
        }
      : null,

    market: hasMarketData
      ? {
          marketCap:
            formatCurrency(
              marketCap,
            ),

          sharePrice:
            formatCurrency(
              currentPrice,
            ),

          peRatio:
            pe !== null
              ? pe.toFixed(2)
              : null,

          weekRange52:
            explicitWeekRange ||
            computedWeekRange ||
            null,

          dividendYield:
            formatPercent(
              dividendYield,
            ),

          beta:
            beta !== null
              ? beta.toFixed(2)
              : null,
        }
      : null,

    financials: hasFinancialData
      ? {
          revenue:
            formatCurrency(
              revenue,
            ),

          revenueGrowth:
            formatPercent(
              revenueGrowth,
            ),

          grossMargin:
            formatPercent(
              grossMargin,
            ),

          operatingMargin:
            formatPercent(
              operatingMargin,
            ),

          eps:
            eps !== null
              ? formatCurrency(
                  eps,
                )
              : asNullableString(
                  financial.eps ??
                    financial.trailing_eps,
                ),
        }
      : null,
  };
}

// ============================================================
// Persisted Overview
// ============================================================

function getTopLevelOverview(
  api: ApiResearchResult,
): OverviewData | null {
  const apiRecord =
    api as unknown as UnknownRecord;

  const raw =
    apiRecord.overview;

  if (!isRecord(raw)) {
    return null;
  }

  const profile =
    isRecord(raw.profile)
      ? raw.profile
      : null;

  const market =
    isRecord(raw.market)
      ? raw.market
      : null;

  const financials =
    isRecord(raw.financials)
      ? raw.financials
      : null;

  if (
    !profile &&
    !market &&
    !financials
  ) {
    return null;
  }

  return {
    profile: profile
      ? {
          description:
            asNullableString(
              profile.description,
            ),

          sector:
            asNullableString(
              profile.sector,
            ),

          industry:
            asNullableString(
              profile.industry,
            ),

          headquarters:
            asNullableString(
              profile.headquarters,
            ),

          ceo:
            asNullableString(
              profile.ceo,
            ),

          employees:
            asNullableString(
              profile.employees,
            ),

          founded:
            asNullableString(
              profile.founded,
            ),

          website:
            asNullableString(
              profile.website,
            ),
        }
      : null,

    market: market
      ? {
          marketCap:
            asNullableString(
              market.marketCap,
            ),

          sharePrice:
            asNullableString(
              market.sharePrice,
            ),

          peRatio:
            asNullableString(
              market.peRatio,
            ),

          weekRange52:
            asNullableString(
              market.weekRange52,
            ),

          dividendYield:
            asNullableString(
              market.dividendYield,
            ),

          beta:
            asNullableString(
              market.beta,
            ),
        }
      : null,

    financials: financials
      ? {
          revenue:
            asNullableString(
              financials.revenue,
            ),

          revenueGrowth:
            asNullableString(
              financials.revenueGrowth,
            ),

          grossMargin:
            asNullableString(
              financials.grossMargin,
            ),

          operatingMargin:
            asNullableString(
              financials.operatingMargin,
            ),

          eps:
            asNullableString(
              financials.eps,
            ),
        }
      : null,
  };
}

// ============================================================
// Evidence
// ============================================================

/**
 * Evidence can arrive from many backend shapes.
 *
 * Supported examples:
 *
 * {
 *   evidence: [...]
 * }
 *
 * {
 *   claims: [...]
 * }
 *
 * {
 *   matched_evidence: [...]
 * }
 *
 * {
 *   citations: [...]
 * }
 *
 * {
 *   sources: [...]
 * }
 *
 * {
 *   verified_claims: [...]
 * }
 *
 * {
 *   findings: [...]
 * }
 *
 * and these can be nested inside:
 *
 *   data
 *   result
 *   output
 *   agent_results
 *   results
 *   executions
 */
function mapEvidenceFromItems(
  items: unknown[],
  executionId = "evidence",
): ResearchEvidenceItem[] {
  return items
    .map(
      (item, index) => {
        if (
          !isRecord(item)
        ) {
          return null;
        }

        const claim =
          firstNonEmpty(
            item.claim,
            item.statement,
            item.text,
            item.description,
            item.finding,
            item.conclusion,
            item.observation,
            item.content,
            item.value,
          );

        /*
         * A document/citation without a claim is not
         * automatically evidence.
         *
         * We only expose objects that contain actual
         * textual evidence content.
         */
        if (!claim) {
          return null;
        }

        const source =
          firstNonEmpty(
            item.source,
            item.source_name,
            item.sourceName,
            item.provider,
            item.document,
            item.document_title,
            item.documentTitle,
            item.filename,
            item.file_name,
            item.fileName,
            item.reference,
          );

        const citation =
          firstNonEmpty(
            item.citation,
            item.citation_text,
            item.citationText,
            item.quote,
            item.excerpt,
            item.url,
            item.source_url,
            item.sourceUrl,
          );

        const date =
          asNullableString(
            item.date ??
              item.published_at ??
              item.publishedAt ??
              item.filing_date ??
              item.filingDate,
          ) ??
          undefined;

        const category =
          asNullableString(
            item.category ??
              item.type ??
              item.evidence_type ??
              item.evidenceType ??
              item.source_type ??
              item.sourceType,
          ) ??
          undefined;

        const confidence =
          normalizeConfidence(
            item.confidence ??
              item.score ??
              item.relevance ??
              item.relevance_score ??
              item.relevanceScore,
          );

        /*
         * Backend IDs are preferred.
         *
         * The fallback is only a React/data-item identifier.
         * It is NOT used as a research ID.
         */
        const id =
          firstNonEmpty(
            item.id,
            item.evidence_id,
            item.evidenceId,
            item.claim_id,
            item.claimId,
            item.finding_id,
            item.findingId,
          ) ||
          `${executionId}-${index}`;

        return {
          id,

          claim,

          source,

          confidence,

          date,

          category,

          citation,
        };
      },
    )
    .filter(
      (
        item,
      ): item is ResearchEvidenceItem =>
        item !== null,
    );
}

// ------------------------------------------------------------
// Evidence Candidate Extraction
// ------------------------------------------------------------

const EVIDENCE_KEYS = [
  "evidence",

  "evidence_items",
  "evidenceItems",

  "claims",

  "verified_claims",
  "verifiedClaims",

  "matched_evidence",
  "matchedEvidence",

  "supporting_evidence",
  "supportingEvidence",

  "supporting_claims",
  "supportingClaims",

  "citations",

  "findings",

  "observations",

  "key_findings",
  "keyFindings",

  "research_findings",
  "researchFindings",

  "references",

  "sources",
];

function collectEvidenceArrays(
  value: unknown,
  results: unknown[][],
  depth = 0,
): void {
  if (depth > 6) {
    return;
  }

  if (Array.isArray(value)) {
    for (const item of value) {
      collectEvidenceArrays(
        item,
        results,
        depth + 1,
      );
    }

    return;
  }

  if (!isRecord(value)) {
    return;
  }

  for (const key of EVIDENCE_KEYS) {
    const candidate =
      value[key];

    if (
      Array.isArray(candidate) &&
      candidate.length > 0
    ) {
      results.push(
        candidate,
      );
    }
  }

  /*
   * Continue through common wrappers.
   */
  const nestedKeys = [
    "data",
    "result",
    "output",
    "research",
    "payload",
    "response",
  ];

  for (const key of nestedKeys) {
    if (value[key] !== undefined) {
      collectEvidenceArrays(
        value[key],
        results,
        depth + 1,
      );
    }
  }
}

function extractEvidenceCandidates(
  value: unknown,
): unknown[] {
  const arrays: unknown[][] = [];

  collectEvidenceArrays(
    value,
    arrays,
  );

  return arrays.flat();
}

// ------------------------------------------------------------
// Evidence Object Detection
// ------------------------------------------------------------

function looksLikeEvidenceObject(
  value: unknown,
): boolean {
  if (!isRecord(value)) {
    return false;
  }

  const hasClaim =
    Boolean(
      firstNonEmpty(
        value.claim,
        value.statement,
        value.text,
        value.description,
        value.finding,
        value.conclusion,
        value.observation,
        value.content,
      ),
    );

  const hasEvidenceMetadata =
    Boolean(
      firstNonEmpty(
        value.source,
        value.source_name,
        value.sourceName,
        value.citation,
        value.quote,
        value.excerpt,
        value.evidence_id,
        value.evidenceId,
        value.claim_id,
        value.claimId,
      ),
    );

  return (
    hasClaim &&
    (
      hasEvidenceMetadata ||
      "confidence" in value ||
      "score" in value ||
      "category" in value ||
      "type" in value
    )
  );
}

// ------------------------------------------------------------
// Recursive Evidence Discovery
// ------------------------------------------------------------

function collectEvidenceObjects(
  value: unknown,
  results: UnknownRecord[],
  depth = 0,
): void {
  if (depth > 7) {
    return;
  }

  if (Array.isArray(value)) {
    for (const item of value) {
      if (
        looksLikeEvidenceObject(
          item,
        )
      ) {
        results.push(
          item as UnknownRecord,
        );
      } else {
        collectEvidenceObjects(
          item,
          results,
          depth + 1,
        );
      }
    }

    return;
  }

  if (!isRecord(value)) {
    return;
  }

  if (
    looksLikeEvidenceObject(
      value,
    )
  ) {
    results.push(value);
  }

  for (const [
    key,
    child,
  ] of Object.entries(value)) {
    /*
     * Skip obviously unrelated scalar fields.
     */
    if (
      typeof child !==
        "object" ||
      child === null
    ) {
      continue;
    }

    /*
     * Avoid recursively treating arbitrary financial
     * numbers/objects as evidence unless they contain
     * evidence-like structures.
     */
    const normalizedKey =
      key
        .toLowerCase()
        .replace(
          /[\s_-]/g,
          "",
        );

    const likelyEvidenceContainer =
      EVIDENCE_KEYS.some(
        (candidate) =>
          candidate
            .toLowerCase()
            .replace(
              /[\s_-]/g,
              "",
            ) ===
          normalizedKey,
      );

    if (
      likelyEvidenceContainer ||
      normalizedKey === "data" ||
      normalizedKey === "result" ||
      normalizedKey === "output" ||
      normalizedKey === "research" ||
      normalizedKey === "payload" ||
      normalizedKey === "response"
    ) {
      collectEvidenceObjects(
        child,
        results,
        depth + 1,
      );
    }
  }
}

// ------------------------------------------------------------
// Evidence Dedupe
// ------------------------------------------------------------

function dedupeEvidence(
  evidence: ResearchEvidenceItem[],
): ResearchEvidenceItem[] {
  const seenIds =
    new Set<string>();

  const seenContent =
    new Set<string>();

  return evidence.filter(
    (item) => {
      const id =
        firstNonEmpty(
          item.id,
        );

      const content =
        [
          item.claim,
          item.source,
          item.date,
          item.citation,
        ]
          .map(
            (value) =>
              asString(value)
                .toLowerCase(),
          )
          .join("|");

      if (
        id &&
        seenIds.has(id)
      ) {
        return false;
      }

      if (
        content &&
        seenContent.has(content)
      ) {
        return false;
      }

      if (id) {
        seenIds.add(id);
      }

      if (content) {
        seenContent.add(
          content,
        );
      }

      return true;
    },
  );
}

// ------------------------------------------------------------
// Evidence Mapper
// ------------------------------------------------------------

function mapEvidence(
  api: ApiResearchResult,
  executions: BackendResearchExecution[],
): ResearchEvidenceItem[] {
  const apiRecord =
    api as unknown as UnknownRecord;

  const evidence: ResearchEvidenceItem[] =
    [];

  // ----------------------------------------------------------
  // 1. Direct top-level evidence
  // ----------------------------------------------------------

  const topLevelCandidates = [
    apiRecord.evidence,
    apiRecord.evidence_items,
    apiRecord.evidenceItems,

    apiRecord.claims,

    apiRecord.verified_claims,
    apiRecord.verifiedClaims,

    apiRecord.matched_evidence,
    apiRecord.matchedEvidence,

    apiRecord.supporting_evidence,
    apiRecord.supportingEvidence,

    apiRecord.citations,
  ];

  for (
    const candidate of
      topLevelCandidates
  ) {
    const items =
      asArray<unknown>(
        candidate,
      );

    if (
      items.length === 0
    ) {
      continue;
    }

    evidence.push(
      ...mapEvidenceFromItems(
        items,
        "evidence",
      ),
    );
  }

  // ----------------------------------------------------------
  // 2. Wrapped top-level containers
  // ----------------------------------------------------------

  const containers: unknown[] = [
    apiRecord.data,
    apiRecord.result,
    apiRecord.output,
    apiRecord.research,
    apiRecord.payload,
    apiRecord.response,
  ];

  for (
    const container of containers
  ) {
    if (!container) {
      continue;
    }

    const candidates =
      extractEvidenceCandidates(
        container,
      );

    if (
      candidates.length > 0
    ) {
      evidence.push(
        ...mapEvidenceFromItems(
          candidates,
          "evidence",
        ),
      );
    }

    /*
     * Recursive object discovery catches structures
     * such as:
     *
     * result:
     *   financial_analysis:
     *     verified_claims: [...]
     */
    const objects: UnknownRecord[] =
      [];

    collectEvidenceObjects(
      container,
      objects,
    );

    if (
      objects.length > 0
    ) {
      evidence.push(
        ...mapEvidenceFromItems(
          objects,
          "evidence",
        ),
      );
    }
  }

  // ----------------------------------------------------------
  // 3. Inspect EVERY successful execution
  // ----------------------------------------------------------
  //
  // This is the important fix.
  //
  // Previously we only looked for an execution whose
  // name was "evidence".
  //
  // Real research pipelines frequently return evidence
  // from:
  //
  //   financial analyst
  //   industry analyst
  //   valuation analyst
  //   risk analyst
  //   document researcher
  //   verification agent
  //   research analyst
  //   investment committee
  //
  // We therefore inspect every successful execution.
  // ----------------------------------------------------------

  for (
    const execution of executions
  ) {
    if (
      execution.success ===
      false
    ) {
      continue;
    }

    const output =
      getOutput(
        execution,
      );

    if (
      Object.keys(output)
        .length === 0
    ) {
      continue;
    }

    const executionId =
      firstNonEmpty(
        execution.execution_id,
        execution.task_id,
        execution.trace_id,
      ) ||
      "evidence";

    // --------------------------------------------------------
    // Explicit evidence fields
    // --------------------------------------------------------

    const explicitCandidates = [
      output.evidence,

      output.evidence_items,
      output.evidenceItems,

      output.claims,

      output.verified_claims,
      output.verifiedClaims,

      output.matched_evidence,
      output.matchedEvidence,

      output.supporting_evidence,
      output.supportingEvidence,

      output.supporting_claims,
      output.supportingClaims,

      output.citations,

      output.findings,

      output.observations,

      output.key_findings,
      output.keyFindings,

      output.research_findings,
      output.researchFindings,

      output.references,

      output.sources,
    ];

    for (
      const candidate of
        explicitCandidates
    ) {
      const items =
        asArray<unknown>(
          candidate,
        );

      if (
        items.length === 0
      ) {
        continue;
      }

      evidence.push(
        ...mapEvidenceFromItems(
          items,
          executionId,
        ),
      );
    }

    // --------------------------------------------------------
    // Deep evidence discovery inside execution output
    // --------------------------------------------------------

    const discoveredObjects:
      UnknownRecord[] =
      [];

    collectEvidenceObjects(
      output,
      discoveredObjects,
    );

    if (
      discoveredObjects.length >
      0
    ) {
      evidence.push(
        ...mapEvidenceFromItems(
          discoveredObjects,
          executionId,
        ),
      );
    }
  }

  return dedupeEvidence(
    evidence,
  );
}

// ============================================================
// Documents
// ============================================================

function mapDocumentsFromItems(
  items: unknown[],
  executionId = "document",
): ResearchDocument[] {
  const documents:
    ResearchDocument[] =
    [];

  items.forEach(
    (item, index) => {
      if (
        !isRecord(item)
      ) {
        return;
      }

      const title =
        firstNonEmpty(
          item.title,
          item.name,
          item.document_title,
          item.documentTitle,
          item.filename,
          item.file_name,
          item.fileName,
          item.display_name,
          item.displayName,
          item.source_name,
          item.sourceName,
        );

      if (!title) {
        return;
      }

      const rawStatus =
        asString(
          item.status,
        ).toLowerCase();

      let status:
        | "processing"
        | "processed"
        | "failed"
        | undefined;

      if (
        rawStatus === "failed" ||
        rawStatus === "error"
      ) {
        status = "failed";
      } else if (
        rawStatus ===
          "processing" ||
        rawStatus ===
          "pending" ||
        rawStatus ===
          "queued" ||
        rawStatus ===
          "running"
      ) {
        status = "processing";
      } else if (
        rawStatus ===
          "processed" ||
        rawStatus ===
          "complete" ||
        rawStatus ===
          "completed" ||
        rawStatus ===
          "success" ||
        rawStatus ===
          "succeeded"
      ) {
        status = "processed";
      }

      documents.push({
        id:
          firstNonEmpty(
            item.id,
            item.document_id,
            item.documentId,
            item.source_id,
            item.sourceId,
            item.file_id,
            item.fileId,
            item.uuid,
          ) ||
          `${executionId}-${index}`,

        title,

        source:
          firstNonEmpty(
            item.source,
            item.source_name,
            item.sourceName,
            item.provider,
            item.url,
          ),

        date:
          asNullableString(
            item.date ??
              item.published_at ??
              item.publishedAt ??
              item.filing_date ??
              item.filingDate,
          ) ??
          undefined,

        status,

        type:
          firstNonEmpty(
            item.type,
            item.document_type,
            item.documentType,
            item.mime_type,
            item.mimeType,
          ),

        size:
          asNullableString(
            item.size ??
              item.file_size ??
              item.fileSize,
          ) ??
          undefined,
      });
    },
  );

  return documents;
}

function collectNestedDocuments(
  value: unknown,
  results: unknown[],
  depth = 0,
): void {
  if (
    depth > 6
  ) {
    return;
  }

  if (
    Array.isArray(value)
  ) {
    for (
      const item of value
    ) {
      collectNestedDocuments(
        item,
        results,
        depth + 1,
      );
    }

    return;
  }

  if (
    !isRecord(value)
  ) {
    return;
  }

  const documentKeys = [
    "documents",
    "document",

    "sources",

    "source_documents",
    "sourceDocuments",

    "retrieved_documents",
    "retrievedDocuments",

    "retrieved_docs",
    "retrievedDocs",

    "research_documents",
    "researchDocuments",

    "reference_documents",
    "referenceDocuments",

    "references",

    "filings",

    "reports",

    "transcripts",

    "articles",
  ];

  for (
    const key of documentKeys
  ) {
    const candidate =
      value[key];

    if (
      Array.isArray(
        candidate,
      )
    ) {
      results.push(
        ...candidate,
      );
    }
  }

  const nestedKeys = [
    "data",
    "result",
    "output",
    "research",
    "payload",
    "response",
  ];

  for (
    const key of nestedKeys
  ) {
    if (
      value[key] !== undefined
    ) {
      collectNestedDocuments(
        value[key],
        results,
        depth + 1,
      );
    }
  }
}

function mapDocuments(
  api: ApiResearchResult,
  executions: BackendResearchExecution[],
): ResearchDocument[] {
  const apiRecord =
    api as unknown as UnknownRecord;

  const candidates:
    unknown[] =
    [];

  collectNestedDocuments(
    apiRecord,
    candidates,
  );

  const documents:
    ResearchDocument[] =
    [];

  if (
    candidates.length > 0
  ) {
    documents.push(
      ...mapDocumentsFromItems(
        candidates,
        "document",
      ),
    );
  }

  for (
    const execution of executions
  ) {
    if (
      execution.success ===
      false
    ) {
      continue;
    }

    const output =
      getOutput(
        execution,
      );

    const executionDocuments:
      unknown[] =
      [];

    collectNestedDocuments(
      output,
      executionDocuments,
    );

    if (
      executionDocuments.length ===
      0
    ) {
      continue;
    }

    documents.push(
      ...mapDocumentsFromItems(
        executionDocuments,
        firstNonEmpty(
          execution.execution_id,
          execution.task_id,
        ) ||
          "document",
      ),
    );
  }

  return dedupeDocuments(
    documents,
  );
}

function dedupeDocuments(
  documents: ResearchDocument[],
): ResearchDocument[] {
  const seen =
    new Set<string>();

  return documents.filter(
    (document) => {
      const key =
        firstNonEmpty(
          document.id,
          document.title,
        );

      if (!key) {
        return true;
      }

      if (
        seen.has(key)
      ) {
        return false;
      }

      seen.add(key);

      return true;
    },
  );
}

// ============================================================
// Insights
// ============================================================

function mapInsightsFromItems(
  items: unknown[],
  defaultType:
    | "insight"
    | "risk"
    | "catalyst",
): ResearchInsight[] {
  return items
    .map(
      (item, index) => {
        if (
          !isRecord(item) &&
          typeof item !==
            "string"
        ) {
          return null;
        }

        const description =
          isRecord(item)
            ? firstNonEmpty(
                item.description,
                item.statement,
                item.text,
                item.claim,
                item.finding,
                item.summary,
                item.risk,
                item.reason,
                item.value,
                item.name,
                item.title,
              )
            : asString(item);

        if (!description) {
          return null;
        }

        const rawType =
          isRecord(item)
            ? asString(
                item.type,
              ).toLowerCase()
            : defaultType;

        const normalizedType =
          rawType === "risk"
            ? "risk"
            : rawType ===
                "catalyst"
              ? "catalyst"
              : defaultType;

        const id =
          isRecord(item)
            ? firstNonEmpty(
                item.id,
                item.insight_id,
                item.insightId,
                item.finding_id,
                item.findingId,
                item.claim_id,
                item.claimId,
              ) ||
              `${defaultType}-${index}`
            : `${defaultType}-${index}`;

        const title =
          isRecord(item)
            ? firstNonEmpty(
                item.title,
                item.name,
                item.heading,
                item.label,
              )
            : "";

        return {
          id,

          type:
            normalizedType,

          title,

          description,

          confidence:
            isRecord(item)
              ? normalizeConfidence(
                  item.confidence ??
                    item.score ??
                    item.relevance,
                )
              : 0,
        };
      },
    )
    .filter(
      (
        item,
      ): item is ResearchInsight =>
        item !== null,
    );
}

function dedupeInsights(
  insights: ResearchInsight[],
): ResearchInsight[] {
  const seenIds =
    new Set<string>();

  const seenContent =
    new Set<string>();

  return insights.filter(
    (insight) => {
      const id =
        firstNonEmpty(
          insight.id,
        );

      const content =
        `${insight.type}|${insight.title}|${insight.description}`
          .trim()
          .toLowerCase();

      if (
        id &&
        seenIds.has(id)
      ) {
        return false;
      }

      if (
        content &&
        seenContent.has(content)
      ) {
        return false;
      }

      if (id) {
        seenIds.add(id);
      }

      if (content) {
        seenContent.add(
          content,
        );
      }

      return true;
    },
  );
}

function mapInsights(
  api: ApiResearchResult,
  executions: BackendResearchExecution[],
): ResearchInsight[] {
  const apiRecord =
    api as unknown as UnknownRecord;

  const topLevelCandidates = [
    apiRecord.insights,

    apiRecord.key_insights,
    apiRecord.keyInsights,

    apiRecord.findings,

    apiRecord.key_findings,
    apiRecord.keyFindings,

    apiRecord.highlights,

    apiRecord.observations,
  ];

  const direct:
    ResearchInsight[] =
    [];

  for (
    const candidate of
      topLevelCandidates
  ) {
    const items =
      asArray<unknown>(
        candidate,
      );

    if (
      items.length ===
      0
    ) {
      continue;
    }

    direct.push(
      ...mapInsightsFromItems(
        items,
        "insight",
      ),
    );
  }

  if (
    direct.length > 0
  ) {
    return dedupeInsights(
      direct,
    );
  }

  const insights:
    ResearchInsight[] =
    [];

  for (
    const execution of executions
  ) {
    if (
      execution.success ===
      false
    ) {
      continue;
    }

    const output =
      getOutput(
        execution,
      );

    const executionName =
      getExecutionName(
        execution,
      ).replace(
        /[\s_-]/g,
        "",
      );

    const risks = [
      ...asArray<unknown>(
        output.risks,
      ),

      ...asArray<unknown>(
        output.key_risks,
      ),

      ...asArray<unknown>(
        output.keyRisks,
      ),

      ...asArray<unknown>(
        output.risk_factors,
      ),

      ...asArray<unknown>(
        output.riskFactors,
      ),

      ...asArray<unknown>(
        output.downside_risks,
      ),

      ...asArray<unknown>(
        output.downsideRisks,
      ),
    ];

    if (
      risks.length > 0
    ) {
      insights.push(
        ...mapInsightsFromItems(
          risks,
          "risk",
        ),
      );
    }

    const catalysts = [
      ...asArray<unknown>(
        output.catalysts,
      ),

      ...asArray<unknown>(
        output.growth_catalysts,
      ),

      ...asArray<unknown>(
        output.growthCatalysts,
      ),

      ...asArray<unknown>(
        output.upside_catalysts,
      ),

      ...asArray<unknown>(
        output.upsideCatalysts,
      ),
    ];

    if (
      catalysts.length > 0
    ) {
      insights.push(
        ...mapInsightsFromItems(
          catalysts,
          "catalyst",
        ),
      );
    }

    const findings = [
      ...asArray<unknown>(
        output.insights,
      ),

      ...asArray<unknown>(
        output.key_insights,
      ),

      ...asArray<unknown>(
        output.keyInsights,
      ),

      ...asArray<unknown>(
        output.findings,
      ),

      ...asArray<unknown>(
        output.key_findings,
      ),

      ...asArray<unknown>(
        output.keyFindings,
      ),

      ...asArray<unknown>(
        output.highlights,
      ),

      ...asArray<unknown>(
        output.observations,
      ),

      ...asArray<unknown>(
        output.key_observations,
      ),

      ...asArray<unknown>(
        output.keyObservations,
      ),

      ...asArray<unknown>(
        output.conclusions,
      ),
    ];

    if (
      findings.length > 0
    ) {
      insights.push(
        ...mapInsightsFromItems(
          findings,
          "insight",
        ),
      );
    }

    const thesis =
      firstNonEmpty(
        output.thesis,
        output.investment_thesis,
        output.investmentThesis,
        output.investment_case,
        output.investmentCase,
        output.core_thesis,
        output.coreThesis,
      );

    if (thesis) {
      insights.push({
        id:
          `${executionName || "execution"}-investment-thesis`,

        type: "insight",

        title:
          "Investment Thesis",

        description:
          thesis,

        confidence:
          normalizeConfidence(
            output.confidence,
          ),
      });
    }

    const recommendation =
      firstNonEmpty(
        output.recommendation,
        output.investment_recommendation,
        output.investmentRecommendation,
        output.rating,
        output.signal,
        output.investment_rating,
        output.investmentRating,
      );

    if (
      recommendation &&
      (
        executionName.includes(
          "committee",
        ) ||
        executionName.includes(
          "recommend",
        ) ||
        executionName.includes(
          "investment",
        )
      )
    ) {
      insights.push({
        id:
          `${executionName || "execution"}-recommendation`,

        type: "insight",

        title:
          "Recommendation",

        description:
          recommendation,

        confidence:
          normalizeConfidence(
            output.confidence,
          ),
      });
    }

    const overallRisk =
      firstNonEmpty(
        output.overall_risk,
        output.overallRisk,
        output.risk_rating,
        output.riskRating,
        output.risk_level,
        output.riskLevel,
      );

    if (
      overallRisk &&
      (
        executionName.includes(
          "risk",
        ) ||
        executionName.includes(
          "committee",
        ) ||
        executionName.includes(
          "investment",
        )
      )
    ) {
      insights.push({
        id:
          `${executionName || "execution"}-overall-risk`,

        type: "risk",

        title:
          "Overall Risk",

        description:
          overallRisk,

        confidence:
          normalizeConfidence(
            output.confidence,
          ),
      });
    }
  }

  return dedupeInsights(
    insights,
  );
}

// ============================================================
// Report Formatting
// ============================================================

function formatReportKey(
  key: string,
): string {
  return key
    .replace(
      /_/g,
      " ",
    )
    .replace(
      /([a-z])([A-Z])/g,
      "$1 $2",
    )
    .replace(
      /\b\w/g,
      (char) =>
        char.toUpperCase(),
    );
}

function textFromValue(
  value: unknown,
  depth = 0,
): string {
  if (
    depth > 6
  ) {
    return "";
  }

  if (
    typeof value ===
    "string"
  ) {
    return value.trim();
  }

  if (
    typeof value ===
      "number" ||
    typeof value ===
      "boolean"
  ) {
    return String(value);
  }

  if (
    Array.isArray(value)
  ) {
    return value
      .map(
        (item) =>
          textFromValue(
            item,
            depth + 1,
          ),
      )
      .filter(Boolean)
      .join("\n\n");
  }

  if (
    isRecord(value)
  ) {
    return Object.entries(
      value,
    )
      .map(
        ([key, item]) => {
          const text =
            textFromValue(
              item,
              depth + 1,
            );

          if (!text) {
            return "";
          }

          return `${formatReportKey(
            key,
          )}: ${text}`;
        },
      )
      .filter(Boolean)
      .join("\n");
  }

  return "";
}

function addReportSection(
  sections: ReportSection[],
  id: string,
  title: string,
  execution:
    | BackendResearchExecution
    | null,
): void {
  if (!execution) {
    return;
  }

  if (
    execution.success ===
    false
  ) {
    return;
  }

  const output =
    getOutput(
      execution,
    );

  const content =
    textFromValue(
      output,
    );

  if (!content) {
    return;
  }

  sections.push({
    id,

    title,

    status:
      "complete",

    content,

    lastUpdated:
      getExecutionTimestamp(
        execution,
      ) ??
      undefined,
  });
}

// ============================================================
// Top-Level Report
// ============================================================

function mapTopLevelReport(
  api: ApiResearchResult,
): ResearchReport | null {
  const apiRecord =
    api as unknown as UnknownRecord;

  const raw =
    apiRecord.report;

  if (
    !isRecord(raw)
  ) {
    return null;
  }

  const rawSections =
    asArray<unknown>(
      raw.sections,
    );

  const sections =
    rawSections
      .map(
        (
          section,
          index,
        ) => {
          if (
            !isRecord(
              section,
            )
          ) {
            return null;
          }

          const content =
            textFromValue(
              section.content,
            );

          if (!content) {
            return null;
          }

          const rawStatus =
            asString(
              section.status,
            ).toLowerCase();

          let status:
            | "complete"
            | "in-progress"
            | "waiting" =
            "complete";

          if (
            rawStatus ===
              "in-progress" ||
            rawStatus ===
              "running"
          ) {
            status =
              "in-progress";
          } else if (
            rawStatus ===
              "waiting" ||
            rawStatus ===
              "pending"
          ) {
            status =
              "waiting";
          }

          const id =
            firstNonEmpty(
              section.id,
            ) ||
            `section-${index}`;

          const title =
            firstNonEmpty(
              section.title,
            ) ||
            id;

          return {
            id,

            title,

            status,

            content,

            lastUpdated:
              firstNonEmpty(
                section.lastUpdated,
                section.last_updated,
              ) ||
              undefined,
          };
        },
      )
      .filter(
        (
          section,
        ): section is ReportSection =>
          section !== null,
      );

  if (
    sections.length ===
    0
  ) {
    return null;
  }

  return {
    title:
      firstNonEmpty(
        raw.title,
      ) ||
      null,

    sections,
  };
}

// ============================================================
// Report
// ============================================================

function mapReport(
  api: ApiResearchResult,
  executions: BackendResearchExecution[],
): ResearchReport {
  const topLevelReport =
    mapTopLevelReport(
      api,
    );

  if (
    topLevelReport
  ) {
    return topLevelReport;
  }

  const sections:
    ReportSection[] =
    [];

  const apiRecord =
    api as unknown as UnknownRecord;

  const summary =
    textFromValue(
      apiRecord.summary,
    );

  if (summary) {
    sections.push({
      id:
        "executive-summary",

      title:
        "Executive Summary",

      status:
        "complete",

      content:
        summary,

      lastUpdated:
        getTimestamp(
          apiRecord.completed_at,
        ) ??
        getTimestamp(
          apiRecord.updated_at,
        ) ??
        undefined,
    });
  }

  addReportSection(
    sections,
    "financial-analysis",
    "Financial Analysis",
    findExecution(
      executions,
      [
        "financial",
        "financial_agent",
        "financial_analysis",
      ],
    ),
  );

  addReportSection(
    sections,
    "industry-analysis",
    "Industry Analysis",
    findExecution(
      executions,
      [
        "industry",
        "industry_agent",
        "industry_analysis",
      ],
    ),
  );

  addReportSection(
    sections,
    "valuation",
    "Valuation",
    findExecution(
      executions,
      [
        "valuation",
        "valuation_agent",
        "valuation_analysis",
      ],
    ),
  );

  addReportSection(
    sections,
    "risk-analysis",
    "Risk Analysis",
    findExecution(
      executions,
      [
        "risk",
        "risk_agent",
        "risk_analysis",
      ],
    ),
  );

  addReportSection(
    sections,
    "research-verification",
    "Research Verification",
    findExecution(
      executions,
      [
        "critic",
        "critic_agent",
        "verification",
        "research_verification",
      ],
    ),
  );

  addReportSection(
    sections,
    "investment-conclusion",
    "Investment Conclusion",
    findExecution(
      executions,
      [
        "investment_committee",
        "investment committee",
        "investmentcommittee",
        "committee",
      ],
    ),
  );

  return {
    title:
      firstNonEmpty(
        apiRecord.title,
      ) ||
      null,

    sections,
  };
}

// ============================================================
// Stages
// ============================================================

function mapStages(
  executions: BackendResearchExecution[],
): ResearchStageInfo[] {
  if (
    executions.length ===
    0
  ) {
    return [];
  }

  return executions
    .map(
      (
        execution,
        index,
      ) => {
        const name =
          firstNonEmpty(
            execution.task_name,
            execution.task_type,
            execution.agent_name,
            execution.agent,
          );

        if (!name) {
          return null;
        }

        const executionId =
          firstNonEmpty(
            execution.execution_id,
            execution.task_id,
          ) ||
          `execution-${index}`;

        const rawStatus =
          firstNonEmpty(
            execution.status,
          ).toLowerCase();

        const success =
          execution.success;

        let status:
          | "waiting"
          | "in-progress"
          | "complete"
          | "failed";

        if (
          success === false ||
          rawStatus === "failed" ||
          rawStatus === "error"
        ) {
          status =
            "failed";
        } else if (
          rawStatus ===
            "completed" ||
          rawStatus ===
            "complete" ||
          rawStatus ===
            "success" ||
          rawStatus ===
            "succeeded" ||
          success === true
        ) {
          status =
            "complete";
        } else if (
          rawStatus ===
            "running" ||
          rawStatus ===
            "in-progress" ||
          rawStatus ===
            "in_progress" ||
          rawStatus ===
            "processing"
        ) {
          status =
            "in-progress";
        } else {
          status =
            "waiting";
        }

        const backendProgress =
          asNullableNumber(
            execution.progress,
          );

        const progress =
          backendProgress !==
          null
            ? clamp(
                backendProgress,
                0,
                100,
              )
            : status ===
                "complete"
              ? 100
              : 0;

        const detail =
          firstNonEmpty(
            execution.error,
            execution.current_step,
          );

        return {
          id:
            executionId,

          name,

          label:
            name,

          status,

          progress,

          startedAt:
            getTimestamp(
              execution.started_at,
            ),

          completedAt:
            getTimestamp(
              execution.completed_at,
            ),

          error:
            execution.success ===
            false
              ? asNullableString(
                  execution.error,
                )
              : null,

          detail:
            detail ||
            undefined,
        };
      },
    )
    .filter(
      (
        stage,
      ): stage is ResearchStageInfo =>
        stage !== null,
    );
}

// ============================================================
// Status
// ============================================================

function normalizeStatus(
  value: unknown,
): string {
  const status =
    asString(
      value,
    ).toLowerCase();

  if (!status) {
    return "";
  }

  switch (status) {
    case "complete":
    case "done":
    case "success":
    case "succeeded":
      return "completed";

    case "in_progress":
    case "in-progress":
      return "running";

    case "error":
      return "failed";

    default:
      return status;
  }
}

// ============================================================
// Main Mapper
// ============================================================

export function mapApiResearchResult(
  api: ApiResearchResult,
): ResearchResult {
  const apiRecord =
    api as unknown as UnknownRecord;

  const executions =
    getExecutions(
      api,
    );

  const researchId =
    apiRecord.research_id ??
    apiRecord.researchId ??
    apiRecord.id ??
    null;

  const id =
    apiRecord.id ??
    researchId ??
    null;

  const status =
    normalizeStatus(
      apiRecord.status,
    );

  const title =
    firstNonEmpty(
      apiRecord.title,
      apiRecord.company,
    );

  const persistedOverview =
    getTopLevelOverview(
      api,
    );

  const overview =
    persistedOverview ??
    mapOverview(
      api,
      executions,
    );

  /*
   * IMPORTANT:
   *
   * Evidence is now extracted from:
   *
   * 1. top-level evidence
   * 2. wrapped response containers
   * 3. every successful execution
   * 4. nested evidence/claims/citations/findings
   *
   * Nothing is fabricated.
   */
  const evidence =
    mapEvidence(
      api,
      executions,
    );

  const documents =
    mapDocuments(
      api,
      executions,
    );

  const insights =
    mapInsights(
      api,
      executions,
    );

  const stages =
    mapStages(
      executions,
    );

  const report =
    mapReport(
      api,
      executions,
    );

  const summary =
    textFromValue(
      apiRecord.summary,
    );

  const metadata =
    isRecord(
      apiRecord.metadata,
    )
      ? apiRecord.metadata
      : isRecord(
            apiRecord.metadata_json,
          )
        ? apiRecord.metadata_json
        : null;

  return {
    id:
      id !== null &&
      id !== undefined
        ? String(id)
        : null,

    researchId:
      researchId !== null &&
      researchId !== undefined
        ? String(researchId)
        : null,

    title:
      title || null,

    summary:
      summary || null,

    status:
      status || null,

    overview,

    stages,

    evidence,

    documents,

    insights,

    report,

    createdAt:
      getTimestamp(
        apiRecord.created_at,
      ),

    updatedAt:
      getTimestamp(
        apiRecord.updated_at,
      ),

    metadata,
  };
}