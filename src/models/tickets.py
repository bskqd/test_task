from sqlalchemy import Column, String, Integer, DECIMAL, DateTime, func, ForeignKey, Enum
from sqlalchemy.orm import relationship

from adapters.database import Base

__all__ = ("Ticket", "TicketProduct",)

from constants import PaymentTypeEnum


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    created_at = Column(DateTime, default=func.now())
    payment_type = Column(Enum(PaymentTypeEnum), default=PaymentTypeEnum.cash)
    payment_amount = Column(DECIMAL(10, 2), nullable=False)
    total = Column(DECIMAL(10, 2), nullable=False)

    user = relationship("User", back_populates="tickets", cascade="all, delete")
    ticket_products = relationship("TicketProduct", back_populates="ticket")


class TicketProduct(Base):
    __tablename__ = "ticket_products"

    id = Column(Integer, primary_key=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), index=True)
    name = Column(String)
    price = Column(DECIMAL(10, 2), nullable=False)
    quantity = Column(DECIMAL(10, 2), nullable=False)

    ticket = relationship("Ticket", back_populates="ticket_products", cascade="all, delete")
