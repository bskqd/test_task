from typing import Callable

import uvicorn
from fastapi import FastAPI

from api.v1.urls import v1_urls_router
from config import Config
from dependencies import DependenciesOverrides


def create_application(dependency_overrides_factory: Callable, config: Config) -> FastAPI:
    application = FastAPI()

    application.dependency_overrides = dependency_overrides_factory(config)

    application.include_router(v1_urls_router)

    return application


def fastapi_dependency_overrides_factory(config: Config) -> dict:
    dependencies_overrides = DependenciesOverrides(config)
    return {
        **dependencies_overrides.overridden_dependencies(),
    }


app = create_application(fastapi_dependency_overrides_factory, Config())


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
