from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from common.enums import TrainStatus


class TrainCreate(BaseModel):
    weight_cost_factor: float
    volume_cost_factor: float
    max_weight: float
    max_volume: float
    available_lines: str
    status: TrainStatus


class TrainResponse(TrainCreate):
    id: str
    operator_id: str
    created_at: datetime
    updated_at: datetime
    is_active: bool


class TrainSchedule(BaseModel):
    train_id: str
    estimated_departure_time: datetime
    assigned_line: str


class ParcelInfo(BaseModel):
    parcel_id: str
    weight: float
    volume: float
    destination: str


class TrainStatusResponse(BaseModel):
    status: Optional[str]
    assigned_line: Optional[str]
    departure_time: Optional[str]
    parcels: Optional[List[ParcelInfo]]


class TrainCapacity(BaseModel):
    current_weight: float
    current_volume: float


class TrainCapacityCostResponse(BaseModel):
    current_capacity: TrainCapacity
    current_cost: float
