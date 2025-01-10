import abc
import uuid
from datetime import datetime, timedelta

from jose import JWTError, jwt

from config import Config
from adapters.exceptions.auth import CredentialsException, InvalidJTIException, TokenExpiredException


class JWTAuthenticator:
    def __init__(self, config: Config):
        self._config = config
        self._valid_token_types = (config.JWT_ACCESS_TOKEN_TYPE, config.JWT_REFRESH_TOKEN_TYPE)
        self._token_type_expiration_minutes_mapping = {
            self._config.JWT_ACCESS_TOKEN_TYPE: self._config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
            self._config.JWT_REFRESH_TOKEN_TYPE: self._config.JWT_REFRESH_TOKEN_EXPIRE_MINUTES,
        }

    def create_access_token(self, user_id: int) -> str:
        return self._create_token(user_id, self._config.JWT_ACCESS_TOKEN_TYPE)

    def create_refresh_token(self, user_id: int) -> str:
        return self._create_token(user_id, self._config.JWT_REFRESH_TOKEN_TYPE)

    def _create_token(self, user_id: int, token_type: str) -> str:
        payload = {
            "user_id": user_id,
            "exp": datetime.now() + timedelta(minutes=self._token_type_expiration_minutes_mapping[token_type]),
            "token_type": token_type,
            "jti": uuid.uuid4().hex,
        }
        token = jwt.encode(payload, self._config.JWT_SECRET_KEY, algorithm=self._config.JWT_ALGORITHM)
        return f"{self._config.JWT_TOKEN_TYPE_NAME} {token}"

    async def validate_authorization_header(self, header: str) -> int:
        try:
            token_type, token = header.split()
        except ValueError:
            raise CredentialsException
        if token_type != self._config.JWT_TOKEN_TYPE_NAME:
            raise CredentialsException
        return await self.validate_token(token)

    async def validate_token(self, token: str) -> int:
        try:
            payload = jwt.decode(token, self._config.JWT_SECRET_KEY, algorithms=[self._config.JWT_ALGORITHM])
        except JWTError:
            raise CredentialsException
        return await self._validate_payload(payload)

    async def _validate_payload(self, payload: dict) -> int:
        user_id = payload.get("user_id")
        exp = payload.get("exp")
        token_type = payload.get("token_type")
        jti = payload.get("jti")
        if not user_id or not exp or not token_type or not jti:
            raise CredentialsException
        try:
            token_expired_at = datetime.utcfromtimestamp(int(exp))
        except TypeError:
            raise CredentialsException
        if token_type not in self._valid_token_types:
            raise CredentialsException
        await self._check_token_expiration(token_expired_at)
        await self._check_jti_is_valid_uuid(jti)
        return user_id

    async def _check_token_expiration(self, token_expired_at: datetime):
        current_datetime = datetime.now()
        if token_expired_at < current_datetime:
            raise TokenExpiredException

    async def _check_jti_is_valid_uuid(self, jti: str):
        try:
            uuid.UUID(jti)
        except ValueError:
            raise InvalidJTIException


class IdentityProviderABC(abc.ABC):
    @abc.abstractmethod
    async def provide_user_id(self) -> int:
        pass


class JWTIdentityProvider(IdentityProviderABC):
    def __init__(self, jwt_authenticator: JWTAuthenticator, authorization_header: str):
        self._jwt_authenticator = jwt_authenticator
        self._authorization_header = authorization_header

    async def provide_user_id(self) -> int:
        return await self._jwt_authenticator.validate_authorization_header(self._authorization_header)
