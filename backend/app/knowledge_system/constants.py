from enum import Enum


class SourceType(str, Enum):
    FILESYSTEM = "filesystem"
    GITHUB = "github"
    DATABASE = "database"
    API = "api"
    WEB = "web"
    ARXIV = "arxiv"


class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    INDEXED = "indexed"
    FAILED = "failed"


class DocumentType(str, Enum):
    PDF = "pdf"
    MARKDOWN = "markdown"
    TEXT = "text"
    HTML = "html"
    DOCX = "docx"
    CODE = "code"


SUPPORTED_FILE_TYPES = {
    ".pdf",
    ".txt",
    ".md",
    ".docx",
    ".html",
    ".py",
    ".js",
    ".ts",
    ".java",
    ".cpp",
    ".json",
    ".yaml",
    ".yml",
}