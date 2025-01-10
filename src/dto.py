from decimal import Decimal

from pydantic import BaseModel


class SuccessLoginResult(BaseModel):
    access_token: str
    refresh_token: str


class TicketProductCreationData(BaseModel):
    name: str
    price: Decimal
    quantity: Decimal


class TicketCreationPaymentData(BaseModel):
    type: str
    amount: Decimal


class TicketCreationData(BaseModel):
    products: list[TicketProductCreationData]
    payment: TicketCreationPaymentData
