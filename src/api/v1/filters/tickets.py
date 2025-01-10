from datetime import datetime
from decimal import Decimal
from typing import Optional

from fastapi_filter.contrib.sqlalchemy import Filter

from models import Ticket


class TicketsFilter(Filter):
    created_at__gte: Optional[datetime] = None
    created_at__lte: Optional[datetime] = None
    total__gte: Optional[Decimal] = None
    total__lte: Optional[Decimal] = None
    payment_type: Optional[str] = None

    class Constants(Filter.Constants):
        model = Ticket
        search_model_fields = ["payment_type"]
