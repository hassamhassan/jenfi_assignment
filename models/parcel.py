from sqlalchemy import Column, String, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from models.base import BaseModel
from models.train import Train


class Parcel(BaseModel):
    __tablename__ = "parcels"

    owner_id = Column(String, ForeignKey("users.id"), nullable=False)
    weight = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    destination = Column(String, nullable=False)
    has_shipped = Column(Boolean, nullable=False, default=False)
    train_id = Column(String, ForeignKey("trains.id"), nullable=True)

    parcel_owner = relationship("User", back_populates="parcels")
    train = relationship("Train", back_populates="parcels")

    def calculate_shipping_cost(self, train: Train) -> float:
        weight_cost_factor = train.weight_cost_factor
        volume_cost_factor = train.volume_cost_factor

        cost = self.weight * weight_cost_factor + self.volume * volume_cost_factor

        return cost
