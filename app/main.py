from fastapi import FastAPI
from app.database import engine, Base
from app.routes.auth import router as auth_router
from app.routes.project import router as project_router
from app.routes.task import router as task_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Task Manager API",
    description="Görev ve proje yönetimi API'si",
    version="1.0.0",
)

app.include_router(auth_router)
app.include_router(project_router)
app.include_router(task_router)


@app.get("/health")
def health_check():
    return {"status": "ok", "version": "1.0.0", "service": "task-manager-api"}
