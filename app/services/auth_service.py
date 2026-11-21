from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.core.security import create_access_token, hash_password, verify_password
from app.models.users import User
from app.schemas.todo import Token, UserCreate

def register_user(payload: UserCreate, db: Session):
    existing_user = db.query(User).filter(User.username == payload.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already existed",
        )
    new_user = User(
        username=payload.username,
        hashed_password=hash_password(payload.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    db.close()
    return new_user

def login_user(payload: UserCreate, db: Session):
    db_user = db.query(User).filter(User.username == payload.username).first()
    if not db_user or not verify_password(payload.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user credentials"
        )
    access_token = create_access_token(data={"sub": str(db_user.username)})
    return Token(access_token=access_token, token_type="bearer")