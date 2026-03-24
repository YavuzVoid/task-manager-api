from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
from app.database import get_db
from app.auth import get_current_user
from app.models.user import User
from app.models.task import Task, Priority, Status
from app.models.project import Project
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/", response_model=TaskResponse, status_code=201)
def create_task(data: TaskCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if data.project_id:
        project = db.query(Project).filter(Project.id == data.project_id, Project.owner_id == user.id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Proje bulunamadı")
    task = Task(
        title=data.title, description=data.description, priority=data.priority,
        status=data.status, deadline=data.deadline, project_id=data.project_id, owner_id=user.id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.get("/", response_model=List[TaskResponse])
def list_tasks(
    status: Optional[Status] = None,
    priority: Optional[Priority] = None,
    project_id: Optional[int] = None,
    search: Optional[str] = None,
    overdue: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = db.query(Task).filter(Task.owner_id == user.id)
    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)
    if project_id:
        query = query.filter(Task.project_id == project_id)
    if search:
        query = query.filter(Task.title.ilike(f"%{search}%"))
    if overdue:
        query = query.filter(Task.deadline < datetime.now(timezone.utc), Task.status != Status.DONE)
    return query.order_by(Task.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return _get_own_task(task_id, user.id, db)


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, data: TaskUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    task = _get_own_task(task_id, user.id, db)
    if data.project_id is not None:
        project = db.query(Project).filter(Project.id == data.project_id, Project.owner_id == user.id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Proje bulunamadı")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    task = _get_own_task(task_id, user.id, db)
    db.delete(task)
    db.commit()


def _get_own_task(task_id: int, user_id: int, db: Session) -> Task:
    task = db.query(Task).filter(Task.id == task_id, Task.owner_id == user_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Görev bulunamadı")
    return task
