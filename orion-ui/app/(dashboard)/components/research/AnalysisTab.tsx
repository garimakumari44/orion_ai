
import { useState } from 'react';
import { cn, Divider } from '../../components/ui';
import type { CompanyData } from '@/types';

interface AnalysisTabProps {
  data: CompanyData;
}

export function AnalysisTab({ data }: AnalysisTabProps) {
  const analysisSections = data.analysisSections ?? [];

  const [activeSection, setActiveSection] = useState(
    analysisSections[0]?.id ?? ''
  );

  return (
    <div className="max-w-4xl mx-auto px-8 py-6 animate-fade-in">
      <div className="flex gap-8">
        <nav className="w-40 shrink-0 sticky top-0 self-start">
          <div className="text-[10px] text-text-faint uppercase tracking-widest font-mono mb-2">
            Sections
          </div>

          <div className="space-y-0.5">
            {analysisSections.map((section) => (
              <button
                key={section.id}
                onClick={() => section.id && setActiveSection(section.id)}
                className={cn(
                  'w-full text-left px-2.5 py-1.5 rounded text-xs transition-colors',
                  activeSection === section.id
                    ? 'bg-bg-hover text-text-primary'
                    : 'text-text-muted hover:text-text-secondary hover:bg-bg-hover/50',
                )}
              >
                {section.title}
              </button>
            ))}
          </div>
        </nav>

        <div className="flex-1 min-w-0 space-y-8 pb-8">
          {analysisSections.map((section) => (
            <section
              key={section.id}
              id={section.id}
              className="scroll-mt-6"
            >
              <h2 className="text-base font-semibold text-text-primary mb-3">
                {section.title}
              </h2>

              <div className="space-y-3">
                {section.content.map((paragraph, i) => (
                  <p
                    key={i}
                    className="text-sm text-text-secondary leading-relaxed"
                  >
                    {paragraph}
                  </p>
                ))}
              </div>

              {section.keyPoints && section.keyPoints.length > 0 && (
                <>
                  <div className="mt-4 mb-2 text-[10px] text-text-faint uppercase tracking-wider font-mono">
                    Key Points
                  </div>

                  <ul className="space-y-1.5">
                    {section.keyPoints.map((keyPoint, i) => (
                      <li
                        key={i}
                        className="flex items-start gap-2.5 text-sm text-text-muted"
                      >
                        <span className="mt-1.5 w-1 h-1 rounded-full bg-accent shrink-0" />
                        {keyPoint}
                      </li>
                    ))}
                  </ul>
                </>
              )}

              <Divider className="mt-8" />
            </section>
          ))}

          {analysisSections.length === 0 && (
            <div className="py-12 text-center">
              <p className="text-sm text-text-muted">
                No analysis is available yet.
              </p>
            </div>
          )}

          <section id="financials-tables">
            <h2 className="text-base font-semibold text-text-primary mb-4">
              Financial Statements
            </h2>

            <div className="space-y-6">
              <div>
                <h3 className="text-sm font-medium text-text-secondary mb-2">
                  Income Statement
                </h3>

                <div className="bg-bg-surface border border-border rounded-lg overflow-hidden">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-border">
                        <th className="text-left text-[10px] text-text-faint uppercase tracking-wider font-mono px-4 py-2.5">
                          Item
                        </th>
                        <th className="text-right text-[10px] text-text-faint uppercase tracking-wider font-mono px-4 py-2.5">
                          FY2024
                        </th>
                        <th className="text-right text-[10px] text-text-faint uppercase tracking-wider font-mono px-4 py-2.5">
                          FY2023
                        </th>
                        <th className="text-right text-[10px] text-text-faint uppercase tracking-wider font-mono px-4 py-2.5">
                          FY2022
                        </th>
                        <th className="text-right text-[10px] text-text-faint uppercase tracking-wider font-mono px-4 py-2.5">
                          YoY
                        </th>
                      </tr>
                    </thead>

                    <tbody>
                      {data.incomeStatement?.map((row, i) => (
                        <tr
                          key={i}
                          className="border-b border-border-subtle last:border-0 hover:bg-bg-hover/20 transition-colors"
                        >
                          <td className="px-4 py-2.5 text-xs text-text-secondary">
                            {row.item}
                          </td>

                          <td className="px-4 py-2.5 text-right font-mono text-xs text-text-primary tabular-nums">
                            {row.fy2024}
                          </td>

                          <td className="px-4 py-2.5 text-right font-mono text-xs text-text-muted tabular-nums">
                            {row.fy2023}
                          </td>

                          <td className="px-4 py-2.5 text-right font-mono text-xs text-text-muted tabular-nums">
                            {row.fy2022}
                          </td>

                          <td
                            className={cn(
                              'px-4 py-2.5 text-right font-mono text-xs tabular-nums',
                              row.change?.startsWith('+')
                                ? 'text-success'
                                : 'text-danger',
                            )}
                          >
                            {row.change}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              <div>
                <h3 className="text-sm font-medium text-text-secondary mb-2">
                  Cash Flow Statement
                </h3>

                <div className="bg-bg-surface border border-border rounded-lg overflow-hidden">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-border">
                        <th className="text-left text-[10px] text-text-faint uppercase tracking-wider font-mono px-4 py-2.5">
                          Item
                        </th>
                        <th className="text-right text-[10px] text-text-faint uppercase tracking-wider font-mono px-4 py-2.5">
                          FY2024
                        </th>
                        <th className="text-right text-[10px] text-text-faint uppercase tracking-wider font-mono px-4 py-2.5">
                          FY2023
                        </th>
                        <th className="text-right text-[10px] text-text-faint uppercase tracking-wider font-mono px-4 py-2.5">
                          FY2022
                        </th>
                      </tr>
                    </thead>

                    <tbody>
                      {data.cashFlow?.map((row, i) => (
                        <tr
                          key={i}
                          className="border-b border-border-subtle last:border-0 hover:bg-bg-hover/20 transition-colors"
                        >
                          <td className="px-4 py-2.5 text-xs text-text-secondary">
                            {row.item}
                          </td>

                          <td className="px-4 py-2.5 text-right font-mono text-xs text-text-primary tabular-nums">
                            {row.fy2024}
                          </td>

                          <td className="px-4 py-2.5 text-right font-mono text-xs text-text-muted tabular-nums">
                            {row.fy2023}
                          </td>

                          <td className="px-4 py-2.5 text-right font-mono text-xs text-text-muted tabular-nums">
                            {row.fy2022}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}


