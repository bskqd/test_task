from typing import Callable

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from config import Config
from dependencies import DependenciesOverrides
from main import create_application

__all__ = ["app", "dependencies_override_factory"]


class TestsDependenciesOverrides(DependenciesOverrides):
    def __init__(self, config: Config, db_session: AsyncSession):
        self.config = config
        self.db_session = db_session

    def overridden_dependencies(self) -> dict:
        origin_dependencies = super().overridden_dependencies()
        origin_dependencies[AsyncSession] = lambda: self.db_session
        return origin_dependencies


@pytest_asyncio.fixture()
def dependencies_override_factory(config: Config, fake_db_session: AsyncSession):

    def get_dependencies_override_factory(config_argument: Config):
        return TestsDependenciesOverrides(config, fake_db_session).overridden_dependencies()

    yield get_dependencies_override_factory


@pytest_asyncio.fixture()
async def app(dependencies_override_factory: Callable, config: Config):
    yield create_application(dependencies_override_factory, config)
