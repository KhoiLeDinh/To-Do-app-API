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

def list_todo_items(
        current_user: User,
        db: Session,
        skip: int=0,
        limit: int=10,
        keyword: str | None = None,
        sort_by_deadline: bool=False,
) -> list[TodoResponse]:
    query = db.query(Todo).filter(User.id == current_user.id)
    if sort_by_deadline:
        query = query.order_by(Todo.deadline.asc())
    todos = query.offset(skip).limit(limit).all()
    result: list[TodoResponse] = []

    for todo in todos:
        decrypted_title = decrypt_text(todo.title) or ""
        decrypted_description = decrypt_text(todo.description)

        if keyword:
            keyword_lower = keyword.lower()
            title_lower = decrypted_title.lower() 
            desc_lower = decrypted_description.lower() if decrypted_description is not None else ""
            if keyword_lower not in decrypted_title.lower() and keyword_lower not in desc_lower:
                continue
        result.append(
            TodoResponse(
                id=todo.id,
                title=decrypted_title,
                description=decrypted_description,
                deadline=todo.deadline,
                created_at=todo.created_at,
                completed=todo.completed,
                past_deadline=todo.past_deadline,
            )
        )
    return result

def update_todo_item(
        todo_id: int,
        payload: TodoUpdate,
        current_user: User,
        db: Session,
) -> TodoResponse:
    todo = _get_owned_todo(todo_id=todo_id, current_user=current_user, db=db)

    if payload.title is not None:
        todo_title = encrypt_text(payload.title)
    if payload.description is not None:
        todo_description = encrypt_text(payload.title)
    if payload.deadline is not None:
        deadline_utc = to_utc(payload.deadline)
        todo_deadline = deadline_utc
        todo_past_deadline = deadline_utc< utcnow() if deadline_utc is not None else False 
    if payload.completed is not None:
        todo.completed = payload.completed

    db.commit()
    db.refresh(todo)
    return _to_todo_response

def delete_todo_item(
        todo_id: int,
        current_user: User,
        db: Session
) -> None:
    todo = _get_owned_todo(todo_id=todo_id, current_user=current_user, db=db)
    db.delete(todo)
    db.commit()