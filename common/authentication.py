from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import decode, encode
from models.user import User
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from sqlalchemy import select

from config.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def encode_jwt(user_id):
    try:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode = {"exp": expire, "user_id": user_id}
        encoded_jwt = encode(to_encode, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials. {err}",
            headers={"WWW-Authenticate": 'Bearer error="invalid_token"'},
        ) from err
    return encoded_jwt


def decode_jwt(
    token: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False)),
):
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer authentication required",
            headers={"WWW-Authenticate": 'Bearer realm="auth_required"'},
        )
    try:
        decoded_token = decode(token.credentials, algorithms=settings.ALGORITHM, key=settings.SECRET_KEY)
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials. {err}",
            headers={"WWW-Authenticate": 'Bearer error="invalid_token"'},
        ) from err
    return decoded_token


def create_access_token(data: dict, expires_delta: int):
    expire = datetime.utcnow() + timedelta(minutes=expires_delta)
    to_encode = {"exp": expire, **data}
    encoded_jwt = encode(to_encode, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


async def get_user_by_username(db: Session, username: str):
    query = await db.execute(select(User).where(User.username == username))  # noqa
    db_user = query.scalars().one_or_none()
    return db_user


async def _create_user(db: Session, username: str, password: str, role: str):
    hashed_password = pwd_context.hash(password)
    db_user = User(username=username, password=hashed_password, role=role)
    db.add(db_user)
    await db.commit()  # noqa
    return db_user
