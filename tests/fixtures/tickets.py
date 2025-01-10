from typing import Callable, Optional

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from adapters.repositories.base import create_repository
from adapters.repositories.tickets import TicketsRepository, TicketProductsRepository
from config import Config
from constants import PaymentTypeEnum
from dto import TicketCreationData, TicketCreationPaymentData, TicketProductCreationData
from models import Ticket, TicketProduct

__all__ = ["tickets_repo", "ticket_products_repo", "create_ticket"]


@pytest_asyncio.fixture()
async def tickets_repo(config: Config, fake_db_session: AsyncSession) -> TicketsRepository:
    yield TicketsRepository(config, create_repository(Ticket, fake_db_session))


@pytest_asyncio.fixture()
async def ticket_products_repo(config: Config, fake_db_session: AsyncSession) -> TicketProductsRepository:
    yield TicketProductsRepository(config, create_repository(TicketProduct, fake_db_session))


@pytest_asyncio.fixture()
async def create_ticket(
        fake_db_session: AsyncSession,
        tickets_repo: TicketsRepository,
        ticket_products_repo: TicketProductsRepository,
) -> Callable[[int, Optional[TicketCreationData]], Ticket]:

    async def _create_ticket(user_id: int, ticket_creation_data: Optional[TicketCreationData] = None) -> Ticket:
        if not ticket_creation_data:
            ticket_creation_data = TicketCreationData(
                payment=TicketCreationPaymentData(
                    type=PaymentTypeEnum.card.value,
                    amount=100.00,
                ),
                products=[
                    TicketProductCreationData(
                        name="test",
                        price=50.00,
                        quantity=2.00,
                    )
                ],
            )
        ticket = await tickets_repo.create_ticket(user_id, ticket_creation_data)
        await fake_db_session.flush(ticket)
        await ticket_products_repo.create_ticket_products(ticket.id, ticket_creation_data.products)
        await fake_db_session.commit()
        ticket = await tickets_repo.get_one_ticket(ticket.id, user_id)
        return ticket

    yield _create_ticket
