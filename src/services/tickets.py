import io
from typing import Optional

from fastapi_filter.contrib.sqlalchemy import Filter
from sqlalchemy.ext.asyncio import AsyncSession

from adapters.auth import IdentityProviderABC
from adapters.files_storage import FilesStorage
from adapters.pagination import BasePaginator
from adapters.repositories.tickets import TicketsRepository, TicketProductsRepository
from config import Config
from constants import PaymentTypeEnum
from dto import TicketCreationData
from models.tickets import Ticket, TicketProduct
from services.exceptions.tickets import TicketNotFoundException, IncorrectTicketAmountException


class CreateTicketService:
    def __init__(
            self,
            identity_provider: IdentityProviderABC,
            uow: AsyncSession,
            tickets_repo: TicketsRepository,
            ticket_products_repo: TicketProductsRepository,
    ):
        self._identity_provider = identity_provider
        self._uow = uow
        self._tickets_repo = tickets_repo
        self._ticket_products_repo = ticket_products_repo

    async def create_ticket(self, ticket_data: TicketCreationData) -> tuple[Ticket, list[TicketProduct]]:
        user_id = await self._identity_provider.provide_user_id()
        ticket_products_total = sum(
            ticket_product.price * ticket_product.quantity for ticket_product in ticket_data.products
        )
        if ticket_products_total > ticket_data.payment.amount:
            raise IncorrectTicketAmountException()
        async with self._uow.begin():
            ticket = await self._tickets_repo.create_ticket(user_id, ticket_data)
            await self._uow.flush(ticket)
            ticket_products = await self._ticket_products_repo.create_ticket_products(ticket.id, ticket_data.products)
            await self._uow.commit()
        await self._uow.refresh(ticket)
        return ticket, ticket_products


class RetrieveTicketsService:
    def __init__(self, identity_provider: IdentityProviderABC, tickets_repo: TicketsRepository):
        self._identity_provider = identity_provider
        self._tickets_repo = tickets_repo

    async def get_one_ticket(self, ticket_id: int) -> Ticket:
        user_id = await self._identity_provider.provide_user_id()
        ticket = await self._tickets_repo.get_one_ticket(ticket_id, user_id)
        if not ticket:
            raise TicketNotFoundException()
        return ticket

    async def get_many_tickets(
            self,
            tickets_filter: Optional[Filter] = None,
            paginator: Optional[BasePaginator] = None,
    ) -> list[Ticket]:
        offset, limit = self._get_offset_limit(paginator)
        user_id = await self._identity_provider.provide_user_id()
        return await self._tickets_repo.get_many_tickets(user_id, tickets_filter, offset, limit)

    def _get_offset_limit(self, paginator: Optional[BasePaginator]) -> tuple[Optional[int], Optional[int]]:
        if paginator:
            return paginator.get_offset_limit()
        return None, None


class DownloadTicketService:
    def __init__(self, config: Config, tickets_repo: TicketsRepository, files_storage: FilesStorage):
        self._config = config
        self._tickets_repo = tickets_repo
        self._files_storage = files_storage

    async def get_download_url(self, ticket_id: int, max_symbols: int) -> str:
        ticket = await self._tickets_repo.get_one_ticket(ticket_id)
        if not ticket:
            raise TicketNotFoundException()
        return await self._save_ticket_file(ticket, max_symbols)

    async def _save_ticket_file(self, ticket: Ticket, max_symbols: int) -> str:
        bucket_name = self._config.TICKET_FILES_BUCKET_NAME
        filename = f"{ticket.id}_{max_symbols}.txt"
        if await self._files_storage.check_object_exists(bucket_name, filename):
            return await self._files_storage.get_object_link(bucket_name, filename)
        generated_data = self._get_ticket_generated_info(ticket, max_symbols)
        data_length = len(generated_data)
        file = io.BytesIO(generated_data)
        return await self._files_storage.put_object(
            bucket_name=bucket_name,
            object_name=filename,
            data=file,
            length=data_length,
            content_type="text/plain; charset=utf-8",
        )

    def _get_ticket_generated_info(self, ticket: Ticket, max_symbols: int) -> bytes:
        separator = "=" * max_symbols
        products_separator = "-" * max_symbols
        payment_type_display_name = PaymentTypeEnum.get_display_name(ticket.payment_type)

        def format_row(left: str, right: str = "", align: str = "left") -> str:
            if align == "left":
                return f"{left:<{max_symbols - len(right)}}{right:>{len(right)}}"
            elif align == "center":
                total_space = max_symbols - len(left)
                left_pad = total_space // 2
                right_pad = total_space - left_pad
                return f"{' ' * left_pad}{left}{' ' * right_pad}"
            return ""

        data = f"{format_row(f'ФОП {ticket.user.name}', align='center')}\n"
        data += f"{separator}\n"

        for product_index, product in enumerate(ticket.ticket_products, 1):
            total_calculation = f"{product.quantity:.2f} x {product.price:.2f}"
            total = f"{product.quantity * product.price:.2f}"
            data += f"{format_row(total_calculation, align='left')}\n"
            data += f"{format_row(product.name, total, align='left')}\n"
            if product_index != len(ticket.ticket_products):
                data += f"{products_separator}\n"

        data += f"{separator}\n"
        data += f"{format_row('СУМА:', f'{ticket.total:.2f}', align='left')}\n"
        data += f"{format_row(f'{payment_type_display_name}:', f'{ticket.payment_amount:.2f}', align='left')}\n"
        data += f"{format_row('Решта:', f'{ticket.payment_amount - ticket.total:.2f}', align='left')}\n"
        data += f"{separator}\n"

        data += f"{format_row(ticket.created_at.strftime('%d.%m.%Y %H:%M'), align='center')}\n"
        data += f"{format_row('Дякуємо за покупку!', align='center')}\n"

        return data.encode("utf-8")


