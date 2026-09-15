/**
 * Company / Equity Research Types
 */

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
}

/* =====================================================
   Income Statement
   ===================================================== */

export interface IncomeStatementRow {
  item: string;

  fy2024: string;
  fy2023: string;

  change: string;
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

  source?: string;

  confidence?: number;

  date?: string;

  category?: string;

  citation?: string;
}

/* =====================================================
   Complete Company Data
   ===================================================== */

export interface CompanyData {
  /* ---------------------------------------------
     Summary
     --------------------------------------------- */

  summary: CompanySummary;

  /* ---------------------------------------------
     Investment Thesis
     --------------------------------------------- */

  thesis: string;
   document: string;

  /* ---------------------------------------------
     Research Sources
     --------------------------------------------- */

  sources: CompanySource[];

  /* ---------------------------------------------
     Analysis Sections
     
     Expected indexes in ReportTab:
       [0] Business
       [1] Financial Analysis
       [2] Industry
       [6] Valuation
     --------------------------------------------- */

  analysisSections: CompanyAnalysisSection[];

  /* ---------------------------------------------
     Income Statement
     --------------------------------------------- */

  incomeStatement: IncomeStatementRow[];

  /* ---------------------------------------------
     DCF Valuation
     --------------------------------------------- */

  dcf: DCFData;

  /* ---------------------------------------------
     Comparable Companies
     --------------------------------------------- */

  comparables: ComparableCompany[];

  /* ---------------------------------------------
     Sensitivity Analysis
     --------------------------------------------- */

  sensitivity: SensitivityData;

  /* ---------------------------------------------
     Evidence
     --------------------------------------------- */

  evidence: CompanyEvidence[];
}



 /**
  * Document Types
  */

export type DocumentStatus =
  | "processing"
  | "processed"
  | "failed";

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
}