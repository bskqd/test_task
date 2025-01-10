from adapters.repositories.base import SQLAlchemyRepository
from config import Config
from models.users import User


class UsersRepository:
    def __init__(self, config: Config, repo: SQLAlchemyRepository):
        self._repo = repo
        self._config = config

    async def create_user(self, name: str, nickname: str, password: str) -> User:
        password = User.hash_password(self._config, password)
        return await self._repo.create(name=name, nickname=nickname, password=password)

    async def get_user(self, nickname: str) -> User:
        return await self._repo.get_one(User.nickname == nickname)
