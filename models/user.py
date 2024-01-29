from sqlalchemy import Column, String, Enum
from sqlalchemy.orm import relationship

from common.enums import UserRole
from models.base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)

    trains = relationship("Train", back_populates="train_operator")
    parcels = relationship("Parcel", back_populates="parcel_owner")
