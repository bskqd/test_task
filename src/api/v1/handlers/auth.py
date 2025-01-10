from fastapi import APIRouter, Depends, exceptions
from starlette import status

from api.v1.schemas.auth import RegistrationRequestSchema, LoginRequestSchema
from dependencies import Stub
from dto import SuccessLoginResult
from services.auth import RegistrationService, LoginService
from services.exceptions.auth import IncorrectPasswordException, InvalidNicknameException

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
        registration_data: RegistrationRequestSchema,
        registration_service: RegistrationService = Depends(Stub(RegistrationService)),
):
    await registration_service.register_user(
        name=registration_data.name,
        nickname=registration_data.nickname,
        password=registration_data.password,
    )
    return {"success": True}


@router.post("/login", response_model=SuccessLoginResult, status_code=status.HTTP_200_OK)
async def login(
        login_data: LoginRequestSchema,
        login_service: LoginService = Depends(Stub(LoginService)),
):
    try:
        return await login_service.login_user(nickname=login_data.nickname, password=login_data.password)
    except IncorrectPasswordException as e:
        raise exceptions.HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except InvalidNicknameException as e:
        raise exceptions.HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
