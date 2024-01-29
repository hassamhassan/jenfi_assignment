from datetime import datetime
from typing import List, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, and_
from sqlalchemy.orm import Session, selectinload

from common.authentication import decode_jwt
from common.enums import UserRole, TrainStatus
from common.helpers import assign_parcels_to_train
from database.db import get_db
from models.parcel import Parcel
from models.train import Train
from schemas.train import (
    TrainCreate,
    TrainResponse,
    TrainStatusResponse,
    TrainCapacityCostResponse
)

train_router = APIRouter()


@train_router.get("/available", response_model=List[TrainResponse], status_code=status.HTTP_200_OK)
async def get_available_trains(db: Session = Depends(get_db), user=Depends(decode_jwt)):
    """
    Retrieve a list of available trains.

    Parameters:
    - db (Session): The database session dependency obtained using FastAPI's dependency injection.
    - user (dict): The user information obtained from the JWT token. Used to check the user's role.

    Returns:
    - A list of TrainResponse objects representing the available trains.
    """
    if user.get("user_role") != UserRole.TRAIN_OPERATOR:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not authorized to view available trains"
        )
    query = await db.execute(select(Train).where(and_(  # noqa
        Train.operator_id == user.get("user_id"),
        Train.status == TrainStatus.AVAILABLE
    )))
    db_trains = query.scalars().all()
    if not db_trains:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Train not found")
    return db_trains


@train_router.get("/train_id/capacity-cost", response_model=TrainCapacityCostResponse, status_code=status.HTTP_200_OK)
async def get_train_capacity_cost(train_id: str, db: Session = Depends(get_db), user=Depends(decode_jwt)):
    """
        Get the current capacity and cost of a train.

        Parameters:
        - train_id (str): The ID of the train for which capacity and cost are requested.
        - db (Session): The database session dependency obtained using FastAPI's dependency injection.
        - user (dict): The user information obtained from the JWT token. Used to check the user's role.

        Returns:
        - TrainCapacityCostResponse: A Pydantic model containing the current capacity and cost of the train.
        """
    if user.get("user_role") != UserRole.TRAIN_OPERATOR:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not authorized"
        )
    train = await db.execute(select(Train).where(and_(  # noqa
        Train.operator_id == user.get("user_id"),
        Train.id == train_id
    )))
    db_train = train.scalars().first()

    if not db_train:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Train not found")

    current_cost = (db_train.current_weight * db_train.weight_cost_factor) + (
            db_train.current_volume * db_train.volume_cost_factor
    )
    return {
        "current_capacity": {
            "current_weight": db_train.current_weight,
            "current_volume": db_train.current_volume
        },
        "current_cost": current_cost
    }


@train_router.get("/rail-lines", response_model=Dict, status_code=status.HTTP_200_OK)
async def get_operable_rail_lines(db: Session = Depends(get_db), user=Depends(decode_jwt)):
    """
    Get the operable rail lines for the trains operated by the logged-in Train Operator.

    Parameters:
    - db (Session): The database session dependency obtained using FastAPI's dependency injection.
    - user (dict): The user information obtained from the JWT token. Used to check the user's role.

    Returns:
    - Dict: A dictionary containing the operable rail lines for the trains.
    """
    if user.get("user_role") != UserRole.TRAIN_OPERATOR:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not authorized"
        )
    query = await db.execute(select(Train).where(and_(  # noqa
        Train.operator_id == user.get("user_id"),
        Train.is_active
    )))
    db_trains = query.scalars().all()
    if not db_trains:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Train not found")

    return {"operable_lines": [train.available_lines for train in db_trains if train.available_lines]}


@train_router.get("/train_id/status", response_model=TrainStatusResponse, status_code=status.HTTP_200_OK)
async def get_train_status(train_id: str, db: Session = Depends(get_db), user=Depends(decode_jwt)):
    """
    Get the status, assigned line, departure time, and parcel information for a specific train.

    Parameters:
    - train_id (str): The ID of the train for which information is requested.
    - db (Session): The database session dependency obtained using FastAPI's dependency injection.
    - user (dict): The user information obtained from the JWT token. Used to check the user's role.

    Returns:
    - A dictionary containing the train's status, assigned line, departure time, and parcel information.
    """
    if user.get("user_role") != UserRole.TRAIN_OPERATOR:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not authorized to view train status"
        )

    query = (
        await db.execute(  # noqa
            select(Train)
            .options(selectinload(Train.parcels))
            .where(Train.id == train_id)
        )
    )
    db_train = query.scalars().one_or_none()

    if not db_train:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Train not found")

    train_status = {
        "status": db_train.status,
        "assigned_line": db_train.assigned_line if db_train.assigned_line else None,
        "departure_time": db_train.departure_time.strftime("%Y-%m-%d %H:%M:%S") if db_train.departure_time else None,
        "parcels": [
            {
                "parcel_id": parcel.id,
                "weight": parcel.weight,
                "volume": parcel.volume,
                "destination": parcel.destination,
            }
            for parcel in db_train.parcels
        ] if db_train.status == TrainStatus.AVAILABLE else None
    }
    return train_status


@train_router.get("/train_id", response_model=TrainResponse, status_code=status.HTTP_200_OK)
async def get_train(train_id: str, db: Session = Depends(get_db), user=Depends(decode_jwt)):
    """
    Retrieve information about a specific train.

    Parameters:
    - train_id (str): The ID of the train to be retrieved.
    - db (Session): The database session dependency obtained using FastAPI's dependency injection.
    - user (dict): The user information obtained from the JWT token.

    Returns:
    - TrainResponse: A Pydantic model containing information about the requested train.
    """
    query = await db.execute(select(Train).where(Train.id == train_id, Train))  # noqa
    db_train = query.scalars().one_or_none()
    if not db_train:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Train not found")
    return db_train


@train_router.delete("/train_id", response_model=Dict, status_code=status.HTTP_200_OK)
async def withdraw_offer(train_id: str, db: Session = Depends(get_db), user=Depends(decode_jwt)):
    """
    Withdraw offer of a specific train.

    Parameters:
    - train_id (str): The ID of the train to be deleted.
    - db (Session): The database session dependency obtained using FastAPI's dependency injection.
    - user (dict): The user information obtained from the JWT token.

    Returns:
    - None: Returns a 204 status code if the train is successfully deleted.
    """
    query = await db.execute(select(Train).where(Train.id == train_id))  # noqa
    db_train = query.scalars().one_or_none()
    if not db_train:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Train not found")
    if db_train.status != "available":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete a train that is not available"
        )
    db_train.is_active = False
    db_train.status = TrainStatus.UNAVAILABLE
    await db.commit()  # noqa
    return {"message": f"train with ID:{train_id} has been withdrawn"}


@train_router.post("/offer", response_model=TrainResponse, status_code=status.HTTP_201_CREATED)
async def train_operator_post_offer(train_data: TrainCreate, db: Session = Depends(get_db), user=Depends(decode_jwt)):
    """
    Train Operator posts an offer for a train.

    Parameters:
    - train_data (TrainCreate): The Pydantic model representing the details of the train offer.
    - db (Session): The database session dependency obtained using FastAPI's dependency injection.
    - user (dict): The user information obtained from the JWT token. Used to check the user's role.

    Raises:
    - HTTPException with a 401 status code if the user is not authorized as a Train Operator.

    Returns:
    - TrainResponse: A Pydantic model containing information about the posted train offer.
    """
    if user.get("user_role") != UserRole.TRAIN_OPERATOR:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not authorized as a Train Operator"
        )

    new_train_offer = Train(**train_data.model_dump(), operator_id=user.get("user_id"))
    db.add(new_train_offer)
    await db.commit()  # noqa

    return new_train_offer


@train_router.get("/all", response_model=List[TrainResponse], status_code=status.HTTP_200_OK)
async def get_all_trains(db: Session = Depends(get_db), user=Depends(decode_jwt)):
    """
    Retrieve a list of available trains.

    Parameters:
    - db (Session): The database session dependency obtained using FastAPI's dependency injection.
    - user (dict): The user information obtained from the JWT token. Used to check the user's role.

    Returns:
    - A list of TrainResponse objects representing the available trains.
    """
    if user.get("user_role") != UserRole.POST_MASTER:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not authorized as a Post Master"
        )
    query = await db.execute(select(Train).where(and_(  # noqa
        Train.status == TrainStatus.AVAILABLE
    )))
    db_trains = query.scalars().all()
    if not db_trains:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Train not found")
    return db_trains


@train_router.post("/train_id/book-fill-send", response_model=TrainResponse, status_code=status.HTTP_201_CREATED)
async def post_master_book_fill_send(train_id: str, db: Session = Depends(get_db), user=Depends(decode_jwt)):
    """
    Post Master books, fills, and sends a train.

    Parameters:
    - train_id (str): The ID of the train to be booked, filled, and sent.
    - db (Session): The database session dependency obtained using FastAPI's dependency injection.
    - user (dict): The user information obtained from the JWT token. Used to check the user's role.

    Raises:
    - HTTPException with a 401 status code if the user is not authorized as a Post Master.

    Returns:
    - TrainResponse: A Pydantic model containing information about the booked, filled, and sent train.
    """
    if user.get("user_role") != UserRole.POST_MASTER:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not authorized as a Post Master"
        )

    train_offer = await db.execute(select(Train).where(and_(  # noqa
        Train.id == train_id,
        Train.operator_id != user.get("user_id"),
        Train.status == TrainStatus.AVAILABLE
    )))
    db_train_offer = train_offer.scalars().first()

    if not db_train_offer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Train offer not found or not available")

    await assign_parcels_to_train(db, db_train_offer)

    assigned_parcels = await db.execute(select(Parcel).where(Parcel.train_id == train_id))  # noqa
    assigned_parcels = assigned_parcels.scalars().all()

    for parcel in assigned_parcels:
        db_train_offer.current_weight += parcel.weight
        db_train_offer.current_volume += parcel.volume

    db_train_offer.status = TrainStatus.SENT
    db_train_offer.departure_time = datetime.now()

    await db.commit()  # noqa

    return db_train_offer
