from fastapi import FastAPI
from app.api.routers import auth, todo

app = FastAPI(title="Todo API")

app.include_router(auth.router)
app.include_router(todo.router)


@app.get("/health")
def health():
    return {"status": "ok"}