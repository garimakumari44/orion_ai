
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

/* -------------------------------------------------------------------------- */
/* Research list                                                              */
/* -------------------------------------------------------------------------- */

export interface ResearchListResponse {
  items: Research[];

  total: number;
}

/* -------------------------------------------------------------------------- */
/* Research create/update                                                     */
/* -------------------------------------------------------------------------- */

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
  | "failed";

export interface ResearchStageInfo {
  /**
   * Mappers always generate an ID for a valid stage.
   */
  id: string;

  name: string;

  label: string;

  status: ResearchStageStatus | null;

  progress: number;

  startedAt: string | null;

  completedAt: string | null;

  error: string | null;

  detail?: string;
}

/* -------------------------------------------------------------------------- */
/* Research context                                                           */
/* -------------------------------------------------------------------------- */

export interface ResearchAssumption {
  label: string;

  value: string;
}

export interface ResearchContext {
  objective?: string | null;

  template?: string | null;

  depth?: string | null;

  assumptions?:
    | ResearchAssumption[]
    | string[]
    | null;

  uploadedDocs?: number | null;

  company?: string | null;

  companyName?: string | null;

  ticker?: string | null;

  industry?: string | null;

  sector?: string | null;

  description?: string | null;

  headquarters?: string | null;

  ceo?: string | null;

  employees?: number | string | null;

  founded?: number | string | null;

  website?: string | null;

  progress?: number | null;

  [key: string]: unknown;
}

/* -------------------------------------------------------------------------- */
/* Research agent                                                             */
/* -------------------------------------------------------------------------- */

export type ResearchAgentActionStatus =
  | "done"
  | "active";

export interface ResearchAgentAction {
  id?: string | number | null;

  label?: string | null;

  detail?: string | null;

  timestamp?: string | number | null;

  status?:
    | ResearchAgentActionStatus
    | string
    | null;

  agent?: string | null;

  action?: string | null;
}

export interface ResearchAgent {
  currentTask?: string | null;

  progress?: number | null;

  evidenceCount?: number | null;

  sourcesCount?: number | null;

  confidence?: number | null;

  recentActions?:
    | ResearchAgentAction[]
    | null;

  [key: string]: unknown;
}

/* -------------------------------------------------------------------------- */
/* Research draft                                                             */
/* -------------------------------------------------------------------------- */

export interface ResearchDraftSection {
  id?: string | number | null;

  title?: string | null;

  status?: string | null;

  content?: string | null;

  order?: number | null;

  lastUpdated?: string | null;
}

export interface ResearchDraft {
  title?: string | null;

  sections?: ResearchDraftSection[] | null;

  [key: string]: unknown;
}

/* -------------------------------------------------------------------------- */
/* Suggested questions                                                        */
/* -------------------------------------------------------------------------- */

export interface ResearchSuggestedQuestion {
  id?: string | number | null;

  text?: string | null;

  question?: string | null;
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

  source: string;

  confidence: number;

  date?: string;

  category?: string;

  citation?: string;

  filing?: string;

  url?: string | null;

  excerpt?: string | null;

  /**
   * Alternative evidence field used by workspace/research APIs.
   */
  statement?: string | null;

  /**
   * Document/source classification.
   */
  docType?: string | null;

  sourceTitle?: string | null;

  sourceUrl?: string | null;

  documentId?: string | null;

  page?: number | null;

  createdAt?: string | null;

  publishedAt?: string | null;

  [key: string]: unknown;
}

export interface ResearchEvidence {
  id?: string;

  title?: string;

  claim?: string;

  statement?: string;

  source?: string;

  url?: string | null;

  sourceUrl?: string | null;

  sourceTitle?: string | null;

  excerpt?: string | null;

  content?: string | null;

  relevance?: number | null;

  confidence?: number | null;

  publishedAt?: string | null;

  createdAt?: string | null;

  date?: string | null;

  category?: string | null;

  citation?: string | null;

  filing?: string | null;

  docType?: string | null;

  documentId?: string | null;

  page?: number | null;

  [key: string]: unknown;
}

/* -------------------------------------------------------------------------- */
/* Documents                                                                  */
/* -------------------------------------------------------------------------- */

export type ResearchDocumentStatus =
  | "uploaded"
  | "pending"
  | "processing"
  | "processed"
  | "ready"
  | "failed"
  | "error";

export interface ResearchDocument {
  id?: string;

  title?: string;

  name?: string;

  type?: string | null;

  url?: string | null;

  source?: string | null;

  /**
   * Optional because API responses may omit status.
   *
   * Components should normalize an absent value before using it
   * as a Record key.
   */
  status?: ResearchDocumentStatus;

  pages?: number | null;

  size?: string | null;

  createdAt?: string | null;

  date?: string | null;

  summary?: string | null;

  description?: string | null;

  uploadedAt?: string | null;

  processedAt?: string | null;

  [key: string]: unknown;
}

/* -------------------------------------------------------------------------- */
/* Insights                                                                   */
/* -------------------------------------------------------------------------- */

export type ResearchInsightType =
  | "insight"
  | "risk"
  | "catalyst";

export interface ResearchInsight {
  /**
   * Mappers generate these fields.
   */
  id: string;

  type: ResearchInsightType;

  title: string;

  description: string;

  confidence: number;

  summary?: string | null;

  impact?: string | null;

  recommendation?: string | null;

  [key: string]: unknown;
}

/* -------------------------------------------------------------------------- */
/* Report                                                                     */
/* -------------------------------------------------------------------------- */

export type ReportSectionStatus =
  | "complete"
  | "in-progress"
  | "waiting";

export interface ReportSection {
  id: string;

  title: string;

  status: ReportSectionStatus;

  content: string;

  /**
   * The mapper may explicitly provide undefined.
   */
  lastUpdated: string | undefined;
}

export type ResearchReportSection = ReportSection;

export interface ResearchReport {
  title: string | null;

  sections: ReportSection[];
}

/* -------------------------------------------------------------------------- */
/* Company data                                                               */
/* -------------------------------------------------------------------------- */

export interface ResearchCompanyData {
  name?: string | null;

  ticker?: string | null;

  industry?: string | null;

  sector?: string | null;

  description?: string | null;

  headquarters?: string | null;

  ceo?: string | null;

  employees?: number | string | null;

  founded?: number | string | null;

  website?: string | null;

  [key: string]: unknown;
}

/* -------------------------------------------------------------------------- */
/* Complete Research Result                                                   */
/* -------------------------------------------------------------------------- */

export interface ResearchResult {
  id: string | null;

  researchId: string | null;

  title: string | null;

  companyName?: string | null;

  company?: string | null;

  ticker?: string | null;

  status: string | null;

  summary: string | null;

  /**
   * Research execution progress.
   */
  progress?: number | null;

  /**
   * Current execution stage.
   */
  currentStage?: string | null;

  industry?: string | null;

  sector?: string | null;

  objective?: string | null;

  template?: string | null;

  depth?: string | null;

  assumptions?:
    | ResearchAssumption[]
    | string[]
    | null;

  context?: ResearchContext | null;

  agent?: ResearchAgent | null;

  currentTask?: string | null;

  recentActions?:
    | ResearchAgentAction[]
    | null;

  confidence?: number | null;

  draft?: ResearchDraft | null;

  sections?: ResearchDraftSection[] | null;

  suggestedQuestions?:
    | ResearchSuggestedQuestion[]
    | string[]
    | null;

  overview: OverviewData;

  stages: ResearchStageInfo[];

  evidence: ResearchEvidenceItem[];

  documents: ResearchDocument[];

  insights: ResearchInsight[];

  report: ResearchReport;

  createdAt: string | null;

  /**
   * Optional because models/research.ts currently does not guarantee
   * this property.
   */
  updatedAt?: string | null;

  metadata: Record<string, unknown> | null;

  [key: string]: unknown;
}

/* -------------------------------------------------------------------------- */
/* Research configuration                                                     */
/* -------------------------------------------------------------------------- */

/**
 * These values match the existing Research Wizard/UI.
 */
export type ResearchType =
  | "company_research"
  | "company_comparison"
  | "industry_research"
  | "theme_research"
  | "portfolio_analysis"
  | "market_macro";

/**
 * API and UI currently use the same research-type values.
 */
export type ApiResearchType = ResearchType;

/**
 * Objectives used by ResearchConfiguration and ResearchReview.
 */
export type ResearchObjective =
  | "full"
  | "earnings"
  | "valuation"
  | "competitive"
  | "risk"
  | "memo";

/**
 * Research depth values.
 */
export type ResearchDepth =
  | "quick"
  | "standard"
  | "comprehensive";

/**
 * Analysis horizon values used by the UI.
 */
export type AnalysisHorizon =
  | "short"
  | "medium"
  | "long";

/**
 * Output formats used by ResearchConfiguration.
 */
export type OutputFormat =
  | "report"
  | "memo"
  | "dashboard"
  | "summary"
  | "presentation";
/* -------------------------------------------------------------------------- */
/* Company search                                                             */
/* -------------------------------------------------------------------------- */

/**
 * Frontend company-search representation.
 *
 * The canonical company ID is numeric because the backend/API uses
 * integer company IDs.
 */
export interface CompanySearchResult {
  id: number;

  name: string;

  ticker?: string | null;

  companyName?: string | null;

  exchange?: string | null;

  sector?: string | null;

  industry?: string | null;

  country?: string | null;

  description?: string | null;

  logoUrl?: string | null;

  color?: string | null;

  [key: string]: unknown;
}

