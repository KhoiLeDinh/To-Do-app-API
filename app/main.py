from fastapi import FastAPI
from app.api.routers import auth, todo

app = FastAPI(title="Todo API")

app.include_router(auth.router, prefix="/api/v1")
app.include_router(todo.router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok"}