import type {
  ResearchInsight,
  ResearchReport,
} from "./research";

/* -------------------------------------------------------------------------- */
/* Workspace                                                                  */
/* -------------------------------------------------------------------------- */

export type WorkspaceTab =
  | "overview"
  | "progress"
  | "evidence"
  | "documents"
  | "insights"
  | "report";

/* -------------------------------------------------------------------------- */
/* Chat                                                                       */
/* -------------------------------------------------------------------------- */

export type ChatMessageRole =
  | "user"
  | "assistant"
  | "system";

export interface ChatMessage {
  id?: string;

  role: ChatMessageRole;

  content: string;

  createdAt?: string | null;
}

/* -------------------------------------------------------------------------- */
/* Suggested questions                                                        */
/* -------------------------------------------------------------------------- */

export interface SuggestedQuestion {
  id?: string;

  question: string;
}

/* -------------------------------------------------------------------------- */
/* Knowledge documents                                                        */
/* -------------------------------------------------------------------------- */

export interface KnowledgeDoc {
  id?: string;

  name: string;

  title?: string | null;

  type?: string | null;

  size?: string | number | null;

  source?: string | null;

  url?: string | null;

  status?: string | null;

  uploadedAt?: string | null;

  createdAt?: string | null;

  processedAt?: string | null;

  pages?: number | null;
}

/* -------------------------------------------------------------------------- */
/* Agent actions                                                              */
/* -------------------------------------------------------------------------- */

export interface AgentAction {
  id?: string;

  agent?: string | null;

  action: string;

  status?: string | null;

  createdAt?: string | null;

  completedAt?: string | null;

  error?: string | null;
}

/* -------------------------------------------------------------------------- */
/* Draft sections                                                             */
/* -------------------------------------------------------------------------- */

export interface DraftSection {
  id?: string;

  title: string;

  content: string;

  status?: string | null;

  order?: number | null;

  lastUpdated?: string | null;
}

/* -------------------------------------------------------------------------- */
/* Workspace evidence                                                         */
/* -------------------------------------------------------------------------- */

export interface WorkspaceEvidence {
  id?: string;

  claim: string;

  source?: string | null;

  sourceTitle?: string | null;

  sourceUrl?: string | null;

  documentId?: string | null;

  page?: number | null;

  excerpt?: string | null;

  confidence?: number | null;

  createdAt?: string | null;

  publishedAt?: string | null;

  category?: string | null;

  citation?: string | null;
}

/* -------------------------------------------------------------------------- */
/* Research context                                                           */
/* -------------------------------------------------------------------------- */

export interface ResearchContextInfo {
  companyName?: string | null;

  ticker?: string | null;

  industry?: string | null;

  sector?: string | null;

  description?: string | null;

  objective?: string | null;

  template?: string | null;

  depth?: string | null;

  assumptions?: string[] | null;

  headquarters?: string | null;

  ceo?: string | null;

  employees?: number | string | null;

  founded?: number | string | null;

  website?: string | null;
}

/* -------------------------------------------------------------------------- */
/* Research stages                                                            */
/* -------------------------------------------------------------------------- */

export interface ResearchStage {
  id?: string;

  name: string;

  label?: string | null;

  status?: string | null;

  progress?: number | null;

  startedAt?: string | null;

  completedAt?: string | null;

  error?: string | null;

  detail?: string | null;
}

/* -------------------------------------------------------------------------- */
/* Workspace data                                                             */
/* -------------------------------------------------------------------------- */

export interface WorkspaceData {
  researchId: string | null;

  title: string | null;

  companyName: string | null;

  ticker: string | null;

  status: string | null;

  summary: string | null;

  progress: number | null;

  currentStage: string | null;

  stages: ResearchStage[];

  evidence: WorkspaceEvidence[];

  documents: KnowledgeDoc[];

  insights: ResearchInsight[];

  report: ResearchReport;

  messages: ChatMessage[];

  suggestedQuestions: SuggestedQuestion[];

  agentActions: AgentAction[];

  draftSections: DraftSection[];

  context: ResearchContextInfo;

  confidence: number | null;

  sourcesCount: number | null;

  evidenceCount: number | null;

  createdAt: string | null;

  updatedAt: string | null;
}