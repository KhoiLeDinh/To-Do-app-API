from datetime import datetime
from pydantic import BaseModel, Field 
from typing import Optional

class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TodoCreate(BaseModel):
    title: str = Field(min_length=1, max_length = 255)
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    completed: bool = False

class TodoResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    created_at: datetime
    deadline: Optional[datetime]
    completed: bool
    past_deadline: bool

    class Config:
        from_attributes = True

class TodoUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    completed: Optional[bool] = None
