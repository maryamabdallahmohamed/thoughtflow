from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class NodeBase(BaseModel):
    title: str
    description: Optional[str] = None
    color: Optional[str] = "#3b82f6"
    x: Optional[float] = 0.0
    y: Optional[float] = 0.0
    parent_id: Optional[str] = None


class NodeCreate(NodeBase):
    mindmap_id: str


class NodeRead(NodeBase):
    id: str
    created_at: datetime
    updated_at: datetime
    children: List["NodeRead"] = []

    class Config:
        orm_mode = True


NodeRead.update_forward_refs()


class MindmapBase(BaseModel):
    title: str
    description: Optional[str] = None


class MindmapCreate(MindmapBase):
    pass


class MindmapRead(MindmapBase):
    id: str
    created_at: datetime
    updated_at: datetime
    nodes: List[NodeRead] = []

    class Config:
        orm_mode = True
