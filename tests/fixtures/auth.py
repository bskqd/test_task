import pytest_asyncio

from adapters.auth import JWTAuthenticator
from config import Config

__all__ = ["jwt_authenticator"]


@pytest_asyncio.fixture(scope="session")
async def jwt_authenticator(config: Config) -> str:
    yield JWTAuthenticator(config)
