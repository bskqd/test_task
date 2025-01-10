from pydantic import BaseModel


class RegistrationRequestSchema(BaseModel):
    name: str
    nickname: str
    password: str


class LoginRequestSchema(BaseModel):
    nickname: str
    password: str
