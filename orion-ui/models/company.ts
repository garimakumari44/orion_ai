// frontend/models/company.ts

export type Recommendation =
  | "STRONG BUY"
  | "BUY"
  | "HOLD"
  | "REDUCE"
  | "SELL";


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