from __future__ import annotations

from urllib.parse import urlparse


class WebsiteUtils:
    """
    Utility functions for company websites.
    """

    @classmethod
    def normalize(cls, website: str | None) -> str:
        """
        Normalize a website URL.
        """

        if not website:
            return ""

        website = website.strip().lower()

        if not website.startswith(("http://", "https://")):
            website = "https://" + website

        parsed = urlparse(website)

        domain = parsed.netloc.replace("www.", "")

        return f"https://{domain}"

    @classmethod
    def domain(cls, website: str | None) -> str:
        """
        Extract domain.
        """

        if not website:
            return ""

        parsed = urlparse(cls.normalize(website))

        return parsed.netloc

    @classmethod
    def validate(cls, website: str | None) -> bool:
        """
        Basic validation.
        """

        domain = cls.domain(website)

        return "." in domain

    @classmethod
    def equals(cls, first: str, second: str) -> bool:
        """
        Compare two company websites.
        """

        return cls.domain(first) == cls.domain(second)

    @classmethod
    def build_cache_key(cls, website: str) -> str:
        """
        Cache key for website.
        """

        return f"website:{cls.domain(website)}"