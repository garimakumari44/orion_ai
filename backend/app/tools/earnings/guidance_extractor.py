# app/tools/earnings/guidance_extractor.py

from typing import Dict, List



class GuidanceExtractor:
    """
    Extracts forward-looking statements
    from earnings transcripts.
    """



    GUIDANCE_TERMS = [

        "expect",
        "forecast",
        "guidance",
        "outlook",
        "target",
        "next quarter",
        "full year"

    ]



    def extract(
        self,
        parsed_transcript: Dict
    ) -> Dict:



        text = self._combine_text(
            parsed_transcript
        )


        statements=[]


        for sentence in text.split("."):

            lower = sentence.lower()


            if any(
                term in lower
                for term in self.GUIDANCE_TERMS
            ):

                statements.append(
                    sentence.strip()
                )



        return {


            "guidance_statements":
                statements,


            "confidence":
                self.calculate_confidence(
                    statements
                ),


            "risk_flags":
                self.detect_risks(
                    statements
                )

        }



    def _combine_text(
        self,
        data:Dict
    ):


        return " ".join(

            data.get(
                "management_commentary",
                []
            )

            +

            data.get(
                "qa_section",
                []
            )

        )



    def calculate_confidence(
        self,
        statements:List[str]
    ):


        if not statements:
            return 0.2


        return min(
            0.5 +
            len(statements)*0.1,
            0.95
        )



    def detect_risks(
        self,
        statements:List[str]
    ):


        risks=[]


        risk_words=[

            "uncertain",
            "pressure",
            "challenge",
            "headwind"

        ]


        for statement in statements:

            for word in risk_words:

                if word in statement.lower():

                    risks.append(
                        statement
                    )


        return risks