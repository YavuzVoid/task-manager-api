from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.auth import get_current_user
from app.models.user import User
from app.models.project import Project
from app.models.task import Task
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("/", response_model=ProjectResponse, status_code=201)
def create_project(data: ProjectCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    project = Project(name=data.name, description=data.description, owner_id=user.id)
    db.add(project)
    db.commit()
    db.refresh(project)
    return _project_with_count(project, db)


@router.get("/", response_model=List[ProjectResponse])
def list_projects(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    projects = db.query(Project).filter(Project.owner_id == user.id).all()
    return [_project_with_count(p, db) for p in projects]


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    project = _get_own_project(project_id, user.id, db)
    return _project_with_count(project, db)


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: int, data: ProjectUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    project = _get_own_project(project_id, user.id, db)
    if data.name is not None:
        project.name = data.name
    if data.description is not None:
        project.description = data.description
    db.commit()
    db.refresh(project)
    return _project_with_count(project, db)


@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    project = _get_own_project(project_id, user.id, db)
    db.delete(project)
    db.commit()


def _get_own_project(project_id: int, user_id: int, db: Session) -> Project:
    project = db.query(Project).filter(Project.id == project_id, Project.owner_id == user_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Proje bulunamadı")
    return project


def _project_with_count(project: Project, db: Session) -> dict:
    count = db.query(Task).filter(Task.project_id == project.id).count()
    return ProjectResponse(
        id=project.id, name=project.name, description=project.description,
        owner_id=project.owner_id, created_at=project.created_at, task_count=count,
    )
