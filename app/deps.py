from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.handlers import RequestError
from app.models import User
from .utils import decodeAuth

jwt_scheme = HTTPBearer(auto_error=False)


async def get_user(
    token: HTTPAuthorizationCredentials = Depends(jwt_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not token:
        raise RequestError(
            err_msg="Unauthorized User!",
            status_code=401,
        )
    user = await decodeAuth(db, token.credentials)
    if not user:
        raise RequestError(
            err_msg="Auth Token is Invalid or Expired",
            status_code=401,
        )
    return user
