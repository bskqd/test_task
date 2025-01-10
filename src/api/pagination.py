from typing import Optional

from pydantic import BaseModel


class BasePaginatedResponse(BaseModel):
    page_size: Optional[int]
    page: Optional[int]
    items: list[BaseModel]
