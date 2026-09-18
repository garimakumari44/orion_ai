
/**
 * Backend API Types
 *
 * These types represent the RAW responses returned by FastAPI.
 *
 * IMPORTANT:
 * Do not use these types directly inside the UI.
 *
 * Flow:
 *
 * Backend API
 *      ↓
 * ApiResearchResult
 *      ↓
 * mapApiResearchResult()
 *      ↓
 * ResearchResult
 *      ↓
 * ResearchWorkspace
 *
 * The backend currently exposes research data through:
 *
 *   GET /api/research/{research_id}
 *   GET /api/research/{research_id}/results
 *
 * The frontend API client may use either endpoint depending
 * on the application flow.
 */

/* =========================================================
   Primitive / Shared Types
   ========================================================= */

export type ApiId = string | number;

export type ApiResearchStatus =
  | "planning"
  | "pending"
  | "running"
  | "in-progress"
  | "collecting"
  | "analyzing"
  | "generating"
  | "completed"
  | "complete"
  | "failed"
  | "error"
  | "cancelled"
  | string;

/* =========================================================
   Start Research Response
   ========================================================= */

/**
 * Response returned when a research execution is started.
 *
 * The backend may return the research ID either directly:
 *
 * {
 *   "research_id": 61
 * }
 *
 * or through:
 *
 * {
 *   "research": {
 *      "id": 61
 *   }
 * }
 */
export interface StartResearchResponse {
  research_id?: ApiId | null;

  id?: ApiId | null;

  status?: ApiResearchStatus | null;

  message?: string | null;

  created_at?: string | null;

  research?: {
    id?: ApiId | null;

    research_id?: ApiId | null;

    status?: ApiResearchStatus | null;

    title?: string | null;

    company?: string | null;

    ticker?: string | null;

    industry?: string | null;

    created_at?: string | null;
  } | null;

  [key: string]: unknown;
}

/* =========================================================
   Execution Metadata
   ========================================================= */

/**
 * Metadata attached to an individual research execution.
 *
 * Examples from the backend:
 *
 * {
 *   "agent_name": "financial",
 *   "agent_status": "completed",
 *   "confidence": 1.0,
 *   "sources": [],
 *   "reasoning": null
 * }
 */
export interface ApiResearchExecutionMetadata {
  agent?: string | null;

  agent_name?: string | null;

  agent_status?: string | null;

  executor?: string | null;

  executor_name?: string | null;

  confidence?: number | null;

  sources?: unknown[];

  reasoning?: string | null;

  execution_time?: number | null;

  status?: string | null;

  [key: string]: unknown;
}

/* =========================================================
   Research Execution Result
   ========================================================= */

/**
 * One agent/executor result inside ApiResearchResult.results.
 *
 * Example:
 *
 * {
 *   "task_id": "...",
 *   "success": true,
 *   "execution_id": "...",
 *   "trace_id": "...",
 *   "output": {...},
 *   "error": null,
 *   "started_at": "...",
 *   "completed_at": "...",
 *   "metadata": {...}
 * }
 */
export interface ApiResearchExecutionResult {
  task_id?: string | null;

  success?: boolean | null;

  execution_id?: string | null;

  trace_id?: string | null;

  output?: unknown;

  error?: string | null;

  started_at?: string | null;

  completed_at?: string | null;

  metadata?: ApiResearchExecutionMetadata | null;

  [key: string]: unknown;
}

/* =========================================================
   Citation
   ========================================================= */

/**
 * Raw citation/source returned by the backend.
 *
 * Example:
 *
 * {
 *   "provider": "yahoo_finance",
 *   "type": "financial_market_data"
 * }
 */
export interface ApiResearchCitation {
  provider?: string | null;

  type?: string | null;

  title?: string | null;

  url?: string | null;

  source?: string | null;

  citation?: string | null;

  date?: string | null;

  published_at?: string | null;

  [key: string]: unknown;
}

/* =========================================================
   Generic Raw Financial Value
   ========================================================= */

/**
 * Financial data from Yahoo Finance can appear in multiple forms.
 *
 * Scalar:
 *
 *   113538000000
 *
 * or year/date keyed:
 *
 * {
 *   "2026-01-31 00:00:00": 113538000000,
 *   "2025-01-31 00:00:00": 95567000000
 * }
 */
export type ApiFinancialValue =
  | number
  | string
  | null
  | Record<string, number | string | null>;

/* =========================================================
   Financial Statement Row
   ========================================================= */

/**
 * Raw financial statement row.
 *
 * Example:
 *
 * {
 *   "index": "Total Revenue",
 *   "2026-01-31 00:00:00": 113538000000,
 *   "2025-01-31 00:00:00": 95567000000
 * }
 */
export interface ApiFinancialStatementRow {
  index?: string | null;

  [date: string]: string | number | null | undefined;
}

/* =========================================================
   Financial Metrics
   ========================================================= */

/**
 * Financial market metrics returned by the financial agent.
 *
 * These are RAW backend fields and intentionally use snake_case.
 */
export interface ApiFinancialMetrics {
  current_price?: number | null;

  previous_close?: number | null;

  open?: number | null;

  day_high?: number | null;

  day_low?: number | null;

  "52_week_high"?: number | null;

  "52_week_low"?: number | null;

  volume?: number | null;

  average_volume?: number | null;

  market_cap?: number | null;

  enterprise_value?: number | null;

  trailing_pe?: number | null;

  forward_pe?: number | null;

  peg_ratio?: number | null;

  price_to_sales?: number | null;

  price_to_book?: number | null;

  enterprise_to_revenue?: number | null;

  enterprise_to_ebitda?: number | null;

  profit_margin?: number | null;

  operating_margin?: number | null;

  return_on_assets?: number | null;

  return_on_equity?: number | null;

  dividend_yield?: number | null;

  dividend_rate?: number | null;

  earnings_growth?: number | null;

  revenue_growth?: number | null;

  [key: string]: unknown;
}

/* =========================================================
   Raw Financial Agent Output
   ========================================================= */

/**
 * Financial agent output.
 *
 * This mirrors the structure currently returned by the backend
 * while intentionally allowing additional provider fields.
 */
export interface ApiFinancialOutput {
  research_id?: ApiId | null;

  company_id?: ApiId | null;

  company?: string | null;

  ticker?: string | null;

  currency?: string | null;

  income_statement?: ApiFinancialStatementRow[];

  cash_flow_statement?: ApiFinancialStatementRow[];

  balance_sheet?: ApiFinancialStatementRow[];

  financial_metrics?: ApiFinancialMetrics | null;

  overview?: Record<string, unknown> | null;

  sources?: ApiResearchCitation[];

  metadata?: Record<string, unknown> | null;

  [key: string]: unknown;
}

/* =========================================================
   Raw Industry Output
   ========================================================= */

export interface ApiIndustryMetadata {
  id?: ApiId | null;

  name?: string | null;

  slug?: string | null;

  company_id?: ApiId | null;

  company?: string | null;

  ticker?: string | null;

  industry?: string | null;

  [key: string]: unknown;
}

export interface ApiPorterAnalysis {
  industry?: string | null;

  supplier_power?: string | null;

  buyer_power?: string | null;

  competitive_rivalry?: string | null;

  threat_of_substitutes?: string | null;

  threat_of_new_entrants?: string | null;

  summary?: string | null;

  [key: string]: unknown;
}

export interface ApiIndustryMarketSize {
  industry?: string | null;

  tam?: number | string | null;

  sam?: number | string | null;

  som?: number | string | null;

  growth_rate?: number | string | null;

  forecast?: unknown;

  [key: string]: unknown;
}

export interface ApiSupplyChain {
  suppliers?: unknown[];

  manufacturers?: unknown[];

  distributors?: unknown[];

  customers?: unknown[];

  dependencies?: unknown[];

  risks?: unknown[];

  [key: string]: unknown;
}

export interface ApiIndustryData {
  company?: string | null;

  ticker?: string | null;

  industry?: string | null;

  industry_metadata?: ApiIndustryMetadata | null;

  porter?: ApiPorterAnalysis | null;

  market?: Record<string, unknown> | null;

  market_size?: unknown[];

  competitors?: unknown[];

  supply_chain?: ApiSupplyChain | null;

  trends?: unknown[];

  companies?: unknown[];

  statistics?: unknown[];

  reports?: unknown[];

  raw?: unknown[];

  research_id?: ApiId | null;

  company_id?: ApiId | null;

  industry_name?: string | null;

  industry_source?: string | null;

  industry_confidence?: number | null;

  metadata?: Record<string, unknown> | null;

  providers?: unknown[];

  [key: string]: unknown;
}

export interface ApiIndustryReport {
  industry?: string | null;

  porter_analysis?: ApiPorterAnalysis | null;

  market_size?: ApiIndustryMarketSize | null;

  competitors?: unknown[];

  trends?: unknown[];

  supply_chain?: ApiSupplyChain | null;

  [key: string]: unknown;
}

export interface ApiIndustryOutput {
  research_id?: ApiId | null;

  company_id?: ApiId | null;

  company?: string | null;

  ticker?: string | null;

  industry?: string | null;

  industry_data?: ApiIndustryData | null;

  report?: ApiIndustryReport | null;

  [key: string]: unknown;
}

/* =========================================================
   Raw Valuation Output
   ========================================================= */

export interface ApiValuationOutput {
  company?: string | null;

  dcf?: Record<string, unknown> | null;

  comparable_analysis?: Record<string, unknown> | null;

  multiples_analysis?: Record<string, unknown> | null;

  sensitivity_analysis?: Record<string, unknown> | null;

  conclusion?: string | null;

  [key: string]: unknown;
}

/* =========================================================
   Raw Risk Output
   ========================================================= */

export interface ApiRiskMetadata {
  risk_model?: string | null;

  risk_scale?: string | null;

  risk_count?: number | null;

  has_scenarios?: boolean | null;

  scenarios?: unknown;

  [key: string]: unknown;
}

export interface ApiRiskOutput {
  company?: string | null;

  overall_risk?: string | null;

  risk_score?: number | null;

  risks?: unknown[];

  scenarios?: unknown;

  summary?: string | null;

  recommendations?: unknown[];

  metadata?: ApiRiskMetadata | null;

  [key: string]: unknown;
}

/* =========================================================
   Raw Evidence Output
   ========================================================= */

export interface ApiEvidenceOutput {
  agent?: string | null;

  agent_name?: string | null;

  research_id?: ApiId | null;

  task_id?: string | null;

  company?: string | null;

  ticker?: string | null;

  claims?: unknown[];

  matched_evidence?: unknown[];

  citations?: ApiResearchCitation[];

  evidence_count?: number | null;

  citation_count?: number | null;

  status?: string | null;

  [key: string]: unknown;
}

/* =========================================================
   Raw Critic Output
   ========================================================= */

export interface ApiCriticVerification {
  total_claims?: number | null;

  verified?: unknown[];

  failed?: unknown[];

  verification_score?: number | null;

  [key: string]: unknown;
}

export interface ApiCriticHallucination {
  hallucination_risk?: string | null;

  issues?: unknown[];

  [key: string]: unknown;
}

export interface ApiCriticQuality {
  claim_count?: number | null;

  verification_score?: number | null;

  hallucination_score?: number | null;

  assessment?: string | null;

  [key: string]: unknown;
}

export interface ApiCriticOutput {
  agent?: string | null;

  status?: string | null;

  claims?: unknown[];

  verification?: ApiCriticVerification | null;

  hallucination?: ApiCriticHallucination | null;

  quality?: ApiCriticQuality | null;

  metadata?: Record<string, unknown> | null;

  [key: string]: unknown;
}

/* =========================================================
   Raw Investment Committee Output
   ========================================================= */

export interface ApiInvestmentCommitteeOutput {
  decision?: string | null;

  thesis?: string | null;

  key_reasons?: unknown[];

  major_risks?: unknown[];

  catalysts?: unknown[];

  valuation_view?: string | null;

  findings?: unknown[];

  confidence?: number | null;

  [key: string]: unknown;
}

/* =========================================================
   Research Result Output Union
   ========================================================= */

/**
 * We deliberately keep output as unknown at the execution level,
 * because the same `results[]` array contains outputs from
 * multiple agents.
 *
 * These interfaces are available to the mapper when it needs
 * to narrow a particular execution.
 */
export type ApiResearchAgentOutput =
  | ApiFinancialOutput
  | ApiIndustryOutput
  | ApiValuationOutput
  | ApiRiskOutput
  | ApiEvidenceOutput
  | ApiCriticOutput
  | ApiInvestmentCommitteeOutput
  | Record<string, unknown>;

/* =========================================================
   API Research Result
   ========================================================= */

/**
 * Actual response returned by:
 *
 *   GET /api/research/{research_id}
 *
 * and the core fields returned by:
 *
 *   GET /api/research/{research_id}/results
 *
 * IMPORTANT:
 *
 * The backend's research result contains BOTH:
 *
 *   results[]
 *
 * and, for the dedicated results endpoint:
 *
 *   overview
 *   evidence
 *   documents
 *   insights
 *   report
 *   agent_results
 *
 * Therefore this interface supports both forms.
 */
export interface ApiResearchResult {
  /* -------------------------------------------------------
     Identity
     ------------------------------------------------------- */

  id?: ApiId | null;

  research_id?: ApiId | null;

  title?: string | null;

  query?: string | null;

  intent?: string | null;

  research_type?: string | null;

  /* -------------------------------------------------------
     Status
     ------------------------------------------------------- */

  status?: ApiResearchStatus | null;

  progress?: number | null;

  current_step?: string | null;

  /* -------------------------------------------------------
     Company
     ------------------------------------------------------- */

  company_id?: ApiId | null;

  company?: string | null;

  ticker?: string | null;

  industry?: string | null;

  /* -------------------------------------------------------
     Summary
     ------------------------------------------------------- */

  summary?: string | null;

  /* -------------------------------------------------------
     Execution Results
     ------------------------------------------------------- */

  results?: ApiResearchExecutionResult[];

  executions?: ApiResearchExecutionResult[];

  agent_results?: ApiResearchExecutionResult[];

  /* -------------------------------------------------------
     Dedicated normalized backend result fields
     ------------------------------------------------------- */

  overview?: unknown;

  evidence?: unknown;

  documents?: unknown;

  insights?: unknown;

  report?: unknown;

  /* -------------------------------------------------------
     Sources / Citations
     ------------------------------------------------------- */

  citations?: ApiResearchCitation[];

  sources?: ApiResearchCitation[];

  /* -------------------------------------------------------
     Timestamps
     ------------------------------------------------------- */

  created_at?: string | null;

  started_at?: string | null;

  completed_at?: string | null;

  updated_at?: string | null;

  /* -------------------------------------------------------
     Metadata
     ------------------------------------------------------- */

  metadata?: Record<string, unknown> | null;

  metadata_json?: Record<string, unknown> | null;

  /* -------------------------------------------------------
     Legacy API compatibility
     ------------------------------------------------------- */

  sections?: Array<{
    title: string;

    content: string;
  }>;

  findings?: Array<{
    title: string;

    description: string;

    evidence?: string[];
  }>;

  financial_analysis?: {
    revenue?: string;

    growth?: string;

    margins?: string;

    valuation?: string;
  };

  risks?: string[];

  recommendations?: string[];

  /* -------------------------------------------------------
     Future backend fields
     ------------------------------------------------------- */

  [key: string]: unknown;
}

/* =========================================================
   Dedicated Research Results Response
   ========================================================= */

/**
 * This represents the response from:
 *
 *   GET /api/research/{research_id}/results
 *
 * Based on the current backend response, these fields are
 * explicitly present.
 */
export interface ApiResearchResultsResponse {
  research_id: ApiId;

  status?: ApiResearchStatus | null;

  title?: string | null;

  company_id?: ApiId | null;

  company?: string | null;

  ticker?: string | null;

  industry?: string | null;

  research_type?: string | null;

  overview?: unknown;

  evidence?: unknown;

  documents?: unknown;

  insights?: unknown;

  report?: unknown;

  agent_results?: ApiResearchExecutionResult[];

  citations?: ApiResearchCitation[];

  created_at?: string | null;

  started_at?: string | null;

  completed_at?: string | null;

  [key: string]: unknown;
}

/* =========================================================
   Company Search API
   ========================================================= */

export interface ApiCompanySearchResult {
  id: number;

  name: string;

  legal_name?: string | null;

  ticker?: string | null;

  exchange?: string | null;

  country?: string | null;

  industry?: string | null;

  sector?: string | null;

  website?: string | null;

  logo_url?: string | null;

  market_cap?: number | string | null;

  [key: string]: unknown;
}

/* =========================================================
   Research Config API
   ========================================================= */

export interface ResearchConfigData {
  type?: string | null;

  research_type?: string | null;

  company?: {
    id: number;

    name: string;

    ticker?: string | null;
  } | null;

  company_id?: number | null;

  comparisonCompanies?: Array<{
    id: number;

    name: string;

    ticker?: string | null;
  }>;

  comparison_companies?: Array<{
    id: number;

    name: string;

    ticker?: string | null;
  }>;

  industry?: string | null;

  theme?: string | null;

  objective?: string | null;

  depth?: string | null;

  horizon?: string | null;

  dataSources?: string[];

  data_sources?: string[];

  outputFormats?: string[];

  output_formats?: string[];

  output?: string[];

  [key: string]: unknown;
}

/* =========================================================
   Start Research Request
   ========================================================= */

export interface StartResearchRequest {
  company_id?: number;

  research_type: string;

  query: string;

  type?: string;

  config?: ResearchConfigData;

  [key: string]: unknown;
}

/* =========================================================
   Research Status
   ========================================================= */

export interface ResearchStatusResponse {
  id: ApiId;

  status: ApiResearchStatus;

  label?: string | null;

  detail?: string | null;

  current_step?: string | null;

  progress?: number | null;

  created_at?: string | null;

  started_at?: string | null;

  completed_at?: string | null;

  updated_at?: string | null;

  [key: string]: unknown;
}

/* =========================================================
   Generic API Response
   ========================================================= */

export interface ApiResponse<T> {
  data: T;

  message?: string | null;
}

/* =========================================================
   API Error
   ========================================================= */

export interface ApiError {
  detail?: string | null;

  message?: string | null;

  error?: string | null;

  status_code?: number;

  [key: string]: unknown;
}

/* =========================================================
   Paginated API Response
   ========================================================= */

export interface PaginatedResponse<T> {
  items: T[];

  total: number;

  page?: number;

  page_size?: number;

  pages?: number;
}

