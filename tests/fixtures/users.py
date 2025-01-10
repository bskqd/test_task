from typing import Callable

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from adapters.repositories.base import create_repository
from adapters.repositories.users import UsersRepository
from config import Config
from models import User

__all__ = ["users_repo", "create_user"]


@pytest_asyncio.fixture()
async def users_repo(config: Config, fake_db_session: AsyncSession) -> UsersRepository:
    yield UsersRepository(config, create_repository(User, fake_db_session))


@pytest_asyncio.fixture()
async def create_user(fake_db_session: AsyncSession, users_repo: UsersRepository) -> Callable[..., User]:

    async def _create_user(**kwargs) -> User:
        user = await users_repo.create_user(**kwargs)
        await fake_db_session.flush(user)
        await fake_db_session.commit()
        return user

    yield _create_user
