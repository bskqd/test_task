from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, computed_field, Field

from api.pagination import BasePaginatedResponse
from dto import TicketCreationData
from constants import PaymentTypeEnum


class TicketCreationSchema(TicketCreationData):
    pass


class TicketProductSchema(BaseModel):
    ticket_id: int
    name: str
    price: Decimal
    quantity: Decimal

    @computed_field
    @property
    def total(self) -> Decimal:
        return (self.price * self.quantity).quantize(Decimal("0.01"))

    class Config:
        from_attributes = True


class TicketPaymentSchema(BaseModel):
    type: PaymentTypeEnum = Field(validation_alias="payment_type")
    amount: Decimal = Field(validation_alias="payment_amount")

    class Config:
        from_attributes = True


class TicketSchema(BaseModel):
    id: int
    created_at: datetime
    total: Decimal
    payment: TicketPaymentSchema
    products: list[TicketProductSchema]

    @computed_field
    @property
    def rest(self) -> Decimal:
        return self.payment.amount - self.total

    class Config:
        from_attributes = True


class PaginatedTicketSchema(BasePaginatedResponse):
    items: list[TicketSchema]
