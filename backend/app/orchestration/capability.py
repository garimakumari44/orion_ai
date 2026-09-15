from __future__ import annotations

from enum import Enum


class Capability(str, Enum):
    """
    Standardized capabilities supported by tools.

    The orchestration layer uses these values instead of
    hardcoding specific tool names.
    """

    # -------------------------
    # Web
    # -------------------------

    WEB_SEARCH = "web_search"
    WEB_BROWSE = "web_browse"

    # -------------------------
    # GitHub
    # -------------------------

    REPOSITORY_READ = "repository_read"
    REPOSITORY_SEARCH = "repository_search"
    CODE_SEARCH = "code_search"

    # -------------------------
    # Company / Startup
    # -------------------------

    COMPANY_LOOKUP = "company_lookup"
    COMPANY_FINANCIALS = "company_financials"

    # -------------------------
    # News
    # -------------------------

    NEWS_SEARCH = "news_search"

    # -------------------------
    # Documentation
    # -------------------------

    DOCUMENT_SEARCH = "document_search"

    # -------------------------
    # Database
    # -------------------------

    VECTOR_SEARCH = "vector_search"

    SQL_QUERY = "sql_query"

    # -------------------------
    # Browser
    # -------------------------

    PAGE_NAVIGATION = "page_navigation"

    PAGE_SCREENSHOT = "page_screenshot"

    PAGE_EXTRACTION = "page_extraction"

    # -------------------------
    # Python
    # -------------------------

    PYTHON_EXECUTION = "python_execution"

    DATA_ANALYSIS = "data_analysis"

    VISUALIZATION = "visualization"

    # -------------------------
    # File
    # -------------------------

    FILE_READ = "file_read"

    FILE_WRITE = "file_write"

    FILE_UPLOAD = "file_upload"

    FILE_DOWNLOAD = "file_download"

    # -------------------------
    # APIs
    # -------------------------

    API_REQUEST = "api_request"

    # -------------------------
    # AI
    # -------------------------

    LLM_REASONING = "llm_reasoning"

    EMBEDDING = "embedding"

    SUMMARIZATION = "summarization"

    TRANSLATION = "translation"