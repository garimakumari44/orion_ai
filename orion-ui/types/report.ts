import type { SavedArtifact } from "./savedArtifact";

export interface SavedReport extends SavedArtifact {
  destination: "reports";

  companyName?: string | null;

  ticker?: string | null;

  reportType?: string | null;

  recommendation?: string | null;

  confidence?: number | null;

  date?: string | null;

  downloadUrl?: string | null;
}

export interface ReportsListResponse {
  items: SavedReport[];

  total: number;
}