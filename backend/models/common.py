from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class Task(BaseModel):
    id: Optional[str] = None
    title: str
    isActive: bool

    model_config = {
        "extra": "allow"
    }

class PaginatedResponse(BaseModel):
    page: int
    perPage: int
    total: int
    data: List[Dict[str, Any]]