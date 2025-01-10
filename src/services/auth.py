from sqlalchemy.ext.asyncio import AsyncSession

from adapters.auth import JWTAuthenticator
from adapters.repositories.users import UsersRepository
from config import Config
from dto import SuccessLoginResult
from services.exceptions.auth import IncorrectPasswordException, InvalidNicknameException


class RegistrationService:
    def __init__(self, config: Config, uow: AsyncSession, users_repo: UsersRepository):
        self._config = config
        self._uow = uow
        self._users_repo = users_repo

    async def register_user(self, name: str, nickname: str, password: str):
        user = await self._users_repo.create_user(name, nickname, password)
        await self._uow.commit()
        await self._uow.refresh(user)


class LoginService:
    def __init__(self, config: Config, jwt_authenticator: JWTAuthenticator, users_repo: UsersRepository):
        self._config = config
        self._jwt_authenticator = jwt_authenticator
        self._users_repo = users_repo

    async def login_user(self, nickname: str, password: str) -> SuccessLoginResult:
        user = await self._users_repo.get_user(nickname)
        if not user:
            raise InvalidNicknameException()
        if not user.check_password(self._config, password):
            raise IncorrectPasswordException()
        access_token = self._jwt_authenticator.create_access_token(user.id)
        refresh_token = self._jwt_authenticator.create_refresh_token(user.id)
        return SuccessLoginResult(access_token=access_token, refresh_token=refresh_token)
