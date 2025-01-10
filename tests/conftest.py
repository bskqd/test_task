import asyncio
import time

import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine

from adapters.database import Base
from config import Config
from models import *  # noqa
from tests.fixtures import *  # noqa


time.sleep(5)  # waiting for db to be ready to accept connections


async def init_models():
    counter = 0
    while True:
        try:
            async with create_async_engine(Config().DATABASE_URL).begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
                await conn.run_sync(Base.metadata.create_all)
            return
        except Exception as e:
            # waiting some more time for db to be ready to accept connections
            time.sleep(5)
            counter += 1
            if counter >= 3:
                raise e


loop = asyncio.get_event_loop()
loop.run_until_complete(init_models())


@pytest_asyncio.fixture(scope="session", autouse=True)
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
def config():
    yield Config()
