from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

from adapters.database import Base
from config import Config

__all__ = ("User",)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    nickname = Column(String, unique=True)
    name = Column(String, unique=True)
    password = Column(String)

    tickets = relationship("Ticket", back_populates="user")

    @classmethod
    def hash_password(cls, config: Config, password: str) -> str:
        return config.PWD_CONTEXT.hash(password)

    def check_password(self, config: Config, password: str) -> bool:
        return config.PWD_CONTEXT.verify(password, self.password)
