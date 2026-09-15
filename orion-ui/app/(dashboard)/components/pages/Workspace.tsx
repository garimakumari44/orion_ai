
'use client';

import { useState } from 'react';
import {
  Bot,
  FileEdit,
  FileText,
  FolderOpen,
  MessageSquare,
  ShieldCheck,
  Sparkles,
} from 'lucide-react';

import { cn, ProgressBar } from '../../components/ui';

import { ConversationTab } from '../../components/workplace/ConversationTab';
import { ContextTab } from '../workplace/ContextTab';
import { AnalystTab } from '../workplace/AnalystTab';
import { DraftTab } from '../workplace/DraftTab';
import { EvidenceTab } from '../workplace/EvidenceTab';
import { KnowledgeTab } from '../workplace/KnowledgeTab';

import type { WorkspaceData } from '@/types/workspace';

/* ============================================================================
 * TYPES
 * ========================================================================== */

type Tab =
  | 'conversation'
  | 'context'
  | 'knowledge'
  | 'analyst'
  | 'draft'
  | 'evidence';

interface WorkspacePageProps {
  data?: WorkspaceData | null;
}

/* ============================================================================
 * TABS
 * ========================================================================== */

const tabs: Array<{
  id: Tab;
  label: string;
  icon: typeof MessageSquare;
}> = [
  {
    id: 'conversation',
    label: 'Assistant',
    icon: MessageSquare,
  },
  {
    id: 'context',
    label: 'Context',
    icon: FileText,
  },
  {
    id: 'knowledge',
    label: 'Knowledge',
    icon: FolderOpen,
  },
  {
    id: 'analyst',
    label: 'AI Analyst',
    icon: Bot,
  },
  {
    id: 'draft',
    label: 'Draft',
    icon: FileEdit,
  },
  {
    id: 'evidence',
    label: 'Evidence',
    icon: ShieldCheck,
  },
];

/* ============================================================================
 * HELPERS
 * ========================================================================== */

function normalizeProgress(value: number | null | undefined): number {
  if (
    typeof value !== 'number' ||
    !Number.isFinite(value)
  ) {
    return 0;
  }

  return Math.min(100, Math.max(0, value));
}

/* ============================================================================
 * COMPONENT
 * ========================================================================== */

export function WorkspacePage({
  data,
}: WorkspacePageProps) {
  const [activeTab, setActiveTab] =
    useState<Tab>('conversation');

  /* --------------------------------------------------------------------------
   * Loading state
   * ------------------------------------------------------------------------ */

  if (!data) {
    return (
      <div className="flex h-full min-h-0 items-center justify-center">
        <div className="flex flex-col items-center gap-4 text-center">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-accent/20 bg-accent/10">
            <Sparkles className="h-5 w-5 animate-pulse text-accent" />
          </div>

          <div>
            <p className="text-sm font-medium text-text-primary">
              Starting your AI assistant
            </p>

            <p className="mt-1 max-w-xs text-xs leading-5 text-text-muted">
              Preparing your conversation, knowledge,
              research context, and evidence.
            </p>
          </div>
        </div>
      </div>
    );
  }

  /* --------------------------------------------------------------------------
   * Workspace data
   * ------------------------------------------------------------------------ */

  const messages = data.messages ?? [];
  const suggestedQuestions =
    data.suggestedQuestions ?? [];

  const documents = data.documents ?? [];
  const evidence = data.evidence ?? [];

  const context = data.context;

  const draftSections =
    data.draftSections ?? [];

  const progress = normalizeProgress(
    data.progress,
  );

  /* --------------------------------------------------------------------------
   * Workspace identity
   * ------------------------------------------------------------------------ */

  const workspaceTitle =
    data.title?.trim() ||
    data.companyName?.trim() ||
    'AI Research Assistant';

  const companyName =
    data.companyName?.trim() || null;

  const ticker =
    data.ticker?.trim() || null;

  const status =
    data.status?.trim() || 'Ready to assist';

  const currentStage =
    data.currentStage?.trim() || null;

  /* --------------------------------------------------------------------------
   * Derived state
   * ------------------------------------------------------------------------ */

  const hasContext = Boolean(
    context &&
      (
        context.companyName ||
        context.industry ||
        context.sector ||
        context.description ||
        context.objective ||
        context.template ||
        context.depth ||
        context.headquarters ||
        context.ceo ||
        context.website
      ),
  );

  const hasDocuments =
    documents.length > 0;

  const hasEvidence =
    evidence.length > 0;

  const hasDraft =
    draftSections.length > 0;

  return (
    <div className="flex h-full min-h-0 overflow-hidden bg-bg">
      <div className="flex min-w-0 flex-1 flex-col overflow-hidden">

        {/* ==================================================================
            HEADER
            ================================================================== */}

        <header className="shrink-0 border-b border-border bg-bg">
          <div className="px-6 py-4">

            <div className="flex min-w-0 items-center gap-4">

              {/* Assistant identity */}

              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-accent/20 bg-accent/10">
                <Sparkles className="h-5 w-5 text-accent" />
              </div>

              {/* Title */}

              <div className="min-w-0 flex-1">

                <div className="flex min-w-0 items-center gap-2.5">

                  <h1 className="truncate text-lg font-semibold text-text-primary">
                    {workspaceTitle}
                  </h1>

                  {ticker && (
                    <span className="shrink-0 rounded border border-border bg-bg-secondary px-1.5 py-0.5 font-mono text-[10px] text-text-muted">
                      {ticker}
                    </span>
                  )}
                </div>

                <div className="mt-1 flex min-w-0 items-center gap-2">

                  {companyName &&
                    companyName !== workspaceTitle && (
                      <span className="truncate text-xs text-text-muted">
                        {companyName}
                      </span>
                    )}

                  {companyName &&
                    companyName !== workspaceTitle &&
                    status && (
                      <span className="text-text-faint">
                        ·
                      </span>
                    )}

                  <span className="truncate text-xs text-text-muted">
                    {status}
                  </span>

                  {currentStage && (
                    <>
                      <span className="text-text-faint">
                        ·
                      </span>

                      <span className="shrink-0 text-xs text-text-muted">
                        {currentStage}
                      </span>
                    </>
                  )}
                </div>
              </div>

              {/* Progress */}

              <div className="hidden w-32 shrink-0 sm:block">

                <div className="mb-1 flex items-center justify-between">

                  <span className="font-mono text-[10px] uppercase tracking-wider text-text-faint">
                    Progress
                  </span>

                  <span className="tabular-nums font-mono text-xs text-text-primary">
                    {progress}%
                  </span>
                </div>

                <ProgressBar value={progress} />
              </div>
            </div>

            {/* =================================================================
                NAVIGATION
                ================================================================= */}

            <nav
              aria-label="Assistant workspace sections"
              className="mt-4 flex items-center gap-1 overflow-x-auto scrollbar-none"
            >
              {tabs.map((tab) => {
                const Icon = tab.icon;

                const isActive =
                  activeTab === tab.id;

                return (
                  <button
                    key={tab.id}
                    type="button"
                    aria-current={
                      isActive
                        ? 'page'
                        : undefined
                    }
                    onClick={() =>
                      setActiveTab(tab.id)
                    }
                    className={cn(
                      'flex shrink-0 items-center gap-1.5 rounded-md px-3 py-1.5 text-sm whitespace-nowrap transition-colors',
                      'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/40',
                      isActive
                        ? 'bg-bg-hover text-text-primary'
                        : 'text-text-muted hover:bg-bg-hover/50 hover:text-text-secondary',
                    )}
                  >
                    <Icon
                      className={cn(
                        'h-3.5 w-3.5',
                        isActive
                          ? 'text-accent'
                          : 'text-text-faint',
                      )}
                    />

                    <span>{tab.label}</span>
                  </button>
                );
              })}
            </nav>
          </div>
        </header>

        {/* ==================================================================
            MAIN CONTENT
            ================================================================== */}

        <main className="min-h-0 flex-1 overflow-hidden">

          {/* ----------------------------------------------------------------
              ASSISTANT
              ---------------------------------------------------------------- */}

          {activeTab === 'conversation' && (
            <div className="h-full min-h-0 overflow-y-auto">
              <ConversationTab
                messages={messages}
                suggestedQuestions={
                  suggestedQuestions
                }
              />
            </div>
          )}

          {/* ----------------------------------------------------------------
              CONTEXT
              ---------------------------------------------------------------- */}

          {activeTab === 'context' && (
            <div className="h-full min-h-0 overflow-y-auto">
              {hasContext ? (
                <ContextTab
                  context={context}
                />
              ) : (
                <EmptyState
                  icon={FileText}
                  title="No research context yet"
                  description="The assistant will build research context as you work with it."
                />
              )}
            </div>
          )}

          {/* ----------------------------------------------------------------
              KNOWLEDGE
              ---------------------------------------------------------------- */}

          {activeTab === 'knowledge' && (
            <div className="h-full min-h-0 overflow-y-auto">
              {hasDocuments ? (
                <KnowledgeTab
                  documents={documents}
                />
              ) : (
                <EmptyState
                  icon={FolderOpen}
                  title="Knowledge base is empty"
                  description="Documents and files available to the assistant will appear here."
                />
              )}
            </div>
          )}

          {/* ----------------------------------------------------------------
              AI ANALYST
              ---------------------------------------------------------------- */}

          {activeTab === 'analyst' && (
            <div className="h-full min-h-0 overflow-y-auto">
              <AnalystTab
                actions={data.agentActions ?? []}
                stages={data.stages ?? []}
                insights={data.insights ?? []}
              />
            </div>
          )}

          {/* ----------------------------------------------------------------
              DRAFT
              ---------------------------------------------------------------- */}

          {activeTab === 'draft' && (
            <div className="h-full min-h-0 overflow-y-auto">
              {hasDraft ? (
                <DraftTab
                  title={
                    data.title ||
                    'Research Draft'
                  }
                  sections={
                    draftSections
                  }
                />
              ) : (
                <EmptyState
                  icon={FileEdit}
                  title="No research draft yet"
                  description="The assistant can build a structured research draft as your analysis develops."
                />
              )}
            </div>
          )}

          {/* ----------------------------------------------------------------
              EVIDENCE
              ---------------------------------------------------------------- */}

          {activeTab === 'evidence' && (
            <div className="h-full min-h-0 overflow-y-auto">
              {hasEvidence ? (
                <EvidenceTab
                  evidence={evidence}
                />
              ) : (
                <EmptyState
                  icon={ShieldCheck}
                  title="No evidence yet"
                  description="Sources and supporting evidence collected by the assistant will appear here."
                />
              )}
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

/* ============================================================================
 * EMPTY STATE
 * ========================================================================== */

interface EmptyStateProps {
  icon: typeof FileText;
  title: string;
  description: string;
}

function EmptyState({
  icon: Icon,
  title,
  description,
}: EmptyStateProps) {
  return (
    <div className="flex h-full min-h-[320px] items-center justify-center px-6">
      <div className="max-w-sm text-center">

        <div className="mx-auto mb-4 flex h-10 w-10 items-center justify-center rounded-lg border border-border bg-bg-secondary">
          <Icon className="h-4 w-4 text-text-faint" />
        </div>

        <h2 className="text-sm font-medium text-text-primary">
          {title}
        </h2>

        <p className="mt-1.5 text-xs leading-5 text-text-muted">
          {description}
        </p>
      </div>
    </div>
  );
}

