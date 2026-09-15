import { Building2, Factory, Target, FileText, ListChecks, Gauge, Upload, TrendingUp } from 'lucide-react';
import { cn, ProgressBar } from '../../components/ui';
import type { ResearchContextInfo } from '@/types'

interface ContextTabProps {
  context: ResearchContextInfo;
}

export function ContextTab({ context }: ContextTabProps) {
  const items = [
    { icon: Building2, label: 'Active Company', value: `${context.company} (${context.ticker})` },
    { icon: Factory, label: 'Industry', value: context.industry },
    { icon: Target, label: 'Research Objective', value: context.objective },
    { icon: FileText, label: 'Research Template', value: context.template },
    { icon: Gauge, label: 'Research Depth', value: context.depth },
    { icon: Upload, label: 'Uploaded Documents', value: `${context.uploadedDocs} files` },
  ];

  return (
    <div className="max-w-3xl mx-auto px-8 py-6 animate-fade-in">
      <div className="mb-6">
        <p className="text-sm text-text-muted">
          The AI Analyst uses the context below for every answer and analysis. Updating any field will re-ground the research.
        </p>
      </div>

      <div className="bg-bg-surface border border-border rounded-lg overflow-hidden">
        {items.map((item, i) => {
          const Icon = item.icon;
          return (
            <div
              key={i}
              className={cn('flex items-center gap-4 px-5 py-3.5', i > 0 && 'border-t border-border-subtle')}
            >
              <div className="w-8 h-8 rounded-lg bg-bg-elevated border border-border flex items-center justify-center shrink-0">
                <Icon className="w-4 h-4 text-text-faint" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-[10px] text-text-faint uppercase tracking-wider font-mono mb-0.5">{item.label}</div>
                <div className="text-sm text-text-primary truncate">{item.value}</div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-6">
        <div className="flex items-center gap-2 mb-3">
          <ListChecks className="w-4 h-4 text-text-faint" />
          <h3 className="text-sm font-medium text-text-primary">Current Assumptions</h3>
        </div>
        <div className="grid grid-cols-2 gap-3">
          {context.assumptions.map((a) => (
            <div key={a.label} className="bg-bg-surface border border-border rounded-lg p-4">
              <div className="text-[10px] text-text-faint uppercase tracking-wider font-mono mb-1">{a.label}</div>
              <div className="font-mono text-lg text-text-primary tabular-nums">{a.value}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-6">
        <div className="flex items-center gap-2 mb-3">
          <TrendingUp className="w-4 h-4 text-text-faint" />
          <h3 className="text-sm font-medium text-text-primary">Research Progress</h3>
        </div>
        <div className="bg-bg-surface border border-border rounded-lg p-5">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-text-secondary">Overall completion</span>
            <span className="font-mono text-sm text-text-primary tabular-nums">{context.progress}%</span>
          </div>
          <ProgressBar value={context.progress} />
        </div>
      </div>
    </div>
  );
}
