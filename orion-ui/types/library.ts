
import type { SavedArtifact } from "./savedArtifact";

/* -------------------------------------------------------------------------- */
/* Library Item                                                               */
/* -------------------------------------------------------------------------- */

/**
 * Canonical frontend representation of a library item.
 *
 * The API layer normalizes backend snake_case fields into camelCase fields
 * before returning LibraryItem objects to the UI.
 */
export interface LibraryItem extends SavedArtifact {
  destination: "library";

  /* ------------------------------------------------------------------------ */
  /* Normalized identifiers                                                  */
  /* ------------------------------------------------------------------------ */

  researchId?: string | number | null;

  companyId?: string | number | null;

  /* ------------------------------------------------------------------------ */
  /* Normalized timestamps                                                   */
  /* ------------------------------------------------------------------------ */

  createdAt?: string | null;

  updatedAt?: string | null;

  /* ------------------------------------------------------------------------ */
  /* Company information                                                     */
  /* ------------------------------------------------------------------------ */

  companyName?: string | null;

  ticker?: string | null;

  sector?: string | null;

  exchange?: string | null;

  /* ------------------------------------------------------------------------ */
  /* Investment information                                                  */
  /* ------------------------------------------------------------------------ */

  recommendation?: string | null;

  currentPrice?: number | null;

  fairValue?: number | null;

  confidence?: number | null;

  logoColor?: string | null;
}

/* -------------------------------------------------------------------------- */
/* Library List Response                                                      */
/* -------------------------------------------------------------------------- */

export interface LibraryListResponse {
  items: LibraryItem[];

  total: number;
}

