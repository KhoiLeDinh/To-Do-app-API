from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.users import User
from app.schemas.todo import TodoCreate, TodoResponse, TodoUpdate
from app.services.todo_service import (
    create_todo_item,
    delete_todo_item,
    list_todo_items,
    update_todo_item,
)
import hashlib
import json


router = APIRouter(prefix="/todos", tags=["todos"])

IDEMPOTENCY_TTL_SECONDS = 86400

def hash_payload(payload_dict:dict) -> str:
    canonical = json.dumps(payload_dict, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

@router.post("", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
def create_todo(
    todo: TodoCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return create_todo_item(payload=todo, current_user = current_user, db=db)

@router.get("", response_model=list[TodoResponse])
def get_todo(
    skip: int = 0,
    limit: int = 10,
    keyword: str | None = None, 
    sort_by_deadline: bool = False,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return list_todo_items(current_user=current_user,
                           db=db,
                           skip=skip,
                           limit=limit,
                           keyword=keyword,
                           sort_by_deadline=sort_by_deadline,
                           )

@router.put("{todo_id}", response_model=TodoResponse)
def update_todo(
    todo_id: int, 
    todo_update: TodoUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return update_todo_item(
        todo_id = todo_id,
        payload = todo_update,
        current_user = current_user,
        db=db
    )

@router.delete("{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(
    todo_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return delete_todo_item(
        todo_id=todo_id,
        current_user=current_user,
        db=db
    )
