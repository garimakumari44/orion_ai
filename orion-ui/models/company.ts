
// frontend/models/company.ts

export type Recommendation =
  | "STRONG BUY"
  | "BUY"
  | "HOLD"
  | "REDUCE"
  | "SELL";

/**
 * Normalize an arbitrary backend recommendation into the canonical
 * frontend Recommendation union.
 *
 * Backend responses are allowed to contain arbitrary strings, while
 * UI components consume the strict Recommendation type.
 */
export function normalizeRecommendation(
  value: string | null | undefined,
): Recommendation {
  switch (value?.trim().toUpperCase()) {
    case "STRONG BUY":
      return "STRONG BUY";

    case "BUY":
      return "BUY";

    case "HOLD":
      return "HOLD";

    case "REDUCE":
      return "REDUCE";

    case "SELL":
      return "SELL";

    default:
      return "HOLD";
  }
}

export interface CompanyData {
  id: string;
  name: string;
  ticker: string;
  exchange: string;
  logoColor: string;
  sector: string;
  industry: string;
  marketCap: string;
  currentPrice: number;
  fairValue: number;
  upside: number;
  recommendation: Recommendation;
  confidence: number;
}

