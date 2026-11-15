from fastapi import FastAPI
from app.core.database import get_db
from app.core.security import encrypt_text, decrypt_text
from app.models.todo import Todo
from app.schemas.todo import TodoCreate, TodoResponse, TodoUpdate
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text, or_
from typing import Optional

app = FastAPI()

@app.post("/api/v1/todos", response_model = TodoResponse, status_code=status.HTTP_201_CREATED)
def create_todo(todo: TodoCreate, db: Session=Depends(get_db)):
    new_todo = Todo(
        title = encrypt_text(todo.title),
        description = encrypt_text(todo.description),
        deadline = todo.deadline
    )
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo 