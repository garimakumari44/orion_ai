/* -------------------------------------------------------------------------- */
/* Saved Artifacts                                                            */
/* -------------------------------------------------------------------------- */

/**

* Where a saved artifact is stored/displayed.
  */
  export type SaveDestination =
  | "library"
  | "research"
  | "reports";

/* -------------------------------------------------------------------------- */
/* Saved Artifact                                                             */
/* -------------------------------------------------------------------------- */

/**

* Canonical frontend representation of a saved artifact.
*
* The backend currently uses integer research IDs in PostgreSQL, while the
* frontend/API layer also supports UUID/string research identifiers.
*
* Therefore both snake_case API fields and the normalized camelCase research
* identifier are supported at the type boundary.
  */
  export interface SavedArtifact {
  id: string;

/**

* Backend/API research identifier.
*
* Supports:
* * PostgreSQL integer IDs
* * UUID/string IDs
    */
    research_id: string | number;

/**

* Normalized frontend research identifier.
*
* API mappers may expose this field for UI components that use camelCase.
  */
  researchId?: string | number | null;

destination: SaveDestination;

title: string;

description?: string | null;

created_at: string;

updated_at?: string | null;
}

/* -------------------------------------------------------------------------- */
/* Create / Save Request                                                      */
/* -------------------------------------------------------------------------- */

/**

* Payload sent to the backend when saving an artifact.
  */
  export interface SaveArtifactRequest {
  /**

  * Research identifier.
* * The API client accepts both numeric and string/UUID identifiers.
    */
    research_id: string | number;

destination: SaveDestination;

title: string;

description?: string | null;
}

/* -------------------------------------------------------------------------- */
/* API Response                                                               */
/* -------------------------------------------------------------------------- */

/**

* Response returned by POST /api/saved-artifacts.
*
* The backend may currently return either:
*
* 1. A wrapped response:
*
* {
* ```
   "success": true,
  ```
* ```
   "artifact": { ... }
  ```
* }
*
* 2. The SavedArtifact directly:
*
* {
* ```
   "id": "...",
  ```
* ```
   "research_id": 73,
  ```
* ```
   ...
  ```
* }
*
* The API layer normalizes either form before exposing the result to the
* application.
  */
  export interface SaveArtifactResponse {
  success?: boolean;

artifact?: SavedArtifact;

/**

* Direct SavedArtifact response fields.
  */
  id?: string;

research_id?: string | number;

destination?: SaveDestination;

title?: string;

description?: string | null;

created_at?: string;

updated_at?: string | null;
}
