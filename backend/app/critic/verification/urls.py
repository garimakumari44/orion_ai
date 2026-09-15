"""
Broken URL Detection

Checks URLs referenced in generated responses.

Future enhancements:
- Redirect analysis
- Malware detection
- Domain reputation
- SSL validation
"""

from __future__ import annotations

import concurrent.futures
from dataclasses import dataclass
from typing import List, Optional

import requests


@dataclass
class URLResult:
    url: str

    reachable: bool

    status_code: Optional[int] = None

    final_url: Optional[str] = None

    error: Optional[str] = None

    response_time: Optional[float] = None


class URLVerifier:
    """
    Verifies URLs concurrently.
    """

    def __init__(
        self,
        timeout: int = 5,
        workers: int = 8,
        user_agent: str = "CriticBot/1.0",
    ):
        self.timeout = timeout
        self.workers = workers

        self.headers = {
            "User-Agent": user_agent,
        }

    def verify(self, url: str) -> URLResult:

        try:

            response = requests.head(
                url,
                allow_redirects=True,
                timeout=self.timeout,
                headers=self.headers,
            )

            if response.status_code >= 400:

                response = requests.get(
                    url,
                    allow_redirects=True,
                    timeout=self.timeout,
                    headers=self.headers,
                )

            return URLResult(
                url=url,
                reachable=response.status_code < 400,
                status_code=response.status_code,
                final_url=str(response.url),
                response_time=response.elapsed.total_seconds(),
            )

        except Exception as e:

            return URLResult(
                url=url,
                reachable=False,
                error=str(e),
            )

    def verify_many(self, urls: List[str]) -> List[URLResult]:

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.workers
        ) as executor:

            futures = [
                executor.submit(self.verify, url)
                for url in urls
            ]

            return [f.result() for f in futures]

    def broken_urls(self, urls: List[str]) -> List[URLResult]:

        return [
            result
            for result in self.verify_many(urls)
            if not result.reachable
        ]


_default = URLVerifier()


def verify_urls(urls: List[str]) -> List[URLResult]:
    """
    Verify multiple URLs.
    """

    return _default.verify_many(urls)


def broken_urls(urls: List[str]) -> List[URLResult]:
    """
    Return only broken URLs.
    """

    return _default.broken_urls(urls)