from datetime import datetime
from collections import defaultdict



class TemporalIndex:

    """
    Time-aware knowledge index.

    Supports:

    - recent documents
    - historical lookup
    - version tracking
    """



    def __init__(self):

        self.documents = {}

        self.timeline = defaultdict(list)



    def add(
        self,
        document_id:str,
        timestamp:datetime,
        metadata=None
    ):


        document = {

            "id":document_id,

            "timestamp":timestamp,

            "metadata":metadata or {}
        }


        self.documents[document_id]=document


        date_key = timestamp.date()


        self.timeline[date_key].append(
            document_id
        )



    def search_by_date(
        self,
        start_date,
        end_date
    ):


        results=[]


        for date,docs in self.timeline.items():

            if start_date <= date <= end_date:

                results.extend(docs)


        return results



    def latest(
        self,
        limit=5
    ):


        docs=list(
            self.documents.values()
        )


        docs.sort(
            key=lambda x:x["timestamp"],
            reverse=True
        )


        return docs[:limit]



    def get_version_history(
        self,
        document_id
    ):


        return [
            doc
            for doc in self.documents.values()
            if doc["id"]==document_id
        ]