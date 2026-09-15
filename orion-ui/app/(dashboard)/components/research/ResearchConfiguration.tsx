import { useState } from 'react';
import { cn } from '../../components/ui';
import { CompanySelector } from './CompanySelector';
import type {
  ResearchType,
  ResearchObjective,
  ResearchDepth,
  AnalysisHorizon,
  OutputFormat,
  CompanySearchResult,
} from '@/types';

interface ResearchConfigurationProps {
  type: ResearchType;
  config: Partial<ResearchConfigData>;
  onChange: (config: Partial<ResearchConfigData>) => void;
}

interface ResearchConfigData {
  company: CompanySearchResult | null;
  comparisonCompanies: CompanySearchResult[];
  industry: string;
  theme: string;
  objective: ResearchObjective;
  depth: ResearchDepth;
  horizon: AnalysisHorizon;
  dataSources: string[];
  outputFormats: OutputFormat[];
}

const objectives: { id: ResearchObjective; title: string; description: string }[] = [
  { id: 'full', title: 'Full Equity Research', description: 'Complete investment analysis' },
  { id: 'earnings', title: 'Earnings Analysis', description: 'Analyze quarterly performance' },
  { id: 'valuation', title: 'Valuation Analysis', description: 'DCF, multiples, price targets' },
  { id: 'competitive', title: 'Competitive Analysis', description: 'Industry and competitor positioning' },
  { id: 'risk', title: 'Risk Assessment', description: 'Identify business and market risks' },
  { id: 'memo', title: 'Investment Memo', description: 'Generate investor-ready summary' },
];

const depths: { id: ResearchDepth; title: string; description: string }[] = [
  { id: 'quick', title: 'Quick', description: 'Basic overview' },
  { id: 'standard', title: 'Standard', description: 'Professional analyst report' },
  { id: 'comprehensive', title: 'Comprehensive', description: 'Deep institutional research' },
];

const horizons: { id: AnalysisHorizon; title: string; description: string }[] = [
  { id: 'short', title: 'Short Term', description: '6–12 months' },
  { id: 'medium', title: 'Medium Term', description: '1–3 years' },
  { id: 'long', title: 'Long Term', description: '3–5 years' },
];

const dataSourcesList = [
  'SEC Filings',
  'Earnings Reports',
  'Earnings Transcripts',
  'Financial Statements',
  'Market Data',
  'News',
  'Analyst Estimates',
  'Industry Data',
];

const outputFormatsList: { id: OutputFormat; label: string }[] = [
  { id: 'report', label: 'Research Report' },
  { id: 'summary', label: 'Executive Summary' },
  { id: 'memo', label: 'Investment Memo' },
  { id: 'dashboard', label: 'Dashboard View' },
  { id: 'presentation', label: 'Presentation' },
];

export function ResearchConfiguration({ type, config, onChange }: ResearchConfigurationProps) {
  const [depth, setDepth] = useState<ResearchDepth>(config.depth || 'comprehensive');
  const [objective, setObjective] = useState<ResearchObjective>(config.objective || 'full');
  const [horizon, setHorizon] = useState<AnalysisHorizon>(config.horizon || 'medium');
  const [sources, setSources] = useState<string[]>(config.dataSources || dataSourcesList);
  const [formats, setFormats] = useState<OutputFormat[]>(config.outputFormats || ['report', 'dashboard', 'memo']);

  const updateField = <K extends keyof ResearchConfigData>(key: K, value: ResearchConfigData[K]) => {
    const update = { [key]: value } as Partial<ResearchConfigData>;
    if (key === 'depth') setDepth(value as ResearchDepth);
    if (key === 'objective') setObjective(value as ResearchObjective);
    if (key === 'horizon') setHorizon(value as AnalysisHorizon);
    if (key === 'dataSources') setSources(value as string[]);
    if (key === 'outputFormats') setFormats(value as OutputFormat[]);
    onChange(update);
  };

  const toggleSource = (source: string) => {
    const next = sources.includes(source) ? sources.filter((s) => s !== source) : [...sources, source];
    updateField('dataSources', next);
  };

  const toggleFormat = (format: OutputFormat) => {
    const next = formats.includes(format) ? formats.filter((f) => f !== format) : [...formats, format];
    updateField('outputFormats', next);
  };

  const typeLabel: Record<ResearchType, string> = {
  company_research: "Company",
  industry_research: "Industry",
  company_comparison: "Comparison",
  theme_research: "Theme",
  portfolio_analysis: "Portfolio",
  market_macro: "Market & Macro",
};
  return (
    <div className="max-w-3xl mx-auto px-8 py-8 animate-fade-in">
      <div className="mb-6">
        <h1 className="text-xl font-semibold text-text-primary">Configure {typeLabel[type]} Research</h1>
        <p className="text-sm text-text-muted mt-1">Customize the scope, depth, and output of your analysis.</p>
      </div>

      {/* Section 1: Target Selection */}
      {(type === "company_research" || type === "company_comparison") && ( 
        <ConfigSection number={1} title="Company Selection">
          <CompanySelector
            label="Primary Company"
            selected={config.company || null}
            onSelect={(c) => updateField('company', c)}
          />
          {type === "company_comparison" && (
            <div className="mt-4">
              <CompanySelector
                label="Comparison Company"
                selected={config.comparisonCompanies?.[0] || null}
                onSelect={(c) => updateField('comparisonCompanies', c ? [c] : [])}
                placeholder="Search company to compare..."
              />
            </div>
          )}
        </ConfigSection>
      )}

      {type === "industry_research" && (
        <ConfigSection number={1} title="Industry Selection">
          <input
            value={config.industry || ''}
            onChange={(e) => updateField('industry', e.target.value)}
            placeholder="e.g. Semiconductors, Renewable Energy, Biotechnology"
            className="w-full bg-bg-surface border border-border rounded-lg px-3 py-2.5 text-sm text-text-primary placeholder:text-text-faint outline-none focus:border-border-hover transition-colors"
          />
        </ConfigSection>
      )}

     {type === "theme_research" && (
        <ConfigSection number={1} title="Investment Theme">
          <input
            value={config.theme || ''}
            onChange={(e) => updateField('theme', e.target.value)}
            placeholder="e.g. AI Infrastructure, Renewable Energy, Semiconductor Growth"
            className="w-full bg-bg-surface border border-border rounded-lg px-3 py-2.5 text-sm text-text-primary placeholder:text-text-faint outline-none focus:border-border-hover transition-colors"
          />
        </ConfigSection>
      )}

      {/* Section 2: Research Objective */}
      <ConfigSection number={2} title="Research Objective">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
          {objectives.map((obj) => (
            <button
              key={obj.id}
              onClick={() => updateField('objective', obj.id)}
              className={cn(
                'text-left p-3.5 rounded-lg border transition-all',
                objective === obj.id
                  ? 'border-accent bg-accent/5 ring-1 ring-accent/20'
                  : 'border-border bg-bg-surface hover:border-border-hover',
              )}
            >
              <div className="text-sm font-medium text-text-primary">{obj.title}</div>
              <div className="text-xs text-text-muted mt-0.5">{obj.description}</div>
            </button>
          ))}
        </div>
      </ConfigSection>

      {/* Section 3: Research Depth */}
      <ConfigSection number={3} title="Research Depth">
        <div className="grid grid-cols-3 gap-3">
          {depths.map((d) => (
            <button
              key={d.id}
              onClick={() => updateField('depth', d.id)}
              className={cn(
                'text-left p-4 rounded-lg border transition-all',
                depth === d.id
                  ? 'border-accent bg-accent/5 ring-1 ring-accent/20'
                  : 'border-border bg-bg-surface hover:border-border-hover',
              )}
            >
              <div className="text-sm font-medium text-text-primary">{d.title}</div>
              <div className="text-xs text-text-muted mt-0.5">{d.description}</div>
            </button>
          ))}
        </div>
      </ConfigSection>

      {/* Section 4: Analysis Horizon */}
      <ConfigSection number={4} title="Analysis Horizon">
        <div className="grid grid-cols-3 gap-3">
          {horizons.map((h) => (
            <button
              key={h.id}
              onClick={() => updateField('horizon', h.id)}
              className={cn(
                'text-left p-4 rounded-lg border transition-all',
                horizon === h.id
                  ? 'border-accent bg-accent/5 ring-1 ring-accent/20'
                  : 'border-border bg-bg-surface hover:border-border-hover',
              )}
            >
              <div className="text-sm font-medium text-text-primary">{h.title}</div>
              <div className="text-xs text-text-muted mt-0.5">{h.description}</div>
            </button>
          ))}
        </div>
      </ConfigSection>

      {/* Section 5: Data Sources */}
      <ConfigSection number={5} title="Data Sources">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2.5">
          {dataSourcesList.map((source) => (
            <button
              key={source}
              onClick={() => toggleSource(source)}
              className={cn(
                'flex items-center gap-2 px-3 py-2.5 rounded-lg border text-sm transition-all',
                sources.includes(source)
                  ? 'border-accent/40 bg-accent/10 text-text-primary'
                  : 'border-border bg-bg-surface text-text-muted hover:border-border-hover',
              )}
            >
              <div
                className={cn(
                  'w-4 h-4 rounded border flex items-center justify-center shrink-0 transition-colors',
                  sources.includes(source) ? 'bg-accent border-accent' : 'border-border',
                )}
              >
                {sources.includes(source) && (
                  <svg className="w-2.5 h-2.5 text-white" viewBox="0 0 12 12" fill="none">
                    <path d="M2.5 6L5 8.5L9.5 3.5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                )}
              </div>
              <span className="text-xs">{source}</span>
            </button>
          ))}
        </div>
      </ConfigSection>

      {/* Section 6: Output Format */}
      <ConfigSection number={6} title="Output Format">
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2.5">
          {outputFormatsList.map((format) => (
            <button
              key={format.id}
              onClick={() => toggleFormat(format.id)}
              className={cn(
                'flex items-center gap-2 px-3 py-2.5 rounded-lg border text-sm transition-all',
                formats.includes(format.id)
                  ? 'border-accent/40 bg-accent/10 text-text-primary'
                  : 'border-border bg-bg-surface text-text-muted hover:border-border-hover',
              )}
            >
              <div
                className={cn(
                  'w-4 h-4 rounded border flex items-center justify-center shrink-0 transition-colors',
                  formats.includes(format.id) ? 'bg-accent border-accent' : 'border-border',
                )}
              >
                {formats.includes(format.id) && (
                  <svg className="w-2.5 h-2.5 text-white" viewBox="0 0 12 12" fill="none">
                    <path d="M2.5 6L5 8.5L9.5 3.5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                )}
              </div>
              <span className="text-xs">{format.label}</span>
            </button>
          ))}
        </div>
      </ConfigSection>
    </div>
  );
}

function ConfigSection({ number, title, children }: { number: number; title: string; children: React.ReactNode }) {
  return (
    <div className="mb-6">
      <div className="flex items-center gap-2 mb-3">
        <span className="w-5 h-5 rounded-full bg-bg-elevated border border-border flex items-center justify-center text-[10px] font-mono text-text-faint">
          {number}
        </span>
        <h2 className="text-sm font-medium text-text-primary">{title}</h2>
      </div>
      {children}
    </div>
  );
}
