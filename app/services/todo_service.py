from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.core.security import decrypt_text, encrypt_text
from app.core.time import to_utc, utcnow
from app.models.todo import Todo
from app.models.users import User
from app.schemas.todo import TodoCreate, TodoResponse, TodoUpdate

def _to_todo_response(todo: Todo) -> TodoResponse:
    return TodoResponse(
        id=todo.id,
        title=decrypt_text(todo.title) or "",
        description=todo.description,
        deadline=todo.deadline,
        created_at=todo.created_at,
        completed=todo.completed,
        past_deadline=todo.past_deadline,
    )

def _get_owned_todo(todo_id: int, current_user: User, db: Session) -> Todo:
    todo = db.query(Todo).filter(Todo.id == todo_id, Todo.user_id == current_user.id).first()
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return todo 

def create_todo_item(payload: TodoCreate, current_user: User, db: Session) -> TodoResponse:
    deadline_utc = to_utc(payload.deadline)
    is_past = deadline_utc < utcnow() if deadline_utc is not None else False

    new_todo = Todo(
        title=encrypt_text(payload.title),
        description=encrypt_text(payload.description),
        deadline=deadline_utc,
        completed=False,
        past_deadline=is_past,
        user_id=current_user.id,
    )
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return _to_todo_response(new_todo)