from fastapi import HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, HTTPBearer
from jose import JWTError, ExpiredSignatureError

from app.core.enums import TokenType
from app.utils.security import decode_token


class TokenBearer(HTTPBearer):
    async def __call__(self, request: Request) -> dict:
        creds = await super().__call__(request)
        token = creds.credentials

        try:
            token_data = decode_token(token)
        except ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        self.verify_token_data(token_data)

        return token_data


    def verify_token_data(self, token_data):
        raise NotImplementedError("Override this method in child classes")


class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and token_data.get("type") != TokenType.access.value:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and token_data.get("type") != TokenType.refresh.value:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
access_token_scheme = AccessTokenBearer()
refresh_token_scheme = RefreshTokenBearer()
