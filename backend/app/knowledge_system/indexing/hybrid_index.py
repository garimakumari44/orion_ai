class HybridIndex:


    """
    Unified retrieval layer.

    Combines:

    - semantic similarity
    - keyword relevance
    - graph relevance
    - metadata filtering
    - temporal ranking

    """



    def __init__(
        self,
        vector_index,
        keyword_index,
        graph_index,
        temporal_index,
        metadata_index
    ):


        self.vector_index=vector_index

        self.keyword_index=keyword_index

        self.graph_index=graph_index

        self.temporal_index=temporal_index

        self.metadata_index=metadata_index




    def search(
        self,
        query,
        embedding=None,
        filters=None,
        top_k=10
    ):


        scores={}



        #
        # Vector retrieval
        #

        if embedding:


            vector_results = (
                self.vector_index.search(
                    embedding,
                    top_k
                )
            )


            for item in vector_results:

                doc=item["id"]

                scores[doc]=(
                    scores.get(doc,0)
                    +
                    item["score"]*0.6
                )



        #
        # Keyword retrieval
        #

        keyword_results = (
            self.keyword_index.search(
                query,
                top_k
            )
        )


        for item in keyword_results:

            doc=item["id"]

            scores[doc]=(
                scores.get(doc,0)
                +
                item["score"]*0.3
            )



        #
        # Metadata filtering
        #

        if filters:


            allowed=set(
                self.metadata_index.filter(
                    filters
                )
            )


            scores={
                k:v
                for k,v in scores.items()
                if k in allowed
            }



        #
        # Final ranking
        #

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