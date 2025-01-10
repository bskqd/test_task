from typing import Optional

from fastapi_filter.contrib.sqlalchemy import Filter
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload

from adapters.repositories.base import SQLAlchemyRepository
from config import Config
from dto import TicketCreationData, TicketProductCreationData
from models import Ticket, TicketProduct


class TicketsRepository:
    def __init__(self, config: Config, repo: SQLAlchemyRepository):
        self._repo = repo
        self._config = config

    async def create_ticket(self, user_id: int, ticket_data: TicketCreationData) -> Ticket:
        total = sum(ticket_product.price * ticket_product.quantity for ticket_product in ticket_data.products)
        return await self._repo.create(
            user_id=user_id,
            payment_type=ticket_data.payment.type,
            payment_amount=ticket_data.payment.amount,
            total=total,
        )

    async def get_many_tickets(
            self,
            user_id: int,
            tickets_filter: Optional[Filter] = None,
            offset: Optional[int] = None,
            limit: Optional[int] = None,
    ) -> list[Ticket]:
        db_query = select(Ticket).where(
            Ticket.user_id == user_id
        ).options(
            selectinload(Ticket.ticket_products),
        )
        return await self._repo.get_many(db_query=db_query, query_filter=tickets_filter, offset=offset, limit=limit)

    async def get_one_ticket(self, ticket_id: int, user_id: Optional[int] = None) -> Ticket:
        where_clause = [Ticket.id == ticket_id]
        if user_id:
            where_clause.append(Ticket.user_id == user_id)
        return await self._repo.get_one(
            db_query=select(Ticket).where(
                *where_clause
            ).options(
                joinedload(Ticket.user),
                selectinload(Ticket.ticket_products),
            )
        )


class TicketProductsRepository:
    def __init__(self, config: Config, repo: SQLAlchemyRepository):
        self._repo = repo
        self._config = config

    async def create_ticket_products(
            self,
            ticket_id: int,
            products: list[TicketProductCreationData],
    ) -> list[TicketProduct]:
        products = [
            {"ticket_id": ticket_id, **product.model_dump()}
            for product in products
        ]
        return await self._repo.create_many(products)
