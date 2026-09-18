"use client";

import {
  Download,
  Printer,
  Share2,
} from "lucide-react";

import { useRef, useState } from "react";
import html2canvas from "html2canvas";
import jsPDF from "jspdf";
import { normalizeRecommendation } from "@/models/company";

import {
  cn,
  RecommendationBadge,
  ConfidenceIndicator,
  Divider,
  SectionCard,
} from "../../components/ui";

import type { CompanyData } from "@/types";

interface ReportTabProps {
  data: CompanyData;
}

function safeNumber(
  value: unknown,
  fallback = 0,
): number {
  const number = Number(value);

  return Number.isFinite(number)
    ? number
    : fallback;
}

function safeArray<T>(
  value: unknown,
): T[] {
  return Array.isArray(value) ? value : [];
}

export function ReportTab({
  data,
}: ReportTabProps) {
  /*
   * ============================================================
   * PDF EXPORT STATE
   * ============================================================
   */

  const reportRef = useRef<HTMLDivElement>(null);

  const [isExporting, setIsExporting] =
    useState(false);

  /*
   * ============================================================
   * SAFE DATA NORMALIZATION
   * ============================================================
   */

  const summary = data.summary;

  const incomeStatement = safeArray<
    typeof data.incomeStatement[number]
  >(data.incomeStatement);

  const evidence = safeArray<
    typeof data.evidence[number]
  >(data.evidence);

  const sources = safeArray<
    typeof data.sources[number]
  >(data.sources);

  const analysisSections = safeArray<
    typeof data.analysisSections[number]
  >(data.analysisSections);

  const dcf = data.dcf ?? {
    fairValue: 0,
    assumptions: [],
  };

  const comparables = safeArray<
    typeof data.comparables[number]
  >(data.comparables);

  const sensitivity = data.sensitivity ?? {
    growthRates: [],
    rows: [],
  };

  /*
   * ============================================================
   * DERIVED VALUES
   * ============================================================
   */

  const sourceCount = sources.reduce(
    (total, source) =>
      total + safeNumber(source.count),
    0,
  );

  const businessSection =
    analysisSections[0];

  const financialSection =
    analysisSections[1];

  const industrySection =
    analysisSections[2];

  const valuationSection =
    analysisSections[6];

  const recommendation =
    summary?.recommendation ?? "HOLD";

  const fairValue =
    safeNumber(summary?.fairValue);

  const currentPrice =
    safeNumber(summary?.currentPrice);

  const upside =
    safeNumber(
      summary?.upside,
      currentPrice > 0 && fairValue > 0
        ? ((fairValue - currentPrice) /
            currentPrice) *
            100
        : 0,
    );

  const confidence =
    safeNumber(summary?.confidence);

  /*
   * ============================================================
   * REAL PDF EXPORT
   * ============================================================
   */

  const exportPDF = async () => {
    if (!reportRef.current || isExporting) {
      return;
    }

    try {
      setIsExporting(true);

      const report = reportRef.current;

      /*
       * Wait one browser frame so React has finished
       * rendering the latest research result.
       */
      await new Promise<void>((resolve) => {
        requestAnimationFrame(() => {
          resolve();
        });
      });

      /*
       * Capture the complete rendered report.
       */
      const canvas = await html2canvas(
        report,
        {
          scale: 2,
          useCORS: true,
          allowTaint: true,
          backgroundColor: "#ffffff",
          logging: false,

          /*
           * Capture the complete report width/height,
           * not only the visible viewport.
           */
          width: report.scrollWidth,
          height: report.scrollHeight,

          windowWidth:
            report.scrollWidth,

          windowHeight:
            report.scrollHeight,
        },
      );

      const imageData =
        canvas.toDataURL("image/png", 1.0);

      /*
       * Create A4 PDF.
       */
      const pdf = new jsPDF({
        orientation: "portrait",
        unit: "mm",
        format: "a4",
        compress: true,
      });

      const pageWidth =
        pdf.internal.pageSize.getWidth();

      const pageHeight =
        pdf.internal.pageSize.getHeight();

      /*
       * PDF margins.
       */
      const margin = 10;

      const usableWidth =
        pageWidth - margin * 2;

      /*
       * Calculate image dimensions while
       * preserving aspect ratio.
       */
      const imageWidth =
        usableWidth;

      const imageHeight =
        (canvas.height * imageWidth) /
        canvas.width;

      /*
       * Track how much content remains.
       */
      let heightLeft = imageHeight;

      let position = margin;

      /*
       * First page.
       */
      pdf.addImage(
        imageData,
        "PNG",
        margin,
        position,
        imageWidth,
        imageHeight,
        undefined,
        "FAST",
      );

      heightLeft -=
        pageHeight - margin * 2;

      /*
       * Additional pages.
       */
      while (heightLeft > 0) {
        position =
          margin -
          (imageHeight - heightLeft);

        pdf.addPage();

        pdf.addImage(
          imageData,
          "PNG",
          margin,
          position,
          imageWidth,
          imageHeight,
          undefined,
          "FAST",
        );

        heightLeft -=
          pageHeight - margin * 2;
      }

      /*
       * ========================================================
       * FILE NAME
       * ========================================================
       */

      const companyName =
        summary?.name ??
        "Company Research";

      const ticker =
        summary?.ticker ??
        "";

      const safeFileName =
        `${companyName}${
          ticker
            ? `-${ticker}`
            : ""
        }-Research-Report`
          .replace(
            /[^a-z0-9-_]+/gi,
            "-",
          )
          .replace(
            /-+/g,
            "-",
          )
          .replace(
            /^-|-$/g,
            "",
          );

      /*
       * Download the PDF.
       */
      pdf.save(
        `${safeFileName}.pdf`,
      );

      console.info(
        "Research report PDF exported successfully:",
        `${safeFileName}.pdf`,
      );
    } catch (error) {
      console.error(
        "Failed to export research report:",
        error,
      );

      window.alert(
        "Failed to export the research report. Please try again.",
      );
    } finally {
      setIsExporting(false);
    }
  };

  /*
   * ============================================================
   * REPORT
   * ============================================================
   */

  return (
    <div
      ref={reportRef}
      className="max-w-3xl mx-auto px-8 py-8 animate-fade-in bg-white"
    >
      {/* ================================================= */}
      {/* Header */}
      {/* ================================================= */}

      <div className="flex items-center justify-between mb-6 pb-6 border-b border-border">
        <div>
          <div className="text-[10px] text-text-faint uppercase tracking-widest font-mono mb-1">
            Research Report
          </div>

          <h1 className="text-xl font-semibold text-text-primary">
            {summary?.name ??
              "Company Research"}

            {summary?.ticker
              ? ` (${summary.ticker})`
              : ""}
          </h1>

          <p className="text-xs text-text-muted mt-1">
            Generated{" "}
            {summary?.lastResearched ??
              "—"}{" "}
            · {sourceCount} sources analyzed
          </p>
        </div>

        <div className="flex items-center gap-1">
          {/* Share */}

          <button
            type="button"
            onClick={async () => {
              try {
                const shareText =
                  `${
                    summary?.name ??
                    "Company Research"
                  } Research Report`;

                if (
                  navigator.share
                ) {
                  await navigator.share(
                    {
                      title:
                        shareText,
                      text:
                        data.thesis ??
                        shareText,
                    },
                  );
                } else {
                  await navigator.clipboard.writeText(
                    window.location.href,
                  );

                  window.alert(
                    "Report link copied to clipboard.",
                  );
                }
              } catch (error) {
                console.error(
                  "Share failed:",
                  error,
                );
              }
            }}
            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-md text-xs text-text-muted hover:text-text-primary hover:bg-bg-hover transition-colors"
          >
            <Share2 className="w-3.5 h-3.5" />

            Share
          </button>

          {/* Print */}

          <button
            type="button"
            onClick={() =>
              window.print()
            }
            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-md text-xs text-text-muted hover:text-text-primary hover:bg-bg-hover transition-colors"
          >
            <Printer className="w-3.5 h-3.5" />

            Print
          </button>

          {/* REAL PDF EXPORT */}

          <button
            type="button"
            onClick={exportPDF}
            disabled={isExporting}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium bg-accent/10 border border-accent/20 text-accent hover:bg-accent/15 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Download
              className={cn(
                "w-3.5 h-3.5",
                isExporting &&
                  "animate-pulse",
              )}
            />

            {isExporting
              ? "Generating PDF..."
              : "Export PDF"}
          </button>
        </div>
      </div>

      {/* ================================================= */}
      {/* Executive Summary */}
      {/* ================================================= */}

      <section className="mb-8">
        <h2 className="text-sm font-semibold text-text-primary uppercase tracking-wider mb-3">
          Executive Summary
        </h2>

        <p className="text-sm text-text-secondary leading-relaxed">
          {data.thesis ||
            "The research completed successfully, but a complete investment thesis was not generated from the available evidence."}
        </p>

        <div className="flex items-center gap-6 mt-4 flex-wrap">
          {/* Recommendation */}

          <div>
            <div className="text-[10px] text-text-faint uppercase tracking-wider font-mono mb-1">
              Recommendation
            </div>

            <RecommendationBadge
  value={normalizeRecommendation(recommendation)}
  size="md"
/>
          </div>

          {/* Fair Value */}

          <div>
            <div className="text-[10px] text-text-faint uppercase tracking-wider font-mono mb-1">
              Fair Value
            </div>

            <div className="font-mono text-base text-text-primary tabular-nums">
              {fairValue > 0
                ? `$${fairValue.toFixed(
                    2,
                  )}`
                : "N/A"}
            </div>
          </div>

          {/* Upside */}

          <div>
            <div className="text-[10px] text-text-faint uppercase tracking-wider font-mono mb-1">
              Upside
            </div>

            <div
              className={cn(
                "font-mono text-base tabular-nums",
                upside >= 0
                  ? "text-success"
                  : "text-danger",
              )}
            >
              {currentPrice >
                0 &&
              fairValue >
                0
                ? `${
                    upside >=
                    0
                      ? "+"
                      : ""
                  }${upside.toFixed(
                    1,
                  )}%`
                : "N/A"}
            </div>
          </div>

          {/* Confidence */}

          <div>
            <div className="text-[10px] text-text-faint uppercase tracking-wider font-mono mb-1">
              Confidence
            </div>

            {confidence >
            0 ? (
              <ConfidenceIndicator
                value={
                  confidence
                }
              />
            ) : (
              <span className="text-sm text-text-muted">
                N/A
              </span>
            )}
          </div>
        </div>
      </section>

      <Divider className="mb-8" />

      {/* ================================================= */}
      {/* Business */}
      {/* ================================================= */}

      <section className="mb-8">
        <h2 className="text-sm font-semibold text-text-primary uppercase tracking-wider mb-3">
          Business
        </h2>

        {businessSection?.content
          ?.length ? (
          businessSection.content.map(
            (
              paragraph,
              index,
            ) => (
              <p
                key={index}
                className="text-sm text-text-secondary leading-relaxed mb-3"
              >
                {paragraph}
              </p>
            ),
          )
        ) : (
          <p className="text-sm text-text-muted">
            Business analysis was
            not returned by the
            research execution.
          </p>
        )}
      </section>

      <Divider className="mb-8" />

      {/* ================================================= */}
      {/* Financial Analysis */}
      {/* ================================================= */}

      <section className="mb-8">
        <h2 className="text-sm font-semibold text-text-primary uppercase tracking-wider mb-3">
          Financial Analysis
        </h2>

        {financialSection?.content
          ?.length ? (
          financialSection.content.map(
            (
              paragraph,
              index,
            ) => (
              <p
                key={index}
                className="text-sm text-text-secondary leading-relaxed mb-3"
              >
                {paragraph}
              </p>
            ),
          )
        ) : (
          <p className="text-sm text-text-muted mb-3">
            Financial analysis was
            generated from market
            data.
          </p>
        )}

        {incomeStatement.length >
          0 && (
          <div className="mt-4 bg-bg-surface border border-border rounded-lg overflow-hidden">
            <div className="px-4 py-2.5 border-b border-border">
              <span className="text-xs font-medium text-text-secondary">
                Income Statement
                Summary
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-border">
                    <th className="text-left text-[10px] text-text-faint uppercase tracking-wider font-mono px-4 py-2">
                      Item
                    </th>

                    <th className="text-right text-[10px] text-text-faint uppercase tracking-wider font-mono px-4 py-2">
                      FY2026
                    </th>

                    <th className="text-right text-[10px] text-text-faint uppercase tracking-wider font-mono px-4 py-2">
                      FY2025
                    </th>

                    <th className="text-right text-[10px] text-text-faint uppercase tracking-wider font-mono px-4 py-2">
                      Change
                    </th>
                  </tr>
                </thead>

                <tbody>
                  {incomeStatement
                    .slice(
                      0,
                      5,
                    )
                    .map(
                      (
                        row,
                        index,
                      ) => (
                        <tr
                          key={
                            index
                          }
                          className="border-b border-border-subtle last:border-0"
                        >
                          <td className="px-4 py-2 text-xs text-text-secondary">
                            {
                              row.item
                            }
                          </td>

                          <td className="px-4 py-2 text-right font-mono text-xs text-text-primary tabular-nums">
                            {row.fy2026 ??
                              row.fy2024 ??
                              "—"}
                          </td>

                          <td className="px-4 py-2 text-right font-mono text-xs text-text-muted tabular-nums">
                            {row.fy2025 ??
                              row.fy2023 ??
                              "—"}
                          </td>

                          <td
                            className={cn(
                              "px-4 py-2 text-right font-mono text-xs tabular-nums",
                              String(
                                row.change ??
                                  "",
                              ).startsWith(
                                "+",
                              )
                                ? "text-success"
                                : "text-danger",
                            )}
                          >
                            {row.change ??
                              "—"}
                          </td>
                        </tr>
                      ),
                    )}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </section>

      <Divider className="mb-8" />

      {/* ================================================= */}
      {/* Industry */}
      {/* ================================================= */}

      <section className="mb-8">
        <h2 className="text-sm font-semibold text-text-primary uppercase tracking-wider mb-3">
          Industry
        </h2>

        {industrySection?.content
          ?.length ? (
          industrySection.content.map(
            (
              paragraph,
              index,
            ) => (
              <p
                key={index}
                className="text-sm text-text-secondary leading-relaxed mb-3"
              >
                {paragraph}
              </p>
            ),
          )
        ) : (
          <p className="text-sm text-text-secondary leading-relaxed">
            Industry
            classification:{" "}
            <span className="text-text-primary">
              {data.summary
                ?.industry ??
                "Computer Hardware"}
            </span>
            .
          </p>
        )}
      </section>

      <Divider className="mb-8" />

      {/* ================================================= */}
      {/* Valuation */}
      {/* ================================================= */}

      <section className="mb-8">
        <h2 className="text-sm font-semibold text-text-primary uppercase tracking-wider mb-3">
          Valuation
        </h2>

        {valuationSection?.content
          ?.length ? (
          valuationSection.content.map(
            (
              paragraph,
              index,
            ) => (
              <p
                key={index}
                className="text-sm text-text-secondary leading-relaxed mb-3"
              >
                {paragraph}
              </p>
            ),
          )
        ) : (
          <p className="text-sm text-text-secondary leading-relaxed mb-4">
            Trading-multiple
            valuation is
            available. A complete
            intrinsic DCF valuation
            was not returned by the
            valuation agent.
          </p>
        )}

        <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* DCF */}

          <SectionCard title="DCF Assumptions">
            {dcf.assumptions
              ?.length ? (
              <div className="space-y-2">
                {dcf.assumptions.map(
                  (
                    assumption,
                  ) => (
                    <div
                      key={
                        assumption.label
                      }
                      className="flex items-center justify-between text-xs"
                    >
                      <span className="text-text-muted">
                        {
                          assumption.label
                        }
                      </span>

                      <span className="font-mono text-text-secondary">
                        {
                          assumption.value
                        }
                      </span>
                    </div>
                  ),
                )}
              </div>
            ) : (
              <p className="text-xs text-text-muted leading-relaxed">
                DCF assumptions
                are unavailable.
                The valuation
                agent did not
                produce an
                intrinsic DCF
                model for this
                research.
              </p>
            )}
          </SectionCard>

          {/* Comparables */}

          <SectionCard title="Comparable Companies">
            {comparables.length >
            0 ? (
              <div className="space-y-2">
                {comparables
                  .slice(
                    0,
                    4,
                  )
                  .map(
                    (
                      company,
                    ) => (
                      <div
                        key={
                          company.ticker
                        }
                        className="flex items-center justify-between text-xs"
                      >
                        <div>
                          <span className="font-mono text-text-secondary">
                            {
                              company.ticker
                            }
                          </span>

                          <span className="text-text-muted ml-2">
                            {
                              company.name
                            }
                          </span>
                        </div>

                        <div className="flex items-center gap-3 font-mono text-text-muted">
                          <span>
                            P/E{" "}
                            {company.pe >
                            0
                              ? company.pe.toFixed(
                                  1,
                                )
                              : "N/A"}
                          </span>

                          <span>
                            {company.revenueGrowth ??
                              "N/A"}
                          </span>
                        </div>
                      </div>
                    ),
                  )}
              </div>
            ) : (
              <p className="text-xs text-text-muted leading-relaxed">
                Comparable-company
                data is unavailable.
                The valuation agent
                returned multiple
                valuation methods
                but no peer dataset.
              </p>
            )}
          </SectionCard>
        </div>

        {/* Sensitivity */}

        {sensitivity.growthRates
          ?.length >
          0 &&
        sensitivity.rows
          ?.length >
          0 ? (
          <div className="mt-4">
            <SectionCard title="Sensitivity Analysis">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr>
                      <th className="text-left text-[10px] text-text-faint uppercase tracking-wider font-mono px-3 py-2">
                        WACC \ Growth
                      </th>

                      {sensitivity.growthRates.map(
                        (
                          growth,
                        ) => (
                          <th
                            key={
                              growth
                            }
                            className="text-right text-[10px] text-text-faint uppercase tracking-wider font-mono px-3 py-2"
                          >
                            {
                              growth
                            }
                          </th>
                        ),
                      )}
                    </tr>
                  </thead>

                  <tbody>
                    {sensitivity.rows.map(
                      (
                        row,
                      ) => (
                        <tr
                          key={
                            row.wacc
                          }
                          className="border-t border-border-subtle"
                        >
                          <td className="px-3 py-2 font-mono text-xs text-text-muted">
                            {
                              row.wacc
                            }
                          </td>

                          {row.values.map(
                            (
                              value,
                              index,
                            ) => {
                              const numericValue =
                                parseFloat(
                                  String(
                                    value,
                                  ).replace(
                                    /[$,%]/g,
                                    "",
                                  ),
                                );

                              const isBase =
                                Number.isFinite(
                                  numericValue,
                                ) &&
                                Math.abs(
                                  numericValue -
                                    safeNumber(
                                      dcf.fairValue,
                                    ),
                                ) <
                                  5;

                              return (
                                <td
                                  key={
                                    index
                                  }
                                  className={cn(
                                    "px-3 py-2 text-right font-mono text-xs tabular-nums",
                                    isBase
                                      ? "text-accent bg-accent/5 font-bold"
                                      : "text-text-muted",
                                  )}
                                >
                                  {
                                    value
                                  }
                                </td>
                              );
                            },
                          )}
                        </tr>
                      ),
                    )}
                  </tbody>
                </table>
              </div>
            </SectionCard>
          </div>
        ) : (
          <div className="mt-4 bg-bg-surface border border-border rounded-lg p-4">
            <div className="text-xs font-medium text-text-secondary mb-1">
              Sensitivity Analysis
            </div>

            <p className="text-xs text-text-muted leading-relaxed">
              Sensitivity analysis is
              unavailable because
              the valuation agent
              did not produce a
              complete DCF model.
            </p>
          </div>
        )}
      </section>

      <Divider className="mb-8" />

      {/* ================================================= */}
      {/* Recommendation */}
      {/* ================================================= */}

      <section className="mb-8">
        <h2 className="text-sm font-semibold text-text-primary uppercase tracking-wider mb-3">
          Recommendation
        </h2>

        <div className="bg-bg-surface border border-border rounded-lg p-5">
          <div className="flex items-center gap-4 mb-4 flex-wrap">
           <RecommendationBadge
  value={normalizeRecommendation(recommendation)}
  size="lg"
/>

            <div>
              <span className="text-sm text-text-secondary">
                Fair Value:{" "}
              </span>

              <span className="font-mono text-sm text-text-primary">
                {fairValue > 0
                  ? `$${fairValue.toFixed(
                      2,
                    )}`
                  : "N/A"}
              </span>

              <span className="text-sm text-text-muted mx-2">
                ·
              </span>

              <span className="text-sm text-text-secondary">
                Current:{" "}
              </span>

              <span className="font-mono text-sm text-text-primary">
                {currentPrice >
                0
                  ? `$${currentPrice.toFixed(
                      2,
                    )}`
                  : "N/A"}
              </span>

              <span className="text-sm text-text-muted mx-2">
                ·
              </span>

              <span
                className={cn(
                  "font-mono text-sm",
                  upside >= 0
                    ? "text-success"
                    : "text-danger",
                )}
              >
                {fairValue >
                  0 &&
                currentPrice >
                  0
                  ? `${
                      upside >=
                      0
                        ? "+"
                        : ""
                    }${upside.toFixed(
                      1,
                    )}% upside`
                  : "Upside unavailable"}
              </span>
            </div>
          </div>

          <p className="text-sm text-text-secondary leading-relaxed">
            {data.thesis ||
              "No final investment thesis was generated. The available research contains financial market data, industry classification, valuation-method availability, and risk analysis."}
          </p>

          <div className="mt-4 pt-4 border-t border-border">
            <div className="flex items-center gap-2 mb-2">
              {confidence >
              0 ? (
                <ConfidenceIndicator
                  value={
                    confidence
                  }
                />
              ) : (
                <span className="text-xs text-text-muted">
                  Confidence
                  unavailable
                </span>
              )}

              <span className="text-xs text-text-muted">
                Overall
                Confidence
              </span>
            </div>

            <p className="text-xs text-text-faint">
              Based on{" "}
              {evidence.length}{" "}
              evidence items
              from{" "}
              {sources.length}{" "}
              source types.
              Last updated{" "}
              {summary?.lastResearched ??
                "—"}.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}