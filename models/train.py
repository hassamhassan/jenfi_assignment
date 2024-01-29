from sqlalchemy import Column, String, Float, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship

from common.enums import TrainStatus
from models.base import BaseModel


class Train(BaseModel):
    __tablename__ = "trains"

    operator_id = Column(String, ForeignKey("users.id"), nullable=False)
    weight_cost_factor = Column(Float, nullable=False)
    volume_cost_factor = Column(Float, nullable=False)
    cost = Column(Float, nullable=True, default=0)
    max_weight = Column(Float, nullable=False)
    max_volume = Column(Float, nullable=False)
    current_weight = Column(Float, nullable=False, default=0)
    current_volume = Column(Float, nullable=False, default=0)
    available_lines = Column(String, nullable=False)
    assigned_line = Column(String, nullable=True)
    status = Column(Enum(TrainStatus), nullable=False)
    departure_time = Column(DateTime, nullable=True)

    train_operator = relationship("User", back_populates="trains")
    parcels = relationship("Parcel", back_populates="train")
