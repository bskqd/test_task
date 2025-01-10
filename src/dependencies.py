import functools
from typing import Callable, Type

import miniopy_async
from fastapi import Depends, Header
from miniopy_async import Minio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from adapters.auth import JWTAuthenticator, IdentityProviderABC, JWTIdentityProvider
from adapters.files_storage import FilesStorage
from adapters.repositories.base import SQLAlchemyRepository, Model, create_repository
from adapters.repositories.tickets import TicketsRepository, TicketProductsRepository
from adapters.repositories.users import UsersRepository
from config import Config
from models import Ticket, TicketProduct
from models.users import User
from services.auth import RegistrationService, LoginService
from services.tickets import CreateTicketService, RetrieveTicketsService, DownloadTicketService


class Stub:
    def __init__(self, dependency: Callable, **kwargs):
        self._dependency = dependency
        self._kwargs = kwargs

    def __call__(self):
        raise NotImplementedError

    def __eq__(self, other) -> bool:
        if isinstance(other, Stub):
            return self._dependency == other._dependency and self._kwargs == other._kwargs
        if not self._kwargs:
            return self._dependency == other
        return False

    def __hash__(self):
        if not self._kwargs:
            return hash(self._dependency)
        serial = (self._dependency, *self._kwargs.items(),)
        return hash(serial)


class DependenciesOverrides:
    def __init__(self, config: Config):
        self.config = config
        self.db_sessionmaker = sessionmaker(
            create_async_engine(config.DATABASE_URL),
            autoflush=False,
            expire_on_commit=False,
            class_=AsyncSession,
        )

    def overridden_dependencies(self) -> dict:
        return {
            Config: self.get_config,
            Minio: self.get_minio_client,
            FilesStorage: self.get_files_storage,
            AsyncSession: self.get_db_session,
            JWTAuthenticator: self.get_jwt_authenticator,
            IdentityProviderABC: self.get_identity_provider,
            UsersRepository: self.get_users_repository,
            TicketsRepository: self.get_tickets_repository,
            TicketProductsRepository: self.get_ticket_products_repository,
            RegistrationService: self.get_registration_service,
            LoginService: self.get_login_service,
            CreateTicketService: self.get_create_ticket_service,
            RetrieveTicketsService: self.get_retrieve_tickets_service,
            DownloadTicketService: self.get_download_ticket_service,
        }

    def get_config(self):
        return self.config

    @functools.lru_cache(maxsize=1)
    def get_minio_client(self):
        return miniopy_async.Minio(
            endpoint=self.config.MINIO_URL,
            secure=self.config.MINIO_SECURE,
            access_key=self.config.MINIO_ACCESS_KEY,
            secret_key=self.config.MINIO_SECRET_KEY,
        )

    @functools.lru_cache(maxsize=1)
    def get_files_storage(self, config: Config = Depends(Stub(Config)), minio_client: Minio = Depends(Stub(Minio))):
        return FilesStorage(config, minio_client)

    async def get_db_session(self):
        async with (session := self.db_sessionmaker()):
            yield session

    @functools.lru_cache(maxsize=1)
    def get_jwt_authenticator(self, config: Config = Depends(Stub(Config))):
        return JWTAuthenticator(config)

    def get_identity_provider(
            self,
            authorization: str = Header(...),
            jwt_authenticator: JWTAuthenticator = Depends(Stub(JWTAuthenticator)),
    ):
        return JWTIdentityProvider(jwt_authenticator, authorization)

    def get_users_repository(self, config: Config = Depends(Stub(Config)), db_session: AsyncSession = Depends()):
        repo = create_repository(User, db_session)
        return UsersRepository(config, repo)

    def get_tickets_repository(self, config: Config = Depends(Stub(Config)), db_session: AsyncSession = Depends()):
        repo = create_repository(Ticket, db_session)
        return TicketsRepository(config, repo)
    
    def get_ticket_products_repository(
            self,
            config: Config = Depends(Stub(Config)),
            db_session: AsyncSession = Depends(),
    ):
        repo = create_repository(TicketProduct, db_session)
        return TicketProductsRepository(config, repo)

    def get_registration_service(
            self,
            config: Config = Depends(Stub(Config)),
            db_session: AsyncSession = Depends(),
            users_repo: UsersRepository = Depends(Stub(UsersRepository)),
    ):
        return RegistrationService(config, db_session, users_repo)

    def get_login_service(
            self,
            config: Config = Depends(Stub(Config)),
            jwt_authenticator: JWTAuthenticator = Depends(Stub(JWTAuthenticator)),
            users_repo: UsersRepository = Depends(Stub(UsersRepository)),
    ):
        return LoginService(config, jwt_authenticator, users_repo)

    def get_create_ticket_service(
            self,
            identity_provider: IdentityProviderABC = Depends(),
            db_session: AsyncSession = Depends(),
            tickets_repo: TicketsRepository = Depends(Stub(TicketsRepository)),
            ticket_products_repo: TicketProductsRepository = Depends(Stub(TicketProductsRepository)),
    ):
        return CreateTicketService(identity_provider, db_session, tickets_repo, ticket_products_repo)

    def get_retrieve_tickets_service(
            self,
            identity_provider: IdentityProviderABC = Depends(),
            tickets_repo: TicketsRepository = Depends(Stub(TicketsRepository)),
    ):
        return RetrieveTicketsService(identity_provider, tickets_repo)

    def get_download_ticket_service(
            self,
            config: Config = Depends(Stub(Config)),
            tickets_repo: TicketsRepository = Depends(Stub(TicketsRepository)),
            files_storage: FilesStorage = Depends(Stub(FilesStorage)),
    ):
        return DownloadTicketService(config, tickets_repo, files_storage)
