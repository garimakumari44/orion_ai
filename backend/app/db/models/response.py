from pydantic import BaseModel, Field
from typing import List, Optional


class QueryResponse(BaseModel):
    """
    Standard API response returned to the frontend.
    """

    success: bool
    response: str

    # Intent detected by the parser
    intent: Optional[str] = None

    # Steps executed by the backend
    steps: List[str] = Field(default_factory=list)

    # Tools used to answer the query
    tools_used: List[str] = Field(default_factory=list)