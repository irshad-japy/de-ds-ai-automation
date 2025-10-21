from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any

class Query(BaseModel):
    query: str
    similarity_top_k: Optional[int] = Field(default=5, ge=1, le=10)

    @field_validator("query")
    @classmethod
    def _strip(cls, v: str) -> str:
        v = (v or "").strip()
        if not v:
            raise ValueError("query must not be empty")
        return v

class Response(BaseModel):
    search_result: str
    source: List[Dict[str, Any]] = Field(default_factory=list)
