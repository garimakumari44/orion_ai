"use client";

import {
  Lightbulb,
  AlertTriangle,
  Zap,
  Target,
  BarChart3,
} from "lucide-react";

import {
  cn,
  EmptyState,
} from "../../components/ui";

import type { ResearchInsight } from "@/types";

interface InsightPanelProps {
  /**
   * Insights returned by the research backend.
   *
   * The backend may omit this field while research is
   * running, so this is intentionally optional/null-safe.
   */
  insights?: ResearchInsight[] | null;
}

const typeConfig = {
  insight: {
    icon: Lightbulb,
    label: "Key Insight",
    color: "text-accent",
    bg: "bg-accent/10 border-accent/20",
  },
  risk: {
    icon: AlertTriangle,
    label: "Risk",
    color: "text-warning",
    bg: "bg-warning/10 border-warning/20",
  },
  catalyst: {
    icon: Zap,
    label: "Catalyst",
    color: "text-success",
    bg: "bg-success/10 border-success/20",
  },
} as const;

type InsightType = keyof typeof typeConfig;

type ParsedBlock =
  | {
      type: "heading";
      text: string;
      level: number;
    }
  | {
      type: "paragraph";
      text: string;
    }
  | {
      type: "bullet";
      text: string;
    }
  | {
      type: "separator";
    };

interface ParsedInsight {
  decision?: string;
  blocks: ParsedBlock[];
}

/* -------------------------------------------------------------------------- */
/* Markdown / text helpers                                                    */
/* -------------------------------------------------------------------------- */

function cleanMarkdown(text: string): string {
  return text
    .replace(/\\#/g, "#")
    .replace(/\\\*/g, "*")
    .replace(/\*\*(.*?)\*\*/g, "$1")
    .replace(/__(.*?)__/g, "$1")
    .replace(/`([^`]+)`/g, "$1")
    .trim();
}

function safeText(
  value: unknown,
  fallback = "",
): string {
  if (
    typeof value === "string" &&
    value.trim().length > 0
  ) {
    return value.trim();
  }

  return fallback;
}

function isRedundantHeading(
  text: string,
): boolean {
  const normalized = text
    .replace(/\*\*/g, "")
    .trim()
    .toLowerCase();

  if (
    normalized.startsWith(
      "investment decision:",
    ) ||
    normalized ===
      "structured investment analysis" ||
    normalized ===
      "structured investment analysis:" ||
    normalized === "investment analysis"
  ) {
    return true;
  }

  return false;
}

/* -------------------------------------------------------------------------- */
/* Insight parser                                                             */
/* -------------------------------------------------------------------------- */

function parseInsightDescription(
  description: string,
): ParsedInsight {
  if (!description) {
    return {
      blocks: [],
    };
  }

  const normalized = description
    .replace(/\r\n/g, "\n")
    .replace(/\r/g, "\n")
    .replace(/\\#/g, "#")
    .trim();

  if (!normalized) {
    return {
      blocks: [],
    };
  }

  const lines = normalized.split("\n");

  const blocks: ParsedBlock[] = [];

  let paragraphBuffer: string[] = [];

  let decision: string | undefined;

  const flushParagraph = () => {
    if (paragraphBuffer.length === 0) {
      return;
    }

    const text = cleanMarkdown(
      paragraphBuffer
        .join(" ")
        .replace(/\s+/g, " ")
        .trim(),
    );

    if (text) {
      blocks.push({
        type: "paragraph",
        text,
      });
    }

    paragraphBuffer = [];
  };

  for (const rawLine of lines) {
    const line = rawLine.trim();

    /* Empty line = paragraph boundary */
    if (!line) {
      flushParagraph();
      continue;
    }

    /* Markdown separator */
    if (/^[-*_]{3,}$/.test(line)) {
      flushParagraph();

      blocks.push({
        type: "separator",
      });

      continue;
    }

    /* Markdown heading */
    const headingMatch =
      line.match(/^(#{1,6})\s*(.+)$/);

    if (headingMatch) {
      flushParagraph();

      const level =
        headingMatch[1].length;

      const text = cleanMarkdown(
        headingMatch[2],
      );

      if (isRedundantHeading(text)) {
        continue;
      }

      if (
        text.toLowerCase() ===
        "decision"
      ) {
        continue;
      }

      blocks.push({
        type: "heading",
        text,
        level,
      });

      continue;
    }

    /* Bullet list */
    const bulletMatch =
      line.match(/^[-*•]\s+(.+)$/);

    if (bulletMatch) {
      flushParagraph();

      blocks.push({
        type: "bullet",
        text: cleanMarkdown(
          bulletMatch[1],
        ),
      });

      continue;
    }

    /* Numbered list */
    const numberedMatch =
      line.match(/^\d+[.)]\s+(.+)$/);

    if (numberedMatch) {
      flushParagraph();

      blocks.push({
        type: "bullet",
        text: cleanMarkdown(
          numberedMatch[1],
        ),
      });

      continue;
    }

    /*
     * Explicit decision:
     *
     * DECISION: HOLD
     * DECISION **HOLD / NEUTRAL**
     */
    const decisionMatch = line.match(
      /^(?:\*\*)?DECISION(?:\*\*)?\s*:?\s*(?:\*\*)?(.+?)(?:\*\*)?$/i,
    );

    if (decisionMatch) {
      flushParagraph();

      const candidate = cleanMarkdown(
        decisionMatch[1],
      ).trim();

      if (candidate) {
        decision = candidate;
      }

      continue;
    }

    /*
     * Standalone investment decision:
     *
     * **HOLD / NEUTRAL**
     */
    const standaloneDecision =
      line.match(
        /^\*\*(BUY|SELL|HOLD|NEUTRAL|HOLD\s*\/\s*NEUTRAL|BUY\s*\/\s*STRONG BUY|SELL\s*\/\s*STRONG SELL)\*\*$/i,
      );

    if (standaloneDecision) {
      flushParagraph();

      decision = cleanMarkdown(
        standaloneDecision[1],
      );

      continue;
    }

    paragraphBuffer.push(line);
  }

  flushParagraph();

  return {
    decision,
    blocks,
  };
}

/* -------------------------------------------------------------------------- */
/* Inline markdown rendering                                                  */
/* -------------------------------------------------------------------------- */

function renderInlineText(
  text: string,
) {
  const parts = text.split(
    /(\*\*.*?\*\*|\*.*?\*)/g,
  );

  return parts.map((part, index) => {
    if (!part) {
      return null;
    }

    if (
      part.startsWith("**") &&
      part.endsWith("**")
    ) {
      return (
        <strong
          key={index}
          className="font-semibold text-text-primary"
        >
          {part.slice(2, -2)}
        </strong>
      );
    }

    if (
      part.startsWith("*") &&
      part.endsWith("*")
    ) {
      return (
        <em key={index}>
          {part.slice(1, -1)}
        </em>
      );
    }

    return (
      <span key={index}>
        {part}
      </span>
    );
  });
}

/* -------------------------------------------------------------------------- */
/* Decision styling                                                           */
/* -------------------------------------------------------------------------- */

function getDecisionClasses(
  decision: string,
): string {
  const normalized =
    decision.toLowerCase();

  if (
    normalized.includes("strong buy") ||
    normalized === "buy"
  ) {
    return cn(
      "border-success/30",
      "bg-success/10",
      "text-success",
    );
  }

  if (
    normalized.includes("strong sell") ||
    normalized === "sell"
  ) {
    return cn(
      "border-warning/30",
      "bg-warning/10",
      "text-warning",
    );
  }

  return cn(
    "border-border",
    "bg-bg-surface",
    "text-text-primary",
  );
}

/* -------------------------------------------------------------------------- */
/* Structured insight renderer                                                */
/* -------------------------------------------------------------------------- */

function StructuredInsight({
  description,
}: {
  description: string;
}) {
  const parsed =
    parseInsightDescription(
      description,
    );

  if (
    parsed.blocks.length === 0 &&
    !parsed.decision
  ) {
    return null;
  }

  return (
    <div className="mt-6">
      {/* Investment Decision */}
      {parsed.decision && (
        <section className="mb-8">
          <div className="flex items-center gap-2 mb-3">
            <Target
              className="w-4 h-4 text-accent"
              aria-hidden="true"
            />

            <span className="text-[10px] uppercase tracking-[0.16em] font-mono text-text-muted">
              Investment Decision
            </span>
          </div>

          <div
            className={cn(
              "inline-flex items-center",
              "rounded-lg border",
              "px-4 py-2.5",
              "text-sm font-semibold",
              "tracking-wide",
              getDecisionClasses(
                parsed.decision,
              ),
            )}
          >
            {parsed.decision}
          </div>
        </section>
      )}

      {/* Analysis content */}
      <div>
        {parsed.blocks.map(
          (block, index) => {
            /* Separator */
            if (
              block.type ===
              "separator"
            ) {
              return (
                <div
                  key={`separator-${index}`}
                  className="my-8 h-px bg-border"
                />
              );
            }

            /* Heading */
            if (
              block.type ===
              "heading"
            ) {
              const heading =
                block.text.toLowerCase();

              const isMajorHeading =
                block.level <= 3 ||
                [
                  "thesis",
                  "investment thesis",
                  "key risks",
                  "risks",
                  "catalysts",
                  "growth catalysts",
                  "valuation",
                  "financial analysis",
                  "financial performance",
                  "conclusion",
                  "recommendation",
                  "assessment",
                ].some(
                  (value) =>
                    heading.includes(
                      value,
                    ),
                );

              return (
                <div
                  key={`heading-${index}`}
                  className={cn(
                    "pt-7 pb-3",
                    index === 0 &&
                      "pt-0",
                  )}
                >
                  <h4
                    className={cn(
                      isMajorHeading
                        ? [
                            "text-base",
                            "font-semibold",
                            "text-text-primary",
                          ]
                        : [
                            "text-sm",
                            "font-medium",
                            "text-text-primary",
                          ],
                    )}
                  >
                    {renderInlineText(
                      block.text,
                    )}
                  </h4>
                </div>
              );
            }

            /* Bullet */
            if (
              block.type ===
              "bullet"
            ) {
              return (
                <div
                  key={`bullet-${index}`}
                  className="flex items-start gap-3 py-1.5"
                >
                  <span
                    className="
                      mt-2.5
                      h-1.5
                      w-1.5
                      shrink-0
                      rounded-full
                      bg-text-muted
                    "
                  />

                  <p className="text-sm text-text-secondary leading-7">
                    {renderInlineText(
                      block.text,
                    )}
                  </p>
                </div>
              );
            }

            /* Paragraph */
            return (
              <p
                key={`paragraph-${index}`}
                className="
                  max-w-3xl
                  text-sm
                  text-text-secondary
                  leading-7
                  mb-5
                "
              >
                {renderInlineText(
                  block.text,
                )}
              </p>
            );
          },
        )}
      </div>
    </div>
  );
}

/* -------------------------------------------------------------------------- */
/* Insight panel                                                              */
/* -------------------------------------------------------------------------- */

export function InsightPanel({
  insights,
}: InsightPanelProps) {
  /*
   * ---------------------------------------------------------
   * Normalize backend data
   * ---------------------------------------------------------
   *
   * This is the critical runtime fix.
   *
   * The backend may return:
   *
   *   undefined
   *   null
   *   []
   *   [...]
   *
   * We only render actual backend insights.
   */
  const safeInsights: ResearchInsight[] =
    Array.isArray(insights)
      ? insights
      : [];

  /*
   * ---------------------------------------------------------
   * Empty state
   * ---------------------------------------------------------
   */
  if (safeInsights.length === 0) {
    return (
      <EmptyState
        icon={
          <Lightbulb className="w-5 h-5" />
        }
        title="No insights generated yet"
        description="AI-generated findings will appear here as the research progresses through analysis stages."
      />
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-6 lg:px-8 py-8 animate-fade-in">
      {/* Page header */}
      <header className="mb-8">
        <div className="flex items-center gap-2 mb-2">
          <BarChart3
            className="w-4 h-4 text-accent"
            aria-hidden="true"
          />

          <span
            className="
              text-[10px]
              uppercase
              tracking-[0.16em]
              font-mono
              text-text-muted
            "
          >
            Research Intelligence
          </span>
        </div>

        <h2
          className="
            text-lg
            font-semibold
            text-text-primary
          "
        >
          Insights & Analysis
        </h2>

        <p
          className="
            mt-2
            max-w-2xl
            text-sm
            text-text-muted
            leading-6
          "
        >
          AI-generated findings, investment
          signals, risks, and catalysts derived
          from the research workflow.
        </p>
      </header>

      {/* Insight cards */}
      <div className="space-y-6">
        {safeInsights.map(
          (insight, index) => {
            /*
             * Defensive normalization of an individual
             * backend insight.
             */
            const rawType =
              safeText(
                insight?.type,
                "insight",
              ).toLowerCase();

            const insightType: InsightType =
              rawType === "risk" ||
              rawType === "catalyst" ||
              rawType === "insight"
                ? rawType
                : "insight";

            const config =
              typeConfig[insightType];

            const Icon = config.icon;

            const title =
              safeText(
                insight?.title,
                "Research Insight",
              );

            const description =
              safeText(
                insight?.description,
                "",
              );

            /*
             * Never access description.length
             * directly on potentially malformed data.
             */
            const isLongInsight =
              insightType === "insight" &&
              description.length > 600;

            /*
             * Backend IDs are preferred.
             *
             * The index is only a rendering fallback
             * and is not exposed as a research ID.
             */
            const key =
              safeText(
                insight?.id,
                "",
              ) ||
              `insight-${index}`;

            return (
              <article
                key={key}
                className={cn(
                  "bg-bg-surface",
                  "border border-border",
                  "rounded-xl",
                  "transition-all duration-200",
                  "hover:border-border-hover",
                  isLongInsight
                    ? "p-7 lg:p-8"
                    : "p-5",
                )}
              >
                {/* Card header */}
                <div
                  className="
                    flex
                    items-start
                    gap-4
                  "
                >
                  <div
                    className={cn(
                      "w-10 h-10",
                      "rounded-xl",
                      "border",
                      "flex items-center",
                      "justify-center",
                      "shrink-0",
                      config.bg,
                    )}
                  >
                    <Icon
                      className={cn(
                        "w-[18px] h-[18px]",
                        config.color,
                      )}
                      aria-hidden="true"
                    />
                  </div>

                  <div
                    className="
                      flex-1
                      min-w-0
                    "
                  >
                    <span
                      className={cn(
                        "text-[10px]",
                        "uppercase",
                        "tracking-[0.16em]",
                        "font-mono",
                        config.color,
                      )}
                    >
                      {config.label}
                    </span>

                    <h3
                      className="
                        mt-1.5
                        text-base
                        font-semibold
                        text-text-primary
                      "
                    >
                      {title}
                    </h3>
                  </div>
                </div>

                {/* Card content */}
                <div
                  className="
                    mt-1
                    ml-0
                    sm:ml-14
                  "
                >
                  {description ? (
                    <StructuredInsight
                      description={
                        description
                      }
                    />
                  ) : (
                    <p className="mt-4 text-sm text-text-muted">
                      No detailed description
                      is available yet.
                    </p>
                  )}
                </div>
              </article>
            );
          },
        )}
      </div>
    </div>
  );
}