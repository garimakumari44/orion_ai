
import type {
  ResearchAssumption,
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

export interface ChatMessageTable {
  headers: string[];

  rows: string[][];
}

export interface ChatCitation {
  id?: string;

  title?: string;

  source?: string;

  url?: string | null;
}

export interface ChatMessage {
  id?: string;

  role: ChatMessageRole;

  content: string;

  createdAt?: string | null;

  timestamp?: string | null;

  tables?: ChatMessageTable[];

  citations?: ChatCitation[];
}

/* -------------------------------------------------------------------------- */
/* Suggested questions                                                        */
/* -------------------------------------------------------------------------- */

export interface SuggestedQuestion {
  id: string;

  text: string;
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

  summary?: string | null;

  description?: string | null;
}

/* -------------------------------------------------------------------------- */
/* Agent actions                                                              */
/* -------------------------------------------------------------------------- */

export type AgentActionStatus =
  | "done"
  | "active"
  | "pending"
  | "failed";

export interface AgentAction {
  id?: string;

  agent?: string | null;

  label: string;

  detail: string;

  timestamp: string;

  status?: AgentActionStatus | null;

  /**
   * Original action name retained for API compatibility.
   */
  action?: string;
}

/* -------------------------------------------------------------------------- */
/* Agent                                                                      */
/* -------------------------------------------------------------------------- */

export interface WorkspaceAgent {
  currentTask: string;

  progress: number;

  evidenceCount: number;

  sourcesCount: number;

  confidence: number;

  recentActions: AgentAction[];
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
  id: string;

  statement: string;

  claim?: string;

  source: string;

  docType?: string | null;

  sourceTitle?: string | null;

  sourceUrl?: string | null;

  documentId?: string | null;

  page?: number | null;

  excerpt?: string | null;

  confidence: number;

  date?: string | null;

  createdAt?: string | null;

  publishedAt?: string | null;

  category?: string | null;

  citation?: string | null;

  filing?: string | null;
}

/* -------------------------------------------------------------------------- */
/* Research context                                                           */
/* -------------------------------------------------------------------------- */

export interface ResearchContextInfo {
  company: string;

  ticker: string;

  companyName?: string | null;

  industry: string;

  sector?: string | null;

  description?: string | null;

  objective: string;

  template: string;

  depth: string;

  assumptions: ResearchAssumption[];

  uploadedDocs: number;

  progress: number;

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

  /**
   * Some API responses provide only a label.
   * The mapper supplies a name where necessary.
   */
  name?: string;

  label?: string | null;

  status?: string | null;

  progress?: number | null;

  startedAt?: string | null;

  completedAt?: string | null;

  error?: string | null;

  detail?: string | null;
}

/* -------------------------------------------------------------------------- */
/* Workspace draft                                                            */
/* -------------------------------------------------------------------------- */

export interface WorkspaceDraft {
  title: string;

  sections: DraftSection[];
}

/* -------------------------------------------------------------------------- */
/* Workspace data                                                             */
/* -------------------------------------------------------------------------- */

export interface WorkspaceData {
  /**
   * Backend/project name.
   */
  projectName: string;

  /**
   * Company name supplied by the workspace service.
   */
  company: string;

  /**
   * Display title used by Workspace.tsx.
   */
  title?: string | null;

  /**
   * Alias used by the dashboard/workspace UI.
   */
  companyName?: string | null;

  ticker: string;

  status: string;

  progress: number;

  estimatedTime: string;

  currentStage: string;

  stages: ResearchStage[];

  messages: ChatMessage[];

  suggestedQuestions: SuggestedQuestion[];

  context: ResearchContextInfo;

  documents: KnowledgeDoc[];

  agent: WorkspaceAgent;

  /**
   * Flattened agent actions consumed by Workspace.tsx.
   */
  agentActions?: AgentAction[];

  draft: WorkspaceDraft;

  /**
   * Flattened draft sections consumed by Workspace.tsx.
   */
  draftSections?: DraftSection[];

  evidence: WorkspaceEvidence[];

  insights?: ResearchInsight[];

  report?: ResearchReport;

  researchId?: string | null;

  createdAt?: string | null;

  updatedAt?: string | null;
}

