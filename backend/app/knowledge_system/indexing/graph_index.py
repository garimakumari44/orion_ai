from collections import defaultdict


class GraphIndex:


    """
    Knowledge graph index.

    Stores:

    Entity -> Relationship -> Entity

    """



    def __init__(self):

        self.graph = defaultdict(list)



    def add_relationship(
        self,
        source:str,
        relation:str,
        target:str
    ):


        self.graph[source].append(
            {
                "relation":relation,
                "target":target
            }
        )



    def get_neighbors(
        self,
        entity:str
    ):

        return self.graph.get(
            entity,
            []
        )



    def traverse(
        self,
        start_entity:str,
        depth:int=2
    ):


        visited=set()

        results=[]


        def dfs(node,current_depth):

            if current_depth>depth:
                return


            if node in visited:
                return


            visited.add(node)


            for edge in self.graph[node]:

                results.append(
                    {
                        "source":node,
                        "relation":edge["relation"],
                        "target":edge["target"]
                    }
                )


                dfs(
                    edge["target"],
                    current_depth+1
                )


        dfs(
            start_entity,
            0
        )


        return results