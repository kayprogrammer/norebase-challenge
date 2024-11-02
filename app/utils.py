from datetime import UTC, datetime, timedelta
from uuid import UUID
from passlib.context import CryptContext
import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.conf import settings
from app.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"


# PASSWORDS
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# TOKENS
def create_auth_token(user_id: UUID):
    # generate auth token based and encode user's id
    expire = datetime.now(UTC) + timedelta(hours=100)
    to_encode = {"exp": expire, "user_id": str(user_id)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def decodeAuth(db: AsyncSession, token: str):
    try:
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        user = (
            await db.execute(select(User).where(User.id == decoded["user_id"]))
        ).scalar_one_or_none()
        return user
    except:
        return None
