# app/tools/earnings/transcript_parser.py

from typing import Dict, List



class TranscriptParser:
    """
    Parses earnings call transcripts.
    """



    def parse(
        self,
        transcript: Dict
    ) -> Dict:


        text = transcript.get(
            "transcript",
            ""
        )


        return {


            "company":
                transcript.get(
                    "company"
                ),


            "period":
                transcript.get(
                    "period"
                ),



            "management_commentary":

                self.extract_management(
                    text
                ),



            "qa_section":

                self.extract_qa(
                    text
                ),



            "financial_highlights":

                self.extract_financial_points(
                    text
                )

        }



    def extract_management(
        self,
        text:str
    ) -> List[str]:


        sections=[]


        lines=text.split("\n")


        for line in lines:

            if (
                "CEO" in line
                or
                "CFO" in line
            ):
                sections.append(
                    line.strip()
                )


        return sections



    def extract_qa(
        self,
        text:str
    ) -> List[str]:


        if "Q&A" in text:

            return [

                text.split(
                    "Q&A"
                )[1]

            ]


        return []



    def extract_financial_points(
        self,
        text:str
    ) -> List[str]:


        keywords=[
            "revenue",
            "margin",
            "growth",
            "profit"
        ]


        results=[]


        for word in keywords:

            if word in text.lower():

                results.append(
                    word
                )


        return results