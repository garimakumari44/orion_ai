import { Building2, Factory, Scale, TrendingUp, Briefcase, Globe } from 'lucide-react';
import { cn } from '../../components/ui';
import type { ApiResearchType } from '@/types';

interface ResearchTypeSelectorProps {
  selected: ApiResearchType | null;
  onSelect: (type: ApiResearchType) => void;
}

const researchTypes: {
  id: ApiResearchType;
  icon: typeof Building2;
  title: string;
  description: string;
  items: string[];
}[] = [
  {
    id: "company_research",
    icon: Building2,
    title: "Company Research",
    description: "Analyze a public company in depth",
    items: [
      "Business model",
      "Financial performance",
      "Competitive position",
      "Valuation",
      "Risks",
      "Investment thesis",
    ],
  },

  {
    id: "industry_research",
    icon: Factory,
    title: "Industry Research",
    description: "Analyze an industry or sector",
    items: [
      "Industry structure",
      "Market size",
      "Growth drivers",
      "Competitive landscape",
      "Future outlook",
    ],
  },

  {
    id: "company_comparison",
    icon: Scale,
    title: "Company Comparison",
    description: "Compare multiple companies head-to-head",
    items: [
      "Financial comparison",
      "Growth",
      "Margins",
      "Valuation",
      "Strengths and weaknesses",
    ],
  },

  {
    id: "theme_research",
    icon: TrendingUp,
    title: "Investment Theme",
    description: "Research market themes and trends",
    items: [
      "AI Infrastructure",
      "Renewable Energy",
      "Semiconductor Growth",
      "Market themes",
    ],
  },

  {
    id: "portfolio_analysis",
    icon: Briefcase,
    title: "Portfolio Analysis",
    description: "Analyze portfolio composition and risk",
    items: [
      "Holdings",
      "Exposure",
      "Risks",
      "Diversification",
    ],
  },

  {
    id: "market_macro",
    icon: Globe,
    title: "Market & Macro",
    description: "Analyze macroeconomic conditions",
    items: [
      "Interest rates",
      "Inflation",
      "Economic trends",
      "Market conditions",
    ],
  },
];

export function ResearchTypeSelector({ selected, onSelect }: ResearchTypeSelectorProps) {
  return (
    <div className="max-w-5xl mx-auto px-8 py-8 animate-fade-in">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-text-primary">Create New Research</h1>
        <p className="text-sm text-text-muted mt-1.5">
          Define your research objective and let AI build a structured investment analysis.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {researchTypes.map((type) => {
          const Icon = type.icon;
          const isSelected = selected === type.id;
          return (
            <button
              key={type.id}
              onClick={() => onSelect(type.id)}
              className={cn(
                'text-left bg-bg-surface border rounded-lg p-5 transition-all',
                isSelected
                  ? 'border-accent ring-1 ring-accent/30 bg-accent/5'
                  : 'border-border hover:border-border-hover hover:bg-bg-elevated/50',
              )}
            >
              <div className="flex items-center gap-3 mb-3">
                <div
                  className={cn(
                    'w-10 h-10 rounded-lg flex items-center justify-center transition-colors',
                    isSelected ? 'bg-accent/15 border border-accent/30' : 'bg-bg-elevated border border-border',
                  )}
                >
                  <Icon className={cn('w-5 h-5', isSelected ? 'text-accent' : 'text-text-faint')} />
                </div>
                <div>
                  <h3 className="text-sm font-medium text-text-primary">{type.title}</h3>
                  <p className="text-xs text-text-muted mt-0.5">{type.description}</p>
                </div>
              </div>
              <ul className="space-y-1 mt-3 pt-3 border-t border-border-subtle">
                {type.items.map((item, i) => (
                  <li key={i} className="flex items-center gap-1.5 text-xs text-text-faint">
                    <span className="w-1 h-1 rounded-full bg-text-faint shrink-0" />
                    {item}
                  </li>
                ))}
              </ul>
            </button>
          );
        })}
      </div>
    </div>
  );
}
