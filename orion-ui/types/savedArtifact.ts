export type SaveDestination =
  | "library"
  | "research"
  | "reports";

export interface SavedArtifact {
  id: string;

  /**
   * Research.id is an INTEGER in PostgreSQL.
   */
  research_id: number;

  destination: SaveDestination;

  title: string;

  description?: string | null;

  created_at: string;

  updated_at?: string | null;
}

export interface SaveArtifactRequest {
  /**
   * Research.id is an INTEGER.
   *
   * This must be sent as:
   *
   * {
   *   "research_id": 73
   * }
   */
  research_id: number;

  destination: SaveDestination;

  title: string;

  description?: string | null;
}

export interface SaveArtifactResponse {
  success?: boolean;

  artifact?: SavedArtifact;

  /**
   * The backend currently returns SavedArtifactResponse
   * directly from POST /api/saved-artifacts.
   *
   * Keeping the response flexible allows the frontend to
   * support that current API shape.
   */
  id?: string;
  research_id?: number;
  destination?: SaveDestination;
  title?: string;
  description?: string | null;
  created_at?: string;
  updated_at?: string | null;
}