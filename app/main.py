from fastapi import FastAPI
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings
from app.core.database import get_db
import jwt 
from app.core.security import encrypt_text, decrypt_text, hash_password, verify_password, create_access_token
from app.models.todo import Todo, User
from app.schemas.todo import TodoCreate, TodoResponse, TodoUpdate, UserResponse, UserCreate, Token
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text, or_
from typing import Optional
from app.core.database import engine, Base
from app.models.todo import User, Todo
from datetime import datetime, timezone


app = FastAPI()

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

@app.post("/register", response_model = UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session=Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")

    new_user = User(
        username = user.username,
        hashed_password = hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login", response_model = Token)
def login(user: UserCreate, db: Session=Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    access_token = create_access_token(data={"sub": str(db_user.username)})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/v1/todos", response_model = TodoResponse, status_code=status.HTTP_201_CREATED)
def create_todo(todo: TodoCreate, current_user: User=Depends(get_current_user), db: Session=Depends(get_db)):
    # Sử dụng thời gian local thuần túy không kèm tzinfo để khớp hoàn toàn với Postgres
    now_local = datetime.now()
    is_past = todo.deadline.replace(tzinfo=None) < now_local if todo.deadline else False

    new_todo = Todo(
        title = encrypt_text(todo.title),
        description = encrypt_text(todo.description),
        deadline = todo.deadline,
        completed = False,
        past_deadline = is_past,
        user_id = current_user.id
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
    current_user: User=Depends(get_current_user),
    db: Session=Depends(get_db)):
    query = db.query(Todo).filter(Todo.user_id == current_user.id) 
    
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
def delete_todo(todo_id: int, current_user: User=Depends(get_current_user), db: Session=Depends(get_db)):
    todo = db.query(Todo).filter(Todo.id == todo_id, Todo.user_id == current_user.id).first()
    if not todo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    db.delete(todo)
    db.commit()
    return None

@app.put("/api/v1/todos/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, todo_update: TodoUpdate, current_user: User=Depends(get_current_user), db: Session=Depends(get_db)):
    todo = db.query(Todo).filter(Todo.id == todo_id, Todo.user_id == current_user.id).first()
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