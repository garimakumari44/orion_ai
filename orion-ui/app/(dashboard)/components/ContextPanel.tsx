import { useState } from 'react';
import {
  ChevronDown,
  FileText,
  TrendingUp,
  Newspaper,
  DollarSign,
} from 'lucide-react';
import { cn, SentimentDot, Divider } from '../components/ui';
import type { CompanyData } from '@/types';

interface ContextPanelProps {
  data: CompanyData;
  activeTab: string;
}

function CollapsibleSection({
  title,
  icon: Icon,
  children,
  defaultOpen = true,
}: {
  title: string;
  icon: typeof FileText;
  children: React.ReactNode;
  defaultOpen?: boolean;
}) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <div className="border-b border-border">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center gap-2 px-4 py-2.5 text-left hover:bg-bg-hover/30 transition-colors"
      >
        <Icon className="w-3.5 h-3.5 text-text-faint" />

        <span className="text-xs font-medium text-text-secondary flex-1">
          {title}
        </span>

        <ChevronDown
          className={cn(
            'w-3.5 h-3.5 text-text-faint transition-transform',
            open ? '' : '-rotate-90'
          )}
        />
      </button>

      {open && (
        <div className="px-4 pb-3 animate-fade-in">
          {children}
        </div>
      )}
    </div>
  );
}

export function ContextPanel({
  data,
  activeTab,
}: ContextPanelProps) {
  const showFinancials =
    activeTab === 'overview' ||
    activeTab === 'analysis' ||
    activeTab === 'report';

  const showNews =
    activeTab === 'overview' ||
    activeTab === 'analysis';

  const showValuation =
    activeTab === 'analysis' ||
    activeTab === 'report';

  /*
   * Normalize optional backend data.
   *
   * The backend may not return every section for every research.
   * Never call .map() / .slice() directly on potentially undefined
   * values.
   */
  const financialMetrics = data.financialMetrics ?? [];
  const news = data.news ?? [];
  const sources = data.sources ?? [];
  const comparables = data.comparables ?? [];
  const assumptions = data.dcf?.assumptions ?? [];

  return (
    <aside className="w-72 shrink-0 bg-bg-base border-l border-border overflow-y-auto h-full">
      <div className="px-4 py-2.5 border-b border-border">
        <span className="text-[10px] text-text-faint uppercase tracking-widest font-mono">
          Context
        </span>
      </div>

      {showFinancials && (
        <CollapsibleSection
          title="Financial Tables"
          icon={DollarSign}
        >
          <div className="space-y-1">
            <button className="w-full flex items-center justify-between px-2 py-1.5 rounded text-xs text-text-secondary hover:bg-bg-hover transition-colors">
              <span>Income Statement</span>
              <span className="font-mono text-text-faint">→</span>
            </button>

            <button className="w-full flex items-center justify-between px-2 py-1.5 rounded text-xs text-text-secondary hover:bg-bg-hover transition-colors">
              <span>Balance Sheet</span>
              <span className="font-mono text-text-faint">→</span>
            </button>

            <button className="w-full flex items-center justify-between px-2 py-1.5 rounded text-xs text-text-secondary hover:bg-bg-hover transition-colors">
              <span>Cash Flow Statement</span>
              <span className="font-mono text-text-faint">→</span>
            </button>

            <button className="w-full flex items-center justify-between px-2 py-1.5 rounded text-xs text-text-secondary hover:bg-bg-hover transition-colors">
              <span>Key Ratios</span>
              <span className="font-mono text-text-faint">→</span>
            </button>
          </div>

          <div className="mt-3 pt-3 border-t border-border-subtle">
            <div className="text-[10px] text-text-faint uppercase tracking-wider font-mono mb-2">
              Latest Quarter
            </div>

            <div className="space-y-1.5">
              {financialMetrics.length > 0 ? (
                financialMetrics.slice(0, 4).map((m) => (
                  <div
                    key={m.label}
                    className="flex items-center justify-between text-xs"
                  >
                    <span className="text-text-muted">
                      {m.label}
                    </span>

                    <span className="font-mono text-text-secondary tabular-nums">
                      {m.value}
                    </span>
                  </div>
                ))
              ) : (
                <div className="text-xs text-text-faint">
                  No financial metrics available.
                </div>
              )}
            </div>
          </div>
        </CollapsibleSection>
      )}

      {showValuation && (
        <CollapsibleSection
          title="Valuation"
          icon={TrendingUp}
        >
          <div className="space-y-1">
            <button className="w-full flex items-center justify-between px-2 py-1.5 rounded text-xs text-text-secondary hover:bg-bg-hover transition-colors">
              <span>DCF Model</span>

              <span className="font-mono text-text-faint">
                {data.dcf?.fairValue ?? '—'}
              </span>
            </button>

            <button className="w-full flex items-center justify-between px-2 py-1.5 rounded text-xs text-text-secondary hover:bg-bg-hover transition-colors">
              <span>Comparable Companies</span>

              <span className="font-mono text-text-faint">
                {comparables.length}
              </span>
            </button>

            <button className="w-full flex items-center justify-between px-2 py-1.5 rounded text-xs text-text-secondary hover:bg-bg-hover transition-colors">
              <span>Sensitivity Analysis</span>

              <span className="font-mono text-text-faint">
                →
              </span>
            </button>
          </div>

          <div className="mt-3 pt-3 border-t border-border-subtle">
            <div className="text-[10px] text-text-faint uppercase tracking-wider font-mono mb-2">
              DCF Assumptions
            </div>

            <div className="space-y-1.5">
              {assumptions.length > 0 ? (
                assumptions.map((a) => (
                  <div
                    key={a.label}
                    className="flex items-center justify-between text-xs"
                  >
                    <span className="text-text-muted">
                      {a.label}
                    </span>

                    <span className="font-mono text-text-secondary">
                      {a.value}
                    </span>
                  </div>
                ))
              ) : (
                <div className="text-xs text-text-faint">
                  No DCF assumptions available.
                </div>
              )}
            </div>
          </div>
        </CollapsibleSection>
      )}

      {showNews && (
        <CollapsibleSection
          title="News & Sentiment"
          icon={Newspaper}
        >
          <div className="space-y-2.5">
            {news.length > 0 ? (
              news.slice(0, 4).map((n) => (
                <div
                  key={n.id}
                  className="group cursor-pointer"
                >
                  <div className="flex items-start gap-2">
                    <SentimentDot sentiment={n.sentiment} />

                    <div className="flex-1 min-w-0">
                      <p className="text-xs text-text-secondary leading-snug group-hover:text-text-primary transition-colors line-clamp-2">
                        {n.headline}
                      </p>

                      <p className="text-[10px] text-text-faint mt-0.5 font-mono">
                        {n.source} · {n.date}
                      </p>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-xs text-text-faint">
                No news available.
              </div>
            )}
          </div>

          <Divider className="my-3" />

          <div className="text-[10px] text-text-faint uppercase tracking-wider font-mono mb-2">
            Sentiment Trend
          </div>

          <div className="flex items-center gap-1.5">
            <div className="flex-1 h-1.5 bg-border rounded-full overflow-hidden flex">
              <div
                className="bg-success h-full"
                style={{ width: '60%' }}
              />

              <div
                className="bg-text-muted h-full"
                style={{ width: '25%' }}
              />

              <div
                className="bg-danger h-full"
                style={{ width: '15%' }}
              />
            </div>
          </div>

          <div className="flex items-center justify-between mt-1.5 text-[10px] font-mono">
            <span className="text-success">
              60% Positive
            </span>

            <span className="text-text-muted">
              25% Neutral
            </span>

            <span className="text-danger">
              15% Neg
            </span>
          </div>
        </CollapsibleSection>
      )}

      <CollapsibleSection
        title="Sources"
        icon={FileText}
        defaultOpen={false}
      >
        <div className="space-y-1.5">
          {sources.length > 0 ? (
            sources.map((s) => (
              <div
                key={s.name}
                className="flex items-center justify-between text-xs"
              >
                <div>
                  <div className="text-text-secondary">
                    {s.name}
                  </div>

                  <div className="text-[10px] text-text-faint">
                    {s.type}
                  </div>
                </div>

                <span className="font-mono text-text-faint">
                  {s.count}
                </span>
              </div>
            ))
          ) : (
            <div className="text-xs text-text-faint">
              No sources available.
            </div>
          )}
        </div>
      </CollapsibleSection>
    </aside>
  );
}