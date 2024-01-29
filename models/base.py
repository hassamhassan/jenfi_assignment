import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Boolean, String

from database.db import Base


class BaseModel(Base):
    __abstract__ = True

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=True, default=datetime.now, onupdate=datetime.now)
    is_active = Column(Boolean, nullable=False, default=True)



