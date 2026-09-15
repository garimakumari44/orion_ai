from __future__ import annotations

from typing import Dict, Any



class XBRLParser:


    def extract_values(
        self,
        fact: Dict[str,Any]
    ):


        results=[]


        units = fact.get(
            "units",
            {}
        )


        for unit, values in units.items():

            for item in values:

                results.append(
                    {
                        "value":
                            item.get("val"),

                        "date":
                            item.get("fy"),

                        "period":
                            item.get("fp"),

                        "form":
                            item.get("form"),

                        "unit":
                            unit
                    }
                )


        return results



    def latest_value(
        self,
        fact
    ):


        values = self.extract_values(
            fact
        )


        if not values:
            return None


        return sorted(
            values,
            key=lambda x:
            x.get("date") or 0,
            reverse=True
        )[0]