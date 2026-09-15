import type { SavedArtifact } from "./savedArtifact";

export interface LibraryItem extends SavedArtifact {
  destination: "library";

  companyName?: string | null;

  ticker?: string | null;

  sector?: string | null;

  recommendation?: string | null;

  currentPrice?: number | null;

  fairValue?: number | null;

  confidence?: number | null;

  logoColor?: string | null;

  exchange?: string | null;
}

export interface LibraryListResponse {
  items: LibraryItem[];

  total: number;
}