from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """
    Incoming request from the frontend.
    """

    query: str = Field(
        ...,
        min_length=1,
        description="The user's query."
    )