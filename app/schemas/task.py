from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.task import Priority, Status


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    priority: Optional[Priority] = Priority.MEDIUM
    status: Optional[Status] = Status.TODO
    deadline: Optional[datetime] = None
    project_id: Optional[int] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[Priority] = None
    status: Optional[Status] = None
    deadline: Optional[datetime] = None
    project_id: Optional[int] = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    priority: Priority
    status: Status
    deadline: Optional[datetime]
    owner_id: int
    project_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
