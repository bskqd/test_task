from typing import Optional


class BasePaginator:
    def __init__(self, page_size: Optional[int] = None, page: Optional[int] = None):
        self.page_size = page_size
        self.page = page

    def get_offset_limit(self) -> tuple[Optional[int], Optional[int]]:
        if not self.page or not self.page_size:
            return None, None
        offset = (self.page - 1) * self.page_size
        limit = self.page_size
        return offset, limit
