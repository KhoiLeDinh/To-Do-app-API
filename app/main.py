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
        
    # Lấy toàn bộ kết quả phân trang từ DB trước
    todos = query.offset(skip).limit(limit).all()
    
    result = []
    for todo in todos:
        decrypted_title = decrypt_text(todo.title)
        decrypted_desc = decrypt_text(todo.description)
        
        # Nếu có từ khóa, tiến hành lọc bằng Python ở phía ứng dụng
        if keyword:
            keyword_lower = keyword.lower()
            if keyword_lower not in decrypted_title.lower() and keyword_lower not in decrypted_desc.lower():
                continue # Bỏ qua nếu không khớp từ khóa
                
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