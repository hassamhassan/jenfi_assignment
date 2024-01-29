from datetime import datetime

from pydantic import BaseModel


class ParcelCreate(BaseModel):
    weight: float
    volume: float
    destination: str
    # has_shipped: bool = False


class ParcelResponse(ParcelCreate):
    id: str
    owner_id: str
    created_at: datetime
    updated_at: datetime
    is_active: bool
