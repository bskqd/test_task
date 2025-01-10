from typing import Callable

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from starlette import status

from dto import SuccessLoginResult


@pytest.mark.asyncio
async def test_registration(app: FastAPI):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/register", json={"name": "str", "nickname": "str", "password": "str"})
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"success": True}


@pytest.mark.asyncio
async def test_login(app: FastAPI, create_user: Callable):
    await create_user(name="str", nickname="str", password="str")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/login", json={"nickname": "str", "password": "str"})
    assert response.status_code == status.HTTP_200_OK
    assert SuccessLoginResult.model_validate(response.json())


@pytest.mark.asyncio
async def test_login_incorrect_nickname(app: FastAPI, create_user: Callable):
    await create_user(name="str", nickname="str", password="str")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/login", json={"nickname": "str1", "password": "str"})
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_login_incorrect_password(app: FastAPI, create_user: Callable):
    await create_user(name="str", nickname="str", password="str")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/login", json={"nickname": "str", "password": "str1"})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
