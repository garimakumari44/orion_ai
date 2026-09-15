from collections import defaultdict



class MetadataIndex:


    """
    Metadata based retrieval.

    Example:

    source -> github
              |
              doc1
              doc5

    language -> python
              |
              doc2

    """



    def __init__(self):

        self.index = defaultdict(
            lambda: defaultdict(set)
        )


        self.documents={}




    def add(
        self,
        document_id:str,
        metadata:dict
    ):


        self.documents[document_id]=metadata


        for key,value in metadata.items():


            self.index[key][value].add(
                document_id
            )



    def filter(
        self,
        filters:dict
    ):


        result=None


        for key,value in filters.items():

            docs = self.index[key].get(
                value,
                set()
            )


            if result is None:

                result=docs.copy()

            else:

                result &= docs



        return list(result or [])



    def get_metadata(
        self,
        document_id
    ):

        return self.documents.get(
            document_id
        )