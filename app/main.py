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
    return {
        "id": new_todo.id,
        "title": decrypt_text(new_todo.title),
        "description": decrypt_text(new_todo.description),
        "deadline": new_todo.deadline,
        "created_at": new_todo.created_at,
        "completed": new_todo.completed,
        "past_deadline": new_todo.past_deadline
    }

@app.get("/api/v1/todos", response_model = list[TodoResponse])
def get_todos(
    skip: int = 0,
    limit: int = 10,
    keyword: Optional[str] = None,
    sort_by_deadline: bool = False,
    db: Session=Depends(get_db)):
    query = db.query(Todo)
    
    if sort_by_deadline:
        query = query.order_by(Todo.deadline.asc())
        
    todos = query.offset(skip).limit(limit).all()
    
    result = []
    for todo in todos:
        decrypted_title = decrypt_text(todo.title)
        decrypted_desc = decrypt_text(todo.description)
        
        if keyword:
            keyword_lower = keyword.lower()
            if keyword_lower not in decrypted_title.lower() and keyword_lower not in decrypted_desc.lower():
                continue
                
        result.append({
            "id": todo.id,
            "title": decrypted_title,
            "description": decrypted_desc,
            "deadline": todo.deadline,
            "created_at": todo.created_at,
            "completed": todo.completed,
            "past_deadline": todo.past_deadline
        })
        
    return result

@app.delete("/api/v1/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int, db: Session=Depends(get_db)):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    db.delete(todo)
    db.commit()
    return None

@app.put("/api/v1/todos/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, todo_update: TodoUpdate, db: Session=Depends(get_db)):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")

    if todo_update.title is not None:
        todo.title = encrypt_text(todo_update.title)
    if todo_update.description is not None:
        todo.description = encrypt_text(todo_update.description)
    if todo_update.deadline is not None:
        todo.deadline = todo_update.deadline
    if todo_update.completed is not None:
        todo.completed = todo_update.completed

    db.commit()
    db.refresh(todo)
    return {
        "id": todo.id,
        "title": decrypt_text(todo.title),
        "description": decrypt_text(todo.description),
        "deadline": todo.deadline,
        "created_at": todo.created_at,
        "completed": todo.completed,
        "past_deadline": todo.past_deadline
    }