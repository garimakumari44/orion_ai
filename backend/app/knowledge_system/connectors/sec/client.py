from __future__ import annotations

import requests
import logging
from typing import Any, Dict


logger = logging.getLogger(__name__)


class SECClient:
    """
    SEC EDGAR API Client.

    Handles:
    - SEC headers
    - API requests
    - rate limiting
    """


    BASE_URL = "https://data.sec.gov"


    def __init__(
        self,
        user_agent: str = "OrionAI research@example.com"
    ):

        self.session = requests.Session()

        self.session.headers.update(
            {
                "User-Agent": user_agent,
                "Accept-Encoding": "gzip, deflate",
            }
        )


    def get(
        self,
        endpoint: str
    ) -> Dict[str, Any]:

        url = f"{self.BASE_URL}{endpoint}"


        try:

            response = self.session.get(
                url,
                timeout=20
            )

            response.raise_for_status()

            return response.json()


        except requests.RequestException as e:

            logger.error(
                f"SEC request failed: {e}"
            )

            raise