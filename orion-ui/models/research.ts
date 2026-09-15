/**
 * Normalized frontend research model.
 *
 * This is the ONLY ResearchResult shape that UI components
 * should consume.
 */

export type ResearchStageStatus =
  | "waiting"
  | "pending"
  | "running"
  | "in-progress"
  | "complete"
  | "completed"
  | "failed"
  | "cancelled";

export type ResearchInsightType =
  | "insight"
  | "risk"
  | "catalyst";

/* =========================================================
   Overview
   ========================================================= */

export interface OverviewProfile {
  description?: string | null;
  sector?: string | null;
  industry?: string | null;
  headquarters?: string | null;
  ceo?: string | null;
  employees?: string | null;
  founded?: string | null;
  website?: string | null;
}

export interface OverviewMarket {
  marketCap?: string | null;
  sharePrice?: string | null;
  peRatio?: string | null;
  weekRange52?: string | null;
  dividendYield?: string | null;
  beta?: string | null;
}

export interface OverviewFinancials {
  revenue?: string | null;
  revenueGrowth?: string | null;
  grossMargin?: string | null;
  operatingMargin?: string | null;
  eps?: string | null;
}

export interface OverviewData {
  profile: OverviewProfile | null;
  market: OverviewMarket | null;
  financials: OverviewFinancials | null;
}

/* =========================================================
   Stages
   ========================================================= */

export interface ResearchStageInfo {
  id: string;

  label: string;

  status: ResearchStageStatus;

  detail?: string;

  progress?: number;
}

/* =========================================================
   Evidence
   ========================================================= */

export interface ResearchEvidenceItem {
  id: string | number;

  claim: string;

  source: string;

  confidence: number;

  date?: string;

  category?: string;

  citation?: string;
}

/* =========================================================
   Documents
   ========================================================= */

export type ResearchDocumentStatus =
  | "processing"
  | "processed"
  | "failed";

export interface ResearchDocument {
  id: string | number;

  title: string;

  source: string;

  date?: string;

  status: ResearchDocumentStatus;

  type: string;

  size?: string;
}

/* =========================================================
   Insights
   ========================================================= */

export interface ResearchInsight {
  id: string;

  type: ResearchInsightType;

  title: string;

  description: string;

  confidence: number;
}

/* =========================================================
   Report
   ========================================================= */

export type ReportSectionStatus =
  | "waiting"
  | "in-progress"
  | "complete";

export interface ReportSection {
  id: string;

  title: string;

  status: ReportSectionStatus;

  content: string;

  lastUpdated: string;
}

export interface ResearchReport {
  title: string;

  sections: ReportSection[];
}

/* =========================================================
   Canonical Research Result
   ========================================================= */

export interface ResearchResult {
  id: string;

  researchId?: string | number | null;

  title: string;

  summary: string;

  status?: string | null;

  overview: OverviewData;

  stages: ResearchStageInfo[];

  evidence: ResearchEvidenceItem[];

  documents: ResearchDocument[];

  insights: ResearchInsight[];

  report: ResearchReport;

  createdAt: string | null;

  /**
   * Optional raw metadata useful for future UI features.
   */
  metadata?: Record<string, unknown> | null;
}