import pytest_asyncio
from sqlalchemy import event
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from config import Config

__all__ = ["fake_db_session"]


class FakeTransactionBegin:
    def __init__(self, session):
        self.session = session

    async def __aenter__(self):
        return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.commit()


@pytest_asyncio.fixture()
async def fake_db_session(config: Config):
    connection = await create_async_engine(config.DATABASE_URL).connect()
    transaction = await connection.begin()
    db_sessionmaker = sessionmaker(
        create_async_engine(config.DATABASE_URL),
        autoflush=False,
        expire_on_commit=False,
        class_=AsyncSession,
    )
    session = db_sessionmaker(bind=connection)
    nested = await connection.begin_nested()  # Begin a nested transaction (using SAVEPOINT).

    # If the application code calls session.commit, it will end the nested transaction.
    # Need to start a new one when that happens.
    @event.listens_for(session.sync_session, "after_transaction_end")
    def end_savepoint(session, transaction):
        nonlocal nested
        if not nested.is_active:
            nested = connection.sync_connection.begin_nested()

    # For operations in code that begin their own transactions
    session.begin = lambda: FakeTransactionBegin(session)

    yield session

    # Rollback the overall transaction, restoring the state before the test ran.
    await session.close()
    await transaction.rollback()
    await connection.close()
