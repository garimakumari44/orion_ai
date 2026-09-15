from collections import defaultdict
import math


class KeywordIndex:

    """
    Keyword based inverted index.

    Example:

    "rag"
        |
        +---- doc1
        +---- doc5

    """


    def __init__(self):

        self.index = defaultdict(set)

        self.documents = {}



    def tokenize(self,text):

        return (
            text.lower()
            .split()
        )



    def add(
        self,
        document_id:str,
        text:str
    ):

        self.documents[document_id]=text


        tokens=self.tokenize(text)


        for token in tokens:

            self.index[token].add(
                document_id
            )



    def remove(
        self,
        document_id:str
    ):

        if document_id not in self.documents:
            return


        text=self.documents[document_id]

        tokens=self.tokenize(text)


        for token in tokens:

            self.index[token].discard(
                document_id
            )


        del self.documents[document_id]



    def search(
        self,
        query:str,
        top_k:int=5
    ):


        tokens=self.tokenize(query)


        scores=defaultdict(int)


        for token in tokens:

            docs=self.index.get(
                token,
                []
            )


            for doc in docs:

                scores[doc]+=1



        ranked=sorted(
            scores.items(),
            key=lambda x:x[1],
            reverse=True
        )


        return [
            {
                "id":doc,
                "score":score
            }
            for doc,score in ranked[:top_k]
        ]
