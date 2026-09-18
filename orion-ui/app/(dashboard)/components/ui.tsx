import type { ReactNode } from 'react';
import type { Recommendation } from '@/models/company';

export function cn(...classes: (string | false | undefined | null)[]): string {
  return classes.filter(Boolean).join(' ');
}

export function RecommendationBadge({ value, size = 'sm' }: { value: Recommendation; size?: 'sm' | 'md' | 'lg' }) {
  const styles: Record<Recommendation, string> = {
    'STRONG BUY': 'bg-success-soft text-success border-success/30',
    BUY: 'bg-success-soft text-success border-success/30',
    HOLD: 'bg-warning-soft text-warning border-warning/30',
    REDUCE: 'bg-danger-soft text-danger border-danger/30',
    SELL: 'bg-danger-soft text-danger border-danger/30',
  };
  const sizes = {
    sm: 'text-[10px] px-2 py-0.5',
    md: 'text-xs px-2.5 py-1',
    lg: 'text-sm px-3 py-1.5',
  };
  return (
    <span
      className={cn(
        'inline-flex items-center font-mono font-bold uppercase tracking-wider border rounded',
        styles[value],
        sizes[size],
      )}
    >
      {value}
    </span>
  );
}

export function ConfidenceIndicator({ value, showLabel = true }: { value: number; showLabel?: boolean }) {
  const color = value >= 85 ? 'bg-success' : value >= 70 ? 'bg-warning' : 'bg-danger';
  return (
    <div className="flex items-center gap-2">
      <div className="w-16 h-1 bg-border rounded-full overflow-hidden">
        <div className={cn('h-full rounded-full transition-all duration-500', color)} style={{ width: `${value}%` }} />
      </div>
      {showLabel && <span className="font-mono text-xs text-text-secondary">{value}%</span>}
    </div>
  );
}

export function MetricCard({
  label,
  value,
  change,
  positive,
}: {
  label: string;
  value: string;
  change?: string;
  positive?: boolean;
}) {
  return (
    <div className="bg-bg-surface border border-border rounded-lg p-4 transition-colors hover:border-border-hover">
      <div className="text-[11px] text-text-muted uppercase tracking-wide mb-1.5">{label}</div>
      <div className="font-mono text-lg font-medium text-text-primary tabular-nums">{value}</div>
      {change && (
        <div className={cn('font-mono text-xs mt-1 tabular-nums', positive ? 'text-success' : 'text-danger')}>
          {positive ? '+' : ''}
          {change}
        </div>
      )}
    </div>
  );
}

export function Skeleton({ className }: { className?: string }) {
  return <div className={cn('skeleton rounded', className)} />;
}

export function SkeletonText({ lines = 3 }: { lines?: number }) {
  return (
    <div className="space-y-2">
      {Array.from({ length: lines }).map((_, i) => (
        <Skeleton key={i} className={cn('h-4', i === lines - 1 ? 'w-2/3' : 'w-full')} />
      ))}
    </div>
  );
}

export function SectionCard({
  title,
  children,
  action,
  className,
}: {
  title?: string;
  children: ReactNode;
  action?: ReactNode;
  className?: string;
}) {
  return (
    <div className={cn('bg-bg-surface border border-border rounded-lg', className)}>
      {title && (
        <div className="flex items-center justify-between px-5 py-3.5 border-b border-border">
          <h3 className="text-sm font-medium text-text-primary">{title}</h3>
          {action}
        </div>
      )}
      <div className="p-5">{children}</div>
    </div>
  );
}

export function ImpactBadge({ level }: { level: 'high' | 'medium' | 'low' }) {
  const styles = {
    high: 'bg-danger/10 text-danger border-danger/20',
    medium: 'bg-warning/10 text-warning border-warning/20',
    low: 'bg-accent/10 text-accent border-accent/20',
  };
  return (
    <span className={cn('inline-flex items-center text-[10px] font-mono font-bold uppercase tracking-wider px-1.5 py-0.5 rounded border', styles[level])}>
      {level}
    </span>
  );
}

export function SentimentDot({ sentiment }: { sentiment: 'positive' | 'neutral' | 'negative' }) {
  const colors = {
    positive: 'bg-success',
    neutral: 'bg-text-muted',
    negative: 'bg-danger',
  };
  return <span className={cn('inline-block w-2 h-2 rounded-full', colors[sentiment])} />;
}

export function ProgressBar({ value, className }: { value: number; className?: string }) {
  return (
    <div className={cn('w-full h-1 bg-border rounded-full overflow-hidden', className)}>
      <div
        className="h-full bg-accent rounded-full transition-all duration-700 ease-out"
        style={{ width: `${value}%` }}
      />
    </div>
  );
}

export function TickerLogo({
  name,
  color = "#6B7280",
  logoUrl,
  size = 32,
}: {
  name: string;
  color?: string;
  logoUrl?: string | null;
  size?: number;
}) {

  const initials = name
    .split(" ")
    .slice(0, 2)
    .map((w) => w[0])
    .join("")
    .toUpperCase();


  return (
    <div
      className="
      flex
      items-center
      justify-center
      rounded-lg
      font-mono
      font-bold
      text-sm
      shrink-0
      overflow-hidden
      "
      style={{
        width:size,
        height:size,
        backgroundColor:`${color}20`,
        color,
        border:`1px solid ${color}40`,
      }}
    >

      {
        logoUrl ?

        <img
          src={logoUrl}
          alt={name}
          className="
          w-full
          h-full
          object-contain
          "
        />

        :

        initials

      }


    </div>
  );
}
export function Divider({ label, className }: { label?: string; className?: string }) {
  if (!label) return <div className={cn('h-px bg-border', className)} />;
  return (
    <div className="flex items-center gap-3">
      <div className="h-px bg-border flex-1" />
      <span className="text-[10px] text-text-faint uppercase tracking-widest font-mono">{label}</span>
      <div className="h-px bg-border flex-1" />
    </div>
  );
}

export function EmptyState({
  icon,
  title,
  description,
  action,
}: {
  icon: ReactNode;
  title: string;
  description: string;
  action?: ReactNode;
}) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-6 text-center animate-fade-in">
      <div className="w-12 h-12 rounded-lg bg-bg-surface border border-border flex items-center justify-center text-text-muted mb-4">
        {icon}
      </div>
      <h3 className="text-sm font-medium text-text-primary mb-1.5">{title}</h3>
      <p className="text-sm text-text-muted max-w-sm mb-4">{description}</p>
      {action}
    </div>
  );
}

