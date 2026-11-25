from fastapi import FastAPI
from app.api.routers import auth, todo
from app.core.database import Base, engine
from app.models import todo as todo_model, users as users_model  # noqa: F401

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Todo API")

app.include_router(auth.router, prefix="/api/v1")
app.include_router(todo.router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok"}