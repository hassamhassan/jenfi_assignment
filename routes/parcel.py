from typing import List, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, and_
from sqlalchemy.orm import Session

from common.authentication import decode_jwt
from common.enums import UserRole, TrainStatus
from database.db import get_db
from models.parcel import Parcel
from models.train import Train
from schemas.parcel import ParcelCreate, ParcelResponse

parcel_router = APIRouter()


@parcel_router.post("", response_model=ParcelResponse, status_code=status.HTTP_201_CREATED)
async def add_parcel_to_system(parcel: ParcelCreate, db: Session = Depends(get_db), user=Depends(decode_jwt)):
    """
    Add a new parcel to the system.

    Parameters:
    - parcel (ParcelCreate): The Pydantic model representing the details of the parcel to be added.
    - db (Session): The database session dependency obtained using FastAPI's dependency injection.
    - user (dict): The user information obtained from the JWT token. Used to check the user's role.

    Returns:
    - ParcelResponse: A Pydantic model containing information about the added parcel.
    """
    if user.get("user_role") != UserRole.PARCEL_OWNER:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not authorized to add parcel to system"
        )
    db_parcel = Parcel(**parcel.model_dump(), owner_id=user.get("user_id"))
    db.add(db_parcel)
    await db.commit()  # noqa
    return db_parcel


@parcel_router.delete("/parcel_id", response_model=Dict, status_code=status.HTTP_200_OK)
async def withdraw_parcel(parcel_id: str, db: Session = Depends(get_db), user=Depends(decode_jwt)):
    """
    Withdraw a parcel from the system.

    Parameters:
    - parcel_id (str): The ID of the parcel to be withdrawn.
    - db (Session): The database session dependency obtained using FastAPI's dependency injection.
    - user (dict): The user information obtained from the JWT token. Used to check the user's role.

    Returns:
    - dict: A dictionary containing a message indicating the successful withdrawal of the parcel.
    """
    if user.get("user_role") != UserRole.PARCEL_OWNER:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not authorized to withdraw a parcel"
        )
    query = await(db.execute(select(Parcel).where(and_(  # noqa
        Parcel.id == parcel_id,
        Parcel.owner_id == user.get("user_id"),
        Parcel.is_active
    ))))
    db_parcel = query.scalars().one_or_none()
    if not db_parcel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parcel not found")
    if db_parcel.train_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete a parcel already assigned to a train"
        )
    db_parcel.is_active = False
    await db.commit()  # noqa
    return {"message": f"parcel with ID:{parcel_id} has been withdrawn"}


@parcel_router.get("/parcel_id/status", response_model=Dict, status_code=status.HTTP_200_OK)
async def has_parcel_shipped(parcel_id: str, db: Session = Depends(get_db), user=Depends(decode_jwt)):
    """
    Check the shipping status of a parcel.

    Parameters:
    - parcel_id (str): The ID of the parcel for which the shipping status is requested.
    - db (Session): The database session dependency obtained using FastAPI's dependency injection.
    - user (dict): The user information obtained from the JWT token. Used to check the user's role.

    Returns:
    - dict: A dictionary containing the shipping status of the parcel.
    """
    if user.get("user_role") != UserRole.PARCEL_OWNER:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not authorized to check shipping status"
        )
    query = await(db.execute(select(Parcel).where(and_(  # noqa
        Parcel.id == parcel_id,
        Parcel.owner_id == user.get("user_id"),
        Parcel.is_active
    ))))
    db_parcel = query.scalars().one_or_none()

    if not db_parcel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parcel not found")

    return {"has_shipped": db_parcel.has_shipped}


@parcel_router.post("/parcel_id/cost", response_model=Dict, status_code=status.HTTP_200_OK)
async def get_minimal_shipping_cost(parcel_id: str, db: Session = Depends(get_db), user=Depends(decode_jwt)):
    """
    Calculate the minimal cost of shipping for a given parcel.

    Parameters:
    - parcel_id (str): The ID of the parcel for which the shipping status is requested.
    - db (Session): The database session dependency obtained using FastAPI's dependency injection.
    - user (dict): The user information obtained from the JWT token. Used to check the user's role.

    Returns:
    - Dict: A dictionary containing the minimal shipping cost.
    """
    if user.get("user_role") != UserRole.PARCEL_OWNER:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not authorized"
        )

    query = await db.execute(select(Parcel).where(and_(  # noqa
        Parcel.id == parcel_id,
        Parcel.owner_id == user.get("user_id"),
        Parcel.is_active
    )))
    db_parcel = query.scalars().one_or_none()

    if not db_parcel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parcel not found")

    available_trains = await db.execute(select(Train).where(Train.status == TrainStatus.AVAILABLE))  # noqa
    available_trains = available_trains.scalars().all()

    min_cost = float('inf')
    by_train = None

    for train in available_trains:
        cost = db_parcel.calculate_shipping_cost(train)
        if cost < min_cost and db_parcel.destination in train.available_lines.split(','):
            min_cost = cost
            by_train = train

    if not by_train:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Trains are currently unavailable"
        )

    return {"minimal_shipping_cost": min_cost, "by_train": by_train.id}


@parcel_router.get("", response_model=List[ParcelResponse], status_code=status.HTTP_200_OK)
async def get_parcels_for_owner(db: Session = Depends(get_db), user=Depends(decode_jwt)):
    """
    Get a list of parcels for the authenticated parcel owner.

    Parameters:
    - db (Session): The database session dependency obtained using FastAPI's dependency injection.
    - user (dict): The user information obtained from the JWT token. Used to identify the parcel owner.

    Returns:
    - A list of ParcelResponse objects representing the parcels owned by the authenticated user.
    """
    if user.get("user_role") != UserRole.PARCEL_OWNER:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not authorized"
        )
    query = await db.execute(select(Parcel).where(Parcel.owner_id == user.get("user_id"), Parcel.is_active))  # noqa
    db_parcels = query.scalars().all()

    if not db_parcels:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No parcels found for the owner")

    return db_parcels
