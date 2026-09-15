import { Check, Loader, Circle } from 'lucide-react';
import { cn, ProgressBar } from '../../components/ui';
import type { ResearchStageInfo } from '@/types';

interface ResearchProgressProps {
  stages: ResearchStageInfo[];
  progress: number;
  status: string;
  currentStage: string;
}

export function ResearchProgress({ stages, progress, status, currentStage }: ResearchProgressProps) {
  return (
    <div className="max-w-3xl mx-auto px-8 py-6 animate-fade-in">
      <div className="mb-5">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-medium text-text-primary">Research Lifecycle</h3>
          <span className="text-xs text-text-muted">{status}</span>
        </div>
        <ProgressBar value={progress} />
        <div className="flex items-center justify-between mt-1.5">
          <span className="text-xs text-text-faint">Current: {currentStage}</span>
          <span className="font-mono text-xs text-text-primary tabular-nums">{progress}%</span>
        </div>
      </div>

      <div className="space-y-1">
        {stages.map((stage, i) => (
          <div
            key={stage.id}
            className={cn(
              'flex items-center gap-3 px-4 py-3 rounded-lg border transition-colors',
              stage.status === 'in-progress'
                ? 'border-accent/30 bg-accent/5'
                : stage.status === 'complete'
                  ? 'border-border bg-bg-surface'
                  : 'border-border bg-bg-surface/50',
            )}
          >
            <div className="shrink-0">
              {stage.status === 'complete' ? (
                <div className="w-6 h-6 rounded-full bg-success/10 border border-success/20 flex items-center justify-center">
                  <Check className="w-3.5 h-3.5 text-success" />
                </div>
              ) : stage.status === 'in-progress' ? (
                <div className="w-6 h-6 rounded-full bg-accent/10 border border-accent/20 flex items-center justify-center">
                  <Loader className="w-3.5 h-3.5 text-accent animate-spin" />
                </div>
              ) : (
                <div className="w-6 h-6 rounded-full bg-bg-elevated border border-border flex items-center justify-center">
                  <Circle className="w-3 h-3 text-text-faint" />
                </div>
              )}
            </div>

            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <span
                  className={cn(
                    'text-sm',
                    stage.status === 'complete' ? 'text-text-secondary' : stage.status === 'in-progress' ? 'text-text-primary' : 'text-text-faint',
                  )}
                >
                  {stage.label}
                </span>
                {stage.status === 'in-progress' && (
                  <span className="text-[10px] text-accent font-mono uppercase tracking-wider">Running</span>
                )}
              </div>
              {stage.detail && (
                <p className="text-xs text-text-faint mt-0.5">{stage.detail}</p>
              )}
            </div>

            <span className="text-[10px] text-text-faint font-mono shrink-0">
              {stage.status === 'complete' ? 'Done' : stage.status === 'in-progress' ? 'In Progress' : 'Waiting'}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
