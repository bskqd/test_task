from fastapi import APIRouter, Depends, exceptions
from fastapi_filter import FilterDepends
from starlette import status
from starlette.responses import RedirectResponse

from adapters.pagination import BasePaginator
from api.v1.filters.tickets import TicketsFilter
from api.v1.schemas.tickets import (
    TicketSchema, TicketProductSchema, TicketPaymentSchema, TicketCreationSchema, PaginatedTicketSchema,
)
from dependencies import Stub
from services.exceptions.tickets import TicketNotFoundException, IncorrectTicketAmountException
from services.tickets import CreateTicketService, RetrieveTicketsService, DownloadTicketService

router = APIRouter()


@router.post("/create_ticket", response_model=TicketSchema, status_code=status.HTTP_201_CREATED)
async def create_ticket(
        ticket_data: TicketCreationSchema,
        ticket_creation_service: CreateTicketService = Depends(Stub(CreateTicketService)),
):
    try:
        ticket, products = await ticket_creation_service.create_ticket(ticket_data)
    except IncorrectTicketAmountException as e:
        raise exceptions.HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    return TicketSchema(
        id=ticket.id,
        created_at=ticket.created_at,
        total=ticket.total,
        payment=TicketPaymentSchema.from_orm(ticket),
        products=[TicketProductSchema.from_orm(product) for product in products],
    )


@router.get("/tickets/{ticket_id}", response_model=TicketSchema, status_code=status.HTTP_200_OK)
async def get_one_ticket(
        ticket_id: int,
        retrieve_tickets_service: RetrieveTicketsService = Depends(Stub(RetrieveTicketsService)),
):
    try:
        ticket = await retrieve_tickets_service.get_one_ticket(ticket_id)
    except TicketNotFoundException as e:
        raise exceptions.HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return TicketSchema(
        id=ticket.id,
        created_at=ticket.created_at,
        total=ticket.total,
        payment=TicketPaymentSchema.from_orm(ticket),
        products=[TicketProductSchema.from_orm(product) for product in ticket.ticket_products],
    )


@router.get("/tickets", response_model=PaginatedTicketSchema, status_code=status.HTTP_200_OK)
async def get_many_tickets(
        tickets_filter: TicketsFilter = FilterDepends(TicketsFilter),
        paginator: BasePaginator = Depends(),
        retrieve_tickets_service: RetrieveTicketsService = Depends(Stub(RetrieveTicketsService)),
):
    tickets = await retrieve_tickets_service.get_many_tickets(tickets_filter, paginator)
    items = [
        TicketSchema(
            id=ticket.id,
            created_at=ticket.created_at,
            total=ticket.total,
            payment=TicketPaymentSchema.from_orm(ticket),
            products=[TicketProductSchema.from_orm(product) for product in ticket.ticket_products],
        )
        for ticket in tickets
    ]
    return PaginatedTicketSchema(page_size=paginator.page_size, page=paginator.page, items=items)


@router.get("/download_ticket/{ticket_id}", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
async def download_ticket(
        ticket_id: int,
        max_symbols: int,
        download_ticket_service: DownloadTicketService = Depends(Stub(DownloadTicketService)),
):
    try:
        download_url = await download_ticket_service.get_download_url(ticket_id, max_symbols)
    except TicketNotFoundException as e:
        raise exceptions.HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return RedirectResponse(download_url)
