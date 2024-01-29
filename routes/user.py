from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from common.authentication import (
    _create_user,  # noqa
    create_access_token,
    get_user_by_username,
    verify_password, decode_jwt
)
from common.enums import UserRole
from config.config import settings
from database.db import get_db
from models import User
from schemas.user import UserResponse

user_router = APIRouter()


@user_router.post("/signup", response_model=UserResponse)
async def signup(username: str, password: str, role: UserRole, db: Session = Depends(get_db)):
    """
    Endpoint for user registration (sign-up).

    Parameters:
    - username (str): The desired username for the new user.
    - password (str): The password for the new user.
    - role (UserRole): The role of the new user, e.g., 'admin' or 'standard'.
    - db (Session): The database session dependency obtained using FastAPI's dependency injection.

    Returns:
    - A dictionary containing the access token and token type upon successful registration.
    """
    db_user = await get_user_by_username(db, username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    user = await _create_user(db, username, password, role)
    return user


@user_router.post("/login", response_model=dict)
async def login(username: str, password: str, db: Session = Depends(get_db)):
    """
    Endpoint to perform user login.

    Parameters:
    - username (str): The username of the user attempting to log in.
    - password (str): The password of the user attempting to log in.
    - db (Session): The database session dependency obtained using FastAPI's dependency injection.

    Returns:
    - A dictionary containing the access token and token type for the logged-in user.
    """
    user = await get_user_by_username(db, username)

    if not user or not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"user_id": user.id, "username": user.username, "user_role": user.role},
        expires_delta=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return {"access_token": access_token, "token_type": "bearer"}


@user_router.get("", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user(db: Session = Depends(get_db), user=Depends(decode_jwt)):
    """
    Endpoint to retrieve user information by user ID.

    Parameters:
    - user_id (str): The ID of the user for which information is requested.
    - db (Session): The database session dependency obtained using FastAPI's dependency injection.

    Returns:
    - UserResponse: A Pydantic model containing information about the requested user.
    """
    query = await db.execute(select(User).where(User.id == user.get("user_id")))  # noqa
    db_user = query.scalars().one_or_none()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user
