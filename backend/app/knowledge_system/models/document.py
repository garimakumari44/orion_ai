"""
Core document model.

A Document represents a single piece of knowledge entering the
knowledge system before processing.

Examples:
- PDF
- Markdown file
- GitHub repository
- Web page
- Confluence page
- Notion document
- Slack conversation
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import Field

from .base import BaseKnowledgeModel
from .enums import DocumentStatus, DocumentType


class Document(BaseKnowledgeModel):
    """
    Top-level document object.

    This model contains only document-level information.
    Chunks, embeddings, entities, etc. are stored separately.
    """

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    title: str = Field(
        ...,
        description="Human-readable document title.",
    )

    source: str = Field(
        ...,
        description="Original source identifier or URL.",
    )

    type: DocumentType = Field(
        ...,
        description="Type of document.",
    )

    status: DocumentStatus = Field(
        default=DocumentStatus.PENDING,
        description="Processing status.",
    )

    # ------------------------------------------------------------------
    # Content
    # ------------------------------------------------------------------

    content: str = Field(
        ...,
        description="Raw extracted document text.",
    )

    summary: str | None = Field(
        default=None,
        description="Optional generated summary.",
    )

    language: str | None = Field(
        default=None,
        description="Detected language.",
    )

    mime_type: str | None = Field(
        default=None,
        description="Original MIME type.",
    )

    encoding: str | None = Field(
        default="utf-8",
        description="Text encoding.",
    )

    # ------------------------------------------------------------------
    # Source Information
    # ------------------------------------------------------------------

    author: str | None = None

    created_at_source: datetime | None = None

    updated_at_source: datetime | None = None

    version: str | None = None

    # ------------------------------------------------------------------
    # Processing
    # ------------------------------------------------------------------

    checksum: str | None = Field(
        default=None,
        description="SHA256 hash of original content.",
    )

    content_length: int = Field(
        default=0,
        description="Character count.",
    )

    token_count: int | None = Field(
        default=None,
        description="Estimated token count.",
    )

    chunk_count: int = Field(
        default=0,
        description="Number of generated chunks.",
    )

    # ------------------------------------------------------------------
    # Tags
    # ------------------------------------------------------------------

    tags: list[str] = Field(default_factory=list)

    labels: list[str] = Field(default_factory=list)

    # ------------------------------------------------------------------
    # Extra connector-specific information
    # ------------------------------------------------------------------

    extra: dict[str, Any] = Field(
        default_factory=dict,
        description="Connector-specific metadata.",
    )

    # ------------------------------------------------------------------
    # Utility Properties
    # ------------------------------------------------------------------

    @property
    def is_processed(self) -> bool:
        return self.status == DocumentStatus.COMPLETED

    @property
    def has_summary(self) -> bool:
        return self.summary is not None

    @property
    def has_chunks(self) -> bool:
        return self.chunk_count > 0

    @property
    def is_empty(self) -> bool:
        return not self.content.strip()

    @property
    def size_kb(self) -> float:
        return round(self.content_length / 1024, 2)

    # ------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------

    def update_content(self, content: str) -> None:
        """
        Replace document content and update size.
        """
        self.content = content
        self.content_length = len(content)

    def add_tag(self, tag: str) -> None:
        if tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag: str) -> None:
        if tag in self.tags:
            self.tags.remove(tag)

    def add_label(self, label: str) -> None:
        if label not in self.labels:
            self.labels.append(label)

    def mark_processing(self) -> None:
        self.status = DocumentStatus.PROCESSING

    def mark_completed(self) -> None:
        self.status = DocumentStatus.COMPLETED

    def mark_failed(self) -> None:
        self.status = DocumentStatus.FAILED

    def mark_skipped(self) -> None:
        self.status = DocumentStatus.SKIPPED