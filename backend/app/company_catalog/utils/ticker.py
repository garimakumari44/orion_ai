from __future__ import annotations

import re


class TickerUtils:
    """
    Utility functions for working with stock ticker symbols.
    """

    TICKER_PATTERN = re.compile(r"^[A-Z0-9.\-]{1,10}$")

    @classmethod
    def normalize(cls, ticker: str | None) -> str:
        """
        Normalize ticker symbols.
        """

        if not ticker:
            return ""

        ticker = ticker.strip().upper()
        ticker = ticker.replace(" ", "")

        return ticker

    @classmethod
    def validate(cls, ticker: str | None) -> bool:
        """
        Validate ticker format.
        """

        ticker = cls.normalize(ticker)

        if not ticker:
            return False

        return bool(cls.TICKER_PATTERN.fullmatch(ticker))

    @classmethod
    def equals(cls, first: str, second: str) -> bool:
        """
        Compare two ticker symbols.
        """

        return cls.normalize(first) == cls.normalize(second)

    @classmethod
    def parse(cls, value: str) -> tuple[str | None, str]:
        """
        Parse exchange:ticker strings.

        Example:
            NASDAQ:AAPL
            NYSE:IBM
        """

        value = value.strip()

        if ":" not in value:
            return None, cls.normalize(value)

        exchange, ticker = value.split(":", 1)

        return exchange.upper(), cls.normalize(ticker)

    @classmethod
    def build_cache_key(cls, ticker: str) -> str:
        """
        Cache key for ticker.
        """

        return f"ticker:{cls.normalize(ticker)}"