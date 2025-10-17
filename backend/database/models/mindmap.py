from datetime import datetime
from sqlalchemy import (
    Column, String, Text,DateTime
)
from sqlalchemy.orm import relationship
from backend.database.models.base import Base
import uuid
class Mindmap(Base):
    __tablename__ = "mindmaps"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    nodes = relationship("Node", back_populates="mindmap", cascade="all, delete-orphan")
