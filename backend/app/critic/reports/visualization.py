from typing import List, Dict



class VisualizationBuilder:
    """
    Creates visualization-ready data.
    """



    def __init__(
        self,
        results: List[Dict]
    ):

        self.results = results



    def evaluator_score_chart(self):

        """
        Bar chart data.
        """

        return {

            "type":
                "bar",

            "title":
                "Evaluator Scores",

            "data":

                [

                    {
                        "name":
                            r.get(
                                "name"
                            ),

                        "score":
                            r.get(
                                "score",
                                0
                            )

                    }

                    for r in self.results

                ]

        }



    def pass_fail_chart(self):

        passed = 0
        failed = 0


        for r in self.results:

            if r.get("passed"):

                passed += 1

            else:

                failed += 1



        return {

            "type":
                "pie",

            "title":
                "Pass vs Failure",

            "data":

            [

                {
                    "label":
                        "Passed",

                    "value":
                        passed

                },

                {
                    "label":
                        "Failed",

                    "value":
                        failed
                }

            ]

        }



    def severity_chart(self):

        severity = {}


        for result in self.results:

            level = result.get(
                "severity",
                "unknown"
            )


            severity[level] = (
                severity.get(level,0)
                + 1
            )



        return {

            "type":
                "bar",

            "title":
                "Issue Severity",

            "data":

            [

                {
                    "severity":
                        key,

                    "count":
                        value

                }

                for key,value
                in severity.items()

            ]

        }



    def dashboard_payload(self):

        """
        Complete frontend dashboard payload.
        """

        return {

            "charts":

            [

                self.evaluator_score_chart(),

                self.pass_fail_chart(),

                self.severity_chart()

            ]

        }