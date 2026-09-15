import { Sparkles, Check, Loader, Shield, FileStack, BookOpen, Activity } from 'lucide-react';
import { cn, ProgressBar, ConfidenceIndicator } from '../../components/ui';
import type { WorkspaceData } from '../type'

interface AnalystTabProps {
  agent: WorkspaceData['agent'];
}

export function AnalystTab({ agent }: AnalystTabProps) {
  return (
    <div className="max-w-3xl mx-auto px-8 py-6 animate-fade-in">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-10 h-10 rounded-lg bg-accent/10 border border-accent/20 flex items-center justify-center">
          <Sparkles className="w-5 h-5 text-accent" />
        </div>
        <div>
          <h2 className="text-sm font-medium text-text-primary">AI Analyst</h2>
          <p className="text-xs text-text-muted">Your research partner — working behind the scenes</p>
        </div>
      </div>

      <div className="bg-bg-surface border border-border rounded-lg p-5 mb-5">
        <div className="flex items-center gap-2 mb-3">
          <Activity className="w-4 h-4 text-accent" />
          <span className="text-sm font-medium text-text-primary">Current Task</span>
        </div>
        <p className="text-sm text-text-secondary mb-3">{agent.currentTask}</p>
        <div className="flex items-center justify-between mb-1.5">
          <span className="text-[10px] text-text-faint uppercase tracking-wider font-mono">Progress</span>
          <span className="font-mono text-xs text-text-primary tabular-nums">{agent.progress}%</span>
        </div>
        <ProgressBar value={agent.progress} />
      </div>

      <div className="grid grid-cols-3 gap-3 mb-6">
        <div className="bg-bg-surface border border-border rounded-lg p-4">
          <div className="flex items-center gap-1.5 mb-1.5">
            <FileStack className="w-3.5 h-3.5 text-text-faint" />
            <span className="text-[10px] text-text-faint uppercase tracking-wider font-mono">Evidence</span>
          </div>
          <div className="font-mono text-xl text-text-primary tabular-nums">{agent.evidenceCount}</div>
          <div className="text-[10px] text-text-faint mt-0.5">items collected</div>
        </div>
        <div className="bg-bg-surface border border-border rounded-lg p-4">
          <div className="flex items-center gap-1.5 mb-1.5">
            <BookOpen className="w-3.5 h-3.5 text-text-faint" />
            <span className="text-[10px] text-text-faint uppercase tracking-wider font-mono">Sources</span>
          </div>
          <div className="font-mono text-xl text-text-primary tabular-nums">{agent.sourcesCount}</div>
          <div className="text-[10px] text-text-faint mt-0.5">data sources</div>
        </div>
        <div className="bg-bg-surface border border-border rounded-lg p-4">
          <div className="flex items-center gap-1.5 mb-1.5">
            <Shield className="w-3.5 h-3.5 text-text-faint" />
            <span className="text-[10px] text-text-faint uppercase tracking-wider font-mono">Confidence</span>
          </div>
          <div className="mt-1">
            <ConfidenceIndicator value={agent.confidence} />
          </div>
        </div>
      </div>

      <div>
        <h3 className="text-sm font-medium text-text-primary mb-3">Recent Actions</h3>
        <div className="space-y-1">
          {agent.recentActions.map((action) => (
            <div
              key={action.id}
              className="flex items-start gap-3 px-4 py-3 bg-bg-surface border border-border rounded-lg"
            >
              <div className="w-6 h-6 rounded-full flex items-center justify-center shrink-0 mt-0.5">
                {action.status === 'done' ? (
                  <div className="w-5 h-5 rounded-full bg-success/10 border border-success/20 flex items-center justify-center">
                    <Check className="w-3 h-3 text-success" />
                  </div>
                ) : (
                  <div className="w-5 h-5 rounded-full bg-accent/10 border border-accent/20 flex items-center justify-center">
                    <Loader className="w-3 h-3 text-accent animate-spin" />
                  </div>
                )}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-sm text-text-primary">{action.label}</span>
                  {action.status === 'active' && (
                    <span className="text-[10px] text-accent font-mono uppercase tracking-wider">in progress</span>
                  )}
                </div>
                <p className="text-xs text-text-muted mt-0.5">{action.detail}</p>
              </div>
              <span className="text-[10px] text-text-faint font-mono shrink-0 mt-1">{action.timestamp}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
