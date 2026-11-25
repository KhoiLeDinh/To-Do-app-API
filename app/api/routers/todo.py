from fastapi import APIRouter, Depends, status, Header, HTTPException, Response, status
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from app.api.deps import get_current_user, get_redis
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
IDEMPOTENCY_LOCK_TTL_SECONDS = 60

def hash_payload(payload_dict:dict) -> str:
    canonical = json.dumps(payload_dict, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

def cached_json_response(raw: str, payload_hash: str) -> JSONResponse:
    data = json.loads(raw)

    if data.get("state") == "processing":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Request with this Idempotency-Key is already in progress.",
        )

    if data.get("payload_hash") != payload_hash:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Idempotency-Key reused with a different payload.",
        )

    return JSONResponse(
        status_code=data["status_code"],
        content=data["response_body"],
    )

@router.post("", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
def create_todo(
    todo: TodoCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    redis_client = Depends(get_redis),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key")
):
    payload_hash = hash_payload(todo.model_dump(mode="json"))
    if not idempotency_key:
        created = create_todo_item(
        payload=todo,
        current_user=current_user,
        db=db,
        )
        return TodoResponse.model_validate(created)

    redis_key = f"idem:post_todos:{current_user.id}:{idempotency_key}"

    existing_raw = redis_client.get(redis_key)
    if existing_raw:
        return cached_json_response(existing_raw, payload_hash)

    lock_data = json.dumps({"state": "processing", "payload_hash": payload_hash})
    acquired = redis_client.set(redis_key, lock_data, nx=True, ex=IDEMPOTENCY_LOCK_TTL_SECONDS)
    if not acquired:
        raced_raw = redis_client.get(redis_key)
        if raced_raw:
            return cached_json_response(raced_raw, payload_hash)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Request with this Idempotency-Key is already in progress.",
        )

    try:
        created = create_todo_item(
                payload=todo,
                current_user=current_user,
                db=db,
                )
        body = TodoResponse.model_validate(created).model_dump(mode="json")

        completed_data = json.dumps(
            {
                "state": "completed",
                "payload_hash": payload_hash,
                "status_code": status.HTTP_201_CREATED,
                "response_body": body,
            },
            ensure_ascii=False,
        )
        redis_client.set(redis_key, completed_data, ex=IDEMPOTENCY_TTL_SECONDS)
        return JSONResponse(status_code=status.HTTP_201_CREATED, content=body)
    except Exception:
        redis_client.delete(redis_key)
        raise 

        
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
