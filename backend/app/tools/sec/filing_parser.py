"""
SEC Filing Parser

Extracts meaningful sections from SEC filings.
"""


from bs4 import BeautifulSoup

from typing import Dict



class FilingParser:



    def parse(
        self,
        html: str
    ) -> Dict:


        soup = BeautifulSoup(
            html,
            "html.parser"
        )


        text = soup.get_text(
            "\n"
        )


        return {

            "raw_text":
                text,

            "business":
                self.extract_section(
                    text,
                    "Business"
                ),

            "risk_factors":
                self.extract_section(
                    text,
                    "Risk Factors"
                ),

            "management_discussion":
                self.extract_section(
                    text,
                    "Management's Discussion"
                )

        }



    def extract_section(
        self,
        text: str,
        keyword: str
    ) -> str:


        index = text.lower().find(
            keyword.lower()
        )


        if index == -1:
            return ""


        section = text[
            index:index + 5000
        ]


        return section