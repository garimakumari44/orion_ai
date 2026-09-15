import { Check } from "lucide-react";

import { cn } from "../../components/ui";

import type {
  ResearchType,
  ResearchObjective,
  ResearchDepth,
  AnalysisHorizon,
  OutputFormat,
  CompanySearchResult,
} from "@/types";


interface ResearchReviewConfig {

  type: ResearchType;


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



interface ResearchReviewProps {

  config: ResearchReviewConfig;

  onStart: () => void;

  isStarting: boolean;

}



const typeLabels: Record<ResearchType, string> = {

  company_research: "Company Research",

  company_comparison: "Company Comparison",

  industry_research: "Industry Research",

  theme_research: "Investment Theme",

  portfolio_analysis: "Portfolio Analysis",

  market_macro: "Market & Macro",

};



const objectiveLabels: Record<ResearchObjective, string> = {

  full: "Full Equity Research",

  earnings: "Earnings Analysis",

  valuation: "Valuation Analysis",

  competitive: "Competitive Analysis",

  risk: "Risk Assessment",

  memo: "Investment Memo",

};



const depthLabels: Record<ResearchDepth, string> = {

  quick: "Quick",

  standard: "Standard",

  comprehensive: "Comprehensive",

};



const horizonLabels: Record<AnalysisHorizon, string> = {

  short: "Short Term (6–12 months)",

  medium: "Medium Term (1–3 years)",

  long: "Long Term (3–5 years)",

};



const formatLabels: Record<OutputFormat, string> = {

  report: "Research Report",

  summary: "Executive Summary",

  memo: "Investment Memo",

  dashboard: "Dashboard View",

  presentation: "Presentation",

};



export function ResearchReview({
  config,
  onStart,
  isStarting,
}: ResearchReviewProps) {


  const target =
    config.company?.name ||
    config.comparisonCompanies[0]?.name ||
    config.industry ||
    config.theme ||
    "—";



  const rows = [

    {
      label: "Research Type",
      value: typeLabels[config.type],
    },


    {
      label: "Target",
      value: target,
    },


    ...(config.company?.ticker
      ? [
          {
            label: "Ticker",
            value: config.company.ticker,
          },
        ]
      : []),


    {
      label: "Objective",
      value:
        objectiveLabels[config.objective],
    },


    {
      label: "Depth",
      value:
        depthLabels[config.depth],
    },


    {
      label: "Horizon",
      value:
        horizonLabels[config.horizon],
    },

  ];



  return (

    <div className="p-6">

      <div className="mb-6">

        <h2 className="text-lg font-semibold text-text-primary">
          Review Research Plan
        </h2>


        <p className="text-sm text-text-muted mt-1">
          Confirm your configuration before the AI begins research.
        </p>

      </div>



      <div className="bg-bg-surface border border-border rounded-lg overflow-hidden">


        {rows.map((row, i) => (

          <div

            key={i}

            className={cn(
              "flex items-center justify-between px-5 py-3.5",
              i > 0 &&
                "border-t border-border-subtle"
            )}

          >

            <span className="text-xs text-text-faint uppercase tracking-wider font-mono">

              {row.label}

            </span>


            <span className="text-sm text-text-primary">

              {row.value}

            </span>


          </div>

        ))}



        <div className="border-t border-border-subtle px-5 py-3.5">


          <span className="text-xs text-text-faint uppercase tracking-wider font-mono block mb-2">

            Data Sources

          </span>



          <div className="flex flex-wrap gap-1.5">


            {config.dataSources.map((source) => (

              <span

                key={source}

                className="text-xs text-text-secondary bg-bg-elevated border border-border rounded px-2 py-1"

              >

                {source}

              </span>

            ))}


          </div>


        </div>





        <div className="border-t border-border-subtle px-5 py-3.5">


          <span className="text-xs text-text-faint uppercase tracking-wider font-mono block mb-2">

            Expected Output

          </span>




          <div className="flex flex-wrap gap-1.5">


            {config.outputFormats.map((format) => (

              <span

                key={format}

                className="text-xs text-text-secondary bg-bg-elevated border border-border rounded px-2 py-1"

              >

                {formatLabels[format]}

              </span>

            ))}


          </div>


        </div>



      </div>





      <button

        onClick={onStart}

        disabled={isStarting}

        className="w-full mt-6 flex items-center justify-center gap-2 px-4 py-3 rounded-lg bg-accent text-white text-sm font-medium hover:bg-accent-hover transition-colors disabled:opacity-50 disabled:cursor-not-allowed"

      >

        {isStarting ? (

          <>

            <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />

            Starting Research...

          </>

        ) : (

          <>

            <Check className="w-4 h-4" />

            Start Research

          </>

        )}

      </button>



    </div>

  );

}