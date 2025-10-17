from datetime import datetime
from sqlalchemy import (
    Column, String, Text,DateTime
)
from sqlalchemy.orm import relationship
from backend.database.models.base import Base
from sqlalchemy import Float, ForeignKey
import uuid
class Node(Base):
    __tablename__ = "nodes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    color = Column(String(32))
    x = Column(Float)
    y = Column(Float)
    parent_id = Column(String, ForeignKey("nodes.id", ondelete="CASCADE"), nullable=True)
    mindmap_id = Column(String, ForeignKey("mindmaps.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    mindmap = relationship("Mindmap", back_populates="nodes")
    children = relationship("Node", cascade="all, delete-orphan", remote_side=[id])
