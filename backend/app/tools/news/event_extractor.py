# app/tools/news/event_extractor.py


from typing import Dict, List



class EventExtractor:
    """
    Extract investment-relevant events
    from financial news.
    """



    EVENT_KEYWORDS = {


        "EARNINGS":

        [
            "earnings",
            "quarterly results",
            "profit",
            "eps"
        ],


        "MERGER_ACQUISITION":

        [
            "acquisition",
            "merger",
            "buyout"
        ],


        "PRODUCT_LAUNCH":

        [
            "launch",
            "introduced",
            "new product"
        ],


        "LEGAL_RISK":

        [
            "lawsuit",
            "investigation",
            "fine"
        ],


        "MANAGEMENT_CHANGE":

        [
            "appointed",
            "resigned",
            "ceo"
        ]

    }



    def extract_event(
        self,
        article: Dict
    ) -> Dict:


        text = (

            article.get(
                "title",
                ""
            )
            +
            " "
            +
            article.get(
                "summary",
                ""
            )

        ).lower()



        detected = []


        for event, keywords in self.EVENT_KEYWORDS.items():

            for keyword in keywords:

                if keyword in text:

                    detected.append(
                        event
                    )

                    break



        return {

            "article":
                article.get(
                    "title"
                ),

            "events":
                detected,


            "market_impact":
                self.estimate_impact(
                    detected
                ),


            "confidence":
                self.confidence(
                    detected
                )
        }



    def extract_batch(
        self,
        articles: List[Dict]
    ) -> List[Dict]:


        return [

            self.extract_event(article)

            for article in articles

        ]



    def estimate_impact(
        self,
        events:List[str]
    ):


        positive = [

            "EARNINGS",
            "PRODUCT_LAUNCH",
            "MERGER_ACQUISITION"

        ]


        negative = [

            "LEGAL_RISK"

        ]


        if any(
            e in positive
            for e in events
        ):
            return "positive"


        if any(
            e in negative
            for e in events
        ):
            return "negative"


        return "neutral"



    def confidence(
        self,
        events:List[str]
    ) -> float:


        if not events:
            return 0.3


        return min(
            0.5 + 
            (len(events)*0.1),
            0.95
        )