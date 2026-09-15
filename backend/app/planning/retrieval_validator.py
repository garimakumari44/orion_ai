"""
Validates Adaptive Retrieval pipelines.

Responsible for domain-specific
retrieval workflow validation.

Does NOT:
- Validate DAG structure
- Detect cycles
- Validate generic tasks
"""

from .validator import ValidationError
from .models.task_graph import TaskGraph


class RetrievalValidator:
    """
    Validates Knowledge Retrieval pipelines.
    """


    RETRIEVAL_TASKS = {
        "query_rewrite",
        "dense_retrieval",
        "sparse_retrieval",
        "graph_retrieval",
        "memory_retrieval",
        "retrieval_merge",
        "reranking",
        "compression",
        "context_builder",
    }


    def validate(
        self,
        graph: TaskGraph
    ) -> None:

        self.validate_retrieval_dependencies(graph)

        self.validate_merge_nodes(graph)

        self.validate_reranking(graph)

        self.validate_compression(graph)

        self.validate_context_builder(graph)

        self.validate_pipeline(graph)



    def validate_retrieval_dependencies(
        self,
        graph: TaskGraph
    ) -> None:

        for task in graph.tasks.values():

            task_type = task.task_type.lower()


            retrieval_nodes = {
                "dense_retrieval",
                "sparse_retrieval",
                "graph_retrieval",
                "memory_retrieval",
            }


            if task_type in retrieval_nodes:

                if not task.dependencies:

                    raise ValidationError(
                        f"{task_type} must depend on query_rewrite."
                    )


                has_query_rewrite = any(

                    graph.tasks[dep].task_type.lower()
                    == "query_rewrite"

                    for dep in task.dependencies

                )


                if not has_query_rewrite:

                    raise ValidationError(
                        f"{task_type} requires query_rewrite dependency."
                    )



    def validate_merge_nodes(
        self,
        graph: TaskGraph
    ) -> None:

        for task in graph.tasks.values():

            if task.task_type.lower() == "retrieval_merge":


                if len(task.dependencies) < 2:

                    raise ValidationError(
                        "retrieval_merge requires multiple retrieval sources."
                    )


    def validate_reranking(
        self,
        graph: TaskGraph
    ) -> None:

        for task in graph.tasks.values():

            if task.task_type.lower() == "reranking":

                if not task.dependencies:

                    raise ValidationError(
                        "reranking requires retrieval results."
                    )


                valid_parent = any(

                    graph.tasks[d].task_type.lower()
                    in {
                        "retrieval_merge",
                        "dense_retrieval",
                        "sparse_retrieval",
                        "graph_retrieval",
                    }

                    for d in task.dependencies

                )


                if not valid_parent:

                    raise ValidationError(
                        "reranking must receive retrieval output."
                    )



    def validate_compression(
        self,
        graph: TaskGraph
    ) -> None:

        for task in graph.tasks.values():

            if task.task_type.lower() == "compression":

                if not task.dependencies:

                    raise ValidationError(
                        "compression requires ranked context."
                    )



    def validate_context_builder(
        self,
        graph: TaskGraph
    ) -> None:

        for task in graph.tasks.values():

            if task.task_type.lower() == "context_builder":

                if not task.dependencies:

                    raise ValidationError(
                        "context_builder requires retrieval context."
                    )


                valid_sources = {

                    "retrieval_merge",
                    "reranking",
                    "compression",
                    "dense_retrieval",
                    "sparse_retrieval",
                    "graph_retrieval",
                }


                if not any(

                    graph.tasks[d].task_type.lower()
                    in valid_sources

                    for d in task.dependencies

                ):

                    raise ValidationError(
                        "context_builder has invalid dependencies."
                    )



    def validate_pipeline(
        self,
        graph: TaskGraph
    ) -> None:

        task_types = {

            task.task_type.lower()

            for task in graph.tasks.values()

        }


        if "query_rewrite" in task_types:

            if "context_builder" not in task_types:

                raise ValidationError(
                    "Retrieval pipeline must end with context_builder."
                )