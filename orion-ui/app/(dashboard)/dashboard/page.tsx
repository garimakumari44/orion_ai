"use client";

import {
useCallback,
useEffect,
useState,
} from "react";

import { Sidebar } from "../components/Sidebar";
import { Header } from "../components/Header";
import { SearchModal } from "../components/SearchModal";

import { HomePage } from "../components/pages/Home";
import { ResearchPage } from "../components/pages/Research";
import { LibraryPage } from "../components/pages/Library";
import { ReportsPage } from "../components/pages/Reports";
import { SettingsPage } from "../components/pages/Settings";
import { WorkspacePage } from "../components/pages/Workspace";

import { ResearchWizard } from "../components/research/ResearchWizard";
import { NewResearchResult } from "../components/research/NewResearchResult";

/* -------------------------------------------------------------------------- */
/* Page types                                                                 */
/* -------------------------------------------------------------------------- */

export type Page =
| "home"
| "workspace"
| "new-research"
| "new-research-result"
| "research"
| "library"
| "reports"
| "settings";

/* -------------------------------------------------------------------------- */
/* App                                                                        */
/* -------------------------------------------------------------------------- */

export default function App() {
/* ------------------------------------------------------------------------ */
/* Current page                                                             */
/* ------------------------------------------------------------------------ */

const [page, setPage] =
useState<Page>("home");

/* ------------------------------------------------------------------------ */
/* Selected research                                                        */
/* ------------------------------------------------------------------------ */

/**

* This state stores ONLY the backend research ID.
*
* It must never contain:
*
* * company ID
* * company ticker
* * company name
    */

const [
selectedResearchId,
setSelectedResearchId,
] = useState<string | null>(null);

/* ------------------------------------------------------------------------ */
/* Search                                                                   */
/* ------------------------------------------------------------------------ */

const [
searchOpen,
setSearchOpen,
] = useState(false);

/* ======================================================================== */
/* Existing research selection                                             */
/* ======================================================================== */

/**

* Opens an existing research workspace.
*
* This function is the canonical navigation
* function for an existing research.
*
* Used by:
*
* * Library
* * Reports
* * Research lists
* * Search results when they return a research ID
    */

const handleSelectResearch =
useCallback(
(
researchId:
| string
| number,
) => {
const id =
String(
researchId ?? "",
).trim();


    if (
      !id ||
      id === "undefined" ||
      id === "null"
    ) {
      console.error(
        "[Research] Cannot select research: invalid research ID",
        researchId,
      );

      return;
    }

    console.log(
      "[Research] Opening existing research:",
      id,
    );

    setSelectedResearchId(
      id,
    );

    setPage(
      "research",
    );
  },
  [],
);


/* ======================================================================== */
/* Saved research selection                                                 */
/* ======================================================================== */

/**

* Library and Reports contain SAVED RESEARCH.
*
* Their IDs are research IDs, not company IDs.
*
* This is deliberately separate from
* handleSelectCompany().
  */

const handleSelectSavedResearch =
useCallback(
(
researchId:
| string
| number,
) => {
const id =
String(
researchId ?? "",
).trim();


    if (
      !id ||
      id === "undefined" ||
      id === "null"
    ) {
      console.error(
        "[Saved Research] Cannot open research: invalid research ID",
        researchId,
      );

      return;
    }

    console.log(
      "[Saved Research] Opening research workspace:",
      id,
    );

    handleSelectResearch(id);
  },
  [
    handleSelectResearch,
  ],
);


/* ======================================================================== */
/* New research created                                                     */
/* ======================================================================== */

/**

* Called ONLY after ResearchWizard successfully
* creates a research and receives the real
* backend research ID.
*
* Flow:
*
* ResearchWizard
* ```
   ↓
  ```
* onCreated(id)
* ```
   ↓
  ```
* selectedResearchId
* ```
   ↓
  ```
* new-research-result
  */

const handleResearchCreated =
useCallback(
(
researchId:
| string
| number,
) => {
const id =
String(
researchId ?? "",
).trim();


    if (
      !id ||
      id === "undefined" ||
      id === "null"
    ) {
      console.error(
        "[Research] Cannot open newly created research: invalid research ID",
        researchId,
      );

      return;
    }

    console.log(
      "[Research] New research created:",
      id,
    );

    setSelectedResearchId(
      id,
    );

    setPage(
      "new-research-result",
    );
  },
  [],
);


/* ======================================================================== */
/* Company selection                                                        */
/* ======================================================================== */

/**

* Existing components use onSelectCompany
* for actual company selection.
*
* IMPORTANT:
*
* A company ID is NOT a research ID.
*
* Therefore this function intentionally
* does NOT open the research workspace.
  */

const handleSelectCompany =
useCallback(
(
companyId:
| string
| number,
) => {
const id =
String(
companyId ?? "",
).trim();


    if (
      !id ||
      id === "undefined" ||
      id === "null"
    ) {
      console.error(
        "[Company] Cannot select company: invalid company ID",
        companyId,
      );

      return;
    }

    console.log(
      "[Company] Selected company:",
      id,
    );

    /*
     * DO NOT DO:
     *
     * setSelectedResearchId(id);
     *
     * A company ID is not a research ID.
     *
     * Company selection can later be used for:
     *
     * - company overview
     * - creating research
     * - company research history
     */
  },
  [],
);


/* ======================================================================== */
/* Navigation                                                               */
/* ======================================================================== */

const handleNavigate =
useCallback(
(
nextPage: string,
) => {
const validPages: Page[] = [
"home",
"workspace",
"new-research",
"new-research-result",
"research",
"library",
"reports",
"settings",
];


    if (
      !validPages.includes(
        nextPage as Page,
      )
    ) {
      console.warn(
        `[Navigation] Ignoring invalid page: ${nextPage}`,
      );

      return;
    }

    setPage(
      nextPage as Page,
    );
  },
  [],
);


/* ======================================================================== */
/* Open research                                                            */
/* ======================================================================== */

/**

* Used by NewResearchResult.
*
* Once the result page has been displayed,
* this opens the normal existing research page.
  */

const handleOpenResearch =
useCallback(
() => {
if (
!selectedResearchId
) {
console.error(
"[Research] Cannot open research: no research ID selected",
);


      return;
    }

    console.log(
      "[Research] Opening research workspace:",
      selectedResearchId,
    );

    setPage(
      "research",
    );
  },
  [
    selectedResearchId,
  ],
);


/* ======================================================================== */
/* Global search shortcut                                                   */
/* ======================================================================== */

useEffect(() => {
const handler =
(
event: KeyboardEvent,
) => {
if (
(
event.ctrlKey ||
event.metaKey
) &&
event.key.toLowerCase() ===
"k"
) {
event.preventDefault();


      setSearchOpen(
        true,
      );
    }
  };

window.addEventListener(
  "keydown",
  handler,
);

return () => {
  window.removeEventListener(
    "keydown",
    handler,
  );
};


}, []);

/* ======================================================================== */
/* Render                                                                   */
/* ======================================================================== */

return ( <div className="flex h-full w-full flex-col overflow-hidden bg-black text-text-primary"> <div className="flex flex-1 overflow-hidden">


    {/* ================================================================== */}
    {/* Sidebar                                                            */}
    {/* ================================================================== */}

    <Sidebar
      currentPage={
        page
      }
      onNavigate={
        handleNavigate
      }
      onSelectCompany={
        handleSelectCompany
      }
      recentCompanies={
        []
      }
    />

    {/* ================================================================== */}
    {/* Main                                                               */}
    {/* ================================================================== */}

    <div className="flex flex-1 flex-col overflow-hidden">

      <Header
        onOpenSearch={() =>
          setSearchOpen(
            true,
          )
        }
      />

      <main className="flex-1 overflow-hidden">

        {/* ================================================================ */}
        {/* HOME                                                             */}
        {/* ================================================================ */}

        {page === "home" && (
          <HomePage
            onSelectCompany={
              handleSelectCompany
            }
            onNavigate={
              handleNavigate
            }
            onOpenSearch={() =>
              setSearchOpen(
                true,
              )
            }
          />
        )}

        {/* ================================================================ */}
        {/* WORKSPACE                                                        */}
        {/* ================================================================ */}

        {page === "workspace" && (
          <WorkspacePage
            researchId={
              selectedResearchId
            }
          />
        )}

        {/* ================================================================ */}
        {/* NEW RESEARCH                                                     */}
        {/* ================================================================ */}

        {page === "new-research" && (
          <ResearchWizard
            onExit={() =>
              handleNavigate(
                "home",
              )
            }
            onCreated={
              handleResearchCreated
            }
          />
        )}

        {/* ================================================================ */}
        {/* NEW RESEARCH RESULT                                               */}
        {/* ================================================================ */}

        {page === "new-research-result" && (
          <>
            {selectedResearchId ? (
              <NewResearchResult
                researchId={
                  selectedResearchId
                }
                onOpenResearch={
                  handleOpenResearch
                }
                onBack={() =>
                  handleNavigate(
                    "home",
                  )
                }
              />
            ) : (
              <div className="flex h-full min-h-[500px] items-center justify-center px-6">
                <div className="w-full max-w-md rounded-lg border border-border bg-bg-surface p-6">

                  <div className="text-sm font-medium text-text-primary">
                    Research ID missing
                  </div>

                  <p className="mt-2 text-xs leading-5 text-text-muted">
                    The research was created,
                    but no valid research ID
                    was returned to the dashboard.
                  </p>

                  <button
                    type="button"
                    onClick={() =>
                      handleNavigate(
                        "new-research",
                      )
                    }
                    className="mt-5 rounded-md border border-border bg-bg-elevated px-3 py-2 text-xs font-medium text-text-primary transition-colors hover:bg-bg-hover"
                  >
                    Start new research
                  </button>

                </div>
              </div>
            )}
          </>
        )}

        {/* ================================================================ */}
        {/* EXISTING RESEARCH                                                */}
        {/* ================================================================ */}

        {page === "research" && (
          <>
            {selectedResearchId ? (
              <ResearchPage
                researchId={
                  selectedResearchId
                }
              />
            ) : (
              <div className="flex h-full min-h-[500px] items-center justify-center px-6">
                <div className="w-full max-w-md rounded-lg border border-border bg-bg-surface p-6">

                  <div className="text-sm font-medium text-text-primary">
                    No research selected
                  </div>

                  <p className="mt-2 text-xs leading-5 text-text-muted">
                    Select an existing research
                    to open it, or create a new
                    research.
                  </p>

                  <div className="mt-5 flex gap-2">

                    <button
                      type="button"
                      onClick={() =>
                        handleNavigate(
                          "new-research",
                        )
                      }
                      className="rounded-md border border-border bg-bg-elevated px-3 py-2 text-xs font-medium text-text-primary transition-colors hover:bg-bg-hover"
                    >
                      New research
                    </button>

                    <button
                      type="button"
                      onClick={() =>
                        handleNavigate(
                          "home",
                        )
                      }
                      className="rounded-md border border-border px-3 py-2 text-xs font-medium text-text-muted transition-colors hover:bg-bg-hover hover:text-text-primary"
                    >
                      Back home
                    </button>

                  </div>

                </div>
              </div>
            )}
          </>
        )}

        {/* ================================================================ */}
        {/* LIBRARY                                                          */}
        {/* ================================================================ */}

        {page === "library" && (
          <LibraryPage
            /*
             * IMPORTANT:
             *
             * Library contains saved research,
             * therefore it receives the research
             * navigation handler — NOT the
             * company-selection handler.
             */
            onSelectCompany={
              handleSelectSavedResearch
            }
          />
        )}

        {/* ================================================================ */}
        {/* REPORTS                                                          */}
        {/* ================================================================ */}

        {page === "reports" && (
          <ReportsPage
            /*
             * IMPORTANT:
             *
             * Reports contain saved research.
             * The callback receives researchId.
             */
            onSelectCompany={
              handleSelectSavedResearch
            }
          />
        )}

        {/* ================================================================ */}
        {/* SETTINGS                                                         */}
        {/* ================================================================ */}

        {page === "settings" && (
          <SettingsPage />
        )}

      </main>
    </div>
  </div>

  {/* ==================================================================== */}
  {/* SEARCH                                                               */}
  {/* ==================================================================== */}

  <SearchModal
    open={
      searchOpen
    }
    onClose={() =>
      setSearchOpen(
        false,
      )
    }
    onSelectCompany={
      handleSelectCompany
    }
    onNavigate={
      handleNavigate
    }
  />

</div>


);
}
