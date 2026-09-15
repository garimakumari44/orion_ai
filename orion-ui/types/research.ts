/* -------------------------------------------------------------------------- */
/* Research                                                                   */
/* -------------------------------------------------------------------------- */

export interface Research {
  id: string;
  title: string;
  companyName?: string | null;
  ticker?: string | null;
  status?: string | null;
  createdAt: string;
  updatedAt?: string | null;
  description?: string | null;
  data?: unknown;
}

export interface ResearchListResponse {
  items: Research[];
  total: number;
}

export interface CreateResearchRequest {
  title: string;
  companyName?: string;
  ticker?: string;
  description?: string;
  data?: unknown;
}

export interface UpdateResearchRequest {
  title?: string;
  description?: string;
  status?: string;
  data?: unknown;
}

/* -------------------------------------------------------------------------- */
/* Research execution                                                         */
/* -------------------------------------------------------------------------- */

export type ResearchStageStatus =
  | "waiting"
  | "in-progress"
  | "complete"
  | "failed"
  | string;

export interface ResearchStageInfo {
  id?: string;
  name: string;
  label?: string;
  status?: ResearchStageStatus | null;
  progress?: number;
  startedAt?: string | null;
  completedAt?: string | null;
  error?: string | null;
  detail?: string;
}

/* -------------------------------------------------------------------------- */
/* Overview                                                                   */
/* -------------------------------------------------------------------------- */

export interface ResearchCompanyProfile {
  name?: string | null;
  ticker?: string | null;
  description?: string | null;
  sector?: string | null;
  industry?: string | null;
  headquarters?: string | null;
  ceo?: string | null;
  employees?: number | string | null;
  founded?: number | string | null;
  website?: string | null;
}

export interface ResearchMarketData {
  marketCap?: number | string | null;
  sharePrice?: number | string | null;
  peRatio?: number | string | null;
  weekRange52?: string | null;
  dividendYield?: number | string | null;
  beta?: number | string | null;
}

export interface ResearchFinancialData {
  revenue?: number | string | null;
  revenueGrowth?: number | string | null;
  grossMargin?: number | string | null;
  operatingMargin?: number | string | null;
  eps?: number | string | null;
}

export interface OverviewData {
  profile: ResearchCompanyProfile | null;
  market: ResearchMarketData | null;
  financials: ResearchFinancialData | null;
}

export type ResearchOverview = OverviewData;

/* -------------------------------------------------------------------------- */
/* Evidence                                                                   */
/* -------------------------------------------------------------------------- */

export interface ResearchEvidenceItem {
  id: string;
  claim: string;
  source?: string;
  confidence: number;
  date?: string;
  category?: string;
  citation?: string;
  filing?: string;
  url?: string | null;
  excerpt?: string | null;

  [key: string]: unknown;
}

export interface ResearchEvidence {
  id?: string;
  title?: string;
  source?: string;
  url?: string | null;
  excerpt?: string | null;
  content?: string | null;
  relevance?: number | null;
  confidence?: number | null;
  publishedAt?: string | null;
  claim?: string;
  date?: string | null;
  category?: string | null;
  citation?: string | null;
  filing?: string | null;

  [key: string]: unknown;
}

/* -------------------------------------------------------------------------- */
/* Documents                                                                  */
/* -------------------------------------------------------------------------- */

export interface ResearchDocument {
  id?: string;
  title?: string;
  name?: string;
  type?: string | null;
  url?: string | null;
  source?: string | null;
  status?: string | null;
  pages?: number | null;
  size?: string | null;
  createdAt?: string | null;
  date?: string | null;

  [key: string]: unknown;
}

/* -------------------------------------------------------------------------- */
/* Insights                                                                   */
/* -------------------------------------------------------------------------- */

export type ResearchInsightType =
  | "insight"
  | "risk"
  | "catalyst"
  | string;

export interface ResearchInsight {
  id?: string;
  title?: string;
  type?: ResearchInsightType;
  description?: string | null;
  summary?: string | null;
  impact?: string | null;
  confidence?: number | null;
  recommendation?: string | null;

  [key: string]: unknown;
}

/* -------------------------------------------------------------------------- */
/* Report                                                                     */
/* -------------------------------------------------------------------------- */

export type ReportSectionStatus =
  | "complete"
  | "in-progress"
  | "waiting"
  | string;

export interface ReportSection {
  id: string;
  title: string;
  status: ReportSectionStatus;
  content: string;
  lastUpdated?: string;
}

export type ResearchReportSection = ReportSection;

export interface ResearchReport {
  title: string | null;
  sections: ReportSection[];
}

/* -------------------------------------------------------------------------- */
/* Complete Research Result                                                   */
/* -------------------------------------------------------------------------- */

export interface ResearchResult {
  id: string | null;
  researchId: string | null;

  title: string | null;
  companyName?: string | null;
  ticker?: string | null;

  status: string | null;

  summary: string | null;

  overview: OverviewData;

  stages: ResearchStageInfo[];

  evidence: ResearchEvidenceItem[];

  documents: ResearchDocument[];

  insights: ResearchInsight[];

  report: ResearchReport;

  createdAt: string | null;
  updatedAt: string | null;

  metadata: Record<string, unknown> | null;

  [key: string]: unknown;
}