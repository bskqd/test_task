from decimal import Decimal
from typing import Callable, Optional

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from starlette import status

from adapters.auth import JWTAuthenticator
from dto import TicketCreationData
from models import User, Ticket


@pytest.mark.asyncio
async def test_create_ticket(app: FastAPI, jwt_authenticator: JWTAuthenticator, create_user: Callable):
    user = await create_user(name="str", nickname="str", password="str")
    access_token = jwt_authenticator.create_access_token(user.id)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/create_ticket",
            json={
                "products": [
                    {
                        "name": "test1", "price": 50.00, "quantity": 3.00
                    },
                    {
                        "name": "test2", "price": 50.00, "quantity": 2.00
                    }
                ],
                "payment": {
                    "type": "cash",
                    "amount": 250.00
                }
            },
            headers={"Authorization": access_token},
        )
    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()
    assert response_data["id"]
    assert response_data["created_at"]
    assert response_data["products"]
    assert len(response_data["products"]) == 2
    ticket_id = response_data["id"]
    first_product = {"ticket_id": ticket_id, "name": "test1", "price": "50.00", "quantity": "3.00", "total": "150.00"}
    second_product = {"ticket_id": ticket_id, "name": "test2", "price": "50.00", "quantity": "2.00", "total": "100.00"}
    assert first_product in response_data["products"]
    assert second_product in response_data["products"]
    assert response_data["total"] == "250.00"
    assert response_data["rest"] == "0.00"


@pytest.mark.asyncio
async def test_create_ticket_incorrect_amount(app: FastAPI, jwt_authenticator: JWTAuthenticator):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/create_ticket",
            json={
                "products": [
                    {
                        "name": "test1", "price": 50.00, "quantity": 3.00
                    },
                    {
                        "name": "test2", "price": 50.00, "quantity": 2.00
                    }
                ],
                "payment": {
                    "type": "cash",
                    "amount": 200.00
                }
            },
            headers={"Authorization": jwt_authenticator.create_access_token(1)},
        )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_get_many_tickets_pagination(
        app: FastAPI,
        jwt_authenticator: JWTAuthenticator,
        create_user: Callable[..., User],
        create_ticket: Callable[[int, Optional[TicketCreationData]], Ticket],
):
    user = await create_user(name="str", nickname="str", password="str")
    await create_ticket(user.id, None)
    ticket2 = await create_ticket(user.id, None)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(
            "/api/v1/tickets",
            headers={"Authorization": jwt_authenticator.create_access_token(user.id)},
            params={"page_size": 1, "page": 2}

        )
    assert response.status_code == status.HTTP_200_OK
    expected_response = {
        "page_size": 1,
        "page": 2,
        "items": [
            {
                "id": ticket2.id,
                "created_at": ticket2.created_at.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "total": str(ticket2.total),
                "payment": {
                    "type": ticket2.payment_type.value,
                    "amount": str(ticket2.payment_amount)
                },
                "products": [
                    {
                        "ticket_id": ticket2.id,
                        "name": product.name,
                        "price": str(product.price),
                        "quantity": str(product.quantity),
                        "total": str((product.price * product.quantity).quantize(Decimal("0.01"))),
                    }
                    for product in ticket2.ticket_products
                ],
                "rest": str(ticket2.payment_amount - ticket2.total)
            }
        ]
    }
    assert response.json() == expected_response


@pytest.mark.asyncio
async def test_get_many_tickets_filtering(
        app: FastAPI,
        jwt_authenticator: JWTAuthenticator,
        create_user: Callable[..., User],
        create_ticket: Callable[[int, Optional[TicketCreationData]], Ticket],
):
    user = await create_user(name="str", nickname="str", password="str")
    ticket = await create_ticket(user.id, None)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(
            "/api/v1/tickets",
            headers={"Authorization": jwt_authenticator.create_access_token(user.id)},
            params={"total__lte": ticket.total - 1}

        )
    assert response.status_code == status.HTTP_200_OK
    expected_response = {
        "page_size": None,
        "page": None,
        "items": [],
    }
    assert response.json() == expected_response


@pytest.mark.asyncio
async def test_download_ticket(
        app: FastAPI,
        create_user: Callable[..., User],
        create_ticket: Callable[[int, Optional[TicketCreationData]], Ticket],
):
    user = await create_user(name="str", nickname="str", password="str")
    ticket = await create_ticket(user.id, None)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(f"/api/v1/download_ticket/{ticket.id}", params={"max_symbols": 40})
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    location = response.headers["location"]
    async with AsyncClient() as ac:
        response = await ac.get(location)
    assert response.headers["content-type"] == "text/plain; charset=utf-8"


@pytest.mark.asyncio
async def test_download_ticket_invalid_id(
        app: FastAPI,
        create_user: Callable[..., User],
        create_ticket: Callable[[int, Optional[TicketCreationData]], Ticket],
):
    user = await create_user(name="str", nickname="str", password="str")
    ticket = await create_ticket(user.id, None)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get(f"/api/v1/download_ticket/{ticket.id + 1}", params={"max_symbols": 40})
    assert response.status_code == status.HTTP_404_NOT_FOUND
