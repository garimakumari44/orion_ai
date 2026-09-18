
/**
 * Company / Equity Research Types
 */

/* =====================================================
   Recommendation
   ===================================================== */

export type Recommendation =
  | "STRONG BUY"
  | "BUY"
  | "HOLD"
  | "REDUCE"
  | "SELL";

/* =====================================================
   Company Summary
   ===================================================== */

export interface CompanySummary {
  name: string;
  ticker: string;
  recommendation: string;
  fairValue: number;
  currentPrice: number;
  upside: number;
  confidence: number;
  lastResearched: string;
  sector?: string | null;
  industry?: string | null;
}

/* =====================================================
   Research Source
   ===================================================== */

export interface CompanySource {
  id?: string;
  name?: string;
  type?: string;
  count: number;
  url?: string;
}

/* =====================================================
   Analysis Section
   ===================================================== */

export interface CompanyAnalysisSection {
  id?: string;
  title: string;
  content: string[];
  keyPoints?: string[];
}

/* =====================================================
   Financial Metric
   ===================================================== */

/**
 * Normalized metric displayed by the company context panel.
 *
 * This is intentionally different from ApiFinancialMetrics.
 * ApiFinancialMetrics represents the raw backend object, while this
 * represents the UI-ready label/value pairs.
 */
export interface FinancialMetric {
  label: string;
  value: string | number;
}

/* =====================================================
   News Item
   ===================================================== */

export type NewsSentiment =
  | "positive"
  | "negative"
  | "neutral";

export interface CompanyNewsItem {
  id: string | number;
  headline: string;
  source: string;
  date: string;
  sentiment: NewsSentiment;
}

/* =====================================================
   Income Statement
   ===================================================== */

export interface IncomeStatementRow {
  item: string;
  fy2026?: string;
  fy2025?: string;
  fy2024: string;
  fy2023: string;
  fy2022?: string;
  change: string;
}

/* =====================================================
   Cash Flow
   ===================================================== */

export interface CashFlowRow {
  item: string;
  fy2026?: string;
  fy2025?: string;
  fy2024?: string;
  fy2023?: string;
  fy2022?: string;
  change?: string;
}

/* =====================================================
   DCF Assumptions
   ===================================================== */

export interface DCFAssumption {
  label: string;
  value: string;
}

/* =====================================================
   DCF
   ===================================================== */

export interface DCFData {
  fairValue: number;
  assumptions: DCFAssumption[];
}

/* =====================================================
   Comparable Company
   ===================================================== */

export interface ComparableCompany {
  ticker: string;
  name: string;
  pe: number;
  revenueGrowth: string;
}

/* =====================================================
   Sensitivity Analysis
   ===================================================== */

export interface SensitivityRow {
  wacc: string;
  values: string[];
}

export interface SensitivityData {
  growthRates: string[];
  rows: SensitivityRow[];
}

/* =====================================================
   Company Evidence
   ===================================================== */

export interface CompanyEvidence {
  id?: string | number;
  claim?: string;
  statement?: string;
  source?: string;
  sourceTitle?: string | null;
  sourceUrl?: string | null;
  confidence?: number;
  date?: string;
  category?: string;
  citation?: string;
  filing?: string;
  documentId?: string | number | null;
  page?: number | null;
  excerpt?: string | null;
  url?: string | null;
}

/* =====================================================
   Document Types
   ===================================================== */

export type DocumentStatus =
  | "uploaded"
  | "pending"
  | "processing"
  | "processed"
  | "ready"
  | "failed"
  | "error";

export interface DocumentItem {
  id: string | number;
  title: string;
  type: string;
  source: string;
  date?: string | null;
  status?: DocumentStatus;
  size?: string | null;
  url?: string | null;
  content?: string | null;
  pages?: number | null;
  description?: string | null;
  uploadedAt?: string | null;
  processedAt?: string | null;
}

/* =====================================================
   Complete Company Data
   ===================================================== */

export interface CompanyData {
  status?: string | null;

  summary: CompanySummary;

  thesis: string;

  document?: string;

  sources: CompanySource[];

  analysisSections: CompanyAnalysisSection[];

  financialMetrics?: FinancialMetric[];

  news?: CompanyNewsItem[];

  incomeStatement: IncomeStatementRow[];

  cashFlow: CashFlowRow[];

  dcf: DCFData;

  comparables: ComparableCompany[];

  sensitivity: SensitivityData;

  evidence: CompanyEvidence[];

  documents: DocumentItem[];
}

