"""
app/api/router.py

Central API router composition.

This module is responsible for:

- Importing feature routers.
- Registering feature routers on the central API router.
- Providing recursive route inspection compatible with FastAPI 0.139.x.

IMPORTANT
---------

FastAPI 0.139.x represents routers included with
APIRouter.include_router() internally as `_IncludedRouter`
objects.

Therefore:

    api_router.routes

does NOT necessarily contain APIRoute objects directly.

The helper functions below recursively inspect those wrappers.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from app.api.routes.auth import router as auth_router
from app.api.research.companies.search import router as company_router
from app.api.research.research.start import router as research_router
from app.api.routes.saved_artifacts import router as saved_artifacts_router
from app.api.routes.library import router as library_router
from app.api.routes.reports import router as reports_router


# ============================================================
# CENTRAL API ROUTER
# ============================================================

api_router = APIRouter()


# ============================================================
# REGISTER FEATURE ROUTERS
# ============================================================

api_router.include_router(auth_router)

api_router.include_router(company_router)

api_router.include_router(research_router)

api_router.include_router(saved_artifacts_router)

api_router.include_router(library_router)

api_router.include_router(reports_router)


# ============================================================
# ROUTE INSPECTION
# ============================================================

def _collect_routes(routes: list[Any]) -> list[dict[str, Any]]:
    """
    Recursively collect actual FastAPI path-operation routes.

    FastAPI 0.139.x may store included routers as `_IncludedRouter`
    wrappers.

    Those wrappers contain the original router in:

        route.original_router

    This function recursively unwraps those routers and returns
    the actual registered API operations.
    """

    collected: list[dict[str, Any]] = []

    for route in routes:
        # ----------------------------------------------------
        # Direct APIRoute / route-like object
        # ----------------------------------------------------

        path = getattr(route, "path", None)
        methods = getattr(route, "methods", None)

        if path and methods:
            collected.append(
                {
                    "path": str(path),
                    "methods": sorted(
                        str(method)
                        for method in methods
                    ),
                    "name": getattr(
                        route,
                        "name",
                        None,
                    ),
                }
            )

            continue

        # ----------------------------------------------------
        # FastAPI 0.139.x _IncludedRouter
        # ----------------------------------------------------

        original_router = getattr(
            route,
            "original_router",
            None,
        )

        if original_router is not None:
            nested_routes = getattr(
                original_router,
                "routes",
                [],
            )

            collected.extend(
                _collect_routes(
                    nested_routes
                )
            )

            continue

        # ----------------------------------------------------
        # Generic nested route container
        # ----------------------------------------------------

        nested_routes = getattr(
            route,
            "routes",
            None,
        )

        if nested_routes:
            collected.extend(
                _collect_routes(
                    nested_routes
                )
            )

    return collected


def get_registered_routes() -> list[dict[str, Any]]:
    """
    Return all actual path-operation routes registered
    on the central API router.

    This function recursively unwraps FastAPI's internal
    `_IncludedRouter` objects.
    """

    return _collect_routes(
        getattr(
            api_router,
            "routes",
            [],
        )
    )


# ============================================================
# ROUTER VALIDATION
# ============================================================

def validate_api_router() -> None:
    """
    Validate the central API router.

    Critical route:

        POST /saved-artifacts

    Expected route groups:

        /saved-artifacts
        /library
        /reports
    """

    routes = get_registered_routes()

    print()
    print("==============================================")
    print("API ROUTER REGISTRATION")
    print("==============================================")

    print(
        f"Total routes registered: {len(routes)}"
    )

    # --------------------------------------------------------
    # Saved artifacts
    # --------------------------------------------------------

    saved_artifact_routes = [
        route
        for route in routes
        if (
            "/saved-artifacts"
            in route["path"].lower()
            or "/saved_artifacts"
            in route["path"].lower()
        )
    ]

    if saved_artifact_routes:
        print()
        print(
            "   [OK] Saved-artifact routes:"
        )

        for route in saved_artifact_routes:
            print(
                "       "
                f"{route['methods']} "
                f"{route['path']}"
            )

    else:
        print()
        print(
            "   [ERROR] No saved-artifact routes registered."
        )

    # --------------------------------------------------------
    # Library
    # --------------------------------------------------------

    library_routes = [
        route
        for route in routes
        if "/library" in route["path"].lower()
    ]

    if library_routes:
        print()
        print(
            "   [OK] Library routes:"
        )

        for route in library_routes:
            print(
                "       "
                f"{route['methods']} "
                f"{route['path']}"
            )

    else:
        print()
        print(
            "   [WARNING] No library routes registered."
        )

    # --------------------------------------------------------
    # Reports
    # --------------------------------------------------------

    report_routes = [
        route
        for route in routes
        if "/reports" in route["path"].lower()
    ]

    if report_routes:
        print()
        print(
            "   [OK] Reports routes:"
        )

        for route in report_routes:
            print(
                "       "
                f"{route['methods']} "
                f"{route['path']}"
            )

    else:
        print()
        print(
            "   [WARNING] No reports routes registered."
        )

    print(
        "=============================================="
    )

    # --------------------------------------------------------
    # Critical POST route
    # --------------------------------------------------------

    has_saved_artifact_post = any(
        route["path"] == "/saved-artifacts"
        and "POST" in route["methods"]
        for route in routes
    )

    if not has_saved_artifact_post:
        raise RuntimeError(
            "Saved-artifact routes are not registered "
            "on api_router. "
            "Expected POST /saved-artifacts."
        )