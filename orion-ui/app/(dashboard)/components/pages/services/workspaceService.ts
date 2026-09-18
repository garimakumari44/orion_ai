import type {
  WorkspaceData,
  ChatMessage,
  SuggestedQuestion,
  KnowledgeDoc,
  AgentAction,
  DraftSection,
  WorkspaceEvidence,
  ResearchContextInfo,
  ResearchAssumption,
  ResearchStage,
} from "@/types";

import type {
  ResearchResult,
  ResearchStageInfo,
} from "@/types/research";

/**
 * Backend â†’ Workspace mapper
 *
 * IMPORTANT:
 * This file intentionally contains NO mock research data.
 *
 * It must never:
 * - invent financial metrics
 * - invent evidence
 * - invent documents
 * - invent timestamps
 * - invent confidence scores
 * - invent citations
 * - invent research content
 * - invent agent actions
 * - invent chat messages
 *
 * Anything not present in the backend response becomes:
 * - an empty array
 * - an empty string
 * - null/undefined where supported by the type
 *
 * The UI should then render its appropriate empty state.
 */

export function generateWorkspaceData(
  research: ResearchResult,
): WorkspaceData {
  const companyName =
    research.overview?.profile?.name?.trim() ||
    research.companyName?.trim() ||
    research.company?.trim() ||
    "";

  const ticker =
    research.overview?.profile?.ticker?.trim() ||
    research.ticker?.trim() ||
    "";

  const progress =
    normalizeProgress(
      research.progress,
    );

  const status =
    research.status?.trim() ||
    "";

  const currentStage =
    research.currentStage?.trim() ||
    "";

  const stages =
    mapStages(
      research.stages,
    );

  const messages =
    mapMessages(
      research,
    );

  const suggestedQuestions =
    mapSuggestedQuestions(
      research,
    );

  const context =
    mapContext(
      research,
      companyName,
      ticker,
      progress,
    );

  const documents =
    mapDocuments(
      research,
    );

  const agent =
    mapAgent(
      research,
      progress,
    );

  const draft =
    mapDraft(
      research,
    );

  const evidence =
    mapEvidence(
      research,
    );

  return {
    projectName:
      companyName
        ? `${companyName} Research`
        : "Research",

    company:
      companyName,

    ticker:
      ticker,

    status:
      status,

    progress,

    estimatedTime:
      getEstimatedTime(
        research,
      ),

    currentStage:
      currentStage,

    stages,

    messages,

    suggestedQuestions,

    context,

    documents,

    agent,

    draft,

    evidence,
  };
}

/* ================================================================
   HELPERS
================================================================ */

function normalizeProgress(
  value:
    | number
    | null
    | undefined,
): number {
  if (
    typeof value !== "number" ||
    !Number.isFinite(value)
  ) {
    return 0;
  }

  return Math.min(
    100,
    Math.max(
      0,
      value,
    ),
  );
}

/**
 * Only use an estimated time if the backend
 * actually supplied one.
 *
 * Never invent "3â€“5 minutes".
 */
function getEstimatedTime(
  research: ResearchResult,
): string {
  const value =
    research.estimatedTime;

  if (
    typeof value === "string" &&
    value.trim()
  ) {
    return value.trim();
  }

  return "";
}

/* ================================================================
   STAGES
================================================================ */

function mapStages(
  stages:
    | ResearchStageInfo[]
    | null
    | undefined,
): ResearchStage[] {
  if (
    !Array.isArray(stages)
  ) {
    return [];
  }

  return stages.map(
    (
      stage,
      index,
    ) => {
      const id =
        stage.id?.toString().trim() ||
        `stage-${index}`;

      const label =
        stage.label?.trim() ||
        stage.name?.trim() ||
        id;

      const rawStatus =
        String(
          stage.status ?? "",
        )
          .trim()
          .toLowerCase()
          .replace(
            /_/g,
            "-",
          );

      const status =
        normalizeStageStatus(
          rawStatus,
        );

      return {
        id,
        label,
        status,
      };
    },
  );
}

function normalizeStageStatus(
  status: string,
): ResearchStage["status"] {
  switch (status) {
    case "complete":
    case "completed":
    case "success":
    case "succeeded":
    case "done":
      return "complete";

    case "running":
    case "in-progress":
    case "processing":
    case "active":
      return "in-progress";

    case "waiting":
    case "pending":
    case "queued":
      return "waiting";

    case "failed":
    case "error":
      /*
       * If ResearchStage does not have an error
       * state, keep failed stages in the waiting
       * category rather than inventing a new type.
       */
      return "waiting";

    default:
      return "waiting";
  }
}

/* ================================================================
   CHAT
================================================================ */

function mapMessages(
  research: ResearchResult,
): ChatMessage[] {
  const rawMessages =
    research.messages ??
    research.chatMessages ??
    [];

  if (
    !Array.isArray(rawMessages)
  ) {
    return [];
  }

  return rawMessages
    .filter(Boolean)
    .map(
      (
        message,
        index,
      ) => {
        return {
          id:
            message.id?.toString().trim() ||
            `message-${index}`,

          role:
            normalizeMessageRole(
              message.role,
            ),

          content:
            typeof message.content === "string"
              ? message.content
              : "",

          timestamp:
            typeof message.timestamp === "string"
              ? message.timestamp
              : "",

          status:
            message.status,

          citations:
            Array.isArray(
              message.citations,
            )
              ? message.citations
              : undefined,

          tables:
            Array.isArray(
              message.tables,
            )
              ? message.tables
              : undefined,
        };
      },
    )
    .filter(
      (
        message,
      ) =>
        Boolean(
          message.content.trim(),
        ),
    );
}

function normalizeMessageRole(
  role:
    | string
    | undefined,
): ChatMessage["role"] {
  const normalized =
    String(
      role ?? "",
    )
      .trim()
      .toLowerCase();

  if (
    normalized === "user"
  ) {
    return "user";
  }

  return "assistant";
}

/* ================================================================
   SUGGESTED QUESTIONS
================================================================ */

function mapSuggestedQuestions(
  research: ResearchResult,
): SuggestedQuestion[] {
  const questions =
    research.suggestedQuestions ??
    [];

  if (
    !Array.isArray(questions)
  ) {
    return [];
  }

  return questions
    .map(
      (
        question,
        index,
      ) => {
        if (
          typeof question ===
          "string"
        ) {
          const text =
            question.trim();

          if (!text) {
            return null;
          }

          return {
            id:
              `question-${index}`,
            text,
          };
        }

        const text =
          question.text?.trim();

        if (!text) {
          return null;
        }

        return {
          id:
            question.id?.toString().trim() ||
            `question-${index}`,

          text,
        };
      },
    )
    .filter(
      (
        value,
      ): value is SuggestedQuestion =>
        value !== null,
    );
}

/* ================================================================
   CONTEXT
================================================================ */

function mapContext(
  research: ResearchResult,
  companyName: string,
  ticker: string,
  progress: number,
): ResearchContextInfo {
  const profile =
    research.overview?.profile;

  const industry =
    profile?.industry?.trim() ||
    research.industry?.trim() ||
    "";

  const objective =
    research.context?.objective?.trim() ||
    research.objective?.trim() ||
    "";

  const template =
    research.context?.template?.trim() ||
    research.template?.trim() ||
    "";

  const depth =
    research.context?.depth?.trim() ||
    research.depth?.trim() ||
    "";

  const uploadedDocs =
    getUploadedDocumentCount(
      research,
    );

  const rawAssumptions =
    Array.isArray(research.context?.assumptions)
      ? research.context.assumptions
      : Array.isArray(research.assumptions)
        ? research.assumptions
        : [];

  const assumptions: ResearchAssumption[] =
    rawAssumptions
      .map((assumption, index) => {
        if (typeof assumption === "string") {
          const text = assumption.trim();

          if (!text) {
            return null;
          }

          return {
            id: `assumption-${index}`,
            label: text,
            value: text,
          };
        }

        if (
          assumption &&
          typeof assumption === "object"
        ) {
          return assumption as ResearchAssumption;
        }

        return null;
      })
      .filter(
        (assumption): assumption is ResearchAssumption =>
          assumption !== null,
      );

  return {
    company:
      companyName,

    ticker:
      ticker,

    industry:
      industry,

    objective:
      objective,

    template:
      template,

    depth:
      depth,

    uploadedDocs:
      uploadedDocs,

    assumptions:
      assumptions,

    progress,
  };
}

function getUploadedDocumentCount(
  research: ResearchResult,
): number {
  if (
    Array.isArray(
      research.documents,
    )
  ) {
    return research.documents.length;
  }

  if (
    typeof research.context?.uploadedDocs ===
    "number"
  ) {
    return Math.max(
      0,
      research.context.uploadedDocs,
    );
  }

  return 0;
}

/* ================================================================
   DOCUMENTS
================================================================ */

function mapDocuments(
  research: ResearchResult,
): KnowledgeDoc[] {
  const documents =
    research.documents ??
    [];

  if (
    !Array.isArray(documents)
  ) {
    return [];
  }

  return documents
    .map(
      (
        document,
        index,
      ) => {
        const id =
          document.id?.toString().trim() ||
          `document-${index}`;

        const name =
          document.name?.trim() ||
          document.title?.trim() ||
          "";

        return {
          id,

          name,

          type:
            document.type?.trim() ||
            "",

          size:
            document.size?.toString() ||
            "",

          status:
            normalizeDocumentStatus(
              document.status,
            ),

          uploadedAt:
            document.uploadedAt?.toString() ||
            "",

          summary:
            document.summary?.trim() ||
            "",

          tablesExtracted:
            typeof document.tablesExtracted ===
            "number"
              ? document.tablesExtracted
              : 0,
        };
      },
    );
}

function normalizeDocumentStatus(
  status:
    | string
    | undefined,
): KnowledgeDoc["status"] {
  const normalized =
    String(
      status ?? "",
    )
      .trim()
      .toLowerCase();

  if (
    normalized ===
      "processed" ||
    normalized ===
      "complete" ||
    normalized ===
      "completed"
  ) {
    return "processed";
  }

  if (
    normalized ===
      "processing" ||
    normalized ===
      "running"
  ) {
    return "processing";
  }

  /*
   * Do not pretend an unknown document state
   * is processed.
   */
  return "processing";
}

/* ================================================================
   AGENT
================================================================ */

function mapAgent(
  research: ResearchResult,
  progress: number,
) {
  const agent =
    research.agent;

  const actions =
    mapAgentActions(
      research,
    );

  return {
    currentTask:
      agent?.currentTask?.trim() ||
      research.currentTask?.trim() ||
      "",

    progress,

    evidenceCount:
      getEvidenceCount(
        research,
      ),

    sourcesCount:
      getSourcesCount(
        research,
      ),

    confidence:
      getConfidence(
        research,
      ),

    recentActions:
      actions,
  };
}

function mapAgentActions(
  research: ResearchResult,
): AgentAction[] {
  const actions =
    research.agent?.recentActions ??
    research.recentActions ??
    [];

  if (
    !Array.isArray(actions)
  ) {
    return [];
  }

  return actions
    .map(
      (
        action,
        index,
      ) => {
        return {
          id:
            action.id?.toString().trim() ||
            `action-${index}`,

          label:
            action.label?.trim() ||
            "",

          detail:
            action.detail?.trim() ||
            "",

          timestamp:
            action.timestamp?.toString() ||
            "",

          status:
            normalizeAgentActionStatus(
              action.status,
            ),
        };
      },
    )
    .filter(
      (
        action,
      ) =>
        Boolean(
          action.label,
        ),
    );
}

function normalizeAgentActionStatus(
  status:
    | string
    | null
    | undefined,
): AgentAction["status"] {
  const normalized =
    String(
      status ?? "",
    )
      .trim()
      .toLowerCase();

  if (
    normalized ===
      "done" ||
    normalized ===
      "complete" ||
    normalized ===
      "completed"
  ) {
    return "done";
  }

  if (
    normalized ===
      "active" ||
    normalized ===
      "running" ||
    normalized ===
      "in-progress"
  ) {
    return "active";
  }

  return "done";
}

function getEvidenceCount(
  research: ResearchResult,
): number {
  if (
    Array.isArray(
      research.evidence,
    )
  ) {
    return research.evidence.length;
  }

  if (
    typeof research.agent?.evidenceCount ===
    "number"
  ) {
    return Math.max(
      0,
      research.agent.evidenceCount,
    );
  }

  return 0;
}

function getSourcesCount(
  research: ResearchResult,
): number {
  if (
    Array.isArray(
      research.documents,
    )
  ) {
    return research.documents.length;
  }

  if (
    typeof research.agent?.sourcesCount ===
    "number"
  ) {
    return Math.max(
      0,
      research.agent.sourcesCount,
    );
  }

  return 0;
}

function getConfidence(
  research: ResearchResult,
): number {
  const value =
    research.agent?.confidence ??
    research.confidence;

  if (
    typeof value !== "number" ||
    !Number.isFinite(value)
  ) {
    return 0;
  }

  return Math.min(
    100,
    Math.max(
      0,
      value,
    ),
  );
}

/* ================================================================
   DRAFT
================================================================ */

function mapDraft(
  research: ResearchResult,
) {
  const draft =
    research.draft;

  const sections =
    mapDraftSections(
      research,
    );

  return {
    title:
      draft?.title?.trim() ||
      research.report?.title?.trim() ||
      "",

    sections,
  };
}

function mapDraftSections(
  research: ResearchResult,
): DraftSection[] {
  const sections =
    research.draft?.sections ??
    research.sections ??
    [];

  if (
    !Array.isArray(sections)
  ) {
    return [];
  }

  return sections
    .map(
      (
        section,
        index,
      ) => {
        return {
          id:
            section.id?.toString().trim() ||
            `section-${index}`,

          title:
            section.title?.trim() ||
            "",

          status:
            normalizeDraftStatus(
              section.status,
            ),

          content:
            section.content?.trim() ||
            "",

          lastUpdated:
            section.lastUpdated?.toString() ||
            "",
        };
      },
    )
    .filter(
      (
        section,
      ) =>
        Boolean(
          section.title,
        ),
    );
}

function normalizeDraftStatus(
  status:
    | string
    | null
    | undefined,
): DraftSection["status"] {
  const normalized =
    String(
      status ?? "",
    )
      .trim()
      .toLowerCase()
      .replace(
        /_/g,
        "-",
      );

  if (
    normalized ===
      "complete" ||
    normalized ===
      "completed"
  ) {
    return "complete";
  }

  if (
    normalized ===
      "in-progress" ||
    normalized ===
      "running" ||
    normalized ===
      "processing"
  ) {
    return "in-progress";
  }

  return "waiting";
}

/* ================================================================
   EVIDENCE
================================================================ */

function mapEvidence(
  research: ResearchResult,
): WorkspaceEvidence[] {
  const evidence =
    research.evidence ??
    [];

  if (
    !Array.isArray(evidence)
  ) {
    return [];
  }

  return evidence
    .map(
      (
        item,
        index,
      ) => {
        const confidence =
          typeof item.confidence ===
          "number" &&
          Number.isFinite(
            item.confidence,
          )
            ? Math.min(
                100,
                Math.max(
                  0,
                  item.confidence,
                ),
              )
            : 0;

        return {
          id:
            item.id?.toString().trim() ||
            `evidence-${index}`,

          statement:
            item.statement?.trim() ||
            "",

          source:
            item.source?.trim() ||
            "",

          docType:
            item.docType?.trim() ||
            item.filing?.trim() ||
            "",

          date:
            item.date?.toString() ||
            "",

          confidence,

          citation:
            item.citation?.trim() ||
            "",
        };
      },
    )
    .filter(
      (
        item,
      ) =>
        Boolean(
          item.statement,
        ),
    );
}


